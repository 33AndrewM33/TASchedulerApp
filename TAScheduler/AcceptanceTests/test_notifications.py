from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from TAScheduler.models import User, Administrator, Course, Section, Notification


class NotificationTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create client
        self.client = Client()

        # Create admin users (creator and recipient)
        self.admin_user = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="One",
            is_admin=True
        )
        Administrator.objects.create(user=self.admin_user)

        # Create another admin to receive notifications
        self.admin_user2 = User.objects.create_user(
            username="admin2",
            email="admin2@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="Two",
            is_admin=True
        )
        Administrator.objects.create(user=self.admin_user2)

        # Log in the first admin user
        self.client.login(username="admin1", password="adminpassword")

    def test_course_creation_notification(self):
        """Test that admins receive notification when a course is created"""
        # Create a course
        course_data = {
            'course_id': 'CS101',
            'name': 'Test Course',
            'semester': 'Fall 2024',
            'description': 'Test Description',
            'num_of_sections': 2,
            'modality': 'Online'
        }

        self.client.post(reverse('create_course'), course_data)

        # Check notifications
        notifications = Notification.objects.filter(
            recipient=self.admin_user2,
            subject="New Course Created"
        )

        self.assertTrue(notifications.exists())
        notification = notifications.first()
        self.assertIn('CS101', notification.message)
        self.assertIn('Test Course', notification.message)
        self.assertEqual(notification.sender, self.admin_user)

    def test_section_creation_notification(self):
        """Test that admins receive notification when a section is created"""
        # First create a course
        course = Course.objects.create(
            course_id="CS101",
            name="Test Course",
            semester="Fall 2024",
            description="Test Description",
            num_of_sections=2,
            modality="Online"
        )

        # Create a section
        section_data = {
            'course_id': course.course_id,
            'section_id': 1,
            'section_type': 'Lecture',
            'location': 'Room 101',
            'meeting_time': 'MWF 10:00-11:00'
        }

        self.client.post(reverse('create_section'), section_data)

        # Check notifications
        notifications = Notification.objects.filter(
            recipient=self.admin_user2,
            subject="New Section Created"
        )

        self.assertTrue(notifications.exists())
        notification = notifications.first()
        self.assertIn('section', notification.message.lower())
        self.assertIn('ID: 1', notification.message)

    def test_account_creation_notification(self):
        """Test that admins receive notification when an account is created"""
        # Create a new user account
        new_user_data = {
            'action': 'create',
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'role': 'instructor',
            'first_name': 'New',
            'last_name': 'User'
        }

        self.client.post(reverse('account_management'), new_user_data)

        # Check notifications
        notifications = Notification.objects.filter(
            recipient=self.admin_user2,
            subject="New Account Created"
        )

        self.assertTrue(notifications.exists())
        notification = notifications.first()
        self.assertIn('newuser', notification.message)

    def test_clear_notifications(self):
        """Test clearing all notifications for a user"""
        # Create some test notifications
        for i in range(3):
            Notification.objects.create(
                sender=self.admin_user,
                recipient=self.admin_user2,
                subject=f"Test Notification {i}",
                message=f"Test Message {i}"
            )

        # Verify notifications exist
        self.assertEqual(
            Notification.objects.filter(recipient=self.admin_user2).count(),
            3
        )

        # Clear notifications
        self.client.force_login(self.admin_user2)  # Switch to admin2
        response = self.client.post(reverse('clear_notifications'))

        # Verify notifications are cleared
        self.assertEqual(
            Notification.objects.filter(recipient=self.admin_user2).count(),
            0
        )

    def test_notification_count(self):
        """Test that unread notification count is correct"""
        # Create some test notifications
        for i in range(3):
            Notification.objects.create(
                sender=self.admin_user,
                recipient=self.admin_user2,
                subject=f"Test Notification {i}",
                message=f"Test Message {i}"
            )

        # Log in as admin2 and check home page
        self.client.force_login(self.admin_user2)
        response = self.client.get(reverse('home'))

        # Check notification count in context
        self.assertEqual(response.context['unread_notifications_count'], 3)

    def test_notification_attributes(self):
        """Test that notification has correct attributes when created"""
        notification = Notification.objects.create(
            sender=self.admin_user,
            recipient=self.admin_user2,
            subject="Test Subject",
            message="Test Message"
        )

        # Test basic attributes
        self.assertEqual(notification.sender, self.admin_user)
        self.assertEqual(notification.recipient, self.admin_user2)
        self.assertEqual(notification.subject, "Test Subject")
        self.assertEqual(notification.message, "Test Message")
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.timestamp)