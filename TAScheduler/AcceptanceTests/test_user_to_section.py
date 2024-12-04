from django.test import TestCase, Client
from TAScheduler.models import User, Section, Course, TA, Instructor, Administrator


class UserToSectionAssignmentTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        self.admin_account = Administrator.objects.create(user=self.admin_user)

        # Create a test course
        self.course1 = Course.objects.create(
            course_id="CS101",
            semester="Fall 2023",
            name="Intro to CS",
            description="Basic CS course",
            num_of_sections=2,
            modality="In-person"
        )

        # Create test sections
        self.section1 = Section.objects.create(
            section_id=1,
            course=self.course1,
            location="Room 101",
            meeting_time="Monday 10:00 AM"
        )
        self.section2 = Section.objects.create(
            section_id=2,
            course=self.course1,
            location="Room 102",
            meeting_time="Wednesday 10:00 AM"
        )

        # Create a test TA
        self.ta_user = User.objects.create_user(
            username="ta_user",
            email="ta@example.com",
            password="tapass",
            first_name="Test",
            last_name="TA",
            is_ta=True
        )
        self.ta_account = TA.objects.create(user=self.ta_user, grader_status=True, skills="Python")

        # Create a test Instructor
        self.instructor_user = User.objects.create_user(
            username="instructor_user",
            email="instructor@example.com",
            password="instructorpass",
            first_name="Test",
            last_name="Instructor",
            is_instructor=True
        )
        self.instructor_account = Instructor.objects.create(user=self.instructor_user)

    def test_assign_ta_to_section_success(self):
        # Assign the TA to a section
        self.section1.ta = self.ta_account
        self.section1.save()

        # Verify the assignment
        self.assertEqual(self.section1.ta, self.ta_account, "The TA should be assigned to the section.")

    def test_assign_instructor_to_section_success(self):
        # Assign the Instructor to a section
        self.section1.instructor = self.instructor_account
        self.section1.save()

        # Verify the assignment
        self.assertEqual(self.section1.instructor, self.instructor_account, "The Instructor should be assigned to the section.")

    def test_assign_nonexistent_user_to_section(self):
        # Attempt to assign a non-existent user to a section
        with self.assertRaises(User.DoesNotExist):
            non_existent_user = User.objects.get(email="nonexistent@example.com")
            self.section1.ta = non_existent_user
            self.section1.save()

    def test_assign_user_to_nonexistent_section(self):
        # Attempt to assign a user to a non-existent section
        with self.assertRaises(Section.DoesNotExist):
            non_existent_section = Section.objects.get(section_id=999)
            non_existent_section.ta = self.ta_account
            non_existent_section.save()



    def test_clear_ta_from_section(self):
        # Assign and then remove a TA from a section
        self.section1.ta = self.ta_account
        self.section1.save()

        self.section1.ta = None
        self.section1.save()

        self.assertIsNone(self.section1.ta, "The TA should be cleared from the section.")

    def test_clear_instructor_from_section(self):
        # Assign and then remove an Instructor from a section
        self.section1.instructor = self.instructor_account
        self.section1.save()

        self.section1.instructor = None
        self.section1.save()

        self.assertIsNone(self.section1.instructor, "The Instructor should be cleared from the section.")
