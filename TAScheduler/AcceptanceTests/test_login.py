from django.test import TestCase, Client
from django.urls import reverse
from TAScheduler.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        self.ta = User.objects.create_user(
            username="ta",
            email="ta@example.com",
            password="tapassword",
            first_name="TA",
            last_name="User",
            is_ta=True
        )

    def test_admin_login_success(self):
        """Test successful login for admin."""
        # Use username (or email if your view supports that)
        response = self.client.post(reverse('login'), {'username': self.admin.username, 'password': 'adminpassword'})

        # Assert that user is redirected to the home page
        self.assertRedirects(response, '/home/', msg_prefix="Admin should be redirected to '/home/' after login.")

        # Verify that the user is logged in
        response = self.client.get('/')
        self.assertEqual(int(self.client.session['_auth_user_id']), self.admin.pk, "Admin user should be logged in.")

    def test_ta_login_success(self):
        """Test successful login for TA."""
        # Use username (or email if your view supports that)
        response = self.client.post(reverse('login'), {'username': self.ta.username, 'password': 'tapassword'})

        # Assert that user is redirected to the home page
        self.assertRedirects(response, '/home/', msg_prefix="TA should be redirected to '/home/' after login.")

        # Verify that the user is logged in
        response = self.client.get('/')
        self.assertEqual(int(self.client.session['_auth_user_id']), self.ta.pk, "TA user should be logged in.")

    def test_login_failure(self):
        """Test login failure with incorrect credentials."""
        # Try to log in with incorrect credentials
        response = self.client.post(reverse('login'), {'username': "fakeuser", 'password': 'wrongpassword'})

        # Check that the response code is 200 (indicating the login page was re-rendered)
        self.assertEqual(response.status_code, 200, "Login failure should return status code 200 (page reload).")

        # Check that the error message is displayed
        self.assertContains(response, "Invalid username or password", msg_prefix="Error message should be displayed.")

