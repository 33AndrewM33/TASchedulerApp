from django.test import TestCase
from TAScheduler.models import User, TA, Instructor, Course, Section, Lab, Lecture


class ModelsTestCase(TestCase):
    def setUp(self):
        # Create User
        self.user1 = User.objects.create(
            username="ta_user",
            email_address="ta@example.com",
            password="password123",
            first_name="Jane",
            last_name="Doe",
            phone_number="1234567890"
        )
        self.user2 = User.objects.create(
            username="instructor_user",
            email_address="instructor@example.com",
            password="password123",
            first_name="John",
            last_name="Smith",
            phone_number="0987654321"
        )

        # Create TA and Instructor profiles
        self.ta = TA.objects.create(user=self.user1, grader_status=True, skills="Python, Java")
        self.instructor = Instructor.objects.create(user=self.user2)

        # Create Course and Section
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Intro to Computer Science",
            description="Basic programming concepts.",
            num_of_sections=2,
            modality="In-person"
        )
        self.section = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="Mon/Wed 10:00-11:30"
        )

    def test_user_creation(self):
        self.assertEqual(self.user1.email_address, "ta@example.com")
        self.assertEqual(self.user1.first_name, "Jane")

    def test_ta_creation(self):
        self.assertTrue(self.ta.grader_status)
        self.assertEqual(self.ta.skills, "Python, Java")

    def test_instructor_creation(self):
        self.assertEqual(self.instructor.user.email_address, "instructor@example.com")

    def test_course_creation(self):
        self.assertEqual(self.course.name, "Intro to Computer Science")
        self.assertEqual(self.course.num_of_sections, 2)

    def test_section_creation(self):
        self.assertEqual(self.section.course, self.course)
        self.assertEqual(self.section.location, "Room 101")
