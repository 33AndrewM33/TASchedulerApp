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
        self.instructor = Instructor.objects.create(user=self.instructor_user)
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
            'first_name': 'Test2',
            'last_name': 'TA2',
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
        instructor_profile = Instructor.objects.create(user=user_to_delete)
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

    def test_create_instructor(self):
        """Test creating an instructor user"""
        user_data = {
            'action': 'create',
            'username': 'new_instructor',
            'email': 'newinstr@example.com',
            'first_name': 'New',
            'last_name': 'Instructor',
            'password': 'password123',
            'role': 'instructor',
        }
        response = self.client.post(self.account_management_url, user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='new_instructor').exists())
        new_user = User.objects.get(username='new_instructor')
        self.assertTrue(new_user.is_instructor)
        self.assertTrue(hasattr(new_user, 'instructor_profile'))

    def test_create_administrator(self):
        """Test creating an administrator user"""
        user_data = {
            'action': 'create',
            'username': 'new_admin',
            'email': 'newadmin@example.com',
            'first_name': 'New',
            'last_name': 'Admin',
            'password': 'password123',
            'role': 'administrator',
        }
        response = self.client.post(self.account_management_url, user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='new_admin').exists())
        new_user = User.objects.get(username='new_admin')
        self.assertTrue(new_user.is_admin)
        self.assertTrue(hasattr(new_user, 'administrator_profile'))


    def test_delete_nonexistent_user(self):
        """Test deleting a user that doesn't exist"""
        delete_data = {
            'action': 'delete',
            'user_id': 99999,  # Non-existent ID
        }
        response = self.client.post(self.account_management_url, delete_data)

        # Check that error message is sent
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Error deleting user" in str(msg) for msg in messages))


    def test_access_account_management(self):
        """Test accessing the account management page"""
        response = self.client.get(self.account_management_url)
        self.assertEqual(response.status_code, 200)

    def test_create_admin(self):
        """Test creating an admin user"""
        user_data = {
            'action': 'create',
            'username': 'new_admin',
            'email': 'newadmin@example.com',
            'first_name': 'New',
            'last_name': 'Admin',
            'password': 'password123',
            'role': 'administrator',
        }
        response = self.client.post(self.account_management_url, user_data)
        self.assertEqual(response.status_code, 200)
        new_user = User.objects.get(username='new_admin')
        self.assertTrue(new_user.is_admin)

    def test_delete_admin(self):
        """Test deleting an admin user"""
        # Create a user to delete
        admin_to_delete = User.objects.create_user(
            username="admin_to_delete",
            email="admindelete@example.com",
            password="password123",
            is_admin=True
        )
        Administrator.objects.create(user=admin_to_delete)

        delete_data = {
            'action': 'delete',
            'user_id': admin_to_delete.id,
        }
        response = self.client.post(self.account_management_url, delete_data)

        # Verify admin is deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=admin_to_delete.id)
        self.assertEqual(response.status_code, 200)
