from django.core import mail
from django.test import TestCase
from django.core.mail import send_mail

class EmailTests(TestCase):
    def test_email_sent_with_valid_subject(self):
        send_mail(
            "Test Subject",
            "Test Body",
            "no-reply@example.com",
            ["recipient1@example.com"],
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")

    def test_email_sent_with_multiple_recipients(self):
        send_mail(
            "Subject for multiple recipients",
            "Email body",
            "no-reply@example.com",
            ["recipient1@example.com", "recipient2@example.com"],
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 2)

