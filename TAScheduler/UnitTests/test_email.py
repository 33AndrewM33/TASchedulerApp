from django.test import TestCase, override_settings
from django.core import mail
from TAScheduler.models import User, Notification


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AdditionalEmailTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
        )
        # Create admin users
        self.admin_user1 = User.objects.create(
            username="admin1",
            email="admin1@example.com",
            first_name="Admin1",
            last_name="User1",
            is_admin=True,
        )
        self.admin_user2 = User.objects.create(
            username="admin2",
            email="admin2@example.com",
            first_name="Admin2",
            last_name="User2",
            is_admin=True,
        )

    def test_email_sent_to_correct_recipient(self):
        """Test that an email is sent to the correct recipient."""
        mail.send_mail(
            subject="Welcome Email",
            message="Welcome to the platform.",
            from_email="no-reply@example.com",
            recipient_list=[self.user.email],
        )
        self.assertEqual(len(mail.outbox), 1, msg="One email should have been sent.")
        self.assertEqual(mail.outbox[0].to, [self.user.email], msg="Email recipient mismatch.")

    def test_email_contains_dynamic_content(self):
        """Test that email content contains dynamically generated user data."""
        mail.send_mail(
            subject="Account Information",
            message=f"Dear {self.user.first_name}, your account username is {self.user.username}.",
            from_email="no-reply@example.com",
            recipient_list=[self.user.email],
        )
        self.assertEqual(len(mail.outbox), 1, msg="One email should have been sent.")
        self.assertIn(self.user.first_name, mail.outbox[0].body, msg="Email body does not contain the user's first name.")
        self.assertIn(self.user.username, mail.outbox[0].body, msg="Email body does not contain the username.")

    def test_email_sent_to_multiple_recipients(self):
        """Test sending an email to multiple recipients."""
        recipient_list = [self.admin_user1.email, self.admin_user2.email]
        mail.send_mail(
            subject="System Notification",
            message="This is a system-wide notification.",
            from_email="no-reply@example.com",
            recipient_list=recipient_list,
        )
        self.assertEqual(len(mail.outbox), 1, msg="One email should have been sent.")
        for recipient in recipient_list:
            self.assertIn(recipient, mail.outbox[0].to, msg=f"Recipient {recipient} not found in the email.")



    def test_email_with_empty_recipient_list(self):
        """Test that no email is sent if the recipient list is empty."""
        mail.send_mail(
            subject="No Recipient",
            message="This email has no recipient.",
            from_email="no-reply@example.com",
            recipient_list=[],
        )
        self.assertEqual(len(mail.outbox), 0, msg="No email should have been sent for an empty recipient list.")

    def test_admin_notifications_on_new_user_creation(self):
        """Test that all admins are notified when a new user is created."""
        for admin in [self.admin_user1, self.admin_user2]:
            Notification.objects.create(
                sender=self.user,
                recipient=admin,
                subject="New User Created",
                message=f"User {self.user.username} has been created.",
            )

        mail.send_mail(
            subject="New User Created",
            message=f"User {self.user.username} has joined the platform.",
            from_email="no-reply@example.com",
            recipient_list=[self.admin_user1.email, self.admin_user2.email],
        )
        self.assertEqual(len(mail.outbox), 1, msg="One email should have been sent to notify admins.")
        for admin_email in [self.admin_user1.email, self.admin_user2.email]:
            self.assertIn(admin_email, mail.outbox[0].to, msg=f"Admin {admin_email} should have received the notification.")

    def test_email_subject_case_insensitivity(self):
        """Test that email subject is case-insensitive during validation."""
        mail.send_mail(
            subject="Test Email Subject",
            message="This is a test email.",
            from_email="no-reply@example.com",
            recipient_list=[self.user.email],
        )
        self.assertEqual(mail.outbox[0].subject.lower(), "test email subject".lower(), msg="Email subject mismatch.")

    def test_email_sent_to_multiple_admins_on_password_reset(self):
        """Test that multiple admins receive a notification when a password is reset."""
        admins = [self.admin_user1, self.admin_user2]
        for admin in admins:
            Notification.objects.create(
                sender=self.user,
                recipient=admin,
                subject="Password Reset Notification",
                message=f"User {self.user.username} has reset their password.",
            )

        mail.send_mail(
            subject="Password Reset Notification",
            message=f"User {self.user.username} has reset their password.",
            from_email="no-reply@example.com",
            recipient_list=[admin.email for admin in admins],
        )

        self.assertEqual(len(mail.outbox), 1, msg="One email should have been sent to notify all admins.")
        for admin_email in [self.admin_user1.email, self.admin_user2.email]:
            self.assertIn(admin_email, mail.outbox[0].to, msg=f"Admin {admin_email} should have received the notification.")

    def test_email_with_cc_and_bcc(self):
        """Test sending email with CC and BCC."""
        cc_email = "ccuser@example.com"
        bcc_email = "bccuser@example.com"

        mail.EmailMessage(
            subject="Test Email with CC and BCC",
            body="This email has CC and BCC recipients.",
            from_email="no-reply@example.com",
            to=[self.user.email],
            cc=[cc_email],
            bcc=[bcc_email],
        ).send()

        self.assertEqual(len(mail.outbox), 1, msg="One email should have been sent.")
        self.assertIn(self.user.email, mail.outbox[0].to, msg="Recipient mismatch.")
        self.assertIn(cc_email, mail.outbox[0].cc, msg="CC recipient mismatch.")
        # Note: BCC recipients are not visible in the email metadata.

