from django.test import TestCase, Client
from TAScheduler.models import User, Section, Course, TA, Instructor, TAToCourse, InstructorToCourse, Administrator


class UserToSectionAssignmentTestCase(TestCase):
    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create an admin user
        self.admin_user = User.objects.create(
            email_address="admin@example.com", password="adminpass", first_name="Admin", last_name="User"
        )
        self.admin_account = Administrator.objects.create(user=self.admin_user)

        # Create test courses
        self.course1 = Course.objects.create(
            course_id="CS101", semester="Fall 2023", name="Intro to CS", description="Basic CS course", num_of_sections=2, modality="In-person"
        )

        # Create test sections
        self.section1 = Section.objects.create(
            section_id=1, course=self.course1, location="Room 101", meeting_time="Monday 10:00 AM"
        )
        self.section2 = Section.objects.create(
            section_id=2, course=self.course1, location="Room 102", meeting_time="Wednesday 10:00 AM"
        )

        # Create test TA and Instructor users
        self.ta_user = User.objects.create(
            email_address="ta@example.com", password="tapass", first_name="Test", last_name="TA"
        )
        self.ta_account = TA.objects.create(user=self.ta_user, grader_status=True, skills="Python")

        self.instructor_user = User.objects.create(
            email_address="instructor@example.com", password="instructorpass", first_name="Test", last_name="Instructor"
        )
        self.instructor_account = Instructor.objects.create(user=self.instructor_user)

    def test_assign_ta_to_section_success(self):
        # Assign the TA to a section
        response = self.client.post(
            "/home/managesection/assignuser/",
            {"section_id": self.section1.section_id, "user_email": self.ta_user.email_address},
        )

        # Check if the assignment was successful
        self.assertEqual(response.status_code, 200, "The response should return a status code of 200.")
        self.assertContains(response, "User successfully assigned to section.")
        self.assertEqual(self.section1.ta_set.first(), self.ta_account, "The TA should be assigned to the section.")

    def test_assign_instructor_to_section_success(self):
        # Assign the Instructor to a section
        response = self.client.post(
            "/home/managesection/assignuser/",
            {"section_id": self.section1.section_id, "user_email": self.instructor_user.email_address},
        )

        # Check if the assignment was successful
        self.assertEqual(response.status_code, 200, "The response should return a status code of 200.")
        self.assertContains(response, "User successfully assigned to section.")
        self.assertEqual(self.section1.instructor_set.first(), self.instructor_account, "The instructor should be assigned to the section.")

    def test_assign_nonexistent_user_to_section(self):
        # Attempt to assign a non-existent user
        response = self.client.post(
            "/home/managesection/assignuser/",
            {"section_id": self.section1.section_id, "user_email": "nonexistent@example.com"},
        )

        # Check for failure and appropriate error message
        self.assertEqual(response.status_code, 404, "The response should return a status code of 404 for non-existent users.")
        self.assertContains(response, "User not found.", status_code=404)

    def test_assign_user_to_nonexistent_section(self):
        # Attempt to assign a user to a non-existent section
        response = self.client.post(
            "/home/managesection/assignuser/",
            {"section_id": 999, "user_email": self.ta_user.email_address},
        )

        # Check for failure and appropriate error message
        self.assertEqual(response.status_code, 404, "The response should return a status code of 404 for non-existent sections.")
        self.assertContains(response, "Section not found.", status_code=404)

    def test_duplicate_assignment(self):
        # Assign a TA to a section
        TAToCourse.objects.create(ta=self.ta_account, course=self.course1)
        self.section1.ta_set.add(self.ta_account)

        # Attempt to assign the same TA again
        response = self.client.post(
            "/home/managesection/assignuser/",
            {"section_id": self.section1.section_id, "user_email": self.ta_user.email_address},
        )

        # Check for failure and appropriate error message
        self.assertEqual(response.status_code, 400, "The response should return a status code of 400 for duplicate assignments.")
        self.assertContains(response, "User is already assigned to this section.", status_code=400)
