from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from TAScheduler.models import User, Course, Section, TA, Instructor, Administrator


class TAAssignmentTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create instructor user
        self.instructor_user = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="instructorpass",
            first_name="Test",
            last_name="Instructor",
            is_instructor=True
        )
        self.instructor = Instructor.objects.create(user=self.instructor_user)

        # Create TA user
        self.ta_user = User.objects.create_user(
            username="ta",
            email="ta@example.com",
            password="tapass",
            first_name="Test",
            last_name="TA",
            is_ta=True
        )
        self.ta = TA.objects.create(user=self.ta_user)

        # Create a course
        self.course = Course.objects.create(
            course_id="CS101",
            name="Test Course",
            semester="Fall 2024",
            description="Test Description",
            num_of_sections=1,
            modality="Online"
        )

        # Assign instructor to course
        self.course.instructors.add(self.instructor)

        # Create a section
        self.section = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="MWF 10:00-11:00"
        )

    def test_assign_ta_to_section(self):
        """Test successful TA assignment to section"""
        # Login as instructor
        self.client.login(username="instructor", password="instructorpass")

        # Prepare assignment data
        data = {
            'ta_id': self.ta.id,
            'section_id': self.section.id
        }

        # Make assignment request
        response = self.client.post(reverse('assign_ta_to_section'), data)

        # Check if TA was assigned
        self.assertTrue(
            self.section.assigned_tas.filter(id=self.ta.id).exists(),
            "TA should be assigned to section"
        )

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("has been assigned to Section" in str(m) for m in messages)
        )

    def test_unassign_ta_from_section(self):
        """Test successful TA unassignment from section"""
        # Login as instructor
        self.client.login(username="instructor", password="instructorpass")

        # First assign the TA
        self.section.assigned_tas.add(self.ta)

        # Make unassignment request
        response = self.client.get(
            reverse('unassign_ta', args=[self.section.id, self.ta.id])
        )

        # Check if TA was unassigned
        self.assertFalse(
            self.section.assigned_tas.filter(id=self.ta.id).exists(),
            "TA should be unassigned from section"
        )

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("has been unassigned from Section" in str(m) for m in messages)
        )

    def test_unauthorized_ta_assignment(self):
        """Test that non-instructors cannot assign TAs"""
        # Login as TA
        self.client.login(username="ta", password="tapass")

        data = {
            'ta_id': self.ta.id,
            'section_id': self.section.id
        }

        # Attempt assignment
        response = self.client.post(reverse('assign_ta_to_section'))

        # Verify redirect response code
        self.assertEqual(response.status_code, 302)

        # Verify redirect path
        self.assertEqual(response.url, '/home/')

        # Verify TA was not assigned
        self.assertFalse(
            self.section.assigned_tas.filter(id=self.ta.id).exists(),
            "TA should not be assigned to section"
        )

    def test_view_assignment_page(self):
        """Test viewing the TA assignment page"""
        # Login as instructor
        self.client.login(username="instructor", password="instructorpass")

        response = self.client.get(reverse('assign_ta_to_section'))

        # Check response and context
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assign_ta_to_section.html')
        self.assertIn('tas', response.context)
        self.assertIn('sections', response.context)