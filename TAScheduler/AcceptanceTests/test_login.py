from django.test import TestCase, Client
from django.urls import reverse
from TAScheduler.models import User, Instructor
from django.contrib.auth.hashers import make_password

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
        # Add instructor user
        self.instructor_user = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="instructorpass",
            first_name="Test",
            last_name="Instructor",
            is_instructor=True
        )
        self.instructor = Instructor.objects.create(user=self.instructor_user)

    def test_admin_login_success(self):
        """Test successful login for admin."""
        response = self.client.post(reverse('login'), {
            'username': self.admin.username,
            'password': 'adminpassword'
        })
        self.assertRedirects(response, '/home/')
        self.assertEqual(int(self.client.session['_auth_user_id']), self.admin.pk)

    def test_ta_login_success(self):
        """Test successful login for TA."""
        response = self.client.post(reverse('login'), {
            'username': self.ta.username,
            'password': 'tapassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.ta.pk)

    def test_login_failure(self):
        """Test login failure with incorrect credentials."""
        response = self.client.post(reverse('login'), {
            'username': "fakeuser",
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_instructor_login_success(self):
        """Test successful login for instructor."""
        response = self.client.post(reverse('login'), {
            'username': self.instructor_user.username,
            'password': 'instructorpass'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.instructor_user.pk)

    def test_already_logged_in_redirect(self):
        """Test that already logged in users are redirected to home."""
        # First login
        self.client.login(username=self.admin.username, password='adminpassword')
        # Try to access login page again
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, '/home/')

    def test_empty_credentials(self):
        """Test login attempt with empty credentials."""
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_correct_username_wrong_password(self):
        """Test login attempt with correct username but wrong password."""
        response = self.client.post(reverse('login'), {
            'username': self.admin.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_case_sensitive_username(self):
        """Test that username is case sensitive."""
        response = self.client.post(reverse('login'), {
            'username': self.admin.username.upper(),
            'password': 'adminpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_login_with_inactive_user(self):
        """Test login attempt with an inactive user account."""
        # Create inactive user
        inactive_user = User.objects.create_user(
            username="inactive",
            password="inactivepass",
            is_active=False
        )
        response = self.client.post(reverse('login'), {
            'username': 'inactive',
            'password': 'inactivepass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

