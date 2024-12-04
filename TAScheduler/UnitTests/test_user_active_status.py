from django.test import TestCase
from TAScheduler.models import User

class UserModelTests(TestCase):

    def test_user_active_status(self):
        user_active = User.objects.create(
            username="activeuser",
            email="active@example.com",
            password="password123",
            is_active=True
        )
        user_inactive = User.objects.create(
            username="inactiveuser",
            email="inactive@example.com",
            password="password123",
            is_active=False
        )
        self.assertTrue(user_active.is_active)
        self.assertFalse(user_inactive.is_active)
