from django.test import TestCase
from TAScheduler.models import User


class UserModelTests(TestCase):

    def test_create_user(self):
        user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            is_admin=False,
            is_instructor=False,
            is_ta=True
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.is_ta)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_instructor)

    def test_get_role_admin(self):
        user = User.objects.create(
            username="adminuser",
            email="admin@example.com",
            is_admin=True
        )
        self.assertEqual(user.get_role(), "Administrator")

    def test_get_role_instructor(self):
        user = User.objects.create(
            username="instructor",
            email="instructor@example.com",
            is_instructor=True
        )
        self.assertEqual(user.get_role(), "Instructor")

    def test_get_role_ta(self):
        user = User.objects.create(
            username="tauser",
            email="ta@example.com",
            is_ta=True
        )
        self.assertEqual(user.get_role(), "TA")

    def test_get_role_no_role(self):
        user = User.objects.create(
            username="norole",
            email="norole@example.com"
        )
        self.assertEqual(user.get_role(), "No Role")

    def test_user_str_method(self):
        user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            first_name="Test",
            last_name="User"
        )
        self.assertEqual(str(user), "Test User (testuser@example.com)")

    def test_create_user_with_missing_email(self):
        with self.assertRaises(Exception):
            User.objects.create(
                username="noemailuser",
                email=None,
                password="password123"
            )

    def test_create_user_with_missing_username(self):
        with self.assertRaises(Exception):
            User.objects.create(
                username=None,
                email="nouser@example.com",
                password="password123"
            )


    def test_user_update_email(self):
        user = User.objects.create(
            username="updateuser",
            email="oldemail@example.com"
        )
        user.email = "newemail@example.com"
        user.save()
        updated_user = User.objects.get(username="updateuser")
        self.assertEqual(updated_user.email, "newemail@example.com")
