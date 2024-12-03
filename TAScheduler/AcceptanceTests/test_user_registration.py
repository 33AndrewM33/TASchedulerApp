from django.test import TestCase
from TAScheduler.models import User

class UserModelTests(TestCase):

    def test_user_registration(self):
        user = User.objects.create(
            username="testuser",
            email_address="testuser@example.com",
            password="password123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email_address, "testuser@example.com")