from django.test import TestCase
from django.urls import reverse
from TAScheduler.models import User, TA, Instructor, Administrator
from django.contrib.auth.hashers import check_password


class EditUserViewTest(TestCase):
    def setUp(self):
        # Create an admin user for authentication
        self.admin_user = User.objects.create(
            username="admin",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
            is_staff=True,
        )
        self.admin_user.set_password("adminpassword")
        self.admin_user.save()

        # Create a test user to edit
        self.test_user = User.objects.create(
            username="testuser",
            email_address="test@example.com",
            first_name="Test",
            last_name="User",
            is_ta=True,
        )
        self.test_user.set_password("oldpassword")
        self.test_user.save()

        # Create a TA profile for the test user
        TA.objects.create(user=self.test_user)

        # Login the admin user
        self.client.login(username="admin", password="adminpassword")

        # URL for editing user
        self.edit_url = reverse("edit_user", kwargs={"user_id": self.test_user.id})

    def test_edit_user_username_and_email(self):
        # Update username and email
        response = self.client.post(
            self.edit_url,
            {
                "username": "updateduser",
                "email": "updated@example.com",
                "password": "",
                "role": "ta",
            },
        )

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, "updateduser")
        self.assertEqual(self.test_user.email_address, "updated@example.com")
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_edit_user_password(self):
        # Update password
        new_password = "newpassword123"
        response = self.client.post(
            self.edit_url,
            {
                "username": self.test_user.username,
                "email": self.test_user.email_address,
                "password": new_password,
                "role": "ta",
            },
        )

        self.test_user.refresh_from_db()
        self.assertTrue(check_password(new_password, self.test_user.password))
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_edit_user_role_to_instructor(self):
        # Change role to instructor
        response = self.client.post(
            self.edit_url,
            {
                "username": self.test_user.username,
                "email": self.test_user.email_address,
                "password": "",
                "role": "instructor",
            },
        )

        self.test_user.refresh_from_db()
        self.assertFalse(self.test_user.is_ta)
        self.assertTrue(self.test_user.is_instructor)
        self.assertFalse(self.test_user.is_admin)
        self.assertTrue(Instructor.objects.filter(user=self.test_user).exists())
        self.assertFalse(TA.objects.filter(user=self.test_user).exists())
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_edit_user_invalid_email(self):
        # Attempt to use an invalid email
        response = self.client.post(
            self.edit_url,
            {
                "username": self.test_user.username,
                "email": "not-an-email",
                "password": "",
                "role": "ta",
            },
        )

        self.assertContains(response, "Invalid email format.")
        self.assertEqual(response.status_code, 200)  # Remain on the same page for validation errors

    def test_edit_user_duplicate_username(self):
        # Create another user with the same username
        User.objects.create_user(
            username="duplicateuser",
            email_address="duplicate@example.com",
            password="password123",
        )

        response = self.client.post(
            self.edit_url,
            {
                "username": "duplicateuser",
                "email": self.test_user.email_address,
                "password": "",
                "role": "ta",
            },
        )

        self.assertContains(response, "Username already exists.")
        self.assertEqual(response.status_code, 200)  # Remain on the same page for validation errors
