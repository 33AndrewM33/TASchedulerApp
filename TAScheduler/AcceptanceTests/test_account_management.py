from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages
from TAScheduler.models import User, TA, Instructor, Administrator
#creates, edits, and deletes user accounts via the account_management view
class AdminManageUsers(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an admin user with proper password hashing
        self.admin_user = User.objects.create(
            username="admin",
            email="admin@example.com",
            password=make_password("adminpassword"),
            first_name="Admin",
            last_name="User",
            home_address="123 Admin St",
            phone_number="1234567890",
            is_admin=True
        )
    # Log in the admin user
        login_successful = self.client.login(username="admin", password="adminpassword")
        self.assertTrue(login_successful, "Admin user login failed during setup.")
        self.account_management_url = reverse('account_management')
        # Create an instructor
        self.instructor_user = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="instrpassword",
            first_name="John",
            last_name="Deer",
            is_instructor=True
        )
        self.instructor = Instructor.objects.create(user=self.instructor_user, max_assignments=4)
        # Create a test TA
        self.ta_user = User.objects.create_user(
            username="ta_user",
            email="ta@example.com",
            password="tapass",
            first_name="Test",
            last_name="TA",
            is_ta=True
        )
        self.ta_account = TA.objects.create(user=self.ta_user, grader_status=True, skills="C++")
    def test_create_user(self):
        # Data to create a new user
        user_data = {
            'action': 'create',
            'username': 'new_testuser',
            'email': 'user@example.com',
            'password': 'password123',
            'role': 'ta',  # Role can be 'ta', 'instructor', or 'administrator'
        }
        # Send POST request to create user
        response = self.client.post(self.account_management_url, user_data)
        # Check if user was created successfully
        self.assertEqual(response.status_code, 200)  # Should return a success response
        self.assertTrue(User.objects.filter(username='new_testuser').exists(),
                        "New user should be created in the database.")
        self.assertTrue(TA.objects.filter(user__username='new_testuser').exists(), "User should be assigned as a TA.")
    def test_edit_user(self):
        # Create a user to edit
        user_to_edit = User.objects.create_user(
            username="user_to_edit", email="edit@example.com", password="password123"
        )
        edit_url = reverse('account_management')
        # Data to edit user details
        edit_data = {
            'action': 'edit',
            'user_id': user_to_edit.id,
        }
        # Send POST request to edit user
        response = self.client.post(edit_url, edit_data)
        self.assertEqual(response.status_code, 200)
    def test_update_user(self):
        # Create a user to update
        user_to_update = User.objects.create_user(
            username="user_to_update", email="update@example.com", password="password123"
        )
        update_url = reverse('account_management')
        # Data to update user details
        updated_data = {
            'action': 'update',
            'editing_user_id': user_to_update.id,
            'username': 'updated_user',
            'email': 'updateduser@example.com',
            'password': 'updatedpassword123',
            'role': 'instructor',  # Update role
        }
        # Send POST request to update user
        response = self.client.post(update_url, updated_data)
        # Check if the user details were updated successfully
        updated_user = User.objects.get(id=user_to_update.id)
        self.assertEqual(updated_user.username, 'updated_user', "Username should be updated.")
        self.assertEqual(updated_user.email, 'updateduser@example.com', "Email should be updated.")
        self.assertEqual(response.status_code, 200)  # Ensure success response after update
    def test_delete_user(self):
        # Create a user to delete
        user_to_delete = User.objects.create_user(
            username="user_to_delete", email="delete@example.com", password="password123"
        )
        delete_url = reverse('account_management')
        # Data to delete user
        delete_data = {
            'action': 'delete',
            'user_id': user_to_delete.id,
        }
        # Send POST request to delete user
        response = self.client.post(delete_url, delete_data)
        # Verify user is deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_to_delete.id)
        self.assertEqual(response.status_code, 200)  # Ensure success response after deletion
    def test_delete_user_and_related_profiles(self):
        # Create a user to delete
        user_to_delete = User.objects.create_user(
            username="user_with_profile", email="profile@example.com", password="password123"
        )
        ta_profile = TA.objects.create(user=user_to_delete, grader_status=True, skills="Python")
        delete_data = {
            'action': 'delete',
            'user_id': user_to_delete.id,
        }
        # Send POST request to delete user
        response = self.client.post(self.account_management_url, delete_data)
        # Verify user and related profiles are deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_to_delete.id)
        with self.assertRaises(TA.DoesNotExist):
            TA.objects.get(id=ta_profile.id)
        self.assertEqual(response.status_code, 200)
    def test_delete_user_and_related_profiles_instructor(self):
        # Create an instructor user and related profile
        user_to_delete = User.objects.create_user(
            username="user_with_instructor_profile", email="instrprofile@example.com", password="password123"
        )
        instructor_profile = Instructor.objects.create(user=user_to_delete, max_assignments=5)
        delete_data = {
            'action': 'delete',
            'user_id': user_to_delete.id,
        }
        # Send POST request to delete user
        response = self.client.post(self.account_management_url, delete_data)
        # Verify user and related instructor profile are deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_to_delete.id)
        with self.assertRaises(Instructor.DoesNotExist):
            Instructor.objects.get(id=instructor_profile.id)
        self.assertEqual(response.status_code, 200)