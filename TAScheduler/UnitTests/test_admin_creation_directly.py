from django.test import TestCase
from TAScheduler.models import User, TA
#Ensure a created superuser is admin.
class AccountCreationTests(TestCase):
    def test_admin_creation_directly(self):
        admin = User.objects.create_superuser(username="super_admin", email="admin@example.com", password="password123")
        self.assertTrue(admin.is_admin)
        self.assertTrue(admin.is_staff)

    def test_ta_account_creation(self):
        user = User.objects.create(username="ta_user", is_ta=True)
        ta_profile = TA.objects.create(user=user)
        self.assertTrue(user.is_ta)
        self.assertEqual(ta_profile.user.username, "ta_user")

    def test_duplicate_username_fails(self):
        User.objects.create(username="duplicate_user", email="user1@example.com")
        with self.assertRaises(Exception):
            User.objects.create(username="duplicate_user", email="user2@example.com")
