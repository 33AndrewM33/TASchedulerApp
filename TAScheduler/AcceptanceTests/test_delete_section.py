from datetime import datetime
from django.contrib.messages import get_messages
from django.test import TestCase, Client
from TAScheduler.models import Section, Course, Lecture, Lab, Administrator, User, TA


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

    def test_unauthenticated_user_delete(self):
        """Test that unauthenticated users cannot delete sections"""
        # Logout the admin user
        self.client.logout()

        # Try to delete a section
        response = self.client.post(f"/home/managesection/delete/{self.sections[0].id}/")

        # Should redirect to login
        self.assertEqual(response.status_code, 302, "Should redirect to login")
        self.assertIn('login', response.url, "Should redirect to login page")

        # Verify section still exists
        self.assertTrue(
            Section.objects.filter(id=self.sections[0].id).exists(),
            "Section should not be deleted by unauthenticated user"
        )

    def test_delete_section_with_lab(self):
        """Test deletion of a section that has an associated lab"""
        # Create a lab for the section
        lab = Lab.objects.create(section=self.sections[0])

        # Delete the section
        response = self.client.post(f"/home/managesection/delete/{self.sections[0].id}/", follow=True)

        # Verify section and lab are both deleted
        self.assertFalse(
            Section.objects.filter(id=self.sections[0].id).exists(),
            "Section should be deleted"
        )
        self.assertFalse(
            Lab.objects.filter(id=lab.id).exists(),
            "Associated lab should be deleted with section"
        )

    def test_delete_section_with_lecture(self):
        """Test deletion of a section that has an associated lecture"""
        # Create a lecture for the section
        lecture = Lecture.objects.create(section=self.sections[0])

        # Delete the section
        response = self.client.post(f"/home/managesection/delete/{self.sections[0].id}/", follow=True)

        # Verify section and lecture are both deleted
        self.assertFalse(
            Section.objects.filter(id=self.sections[0].id).exists(),
            "Section should be deleted"
        )
        self.assertFalse(
            Lecture.objects.filter(id=lecture.id).exists(),
            "Associated lecture should be deleted with section"
        )

    def test_delete_section_with_assigned_ta(self):
        """Test deletion of a section that has an assigned TA"""
        # Create a TA user
        ta_user = User.objects.create_user(
            username="ta",
            email="ta@example.com",
            password="tapassword",
            is_ta=True
        )
        ta = TA.objects.create(user=ta_user)

        # Assign TA to section
        self.sections[0].assigned_tas.add(ta)

        # Delete the section
        response = self.client.post(f"/home/managesection/delete/{self.sections[0].id}/", follow=True)

        # Verify section is deleted but TA still exists
        self.assertFalse(
            Section.objects.filter(id=self.sections[0].id).exists(),
            "Section should be deleted"
        )
        self.assertTrue(
            TA.objects.filter(id=ta.id).exists(),
            "TA should still exist after section deletion"
        )

    def test_delete_nonexistent_section(self):
        """Test attempting to delete a section that doesn't exist"""
        nonexistent_id = 9999

        # Try to delete nonexistent section
        response = self.client.post(f"/home/managesection/delete/{nonexistent_id}/", follow=True)

        # Verify appropriate error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Error deleting section:" in str(message) for message in messages),
            "Should show error message for nonexistent section"
        )

    def test_delete_multiple_sections_same_course(self):
        """Test deleting multiple sections from the same course"""
        # Create two more sections for the first course
        section2 = Section.objects.create(
            section_id=10,
            course=self.courses[0],
            location="New Location",
            meeting_time="Tue/Thu 10:00-11:30"
        )
        section3 = Section.objects.create(
            section_id=11,
            course=self.courses[0],
            location="Another Location",
            meeting_time="Wed/Fri 10:00-11:30"
        )

        # Delete sections one by one
        for section in [section2, section3]:
            response = self.client.post(f"/home/managesection/delete/{section.id}/", follow=True)
            self.assertFalse(
                Section.objects.filter(id=section.id).exists(),
                f"Section {section.section_id} should be deleted"
            )

        # Verify course still exists
        self.assertTrue(
            Course.objects.filter(id=self.courses[0].id).exists(),
            "Course should still exist after deleting multiple sections"
        )