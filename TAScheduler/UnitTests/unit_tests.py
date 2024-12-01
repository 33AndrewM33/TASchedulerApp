from django.test import TestCase
from TAScheduler.models import (
    User, TA, Instructor, Administrator, Course, Section, Lab, Lecture
)


class ExtendedModelsTestCase(TestCase):

    def setUp(self):
        # Create Users
        self.ta_user = User.objects.create(
            username="ta_user",
            email_address="ta_user@example.com",
            password="password123",
            first_name="TA",
            last_name="User",
            is_ta=True
        )
        self.instructor_user = User.objects.create(
            username="instructor_user",
            email_address="instructor_user@example.com",
            password="password123",
            first_name="Instructor",
            last_name="User",
            is_instructor=True
        )
        self.admin_user = User.objects.create(
            username="admin_user",
            email_address="admin_user@example.com",
            password="password123",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )

        # Create Roles
        self.ta = TA.objects.create(user=self.ta_user, skills="Python, Java", max_assignments=3)
        self.instructor = Instructor.objects.create(user=self.instructor_user, max_assignments=5)
        self.admin = Administrator.objects.create(user=self.admin_user)

        # Create Course
        self.course = Course.objects.create(
            course_id="CS201",
            semester="Spring 2025",
            name="Advanced Programming",
            description="Learn advanced programming concepts.",
            num_of_sections=3,
            modality="In-person"
        )

        # Create Section
        self.section = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="Mon/Wed 9:00-10:30"
        )

    def test_ta_max_assignments(self):
        """Test that TA max_assignments cannot exceed 6."""
        self.ta.max_assignments = 7
        with self.assertRaises(ValueError):
            self.ta.save()

    def test_course_section_relationship(self):
        """Test that deleting a course cascades to its sections."""
        self.assertEqual(self.course.sections.count(), 1)
        self.course.delete()
        self.assertEqual(Section.objects.filter(course=self.course).count(), 0)

    def test_lab_without_ta(self):
        lab = Lab.objects.create(section=self.section, ta=None)
        self.assertIsNone(lab.ta)

    def test_assign_ta_to_lab(self):
        lab = Lab.objects.create(section=self.section, ta=None)
        lab.ta = self.ta
        lab.save()
        self.assertEqual(lab.ta.user.username, "ta_user")

    def test_lecture_without_instructor(self):
        lecture = Lecture.objects.create(section=self.section, instructor=None)
        self.assertIsNone(lecture.instructor)

    def test_assign_instructor_to_lecture(self):
        lecture = Lecture.objects.create(section=self.section, instructor=None)
        lecture.instructor = self.instructor
        lecture.save()
        self.assertEqual(lecture.instructor.user.username, "instructor_user")

    def test_section_string_representation(self):
        self.assertEqual(str(self.section), "Section 1 - Advanced Programming")

    def test_course_modality_choices(self):
        with self.assertRaises(ValueError):
            Course.objects.create(
                course_id="CS202",
                semester="Fall 2025",
                name="Invalid Modality Course",
                description="Testing invalid modality.",
                num_of_sections=2,
                modality="Invalid Choice"
            )

    def test_user_roles(self):
        self.assertTrue(self.ta_user.is_ta)
        self.assertFalse(self.ta_user.is_instructor)
        self.assertFalse(self.ta_user.is_admin)

        self.assertTrue(self.instructor_user.is_instructor)
        self.assertFalse(self.instructor_user.is_ta)
        self.assertFalse(self.instructor_user.is_admin)

        self.assertTrue(self.admin_user.is_admin)
        self.assertFalse(self.admin_user.is_ta)
        self.assertFalse(self.admin_user.is_instructor)

    def test_create_section_with_invalid_course(self):
        with self.assertRaises(Exception):
            Section.objects.create(
                section_id=2,
                course=None,  # Invalid course
                location="Room 202",
                meeting_time="Tue/Thu 2:00-3:30"
            )

    def test_update_course_name(self):
        self.course.name = "Updated Programming"
        self.course.save()
        updated_course = Course.objects.get(course_id="CS201")
        self.assertEqual(updated_course.name, "Updated Programming")

    def test_delete_ta_cascade(self):
        lab = Lab.objects.create(section=self.section, ta=self.ta)
        self.assertEqual(Lab.objects.count(), 1)
        self.ta.delete()
        self.assertEqual(Lab.objects.count(), 0)

    def test_delete_instructor_cascade(self):
        lecture = Lecture.objects.create(section=self.section, instructor=self.instructor)
        self.assertEqual(Lecture.objects.count(), 1)
        self.instructor.delete()
        self.assertEqual(Lecture.objects.count(), 0)

    def test_course_description_length(self):
        long_description = "A" * 1000
        self.course.description = long_description
        self.course.save()
        self.assertEqual(self.course.description, long_description)

    def test_section_unique_constraint(self):
        with self.assertRaises(Exception):
            Section.objects.create(
                section_id=1,  # Duplicate section ID for the same course
                course=self.course,
                location="Room 102",
                meeting_time="Mon/Wed 10:30-12:00"
            )

    def test_invalid_email_format(self):
        with self.assertRaises(ValueError):
            User.objects.create(
                username="invalid_email",
                email_address="invalid-email",  # Invalid email
                password="password123",
                first_name="Invalid",
                last_name="Email"
            )
