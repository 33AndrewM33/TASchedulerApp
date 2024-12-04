from datetime import datetime
from django.contrib.messages import get_messages
from django.test import TestCase, Client
from TAScheduler.models import Section, Course, Lecture, Lab, Administrator, User


class SuccessDeleteSectionTestCase(TestCase):
    def setUp(self):
        # Set up the client and administrator
        self.client = Client()
        self.admin_user = Administrator.objects.create(
            user=User.objects.create_user(
                username="admin",
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                home_address="123 Admin St",
                phone_number="1234567890",
                password="adminpassword",
                is_admin=True,
            )
        )

        self.client.login(username="admin", password="adminpassword")

        # Create courses and sections
        self.courses = []
        self.sections = []
        for i in range(1, 4):  # Create 3 courses
            course = Course.objects.create(
                course_id=f"CS10{i}",
                semester=f"Fall 202{i}",
                name=f"Course {i}",
                description=f"Description for Course {i}",
                num_of_sections=2,
                modality="Remote"
            )
            self.courses.append(course)

        for i in range(1, 4):  # Create 3 sections
            section = Section.objects.create(
                section_id=i,
                course=self.courses[i - 1],
                location=f"Location {i}",
                meeting_time="Mon/Wed 10:00-11:30"
            )
            self.sections.append(section)

    def test_correct_delete(self):
        # Send a POST request to the delete URL for the section
        response = self.client.post(f"/home/managesection/delete/{self.sections[0].id}/", follow=True)

        # Fetch all remaining sections
        remaining_sections = Section.objects.all()

        # Verify the deleted section is no longer in the database
        self.assertNotIn(self.sections[0], remaining_sections, "The deleted section should not exist in the database.")

    def test_correct_num_sections(self):
        # Get the initial count of sections
        initial_count = Section.objects.count()

        # Send a POST request to the correct delete URL for the section
        response = self.client.post(f"/home/managesection/delete/{self.sections[0].id}/", follow=True)

        # Get the final count of sections
        final_count = Section.objects.count()

        # Check that the count has decreased by one
        self.assertEqual(final_count, initial_count - 1,
                         "The number of sections in the database should decrease by one.")

    def test_confirm_delete_message(self):
        # Send a POST request to delete the section
        response = self.client.post(f"/home/managesection/delete/{self.sections[0].id}/", follow=True)

        # Ensure the response followed the redirect
        self.assertEqual(response.status_code, 200, "Expected status code 200 after following the redirect.")

        # Verify the section no longer exists in the database
        self.assertFalse(
            Section.objects.filter(id=self.sections[0].id).exists(),
            "Section was not deleted from the database."
        )

        # Check for the success message in the response
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(f"Section {self.sections[0].section_id} deleted successfully." in str(message) for message in messages),
            "Expected success message not found in messages."
        )

    def test_no_course_deleted(self):
        associated_course = self.sections[0].course
        response = self.client.post("/home/managesection/", data={"section_id": self.sections[0].section_id, "delete": "Delete"})
        all_courses = Course.objects.all()

        self.assertIn(associated_course, all_courses, "The course associated with the deleted section should remain in the database.")