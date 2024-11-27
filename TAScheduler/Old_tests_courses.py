from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from TAScheduler.models import Administrator, Course, Instructor, InstructorToCourse, Section, User
from django.core.exceptions import PermissionDenied
from django.db.models.deletion import ProtectedError


class CourseEditPermissionTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create(username="admin", is_admin=True)
        self.admin_user.set_password("adminpassword")
        self.admin_user.save()

        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person",
        )

        self.edit_url = reverse("edit-course", args=[self.course.course_id])
        
                # Instructor user
        self.instructor_user = User.objects.create(
            username="instructor_user",
            email_address="instructor@example.com",
            first_name="Instructor",
            last_name="User",
            is_instructor=True,
        )
        self.instructor_user.set_password("instructorpassword") # Sets hashed password, allowing use of build in Django testing for autherization capabiltiies 
        self.instructor_user.save()

    def test_admin_can_edit_course(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.post(self.edit_url, {
            "name": "Updated Name",
            "description": "Updated Description",
            "num_of_sections": 5,
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Updated Name")
        
    def test_instructor_can_edit_course(self):
    # Log in as instructor
        self.client.login(username="instructor_user", password="instructorpassword")

        # Make a POST request to edit the course
        response = self.client.post(self.edit_url, {
            "name": "Updated Name by Instructor",
            "description": "Updated Description by Instructor",
            "num_of_sections": 5,
        })

        # Check response status
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Fetch the updated course
        updated_course = Course.objects.get(course_id=self.course.course_id)

        # Verify the updates
        self.assertEqual(updated_course.name, "Updated Name by Instructor")
        self.assertEqual(updated_course.description, "Updated Description by Instructor")
        self.assertEqual(updated_course.num_of_sections, 5)




    def test_ta_cannot_edit_course(self):
        self.client.login(username="ta", password="tapassword")
        response = self.client.post(self.edit_url, {
            "name": "TA Attempted Edit",
            "description": "TA Description",
            "num_of_sections": 2,
        })
        self.assertEqual(response.status_code, 302)  # Forbidden
        self.course.refresh_from_db()
        self.assertNotEqual(self.course.name, "TA Attempted Edit")

    def test_regular_user_cannot_edit_course(self):
        self.client.login(username="regular", password="regularpassword")
        response = self.client.post(self.edit_url, {
            "name": "Regular User Attempted Edit",
            "description": "Regular User Description",
            "num_of_sections": 1,
        })
        self.assertEqual(response.status_code, 302)  # Forbidden
        self.course.refresh_from_db()
        self.assertNotEqual(self.course.name, "Regular User Attempted Edit")

    def test_anonymous_user_cannot_edit_course(self):
        response = self.client.post(self.edit_url, {
            "name": "Anonymous User Attempted Edit",
            "description": "Anonymous Description",
            "num_of_sections": 1,
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.course.refresh_from_db()
        self.assertNotEqual(self.course.name, "Anonymous User Attempted Edit")
    
class CourseCreationTest(TestCase):
    def setUp(self):
        self.course_data = {
            "course_id": "CS101",
            "semester": "Fall 2024",
            "name": "Introduction to Computer Science",
            "description": "A beginner's course in computer science.",
            "num_of_sections": 3,
            "modality": "In-person",
        }
        
    def test_course_with_invalid_sections_at_creation(self):
        course = Course(
            course_id="CS202",
            semester="Fall 2024",
            name="Invalid Course",
            description="This course has invalid sections.",
            num_of_sections=-3,  # Invalid
            modality="Online"
        )
        with self.assertRaises(ValidationError) as context:
            course.full_clean()  # Triggers field validation
        self.assertIn("Ensure this value is greater than or equal to 0.", str(context.exception))

    def test_create_course(self):
        course = Course.objects.create(**self.course_data)
        self.assertIsNotNone(course.id, "Course ID should not be None after creation.")
        self.assertEqual(course.course_id, self.course_data["course_id"])

    def test_create_course_missing_required_fields(self):
        with self.assertRaises(IntegrityError):
            Course.objects.create(modality="In-person")

    def test_create_course_invalid_field_length(self):
        long_course_id = "C" * 21
        course_data_override = {**self.course_data, "course_id": long_course_id}
        with self.assertRaises(ValidationError):
            course = Course(**course_data_override)
            course.full_clean()
            course.save()

    def test_create_course_duplicate_course_id(self):
        Course.objects.create(**self.course_data)
        with self.assertRaises(Exception):
            Course.objects.create(**self.course_data)

    def test_create_course_with_special_characters(self):
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

    def test_create_course_with_empty_description(self):
        course = Course.objects.create(
            course_id="CS107",
            semester="Fall 2024",
            name="Intro to CS",
            description="",
            num_of_sections=3,
            modality="Online",
        )
        self.assertEqual(course.description, "")

    def test_case_insensitive_course_id(self):
        Course.objects.create(**self.course_data)
        course = Course.objects.get(course_id="cs101".upper())
        self.assertEqual(course.name, "Introduction to Computer Science")

class CourseEditingTest(TestCase):
    def setUp(self):
        instructor_user = User.objects.create(
            username="instructor1",
            email_address="instructor1@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            is_instructor=True,
        )
        self.instructor = Instructor.objects.create(
            user=instructor_user, max_assignments=5
        )
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Intro to Computer Science",
            description="A beginner's course in CS.",
            num_of_sections=3,
            modality="In-person",
            instructor=self.instructor,
        )


    def test_edit_course_with_negative_sections(self):
        with self.assertRaises(ValueError) as context:
            self.course.edit_Course(num_of_sections=-5)
        self.assertEqual(str(context.exception), "Number of sections cannot be negative.")

    def test_edit_course_id(self):
        self.course.edit_Course(course_id="CS105")
        self.course.refresh_from_db()
        self.assertEqual(self.course.course_id, "CS105")
        
    def test_edit_course_name(self):
        self.course.edit_Course(name="Data Structures")
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Data Structures")

    def test_edit_course_semester(self):
        self.course.edit_Course(semester="Spring 2024")
        self.course.refresh_from_db()
        self.assertEqual(self.course.semester, "Spring 2024")
        
    def test_edit_course_description(self):
        self.course.edit_Course(description = "A new description")
        self.course.refresh_from_db()
        self.assertEqual(self.course.description, "A new description")
        
    def test_edit_course_number_of_sections(self):
        self.course.edit_Course(num_of_sections = 5)
        self.course.refresh_from_db()
        self.assertEqual(self.course.num_of_sections, 5)
        
    def test_edit_course_modality(self):
        self.course.edit_Course(modality = "Online")
        self.course.refresh_from_db()
        self.assertEqual(self.course.modality, "Online")
        
    def test_edit_course_instructor(self):
        new_instructor_user = User.objects.create(
            username="instructor2",
            email_address="instructor2@example.com",
            password="password123",
            first_name="The",
            last_name="Undertaker",
            is_instructor=True,
        )
        self.instructor = Instructor.objects.create(
            user=new_instructor_user, max_assignments=5
        )
        
        self.course.edit_Course(instructor = self.instructor)
        self.course.refresh_from_db()
            # Assertions
        self.assertEqual(self.course.instructor, self.instructor)  # Compare with the specific Instructor instance
        self.assertEqual(self.course.instructor.user, new_instructor_user)  # Ensure the User object is correct
        self.assertEqual(self.course.instructor.user.first_name, "The")
        self.assertEqual(self.course.instructor.user.last_name, "Undertaker")
        
    def test_edit_every_course_field(self):
        # Create a new instructor
        new_instructor_user = User.objects.create(
            username="instructor2",
            email_address="instructor2@example.com",
            password="password123",
            first_name="The",
            last_name="Undertaker",
            is_instructor=True,
        )
        new_instructor = Instructor.objects.create(
            user=new_instructor_user, max_assignments=5
        )

        # Edit all course fields
        self.course.edit_Course(
            name="Advanced Computer Science",
            semester="Spring 2025",
            description="An advanced course in computer science.",
            num_of_sections=5,
            modality="Online",
            instructor=new_instructor,
        )
        self.course.refresh_from_db()

        # Assertions
        self.assertEqual(self.course.name, "Advanced Computer Science")
        self.assertEqual(self.course.semester, "Spring 2025")
        self.assertEqual(self.course.description, "An advanced course in computer science.")
        self.assertEqual(self.course.num_of_sections, 5)
        self.assertEqual(self.course.modality, "Online")
        self.assertEqual(self.course.instructor, new_instructor)
        self.assertEqual(self.course.instructor.user, new_instructor_user)
        self.assertEqual(self.course.instructor.user.first_name, "The")
        self.assertEqual(self.course.instructor.user.last_name, "Undertaker")


            
    def test_edit_course_with_empty_values(self):
        with self.assertRaises(ValueError):  # Adjust based on how edit_Course handles validation
            self.course.edit_Course(name="")

    def test_edit_course_with_negative_sections(self):
        with self.assertRaises(ValueError):  # Adjust if ValueError is not raised
            self.course.edit_Course(num_of_sections=-1)

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
            course = Course.objects.get(id=999)
            course.delete()

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
        Course.objects.create(
            course_id="cs101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            num_of_sections=3,
            modality="In-person",
        )
        deleted_rows, _ = Course.delete_case_insensitive("CS101")
        self.assertEqual(deleted_rows, 1)
        self.assertFalse(Course.objects.filter(course_id="CS101").exists())

    def test_remove_case_insensitive_no_match(self):
        deleted_rows, _ = Course.delete_case_insensitive("MATH101")
        self.assertEqual(deleted_rows, 0)

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
        course = Course.objects.create(**self.course_data)
        saved_course = Course.objects.get(course_id=self.course_data["course_id"])
        self.assertEqual(saved_course.name, self.course_data["name"])

    def test_create_course_and_save_to_database(self):
        course = Course.objects.create(**self.course_data)
        self.assertIsNotNone(course.id)
        saved_course = Course.objects.get(course_id="CS101")
        self.assertEqual(saved_course.name, self.course_data["name"])
        self.assertEqual(Course.objects.count(), 1)

class CourseCreatePermissionTest(TestCase):
    def setUp(self):
        # Admin user
# Example for setting up admin user
        self.admin_user = User.objects.create(
            username="admin_user",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.admin_user.set_password("adminpassword")  # Hash the password
        self.admin_user.save()


        # Instructor user
        self.instructor_user = User.objects.create(
            username="instructor_user",
            email_address="instructor@example.com",
            first_name="Instructor",
            last_name="User",
            is_instructor=True,
        )
        self.instructor_user.set_password("instructorpassword") # Sets hashed password, allowing use of build in Django testing for autherization capabiltiies 
        self.instructor_user.save()
        # TA user
        self.ta_user = User.objects.create(
            username="ta_user",
            email_address="ta@example.com",
            password="tapassword",
            first_name="TA",
            last_name="User",
            is_ta=True,
        )

        # Regular user
        self.regular_user = User.objects.create(
            username="regular_user",
            email_address="user@example.com",
            password="userpassword",
            first_name="Regular",
            last_name="User",
        )

        # Course data for testing
        self.course_data = {
            "course_id": "CS101",
            "semester": "Fall 2024",
            "name": "Introduction to Computer Science",
            "description": "A beginner's course in computer science.",
            "num_of_sections": 3,
            "modality": "In-person",
        }

    def test_admin_can_create_course(self):
        # Log in as admin
        self.client.login(username="admin_user", password="adminpassword")
        response = self.client.post(reverse("course-create"), self.course_data)

        # Check response and database
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Course.objects.filter(course_id="CS101").exists())

    def test_ta_cannot_create_course(self):
        # Log in as TA
        self.client.login(username="ta_user", password="tapassword")
        response = self.client.post(reverse("course-create"), self.course_data)

        # Check response status and database
        self.assertEqual(response.status_code, 302)  # Redirect if unauthorized
        self.assertFalse(Course.objects.filter(course_id="CS101").exists())  # Ensure no course was created

    def test_instructor_can_create_course(self):
        # Log in as Instructor
        self.client.login(username="instructor_user", password="instructorpassword")
        
        # Try to create a course
        response = self.client.post(reverse("course-create"), self.course_data)

        # Check response and database
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Course.objects.filter(course_id="CS101").exists())

    def test_regular_user_cannot_create_course(self):
        # Log in as a Regular User
        self.client.login(username="regular_user", password="userpassword")
        
        # Try to create a course
        response = self.client.post(reverse("course-create"), self.course_data)

        # Check response and database
        self.assertEqual(response.status_code, 302)  # Forbidden
        self.assertFalse(Course.objects.filter(course_id="CS101").exists())

class AssignInstructorToCourse(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create(
            username="instructor1", email_address="instructor1@example.com", is_instructor=True
        )
        self.user2 = User.objects.create(
            username="instructor2", email_address="instructor2@example.com", is_instructor=True
        )

        # Create instructors
        self.instructor1 = Instructor.objects.create(user=self.user1, max_assignments=3)
        self.instructor2 = Instructor.objects.create(user=self.user2, max_assignments=3)

        # Create a course
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person",
        )
    def test_assign_single_instructor_to_course(self):
        # Assign instructor1 to the course
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)

        # Fetch assignments
        assignments = InstructorToCourse.objects.filter(course=self.course)

        # Assertions
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().instructor, self.instructor1)

    def test_assign_multiple_instructors_to_course(self):
        # Assign both instructors to the course
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)
        InstructorToCourse.objects.create(instructor=self.instructor2, course=self.course)

        # Fetch assignments
        assignments = InstructorToCourse.objects.filter(course=self.course)

        # Assertions
        self.assertEqual(assignments.count(), 2)
        self.assertIn(self.instructor1, [a.instructor for a in assignments])
        self.assertIn(self.instructor2, [a.instructor for a in assignments])

    def test_reassign_instructors_to_course(self):
        # Assign instructor1 initially
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)

        # Reassign to instructor2
        InstructorToCourse.objects.filter(course=self.course).delete()
        InstructorToCourse.objects.create(instructor=self.instructor2, course=self.course)

        # Fetch assignments
        assignments = InstructorToCourse.objects.filter(course=self.course)

        # Assertions
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().instructor, self.instructor2)

    def test_remove_all_instructors_from_course(self):
        # Assign both instructors
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)
        InstructorToCourse.objects.create(instructor=self.instructor2, course=self.course)

        # Remove all instructors
        InstructorToCourse.objects.filter(course=self.course).delete()

        # Fetch assignments
        assignments = InstructorToCourse.objects.filter(course=self.course)

        # Assertions
        self.assertEqual(assignments.count(), 0)


    def test_prevent_duplicate_instructor_assignment(self):
        # Assign instructor1 to the course
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)

        # Attempt to assign the same instructor again
        with self.assertRaises(IntegrityError):
            with transaction.atomic():  # Ensure the operation is isolated
                InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)

        # Fetch assignments
        assignments = InstructorToCourse.objects.filter(course=self.course)

        # Assertions
        self.assertEqual(assignments.count(), 1)

        
    def test_fetch_courses_for_instructor(self):
        # Assign instructor1 to the course
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)

        # Fetch courses for instructor1
        courses = Course.objects.filter(instructor_assignments__instructor=self.instructor1)

        # Assertions
        self.assertEqual(courses.count(), 1)
        self.assertIn(self.course, courses)


    def test_assign_non_instructor_to_course(self):
        # Create a non-instructor user
        non_instructor_user = User.objects.create(
            username="student1", email_address="student1@example.com"
        )

        with self.assertRaises(ValueError):
            InstructorToCourse.objects.create(
                instructor=non_instructor_user,  # Should raise error
                course=self.course
            )
