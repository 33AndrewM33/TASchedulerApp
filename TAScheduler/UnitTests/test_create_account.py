from django.test import TestCase
from TAScheduler.models import User, TA, Instructor, Administrator, Course, Section, Lecture


class CreateAccountTestCase(TestCase):
    def setUp(self):
        # Set up data for tests if needed
        pass

    def test_create_ta_account(self):
        user = User.objects.create(
            username="ta_user",
            email="ta_user@example.com",  # Corrected to 'email'
            password="password123",
            is_ta=True
        )
        TA.objects.create(user=user, grader_status=True)

        # Verify user attributes
        self.assertEqual(user.username, "ta_user")
        self.assertEqual(user.email, "ta_user@example.com")  # Corrected to 'email'
        self.assertTrue(user.is_ta)
        self.assertFalse(user.is_instructor)
        self.assertFalse(user.is_admin)

        # Verify TA profile is created
        self.assertTrue(hasattr(user, "ta_profile"))
        self.assertEqual(user.ta_profile.grader_status, True)

    def test_create_instructor_account(self):
        user = User.objects.create(
            username="instructor_user",
            email="instructor_user@example.com",  # Corrected to 'email'
            password="password123",
            is_instructor=True
        )
        Instructor.objects.create(user=user)

        # Verify user attributes
        self.assertEqual(user.username, "instructor_user")
        self.assertEqual(user.email, "instructor_user@example.com")  # Corrected to 'email'
        self.assertTrue(user.is_instructor)
        self.assertFalse(user.is_ta)
        self.assertFalse(user.is_admin)

        # Verify Instructor profile is created
        self.assertTrue(hasattr(user, "instructor_profile"))

    def test_create_admin_account(self):
        user = User.objects.create(
            username="admin_user",
            email="admin_user@example.com",  # Corrected to 'email'
            password="password123",
            is_admin=True
        )
        Administrator.objects.create(user=user)

        # Verify user attributes
        self.assertEqual(user.username, "admin_user")
        self.assertEqual(user.email, "admin_user@example.com")  # Corrected to 'email'
        self.assertTrue(user.is_admin)
        self.assertFalse(user.is_ta)
        self.assertFalse(user.is_instructor)

        # Verify Administrator profile is created
        self.assertTrue(hasattr(user, "administrator_profile"))

    def test_create_user_without_role(self):
        user = User.objects.create(
            username="basic_user",
            email="basic_user@example.com",  # Corrected to 'email'
            password="password123"
        )

        # Verify user attributes
        self.assertEqual(user.username, "basic_user")
        self.assertEqual(user.email, "basic_user@example.com")  # Corrected to 'email'
        self.assertFalse(user.is_ta)
        self.assertFalse(user.is_instructor)
        self.assertFalse(user.is_admin)

        # Verify no role-specific profiles are created
        self.assertFalse(hasattr(user, "ta_profile"))
        self.assertFalse(hasattr(user, "instructor_profile"))
        self.assertFalse(hasattr(user, "administrator_profile"))
