from django.test import TestCase
from TAScheduler.models import User, TA

class TAModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="tauser",
            email_address="ta@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            is_ta=True
        )
        self.ta = TA.objects.create(
            user=self.user,
            grader_status=True,
            skills="Python, Django, Teaching",
            max_assignments=5
        )

    def test_create_ta(self):
        self.assertEqual(self.ta.user.username, "tauser")
        self.assertTrue(self.ta.grader_status)
        self.assertEqual(self.ta.skills, "Python, Django, Teaching")
        self.assertEqual(self.ta.max_assignments, 5)

    def test_ta_default_grader_status(self):
        new_user = User.objects.create(
            username="newta",
            email_address="newta@example.com",
            password="password123",
            first_name="Jane",
            last_name="Smith",
            is_ta=True
        )
        new_ta = TA.objects.create(user=new_user)
        self.assertFalse(new_ta.grader_status)

    def test_ta_max_assignments_validation(self):
        with self.assertRaises(Exception):
            TA.objects.create(
                user=self.user,
                max_assignments=7  # Exceeding the max value of 6
            )

    def test_ta_str_method(self):
        self.assertEqual(str(self.ta), "John - TA")

    def test_update_ta_skills(self):
        self.ta.skills = "Python, JavaScript, Data Science"
        self.ta.save()
        updated_ta = TA.objects.get(id=self.ta.id)
        self.assertEqual(updated_ta.skills, "Python, JavaScript, Data Science")
