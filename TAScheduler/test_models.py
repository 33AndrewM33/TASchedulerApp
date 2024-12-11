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
            first_name="Instructor",
            last_name="User",
            is_instructor=True,
        )
        self.user2.set_password("instructorpassword")
        self.user2.save()

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
            instructor=self.user2
        )

        # Section
        self.section = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="MWF 9:00-10:00 AM"
        )

        # Lab
        self.lab = Lab.objects.create(
            lab_id=1,
            section=self.section,
            location="Lab 202",
            meeting_time="TTh 10:00-11:00 AM"
        )

        # Lecture
        self.lecture = Lecture.objects.create(
            lecture_id=1,
            section=self.section,
            topic="Introduction to Programming",
            date="2024-09-01"
        )

    # User model tests
    def test_user_creation(self):
        self.assertEqual(self.ta_user.email_address, "ta@example.com")
        self.assertEqual(self.ta_user.first_name, "TA")

    def test_ta_creation(self):
        self.assertTrue(self.ta_user.grader_status)
        self.assertEqual(self.ta_user.skills, "Python, Java")

    def test_instructor_creation(self):
        self.assertEqual(self.user2.email_address, "instructor@example.com")

    def test_user_phone_number_optional(self):
        self.assertEqual(self.user1.phone_number, "1234567890")

    def test_regular_user_password(self):
        self.assertTrue(self.regular_user.check_password("userpassword"))

    # Course model tests
    def test_course_creation(self):
        self.assertEqual(self.course.name, "Intro to Computer Science")
        self.assertEqual(self.course.num_of_sections, 2)

    def test_course_instructor(self):
        self.assertEqual(self.course.instructor, self.user2)

    def test_course_semester(self):
        self.assertEqual(self.course.semester, "Fall 2024")

    # Section model tests
    def test_section_creation(self):
        self.assertEqual(self.section.course, self.course)
        self.assertEqual(self.section.location, "Room 101")

    def test_section_meeting_time(self):
        self.assertEqual(self.section.meeting_time, "MWF 9:00-10:00 AM")

    # Lab model tests
    def test_lab_creation(self):
        self.assertEqual(self.lab.location, "Lab 202")

    def test_lab_meeting_time(self):
        self.assertEqual(self.lab.meeting_time, "TTh 10:00-11:00 AM")

    def test_lab_section_relation(self):
        self.assertEqual(self.lab.section, self.section)

    # Lecture model tests
    def test_lecture_creation(self):
        self.assertEqual(self.lecture.topic, "Introduction to Programming")
        self.assertEqual(self.lecture.date, "2024-09-01")

    def test_lecture_section_relation(self):
        self.assertEqual(self.lecture.section, self.section)

    # Additional tests for edge cases
    def test_empty_skills_for_ta(self):
        self.ta_user.skills = ""
        self.ta_user.save()
        self.assertEqual(self.ta_user.skills, "")

    def test_course_without_instructor(self):
        course = Course.objects.create(
            course_id="CS102",
            semester="Spring 2025",
            name="Advanced CS",
            description="An advanced course in computer science.",
            num_of_sections=1,
            modality="Online"
        )
        self.assertIsNone(course.instructor)

    def test_duplicate_usernames(self):
        with self.assertRaises(Exception):
            User.objects.create(
                username="ta_user",
                email_address="duplicate@example.com",
                password="password123"
            )

    def test_user_email_uniqueness(self):
        with self.assertRaises(Exception):
            User.objects.create(
                username="unique_user",
                email_address="ta@example.com",
                password="password123"
            )

    def test_invalid_email_format(self):
        with self.assertRaises(ValueError):
            User.objects.create(
                username="invalid_email_user",
                email_address="not-an-email",
                password="password123"
            )

    def test_course_with_no_sections(self):
        course = Course.objects.create(
            course_id="CS103",
            semester="Summer 2025",
            name="Algorithms",
            description="An in-depth study of algorithms.",
            num_of_sections=0,
            modality="Hybrid"
        )
        self.assertEqual(course.num_of_sections, 0)

    def test_section_without_meeting_time(self):
        section = Section.objects.create(
            section_id=2,
            course=self.course,
            location="Room 202"
        )
        self.assertIsNone(section.meeting_time)

    def test_create_lab_with_invalid_section(self):
        with self.assertRaises(Exception):
            Lab.objects.create(
                lab_id=2,
                section=None,
                location="Lab 303",
                meeting_time="TTh 2:00-3:00 PM"
            )

    def test_update_section_meeting_time(self):
        self.section.meeting_time = "MWF 10:00-11:00 AM"
        self.section.save()
        self.assertEqual(self.section.meeting_time, "MWF 10:00-11:00 AM")

    def test_delete_course_with_sections(self):
        course_id = self.course.id
        self.course.delete()
        with self.assertRaises(Section.DoesNotExist):
            Section.objects.get(course_id=course_id)

    def test_assign_ta_to_section(self):
        self.section.ta = self.ta_user
        self.section.save()
        self.assertEqual(self.section.ta, self.ta_user)

    def test_section_ta_null(self):
        self.assertIsNone(self.section.ta)

    def test_delete_ta_assigned_to_section(self):
        self.section.ta = self.ta_user
        self.section.save()
        self.ta_user.delete()
        self.section.refresh_from_db()
        self.assertIsNone(self.section.ta)

    def test_create_course_with_invalid_modality(self):
        with self.assertRaises(ValueError):
            Course.objects.create(
                course_id="CS104",
                semester="Fall 2025",
                name="Quantum Computing",
                description="An introduction to quantum computing.",
                num_of_sections=1,
                modality="Invalid Modality"
            )

    def test_update_course_description(self):
        self.course.description = "An updated description."
        self.course.save()
        self.assertEqual(self.course.description, "An updated description.")

    def test_lab_without_location(self):
        lab = Lab.objects.create(
            lab_id=2,
            section=self.section,
            meeting_time="F 3:00-4:00 PM"
        )
        self.assertIsNone(lab.location)

    def test_create_user_without_username(self):
        with self.assertRaises(ValueError):
            User.objects.create(
                username=None,
                email_address="nousername@example.com",
                password="password123"
            )

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create(
                username="nouser_email",
                email_address=None,
                password="password123"
            )

    def test_ta_grader_status_default(self):
        new_ta = TA.objects.create(
            username="new_ta",
            email_address="new_ta@example.com",
            first_name="New",
            last_name="TA",
            is_ta=True
        )
        self.assertFalse(new_ta.grader_status)

    def test_lecture_topic_update(self):
        self.lecture.topic = "Updated Topic"
        self.lecture.save()
        self.assertEqual(self.lecture.topic, "Updated Topic")

    def test_lecture_date_update(self):
        self.lecture.date = "2024-09-15"
        self.lecture.save()
        self.assertEqual(self.lecture.date, "2024-09-15")
