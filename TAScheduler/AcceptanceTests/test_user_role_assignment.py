from django.test import TestCase
from TAScheduler.models import User

class UserRoleAssignmentTests(TestCase):

    def test_user_role_assignment_admin(self):
        user = User.objects.create(
            username="adminuser",
            email_address="admin@example.com",
            password="password123",
            is_admin=True
        )
        self.assertTrue(user.is_admin)
        self.assertEqual(user.get_role(), "Administrator")

    def test_user_role_assignment_instructor(self):
        user = User.objects.create(
            username="instructor",
            email_address="instructor@example.com",
            password="password123",
            is_instructor=True
        )
        self.assertTrue(user.is_instructor)
        self.assertEqual(user.get_role(), "Instructor")

    def test_user_role_assignment_ta(self):
        user = User.objects.create(
            username="tauser",
            email_address="ta@example.com",
            password="password123",
            is_ta=True
        )
        self.assertTrue(user.is_ta)
        self.assertEqual(user.get_role(), "TA")

    def test_user_role_assignment_no_role(self):
        user = User.objects.create(
            username="norole",
            email_address="norole@example.com",
            password="password123"
        )
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_instructor)
        self.assertFalse(user.is_ta)
        self.assertEqual(user.get_role(), "No Role")
