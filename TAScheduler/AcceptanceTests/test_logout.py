from django.test import TestCase, Client
from TAScheduler.models import User, Administrator


class LogoutTest(TestCase):
    def setUp(self):
        # Set up the client and administrator account
        self.client = Client()
        temp = User.objects.create(
            email_address="testadmin@uwm.edu",
            password="pass",
            first_name="Test",
            last_name="Admin",
            home_address="Random location",
            phone_number="9990009999"
        )
        self.account = Administrator.objects.create(user=temp)

        # Simulate user login by setting the session
        ses = self.client.session
        ses["user"] = str(self.account)
        ses.save()

    def test_logout(self):
        """Test that the user is logged out and redirected to the login page."""
        # Send a POST request to the logout URL
        response = self.client.get('/logout/')  # Assuming /logout/ is the logout URL

        # Check if the user is redirected to the login page
        self.assertRedirects(response, '/login/')

        # Check if the user session has been cleared
        self.assertNotIn("user", self.client.session, "The user session should be cleared after logout.")
