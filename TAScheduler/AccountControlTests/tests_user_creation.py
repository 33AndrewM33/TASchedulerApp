from django.test import TestCase
from TAScheduler.models import User, TA, Instructor, Course, Section, Lab, Lecture, TAToCourse, InstructorToCourse


class ModelsTestCase(TestCase):
    def setUp(self):
        # Admin user
        self.admin_user = User.objects.create(
            username="admin_user",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.admin_user.set_password("adminpassword")
        self.admin_user.save()

        # Instructor user
        self.instructor_user = Instructor.objects.create(
            username="instructor_user",
            email_address="instructor@example.com",
            first_name="Instructor",
            last_name="User",
            is_instructor=True,
        )
        self.instructor_user.set_password("instructorpassword")
        self.instructor_user.save()

        # TA user
        self.ta_user = TA.objects.create(
            username="ta_user",
            email_address="ta@example.com",
            first_name="TA",
            last_name="User",
            is_ta=True,
            grader_status=True,
            skills="Python, Java"
        )
        self.ta_user.set_password("tapassword")
        self.ta_user.save()

        # Regular user
        self.regular_user = User.objects.create(
            username="regular_user",
            email_address="user@example.com",
            first_name="Regular",
            last_name="User",
        )
        self.regular_user.set_password("userpassword")
        self.regular_user.save()

        # Course
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Intro to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=2,
            modality="In-person",
            instructor=self.instructor_user
        )

        # Section
        self.section = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="MWF 9:00-10:00 AM"
        )

    def test_user_creation(self):
        self.assertEqual(self.ta_user.email_address, "ta@example.com")
        self.assertEqual(self.ta_user.first_name, "TA")

    def test_ta_creation(self):
        self.assertTrue(self.ta_user.grader_status)
        self.assertEqual(self.ta_user.skills, "Python, Java")

    def test_instructor_creation(self):
        self.assertEqual(self.instructor_user.email_address, "instructor@example.com")

    def test_course_creation(self):
        self.assertEqual(self.course.name, "Intro to Computer Science")
        self.assertEqual(self.course.num_of_sections, 2)

    def test_section_creation(self):
        self.assertEqual(self.section.course, self.course)
        self.assertEqual(self.section.location, "Room 101")
