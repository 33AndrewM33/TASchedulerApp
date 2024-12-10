from django.test import TestCase, Client
from django.urls import reverse
from TAScheduler.models import User, Administrator, Instructor, TA


class LogoutTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email="admin@uwm.edu",
            password="adminpass",
            first_name="Test",
            last_name="Admin",
            is_admin=True
        )
        self.admin = Administrator.objects.create(user=self.admin_user)

        # Create instructor user
        self.instructor_user = User.objects.create_user(
            username='instructor_user',
            email="instructor@uwm.edu",
            password="instrpass",
            first_name="Test",
            last_name="Instructor",
            is_instructor=True
        )
        self.instructor = Instructor.objects.create(user=self.instructor_user)

        # Create TA user
        self.ta_user = User.objects.create_user(
            username='ta_user',
            email="ta@uwm.edu",
            password="tapass",
            first_name="Test",
            last_name="TA",
            is_ta=True
        )
        self.ta = TA.objects.create(user=self.ta_user)

    def test_admin_logout(self):
        """Test that an admin user is logged out properly"""
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Verify cannot access protected pages after logout
        home_response = self.client.get(reverse('home'))
        self.assertNotEqual(home_response.status_code, 200)

    def test_instructor_logout(self):
        """Test that an instructor is logged out properly"""
        self.client.login(username='instructor_user', password='instrpass')
        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Verify cannot access instructor pages after logout
        home_response = self.client.get(reverse('home_instructor'))
        self.assertNotEqual(home_response.status_code, 200)

    def test_ta_logout(self):
        """Test that a TA is logged out properly"""
        self.client.login(username='ta_user', password='tapass')
        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)

        # Verify cannot access TA pages after logout
        home_response = self.client.get(reverse('home_ta'))
        self.assertNotEqual(home_response.status_code, 200)

    def test_logout_without_login(self):
        """Test accessing logout without being logged in"""
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, '/')

    def test_multiple_logout_attempts(self):
        """Test multiple consecutive logout attempts"""
        # First login and logout
        self.client.login(username='admin_user', password='adminpass')
        first_response = self.client.get(reverse('logout'))
        self.assertRedirects(first_response, '/')

        # Try logging out again
        second_response = self.client.get(reverse('logout'))
        self.assertRedirects(second_response, '/')

    def test_post_logout_session(self):
        """Test that the session is completely cleared after logout"""
        self.client.login(username='admin_user', password='adminpass')

        # Add some session data
        session = self.client.session
        session['test_key'] = 'test_value'
        session.save()

        # Logout
        self.client.get(reverse('logout'))

        # Verify session is cleared
        self.assertNotIn('test_key', self.client.session)
        self.assertNotIn('_auth_user_id', self.client.session)