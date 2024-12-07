from django.test import TestCase
from django.core.exceptions import ValidationError
from TAScheduler.models import Course, Section

class CourseModelTestCase(TestCase):
    def setUp(self):
        # Set up initial data for the tests
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="Learn the basics of Computer Science.",
            num_of_sections=3,
            modality="Online"
        )

    def test_create_course(self):
        course = Course.objects.get(course_id="CS101")
        self.assertEqual(course.name, "Introduction to Computer Science")
        self.assertEqual(course.semester, "Fall 2024")
        self.assertEqual(course.description, "Learn the basics of Computer Science.")
        self.assertEqual(course.num_of_sections, 3)
        self.assertEqual(course.modality, "Online")

    def test_update_course(self):
        self.course.name = "Intro to CS"
        self.course.description = "An updated description of the course."
        self.course.num_of_sections = 4
        self.course.save()

        course = Course.objects.get(course_id="CS101")
        self.assertEqual(course.name, "Intro to CS")
        self.assertEqual(course.description, "An updated description of the course.")
        self.assertEqual(course.num_of_sections, 4)

    def test_delete_course(self):
        self.course.delete()
        with self.assertRaises(Course.DoesNotExist):
            Course.objects.get(course_id="CS101")

    def test_retrieve_course(self):
        """Test retrieving a course by its ID."""
        course = Course.objects.get(course_id="CS101")
        self.assertEqual(course.name, "Introduction to Computer Science")

    def test_course_relationship_with_sections(self):
        """Test the relationship between a course and its sections."""
        # Create related sections
        section1 = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="Monday 10:00-11:30"
        )
        section2 = Section.objects.create(
            section_id=2,
            course=self.course,
            location="Room 102",
            meeting_time="Wednesday 2:00-3:30"
        )

        # Verify the course's sections
        sections = self.course.sections.all()
        self.assertEqual(sections.count(), 2)
        self.assertIn(section1, sections)
        self.assertIn(section2, sections)

    def test_delete_course_with_sections(self):
        """Test cascading delete behavior when a course is deleted."""
        # Create related sections
        section1 = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="Monday 10:00-11:30"
        )
        section2 = Section.objects.create(
            section_id=2,
            course=self.course,
            location="Room 102",
            meeting_time="Wednesday 2:00-3:30"
        )

        # Ensure the course and sections are saved
        self.assertIsNotNone(self.course.id, "Course instance must be saved.")
        self.assertIsNotNone(section1.id, "Section 1 must be saved.")
        self.assertIsNotNone(section2.id, "Section 2 must be saved.")

        # Delete the course
        self.course.delete()

        # Verify that the sections related to this course are deleted
        sections_count = Section.objects.filter(course_id=self.course.id).count()
        self.assertEqual(sections_count, 0, "Sections related to the deleted course should be removed.")

    def test_create_course_with_invalid_data(self):
        with self.assertRaises(ValidationError):
            invalid_course = Course(
                course_id="",  # Invalid: empty course ID
                semester="Fall 2024",
                name="Invalid Course",
                description="This course has invalid data.",
                num_of_sections=3,
                modality="Online"
            )
            invalid_course.full_clean()  # Triggers model validation
            invalid_course.save()
