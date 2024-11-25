from django.test import TestCase
from TAScheduler.models import (
    User,
    TA,
    Instructor,
    Course,
    Section,
    Lab,
    Lecture,
    TAToCourse,
    InstructorToCourse
)


class ModelsTestCase(TestCase):
    def setUp(self):
        # Create Users
        self.user1 = User.objects.create(
            username="ta_user",
            email_address="ta@example.com",
            password="password123",
            first_name="Jane",
            last_name="Doe",
            phone_number="1234567890",
            is_ta=True
        )
        self.user2 = User.objects.create(
            username="instructor_user",
            email_address="instructor@example.com",
            password="password123",
            first_name="John",
            last_name="Smith",
            phone_number="0987654321",
            is_instructor=True
        )

        # Create TA and Instructor profiles
        self.ta = TA.objects.create(
            user=self.user1,
            grader_status=True,
            skills="Python, Java",
            max_assignments=4
        )
        self.instructor = Instructor.objects.create(
            user=self.user2,
            max_assignments=5
        )

        # Create Course and Section
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Intro to Computer Science",
            description="Basic programming concepts.",
            num_of_sections=3,
            modality="In-person"
        )
        self.section = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="Mon/Wed 10:00-11:30"
        )

        # Create Lab and Lecture
        self.lab = Lab.objects.create(
            section=self.section,
            ta=self.ta
        )
        self.lecture = Lecture.objects.create(
            section=self.section,
            instructor=self.instructor,
            ta=self.ta
        )

    def test_user_creation(self):
        self.assertEqual(self.user1.username, "ta_user")
        self.assertTrue(self.user1.is_ta)
        self.assertEqual(self.user2.email_address, "instructor@example.com")
        self.assertTrue(self.user2.is_instructor)

    def test_ta_creation(self):
        self.assertTrue(self.ta.grader_status)
        self.assertEqual(self.ta.skills, "Python, Java")
        self.assertEqual(self.ta.max_assignments, 4)

    def test_instructor_creation(self):
        self.assertEqual(self.instructor.user.email_address, "instructor@example.com")
        self.assertEqual(self.instructor.max_assignments, 5)

    def test_course_creation(self):
        self.assertEqual(self.course.course_id, "CS101")
        self.assertEqual(self.course.num_of_sections, 3)
        self.assertEqual(self.course.modality, "In-person")

    def test_section_creation(self):
        self.assertEqual(self.section.course, self.course)
        self.assertEqual(self.section.location, "Room 101")
        self.assertEqual(self.section.meeting_time, "Mon/Wed 10:00-11:30")

    def test_lab_creation(self):
        self.assertEqual(self.lab.section, self.section)
        self.assertEqual(self.lab.ta, self.ta)

    def test_lecture_creation(self):
        self.assertEqual(self.lecture.section, self.section)
        self.assertEqual(self.lecture.instructor, self.instructor)
        self.assertEqual(self.lecture.ta, self.ta)

    def test_ta_to_course_creation(self):
        ta_to_course = TAToCourse.objects.create(ta=self.ta, course=self.course)
        self.assertEqual(ta_to_course.ta, self.ta)
        self.assertEqual(ta_to_course.course, self.course)

    def test_instructor_to_course_creation(self):
        instructor_to_course = InstructorToCourse.objects.create(instructor=self.instructor, course=self.course)
        self.assertEqual(instructor_to_course.instructor, self.instructor)
        self.assertEqual(instructor_to_course.course, self.course)
