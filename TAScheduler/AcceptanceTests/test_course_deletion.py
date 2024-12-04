from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages
from TAScheduler.models import Course, User


class AdminDeleteCourseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create an admin user with proper password hashing
        self.admin_user = User.objects.create(
            username="admin",
            email="admin@example.com",
            password=make_password("adminpassword"),
            first_name="Admin",
            last_name="User",
            home_address="123 Admin St",
            phone_number="1234567890",
            is_admin=True
        )

        # Create a course to test deletion
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Intro to Computer Science",
            description="Basic programming concepts.",
            num_of_sections=2,
            modality="In-person"
        )

        # Log in the admin user
        login_successful = self.client.login(username="admin", password="adminpassword")
        self.assertTrue(login_successful, "Admin user login failed during setup.")

    def test_delete_course_success(self):
        """
        Test successful deletion of a course by an administrator.
        """
        # Verify course existence before deletion
        self.assertTrue(
            Course.objects.filter(course_id=self.course.course_id).exists(),
            "The course should exist in the database before deletion."
        )

        # Make a POST request to delete the course
        response = self.client.post(reverse("delete_course", args=[self.course.course_id]))

        # Verify redirect status and target URL
        self.assertEqual(response.status_code, 302, "Expected a redirect after successful deletion.")
        self.assertRedirects(
            response, reverse("manage_course"),
            msg_prefix="The redirect after course deletion is incorrect."
        )

        # Verify course deletion from database
        self.assertFalse(
            Course.objects.filter(course_id=self.course.course_id).exists(),
            "The course should no longer exist in the database after deletion."
        )

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1, "Expected exactly one success message after deletion.")
        self.assertEqual(
            str(messages[0]), f"Course 'Intro to Computer Science' deleted successfully.",
            "The success message is incorrect or not displayed."
        )

    def test_delete_course_failure_invalid_id(self):
        """
        Test handling of an invalid course ID during deletion.
        """
        invalid_course_id = "INVALID123"

        # Make a POST request to delete a non-existent course
        response = self.client.post(reverse("delete_course", args=[invalid_course_id]))

        # Verify redirect status and target URL
        self.assertEqual(response.status_code, 302, "Expected a redirect after failed deletion.")
        self.assertRedirects(
            response, reverse("manage_course"),
            msg_prefix="The redirect after failed course deletion is incorrect."
        )

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1, "Expected exactly one error message after failed deletion.")
        self.assertIn(
            "Error deleting course:", str(messages[0]),
            "The error message is incorrect or not displayed."
        )



