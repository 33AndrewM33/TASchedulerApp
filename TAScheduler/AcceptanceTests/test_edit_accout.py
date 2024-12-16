from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from TAScheduler.models import User, Instructor, Administrator, TA


class EditAccountTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create an administrator for testing
        self.admin_user = User.objects.create(
            username="admin",
            email="admin@example.com",
            password=make_password("adminpassword"),
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        self.admin = Administrator.objects.create(user=self.admin_user)

        # Log in as admin
        self.client.login(username="admin", password="adminpassword")

        # Create a test user to be edited
        self.test_user = User.objects.create(
            username="testuser",
            email="test@example.com",
            password=make_password("testpassword"),
            first_name="Test",
            last_name="User"
        )

    def test_edit_user_basic_info(self):
        """Test editing basic user information"""
        edit_url = reverse('edit_user', args=[self.test_user.id])
        updated_data = {
            'username': 'updated_username',
            'email': 'updated@example.com',
            'password': 'newpassword123',
            'role': 'instructor'  # No role change yet
        }

        response = self.client.post(edit_url, updated_data)

        # Should redirect back to account management
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_management'))

        # Verify updates
        updated_user = User.objects.get(id=self.test_user.id)
        self.assertEqual(updated_user.username, 'updated_username')
        self.assertEqual(updated_user.email, 'updated@example.com')

    def test_change_user_to_instructor(self):
        """Test changing a regular user to an instructor"""
        edit_url = reverse('edit_user', args=[self.test_user.id])
        updated_data = {
            'username': self.test_user.username,
            'email': self.test_user.email,
            'role': 'instructor'
        }

        response = self.client.post(edit_url, updated_data)

        # Verify user was updated
        updated_user = User.objects.get(id=self.test_user.id)
        self.assertTrue(updated_user.is_instructor)
        self.assertTrue(hasattr(updated_user, 'instructor_profile'))
        self.assertFalse(updated_user.is_ta)
        self.assertFalse(updated_user.is_admin)

    def test_change_user_to_ta(self):
        """Test changing a regular user to a TA"""
        edit_url = reverse('edit_user', args=[self.test_user.id])
        updated_data = {
            'username': self.test_user.username,
            'email': self.test_user.email,
            'role': 'ta'
        }

        response = self.client.post(edit_url, updated_data)

        # Verify user was updated
        updated_user = User.objects.get(id=self.test_user.id)
        self.assertTrue(updated_user.is_ta)
        self.assertTrue(hasattr(updated_user, 'ta_profile'))
        self.assertFalse(updated_user.is_instructor)
        self.assertFalse(updated_user.is_admin)

    def test_change_role_multiple_times(self):
        """Test changing a user's role multiple times"""
        edit_url = reverse('edit_user', args=[self.test_user.id])

        # First change to TA
        self.client.post(edit_url, {
            'username': self.test_user.username,
            'email': self.test_user.email,
            'role': 'ta'
        })

        # Then change to instructor
        self.client.post(edit_url, {
            'username': self.test_user.username,
            'email': self.test_user.email,
            'role': 'instructor'
        })

        # Verify final state
        updated_user = User.objects.get(id=self.test_user.id)
        self.assertTrue(updated_user.is_instructor)
        self.assertTrue(hasattr(updated_user, 'instructor_profile'))
        self.assertFalse(updated_user.is_ta)


    def test_edit_nonexistent_user(self):
        """Test editing a user that doesn't exist"""
        edit_url = reverse('edit_user', args=[99999])  # Non-existent ID
        updated_data = {
            'username': 'updated_username',
            'email': 'updated@example.com',
            'role': 'instructor'
        }

        response = self.client.post(edit_url, updated_data)
        self.assertEqual(response.status_code, 404)