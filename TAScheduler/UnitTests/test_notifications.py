from django.test import TestCase
from django.contrib.auth import get_user_model
from TAScheduler.models import Notification

User = get_user_model()


class NotificationTests(TestCase):
    def setUp(self):
        # Create unique test users
        self.sender = User.objects.create_user(
            username="sender_user", email="sender@example.com", password="password123"
        )
        self.recipient1 = User.objects.create_user(
            username="recipient_user1", email="recipient1@example.com", password="password123"
        )
        self.recipient2 = User.objects.create_user(
            username="recipient_user2", email="recipient2@example.com", password="password123"
        )

    def test_create_notification(self):
        """Test that a notification is created successfully."""
        notification = Notification.objects.create(
            sender=self.sender,
            recipient=self.recipient1,
            subject="Test Notification",
            message="This is a test notification.",
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.subject, "Test Notification")
        self.assertEqual(notification.message, "This is a test notification.")
        self.assertFalse(notification.is_read)

    def test_mark_notification_as_read(self):
        """Test marking a notification as read."""
        notification = Notification.objects.create(
            sender=self.sender,
            recipient=self.recipient1,
            subject="Test Notification",
            message="This is a test notification.",
        )
        notification.is_read = True
        notification.save()

        self.assertTrue(Notification.objects.get(id=notification.id).is_read)

    def test_send_multiple_notifications(self):
        """Test sending multiple notifications to different users."""
        Notification.objects.create(
            sender=self.sender,
            recipient=self.recipient1,
            subject="First Notification",
            message="Message 1",
        )
        Notification.objects.create(
            sender=self.sender,
            recipient=self.recipient2,
            subject="Second Notification",
            message="Message 2",
        )

        self.assertEqual(Notification.objects.count(), 2)
        self.assertTrue(Notification.objects.filter(recipient=self.recipient1).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.recipient2).exists())



    def test_filter_unread_notifications(self):
        """Test filtering unread notifications."""
        Notification.objects.create(
            sender=self.sender,
            recipient=self.recipient1,
            subject="Unread Notification",
            message="This is unread.",
        )
        Notification.objects.create(
            sender=self.sender,
            recipient=self.recipient1,
            subject="Read Notification",
            message="This is read.",
            is_read=True,
        )
        unread_notifications = Notification.objects.filter(recipient=self.recipient1, is_read=False)
        self.assertEqual(unread_notifications.count(), 1)
        self.assertEqual(unread_notifications.first().subject, "Unread Notification")

    def test_delete_notification(self):
        """Test that a notification can be deleted."""
        notification = Notification.objects.create(
            sender=self.sender,
            recipient=self.recipient1,
            subject="To be deleted",
            message="This notification will be deleted.",
        )
        notification.delete()
        self.assertEqual(Notification.objects.count(), 0)
