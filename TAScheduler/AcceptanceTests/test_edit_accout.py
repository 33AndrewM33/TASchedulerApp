from django.test import TestCase, Client
from TAScheduler.models import User, Administrator, TA


class AdminEditAccountTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create an administrator
        admin_user = User.objects.create(
            email_address="admin@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            home_address="123 Admin St",
            phone_number="1234567890"
        )
        self.admin = Administrator.objects.create(user=admin_user)
        ses = self.client.session
        ses["user"] = admin_user.email_address
        ses.save()

        # Create a TA account
        ta_user = User.objects.create(
            email_address="ta@example.com",
            password="tapassword",
            first_name="TA",
            last_name="User",
            home_address="456 TA Lane",
            phone_number="9876543210",
            is_ta=True
        )
        self.ta = TA.objects.create(user=ta_user, grader_status=False, skills="Python")

    def test_edit_account_success(self):
        # Post updated TA information
        response = self.client.post('/home/manageaccount/edit/', {
            "email_address": self.ta.user.email_address,
            "password": "newpassword",
            "first_name": "Updated TA",
            "last_name": "User",
            "home_address": "Updated Address",
            "phone_number": "1122334455",
            "grader_status": True,
            "skills": "Python, Teaching"
        })

        # Fetch updated TA from database
        updated_ta = TA.objects.get(user__email_address=self.ta.user.email_address)

        # Assert the changes
        self.assertEqual(updated_ta.user.first_name, "Updated TA", "First name was not updated.")
        self.assertEqual(updated_ta.user.phone_number, "1122334455", "Phone number was not updated.")
        self.assertTrue(updated_ta.grader_status, "Grader status was not updated.")
        self.assertEqual(updated_ta.skills, "Python, Teaching", "Skills were not updated.")

    def test_invalid_phone_number(self):
        # Post invalid phone number format
        response = self.client.post('/home/manageaccount/edit/', {
            "email_address": self.ta.user.email_address,
            "phone_number": "123"
        })

        # Ensure the phone number was not updated
        updated_ta = TA.objects.get(user__email_address=self.ta.user.email_address)
        self.assertNotEqual(updated_ta.user.phone_number, "123", "Phone number was incorrectly updated.")
        self.assertContains(response, "Phone number must be 10 digits", status_code=200)
