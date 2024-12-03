from django.test import TestCase
from TAScheduler.models import User

class UserModelTests(TestCase):

    def test_user_role_assignment(self):
        user_admin = User.objects.create(
            username="adminuser",
            email="admin@example.com",
            password="password123",
            is_admin=True
        )
        user_instructor = User.objects.create(
            username="instructor",
            email="instructor@example.com",
            password="password123",
            is_instructor=True
        )
        user_ta = User.objects.create(
            username="tauser",
            email="ta@example.com",
            password="password123",
            is_ta=True
        )
        self.assertTrue(user_admin.is_admin)
        self.assertTrue(user_instructor.is_instructor)
        self.assertTrue(user_ta.is_ta)
        self.assertFalse(user_admin.is_instructor)
        self.assertFalse(user_admin.is_ta)
        self.assertFalse(user_instructor.is_admin)
        self.assertFalse(user_instructor.is_ta)
        self.assertFalse(user_ta.is_admin)
        self.assertFalse(user_ta.is_instructor)
