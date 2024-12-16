from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from TAScheduler.models import TA, Administrator, Course, Instructor, Section, User
from django.core.exceptions import PermissionDenied
from django.db.models.deletion import ProtectedError


class AssignInstructorToCourseTest(TestCase):
        def setUp(self):
            # Create instructor users
            self.instructor1 = Instructor.objects.create(
                username="instructor1",
                email_address="instructor1@example.com",
                first_name="John",
                last_name="Doe",
                is_instructor=True,
                max_assignments=3,
            )
            self.instructor1.set_password("password123")
            self.instructor1.save()

            self.instructor2 = Instructor.objects.create(
                username="instructor2",
                email_address="instructor2@example.com",
                first_name="Jane",
                last_name="Smith",
                is_instructor=True,
                max_assignments=3,
            )
            self.instructor2.set_password("password123")
            self.instructor2.save()

            # Create a course
            self.course = Course.objects.create(
                course_id="CS101",
                semester="Fall 2024",
                name="Introduction to Computer Science",
                description="A beginner's course in computer science.",
                num_of_sections=3,
                modality="In-person",
            )

class CourseCreationTest(TestCase):
    def setUp(self):
        self.valid_course_data = {
            "course_id": "CS101",
            "semester": "Fall 2024",
            "name": "Introduction to Computer Science",
            "description": "A beginner's course in computer science.",
            "num_of_sections": 3,
            "modality": "In-person",
        }

    def test_create_valid_course(self):
        course = Course.objects.create(**self.valid_course_data)
        self.assertIsNotNone(course.id, "Course ID should not be None after successful creation.")
        self.assertEqual(course.course_id, self.valid_course_data["course_id"])
        self.assertEqual(course.name, self.valid_course_data["name"])

    def test_missing_required_fields_raises_integrity_error(self):
        with self.assertRaises(IntegrityError):
            Course.objects.create(modality="In-person")  # Missing required fields

    def test_course_id_exceeding_max_length_raises_validation_error(self):
        course_data_override = {**self.valid_course_data, "course_id": "C" * 21}  # Exceed max length
        with self.assertRaises(ValidationError):
            course = Course(**course_data_override)
            course.full_clean()  # Validate fields before saving

    def test_duplicate_course_id_raises_integrity_error(self):
        Course.objects.create(**self.valid_course_data)
        with self.assertRaises(IntegrityError):
            Course.objects.create(**self.valid_course_data)  # Duplicate course ID

    def test_course_creation_with_special_characters_in_fields(self):
        course = Course.objects.create(
            course_id="CS-101!",
            semester="Fall 2024",
            name="Intro to CS @2024",
            description="A beginner's course with symbols.",
            num_of_sections=3,
            modality="Online",
        )
        self.assertEqual(course.course_id, "CS-101!")
        self.assertEqual(course.name, "Intro to CS @2024")

    def test_course_creation_with_empty_description(self):
        course = Course.objects.create(
            course_id="CS107",
            semester="Fall 2024",
            name="Intro to CS",
            description="",  # Empty description
            num_of_sections=3,
            modality="Online",
        )
        self.assertEqual(course.description, "")

    def test_case_insensitive_course_id_lookup(self):
        Course.objects.create(**self.valid_course_data)
        course = Course.objects.get(course_id="cs101".upper())  # Perform case-insensitive lookup
        self.assertEqual(course.name, self.valid_course_data["name"])

class CourseEditingTest(TestCase):
    def setUp(self):
        # Admin user
        self.admin_user = Administrator.objects.create(
            username="admin_user_1",
            email_address="admin1@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        self.admin_user.set_password("adminpassword")
        self.admin_user.save()

        # Instructor user
        self.instructor_user = Instructor.objects.create(
            username="instructor_user_1",
            email_address="instructor1@example.com",
            first_name="Instructor",
            last_name="User",
            is_instructor=True
        )
        self.instructor_user.set_password("instructorpassword")
        self.instructor_user.save()

        # TA user
        self.ta_user = TA.objects.create(
            username="ta_user_1",
            email_address="ta1@example.com",
            first_name="TA",
            last_name="User",
            is_ta=True
        )
        self.ta_user.set_password("tapassword")
        self.ta_user.save()

        # Regular user
        self.regular_user = User.objects.create(
            username="regular_user_1",
            email_address="regular1@example.com",
            first_name="Regular",
            last_name="User"
        )
        self.regular_user.set_password("regularpassword")
        self.regular_user.save()

        # Course
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person"
        )

        self.edit_url = reverse("edit-course", args=[self.course.course_id])

    def create_unique_user_and_instructor(self, username_prefix):
        """
        Helper method to create a unique user and associated instructor.
        """
        username = f"{username_prefix}_{self._testMethodName}"
        email = f"{username}@example.com"
        user = User.objects.create_user(
            username=username,
            email=email,
            password="password123",
            first_name="Test",
            last_name="User"
        )
        return Instructor.objects.create(id=user.id, max_assignments=5)

