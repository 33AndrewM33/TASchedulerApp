from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from TAScheduler.models import User, Administrator


class PasswordResetTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test user
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpassword",
            first_name="Test",
            last_name="User"
        )

        # Create admin for notifications
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        Administrator.objects.create(user=self.admin_user)

    def test_forgot_password_page_load(self):
        """Test that forgot password page loads"""
        response = self.client.get(reverse('forgot_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forgot_password.html')

    def test_security_question_success(self):
        """Test successful security question submission"""
        data = {
            'username': 'testuser',
            'answer_1': 'university of wisconsin milwaukee',
            'answer_2': 'rock',
            'answer_3': 'django'
        }

        response = self.client.post(reverse('forgot_password'), data)
        self.assertTemplateUsed(response, 'reset_password.html')

    def test_temporary_password_request(self):
        """Test requesting a temporary password"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'temp_password': True
        }

        response = self.client.post(reverse('forgot_password'), data)
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_temporary_password)

    def test_password_reset_complete(self):
        """Test complete password reset process"""
        # Set up session
        session = self.client.session
        session['valid_user'] = 'testuser'
        session.save()

        # Submit new password
        data = {
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }

        response = self.client.post(
            reverse('forgot_password'),
            {'new_password': data['new_password'],
             'confirm_password': data['confirm_password'],
             'new_password': True}  # Add the flag that views.py checks for
        )

        self.assertTemplateUsed(response, 'forgot_password.html')
        self.test_user.refresh_from_db()
        self.assertFalse(self.test_user.is_temporary_password)