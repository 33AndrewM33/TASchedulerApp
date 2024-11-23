from django.test import TestCase, Client
from TAScheduler.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users
        self.admin = User.objects.create(
            email_address="admin@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        self.ta = User.objects.create(
            email_address="ta@example.com",
            password="tapassword",
            first_name="TA",
            last_name="User",
            is_ta=True
        )

    def test_admin_login_success(self):
        response = self.client.post('/login/', {'email_address': self.admin.email_address, 'password': 'adminpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, Admin")

    def test_ta_login_success(self):
        response = self.client.post('/login/', {'email_address': self.ta.email_address, 'password': 'tapassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, TA")

    def test_login_failure(self):
        response = self.client.post('/login/', {'email_address': "fake@example.com", 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)
        self.assertContains(response, "Invalid credentials")