class CourseDatabaseTest(TestCase):
    def setUp(self):
        self.course_data = {
            "course_id": "CS101",
            "semester": "Fall 2024",
            "name": "Introduction to Computer Science",
            "description": "A beginner's course in computer science.",
            "num_of_sections": 3,
            "modality": "In-person",
        }

    def test_save_and_retrieve_course(self):
        # Create a course and save it to the database
        course = Course.objects.create(**self.course_data)

        # Retrieve the saved course from the database
        saved_course = Course.objects.get(course_id=self.course_data["course_id"])

        # Assertions
        self.assertEqual(saved_course.name, self.course_data["name"])
        self.assertEqual(saved_course.semester, self.course_data["semester"])
        self.assertEqual(saved_course.description, self.course_data["description"])
        self.assertEqual(saved_course.num_of_sections, self.course_data["num_of_sections"])
        self.assertEqual(saved_course.modality, self.course_data["modality"])

    def test_create_course_and_save_to_database(self):
        # Create a course and save it to the database
        course = Course.objects.create(**self.course_data)

        # Verify the course has been saved correctly
        self.assertIsNotNone(course.id)  # Ensure the course ID is not None (saved in DB)
        saved_course = Course.objects.get(course_id="CS101")  # Retrieve course

        # Assertions
        self.assertEqual(saved_course.name, self.course_data["name"])
        self.assertEqual(saved_course.semester, self.course_data["semester"])
        self.assertEqual(saved_course.description, self.course_data["description"])
        self.assertEqual(saved_course.num_of_sections, self.course_data["num_of_sections"])
        self.assertEqual(saved_course.modality, self.course_data["modality"])
        self.assertEqual(Course.objects.count(), 1)  # Ensure only one course exists

class CourseRemovalTest(TestCase):

    def test_remove_course_from_database(self):
        course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person",
        )
        self.assertTrue(Course.objects.filter(id=course.id).exists())
        course.delete()
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    def test_remove_nonexistent_course(self):
        with self.assertRaises(Course.DoesNotExist):
            Course.objects.get(id=999).delete()

    def test_remove_course_cascade_delete(self):
        course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person",
        )
        section = Section.objects.create(
            section_id=1,
            course=course,
            location="Room 101",
            meeting_time="Monday 10AM",
        )
        course.delete()
        self.assertFalse(Course.objects.filter(id=course.id).exists())
        self.assertFalse(Section.objects.filter(id=section.id).exists())

    def test_remove_all_courses(self):
        Course.objects.bulk_create(
            [
                Course(
                    course_id=f"CS10{i}",
                    semester="Fall 2024",
                    name=f"Course {i}",
                    description="A sample course.",
                    num_of_sections=i,
                    modality="Online" if i % 2 == 0 else "In-person",
                )
                for i in range(1, 6)
            ]
        )
        self.assertEqual(Course.objects.count(), 5)
        Course.objects.all().delete()
        self.assertEqual(Course.objects.count(), 0)

    def test_remove_course_with_long_description(self):
        long_description = "A" * 1000
        course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description=long_description,
            num_of_sections=3,
            modality="In-person",
        )
        course.delete()
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    def test_remove_case_insensitive_exact_match(self):
        course = Course.objects.create(
            course_id="cs101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person",
        )

        # Simulating case-insensitive deletion
        deleted_rows = Course.objects.filter(course_id__iexact="CS101").delete()
        self.assertEqual(deleted_rows[0], 1)  # Number of rows deleted
        self.assertFalse(Course.objects.filter(course_id="cs101").exists())

    def test_remove_case_insensitive_no_match(self):
        deleted_rows = Course.objects.filter(course_id__iexact="MATH101").delete()
        self.assertEqual(deleted_rows[0], 0)  # No rows deleted