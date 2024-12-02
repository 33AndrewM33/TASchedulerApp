from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class AccountCreationTests(TestCase):
    def setUp(self):
        # Create an admin user
        User = get_user_model()
        self.admin_user = User.objects.create(
            username="admin_user",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.admin_user.set_password("adminpassword")
        self.admin_user.save()

        # Log in as admin
        self.client.login(username="admin_user", password="adminpassword")

        # URL for account creation
        self.create_account_url = reverse("create-account")

    def test_create_ta(self):
        response = self.client.post(self.create_account_url, {
            "username": "ta_user",
            "email_address": "ta@example.com",
            "password": "tapassword",
            "first_name": "TA",
            "last_name": "User",
            "role": "ta",
        })

        # Assert the response status code
        self.assertEqual(response.status_code, 302)  # Expect a redirect on success

        # Check the created TA user
        User = get_user_model()
        ta_user = User.objects.get(username="ta_user")
        self.assertTrue(ta_user.is_ta)
        self.assertEqual(ta_user.email_address, "ta@example.com")

    def test_create_instructor(self):
        response = self.client.post(self.create_account_url, {
            "username": "instructor_user",
            "email_address": "instructor@example.com",
            "password": "instructorpassword",
            "first_name": "Instructor",
            "last_name": "User",
            "role": "instructor",
        })

        # Assert the response status code
        self.assertEqual(response.status_code, 302)  # Expect a redirect on success

        # Check the created Instructor user
        User = get_user_model()
        instructor_user = User.objects.get(username="instructor_user")
        self.assertTrue(instructor_user.is_instructor)
        self.assertEqual(instructor_user.email_address, "instructor@example.com")
