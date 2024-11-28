from datetime import datetime
from django.test import TestCase, Client
from TAScheduler.models import Section, Course, Lecture, Lab, Administrator, User


class SuccessDeleteSectionTestCase(TestCase):
    def setUp(self):
        # Set up the client and administrator
        self.client = Client()
        self.admin_user = Administrator.objects.create(
            user=User.objects.create(
                username="admin",
                email_address="admin@example.com",
                password="adminpassword",
                first_name="Admin",
                last_name="User",
                home_address="123 Admin St",
                phone_number="1234567890",
                is_admin=True,
            )
        )
        self.client.login(username=self.admin_user.user.username, password="adminpassword")

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
        response = self.client.post("/home/managesection/", data={"section_id": self.sections[0].section_id, "delete": "Delete"})
        remaining_sections = Section.objects.all()

        self.assertNotIn(self.sections[0], remaining_sections, "The deleted section should not exist in the database.")

    def test_correct_num_sections(self):
        initial_count = Section.objects.count()
        response = self.client.post("/home/managesection/", data={"section_id": self.sections[0].section_id, "delete": "Delete"})
        final_count = Section.objects.count()

        self.assertEqual(final_count, initial_count - 1, "The number of sections in the database should decrease by one.")

    def test_confirm_delete_message(self):
        response = self.client.post("/home/managesection/", data={"section_id": self.sections[0].section_id, "delete": "Delete"})
        self.assertContains(response, "Successfully Deleted Section")

    def test_no_course_deleted(self):
        associated_course = self.sections[0].course
        response = self.client.post("/home/managesection/", data={"section_id": self.sections[0].section_id, "delete": "Delete"})
        all_courses = Course.objects.all()

        self.assertIn(associated_course, all_courses, "The course associated with the deleted section should remain in the database.")
