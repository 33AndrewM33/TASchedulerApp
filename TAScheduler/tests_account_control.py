from django.test import TestCase
from django.urls import reverse
from TAScheduler.models import User
from django.contrib.auth import get_user_model

class AccountCreationTests(TestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = get_user_model().objects.create_user(
            username='adminuser',
            email_address='admin@example.com',
            password='password123',
            is_admin=True
        )
        # Log in as admin
        self.client.login(username='adminuser', password='password123')

    def test_create_ta(self):
        response = self.client.post(reverse('create-account'), {
            'username': 'tauser',
            'email_address': 'tauser@example.com',
            'password': 'password123',
            'first_name': 'TA',
            'last_name': 'User',
            'is_ta': 'on',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.assertTrue(User.objects.filter(username='tauser').exists())

    def test_create_instructor(self):
        response = self.client.post(reverse('create-account'), {
            'username': 'instructoruser',
            'email_address': 'instructor@example.com',
            'password': 'password123',
            'first_name': 'Instructor',
            'last_name': 'User',
            'is_instructor': 'on',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.assertTrue(User.objects.filter(username='instructoruser').exists())

    def test_create_user_without_admin_access(self):
        # Log out admin user
        self.client.logout()

        # Create a non-admin user
        self.non_admin_user = get_user_model().objects.create_user(
            username='regularuser',
            email_address='user@example.com',
            password='password123',
            is_admin=False
        )
        self.client.login(username='regularuser', password='password123')

        # Attempt to access account creation view
        response = self.client.post(reverse('create-account'), {
            'username': 'newuser',
            'email_address': 'newuser@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
        })

        # Should return forbidden since the user is not an admin
        self.assertEqual(response.status_code, 302)
