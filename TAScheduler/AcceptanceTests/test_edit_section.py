from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from TAScheduler.models import Section, Course, User, Administrator, TA, Instructor


class SectionEditingTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create client
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        Administrator.objects.create(user=self.admin_user)

        # Create a TA user
        self.ta_user = User.objects.create_user(
            username="ta",
            email="ta@example.com",
            password="tapassword",
            first_name="Test",
            last_name="TA",
            is_ta=True
        )
        self.ta = TA.objects.create(user=self.ta_user)

        # Create an instructor user
        self.instructor_user = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="instructorpassword",
            first_name="Test",
            last_name="Instructor",
            is_instructor=True
        )
        self.instructor = Instructor.objects.create(user=self.instructor_user)

        # Create a test course
        self.course = Course.objects.create(
            course_id="CS101",
            name="Test Course",
            semester="Fall 2024",
            description="Test Description",
            num_of_sections=2,
            modality="Online"
        )

        # Create a test section
        self.section = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="MWF 10:00-11:00"
        )

        # Log in the admin user
        self.client.login(username="admin", password="adminpassword")

    def test_view_section_details(self):
        """Test viewing section details"""
        response = self.client.get(reverse('edit_section', args=[self.section.id]))

        # Check response is successful
        self.assertEqual(response.status_code, 200)

        # Check section details are in context
        self.assertIn('section', response.context)
        section = response.context['section']
        self.assertEqual(section.section_id, 1)
        self.assertEqual(section.location, "Room 101")

        # Check that TAs and instructors are in context
        self.assertIn('tas', response.context)
        self.assertIn('instructors', response.context)

    def test_edit_section_basic_info(self):
        """Test editing basic section information"""
        edit_data = {
            'location': 'Room 202',
            'meeting_time': 'TTh 13:00-14:30'
        }

        response = self.client.post(
            reverse('edit_section', args=[self.section.id]),
            edit_data,
            follow=True
        )

        # Refresh section from database
        updated_section = Section.objects.get(id=self.section.id)

        # Check that section was updated
        self.assertEqual(updated_section.location, 'Room 202')
        self.assertEqual(updated_section.meeting_time, 'TTh 13:00-14:30')

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(f"Section {self.section.section_id} updated successfully" in str(m) for m in messages))

    def test_assign_ta_to_section(self):
        """Test assigning a TA to a section"""
        edit_data = {
            'location': 'Room 101',
            'meeting_time': 'MWF 10:00-11:00',
            'assigned_ta': str(self.ta_user.id)
        }

        response = self.client.post(
            reverse('edit_section', args=[self.section.id]),
            edit_data,
            follow=True
        )

        # Refresh section from database
        updated_section = Section.objects.get(id=self.section.id)

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(f"Section {self.section.section_id} updated successfully" in str(m) for m in messages))

    def test_assign_instructor_to_section(self):
        """Test assigning an instructor to a section"""
        edit_data = {
            'location': 'Room 101',
            'meeting_time': 'MWF 10:00-11:00',
            'assigned_instructor': str(self.instructor_user.id)
        }

        response = self.client.post(
            reverse('edit_section', args=[self.section.id]),
            edit_data,
            follow=True
        )

        # Refresh section from database
        updated_section = Section.objects.get(id=self.section.id)

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(f"Section {self.section.section_id} updated successfully" in str(m) for m in messages))

    def test_unauthorized_access(self):
        """Test unauthorized access to section editing"""
        # Logout admin
        self.client.logout()

        response = self.client.get(reverse('edit_section', args=[self.section.id]))

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_invalid_section_id(self):
        """Test editing with invalid section ID"""
        invalid_id = 9999
        response = self.client.get(reverse('edit_section', args=[invalid_id]))

        # Should return 404
        self.assertEqual(response.status_code, 404)