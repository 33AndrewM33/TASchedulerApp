from django.test import TestCase
from TAScheduler.models import User

class UserModelTests(TestCase):

    def setUp(self):
        # Create sample users
        self.user_admin = User.objects.create(
            username="adminuser",
            email="admin@example.com",
            password="password123",
            is_admin=True
        )
        self.user_instructor = User.objects.create(
            username="instructor",
            email="instructor@example.com",
            password="password123",
            is_instructor=True
        )
        self.user_ta = User.objects.create(
            username="tauser",
            email="ta@example.com",
            password="password123",
            is_ta=True
        )

    # Existing test split into multiple test cases
    def test_admin_role_assignment(self):
        self.assertTrue(self.user_admin.is_admin)
        self.assertFalse(self.user_admin.is_instructor)
        self.assertFalse(self.user_admin.is_ta)

    def test_instructor_role_assignment(self):
        self.assertTrue(self.user_instructor.is_instructor)
        self.assertFalse(self.user_instructor.is_admin)
        self.assertFalse(self.user_instructor.is_ta)

    def test_ta_role_assignment(self):
        self.assertTrue(self.user_ta.is_ta)
        self.assertFalse(self.user_ta.is_admin)
        self.assertFalse(self.user_ta.is_instructor)

    # New tests
    def test_admin_email(self):
        self.assertEqual(self.user_admin.email, "admin@example.com")

    def test_instructor_email(self):
        self.assertEqual(self.user_instructor.email, "instructor@example.com")

    def test_ta_email(self):
        self.assertEqual(self.user_ta.email, "ta@example.com")

    def test_admin_username(self):
        self.assertEqual(self.user_admin.username, "adminuser")

    def test_instructor_username(self):
        self.assertEqual(self.user_instructor.username, "instructor")

    def test_ta_username(self):
        self.assertEqual(self.user_ta.username, "tauser")

    def test_user_password(self):
        self.assertEqual(self.user_admin.password, "password123")
        self.assertEqual(self.user_instructor.password, "password123")
        self.assertEqual(self.user_ta.password, "password123")

    def test_is_not_admin_by_default(self):
        new_user = User.objects.create(
            username="newuser",
            email="newuser@example.com",
            password="password123"
        )
        self.assertFalse(new_user.is_admin)

    def test_is_not_instructor_by_default(self):
        new_user = User.objects.create(
            username="newuser",
            email="newuser@example.com",
            password="password123"
        )
        self.assertFalse(new_user.is_instructor)

    def test_is_not_ta_by_default(self):
        new_user = User.objects.create(
            username="newuser",
            email="newuser@example.com",
            password="password123"
        )
        self.assertFalse(new_user.is_ta)

    def test_email_is_unique(self):
        with self.assertRaises(Exception):
            User.objects.create(
                username="duplicate",
                email="admin@example.com",
                password="password123"
            )

    def test_username_is_unique(self):
        with self.assertRaises(Exception):
            User.objects.create(
                username="adminuser",
                email="uniqueemail@example.com",
                password="password123"
            )

    def test_user_creation_without_roles(self):
        user = User.objects.create(
            username="basicuser",
            email="basicuser@example.com",
            password="password123"
        )
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_instructor)
        self.assertFalse(user.is_ta)
