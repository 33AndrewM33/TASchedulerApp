from django.test import TestCase
from TAScheduler.models import User, TA, Lab, Section, Course

class TAModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="tauser",
            email="tauser@example.com",  # Corrected to 'email'
            password="password123",
            first_name="Test",
            last_name="Assistant",
            is_ta=True
        )
        self.ta = TA.objects.create(
            user=self.user,
            grader_status=True,
            skills="Python, Django",
            max_assignments=4
        )

    def test_create_ta(self):
        self.assertEqual(self.ta.user.username, "tauser")
        self.assertEqual(self.ta.user.email, "tauser@example.com")  # Corrected to 'email'
        self.assertTrue(self.ta.grader_status)
        self.assertEqual(self.ta.skills, "Python, Django")
        self.assertEqual(self.ta.max_assignments, 4)

    def test_default_grader_status(self):
        user = User.objects.create(
            username="nograder",
            email="nograder@example.com",  # Corrected to 'email'
            password="password123",
            first_name="No",
            last_name="Grader",
            is_ta=True
        )
        ta = TA.objects.create(user=user)
        self.assertFalse(ta.grader_status)

    def test_default_skills(self):
        user = User.objects.create(
            username="noskills",
            email="noskills@example.com",  # Corrected to 'email'
            password="password123",
            first_name="No",
            last_name="Skills",
            is_ta=True
        )
        ta = TA.objects.create(user=user)
        self.assertEqual(ta.skills, "No skills listed")

    def test_max_assignments_validator(self):
        with self.assertRaises(Exception):
            TA.objects.create(
                user=self.user,
                max_assignments=7  # Exceeds the MaxValueValidator limit (6)
            )

    def test_min_assignments_validator(self):
        with self.assertRaises(Exception):
            TA.objects.create(
                user=self.user,
                max_assignments=-1  # Below the MinValueValidator limit (0)
            )

    def test_update_ta_info(self):
        self.ta.grader_status = False
        self.ta.skills = "Java, C++"
        self.ta.max_assignments = 6
        self.ta.save()

        updated_ta = TA.objects.get(id=self.ta.id)
        self.assertFalse(updated_ta.grader_status)
        self.assertEqual(updated_ta.skills, "Java, C++")
        self.assertEqual(updated_ta.max_assignments, 6)

    def test_ta_str_method(self):
        self.assertEqual(str(self.ta), "Test - TA")

    def test_ta_user_relationship(self):
        self.assertEqual(self.ta.user.first_name, "Test")
        self.assertEqual(self.ta.user.get_role(), "TA")

    def test_ta_creation_without_user(self):
        with self.assertRaises(Exception):
            TA.objects.create(grader_status=True)

    def test_reassign_ta_to_different_user(self):
        new_user = User.objects.create(
            username="newta",
            email="newta@example.com",  # Corrected to 'email'
            password="password123",
            first_name="New",
            last_name="Assistant",
            is_ta=True
        )
        self.ta.user = new_user
        self.ta.save()

        self.assertEqual(self.ta.user.username, "newta")
        self.assertEqual(self.ta.user.email, "newta@example.com")  # Corrected to 'email'

    def test_ta_with_multiple_labs(self):
        course = Course.objects.create(
            course_id="CS101",
            name="Intro to CS",
            semester="Fall 2024",
            description="Introductory Computer Science",
            num_of_sections=2,
            modality="In-person"
        )
        section1 = Section.objects.create(
            section_id=1,
            course=course,
            location="Room 101",
            meeting_time="Mon 9-11"
        )
        section2 = Section.objects.create(
            section_id=2,
            course=course,
            location="Room 102",
            meeting_time="Wed 9-11"
        )
        lab1 = Lab.objects.create(section=section1, ta=self.ta)
        lab2 = Lab.objects.create(section=section2, ta=self.ta)

        self.assertEqual(self.ta.assigned_labs.count(), 2)
        self.assertIn(lab1, self.ta.assigned_labs.all())
        self.assertIn(lab2, self.ta.assigned_labs.all())
