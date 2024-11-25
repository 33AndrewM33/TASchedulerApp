from django.test import TestCase
from TAScheduler.models import (
    User, Supervisor, TA, Instructor, Course, Section, Lab, Lecture,
    TAToCourse, InstructorToCourse, Administrator
)

class ModelsTestCase(TestCase):

    def setUp(self):
        # Create User
        self.user1 = User.objects.create(
            username="user1",
            email_address="user1@example.com",
            password="password123",
            first_name="John",
            last_name="Doe"
        )
        self.user2 = User.objects.create(
            username="user2",
            email_address="user2@example.com",
            password="password123",
            first_name="Jane",
            last_name="Smith"
        )
        self.user3 = User.objects.create(
            username="user3",
            email_address="user3@example.com",
            password="password123",
            first_name="Michael",
            last_name="Brown"
        )

    def test_user_creation(self):
        user = User.objects.get(username="user1")
        self.assertEqual(user.email_address, "user1@example.com")
        self.assertEqual(user.first_name, "John")

    def test_supervisor_creation(self):
        supervisor = Supervisor.objects.create(user=self.user1)
        self.assertEqual(supervisor.user.username, "user1")

    def test_ta_creation(self):
        ta = TA.objects.create(user=self.user1, grader_status=True, skills="Python, Java")
        self.assertTrue(ta.grader_status)
        self.assertEqual(ta.skills, "Python, Java")

    def test_instructor_creation(self):
        instructor = Instructor.objects.create(user=self.user2)
        self.assertEqual(instructor.user.email_address, "user2@example.com")
        self.assertEqual(instructor.max_assignments, 6)

    def test_course_creation(self):
        course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Intro to Programming",
            description="Learn programming basics.",
            num_of_sections=3,
            modality="Online"
        )
        self.assertEqual(course.course_id, "CS101")
        self.assertEqual(course.name, "Intro to Programming")

    def test_section_creation(self):
        course = Course.objects.create(
            course_id="CS102",
            semester="Spring 2024",
            name="Data Structures",
            description="Advanced data structures.",
            num_of_sections=2,
            modality="In-person"
        )
        section = Section.objects.create(
            section_id=1,
            course=course,
            location="Room 101",
            meeting_time="Mon/Wed 9:00-10:30"
        )
        self.assertEqual(section.course.name, "Data Structures")
        self.assertEqual(section.location, "Room 101")

    def test_lab_creation(self):
        ta = TA.objects.create(user=self.user1, grader_status=True)
        course = Course.objects.create(
            course_id="CS103",
            semester="Fall 2024",
            name="Algorithms",
            description="Algorithm design and analysis.",
            num_of_sections=1,
            modality="Online"
        )
        section = Section.objects.create(
            section_id=1,
            course=course,
            location="Room 201",
            meeting_time="Tue/Thu 11:00-12:30"
        )
        lab = Lab.objects.create(section=section, ta=ta)
        self.assertEqual(lab.section.section_id, 1)
        self.assertEqual(lab.ta.user.username, "user1")

    def test_lecture_creation(self):
        instructor = Instructor.objects.create(user=self.user2)
        course = Course.objects.create(
            course_id="CS104",
            semester="Winter 2024",
            name="Operating Systems",
            description="Introduction to OS concepts.",
            num_of_sections=1,
            modality="In-person"
        )
        section = Section.objects.create(
            section_id=1,
            course=course,
            location="Room 301",
            meeting_time="Mon/Wed 1:00-2:30"
        )
        lecture = Lecture.objects.create(section=section, instructor=instructor)
        self.assertEqual(lecture.section.section_id, 1)
        self.assertEqual(lecture.instructor.user.username, "user2")

    def test_ta_to_course_creation(self):
        ta = TA.objects.create(user=self.user1, grader_status=True)
        course = Course.objects.create(
            course_id="CS105",
            semester="Summer 2024",
            name="Machine Learning",
            description="Introduction to ML concepts.",
            num_of_sections=2,
            modality="Online"
        )
        ta_to_course = TAToCourse.objects.create(ta=ta, course=course)
        self.assertEqual(ta_to_course.ta.user.username, "user1")
        self.assertEqual(ta_to_course.course.course_id, "CS105")

    def test_instructor_to_course_creation(self):
        instructor = Instructor.objects.create(user=self.user2)
        course = Course.objects.create(
            course_id="CS106",
            semester="Fall 2024",
            name="Artificial Intelligence",
            description="Introduction to AI concepts.",
            num_of_sections=1,
            modality="In-person"
        )
        instructor_to_course = InstructorToCourse.objects.create(instructor=instructor, course=course)
        self.assertEqual(instructor_to_course.instructor.user.username, "user2")
        self.assertEqual(instructor_to_course.course.course_id, "CS106")

    def test_administrator_creation(self):
        admin = Administrator.objects.create(user=self.user3)
        self.assertEqual(admin.user.email_address, "user3@example.com")
