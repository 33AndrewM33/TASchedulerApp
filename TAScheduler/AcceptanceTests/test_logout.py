from django.test import TestCase, Client
from django.urls import reverse
from TAScheduler.models import User, Administrator


class LogoutTest(TestCase):
    def setUp(self):
        # Set up the client and administrator account
        self.client = Client()

        # Create a user and administrator profile
        self.user = User.objects.create_user(
            username='testuser',
            email="testadmin@uwm.edu",
            password="pass",
            first_name="Test",
            last_name="Admin",
            home_address="Random location",
            phone_number="9990009999"
        )
        self.account = Administrator.objects.create(user=self.user)

    def test_logout(self):
        """Test that the user is logged out and redirected to the login page."""
        # Log in the user using Django's login function
        self.client.login(username='testuser', password='pass')

        # Send a GET request to the logout URL
        response = self.client.get(reverse('logout'))  # Assuming 'logout' is named in urls.py

        # Check if the user is redirected to the login page after logout
        self.assertRedirects(response, reverse('login'),
                             msg_prefix="User should be redirected to the login page after logout.")

        # Check if the user session has been cleared
        self.assertNotIn('_auth_user_id', self.client.session, "The user session should be cleared after logout.")