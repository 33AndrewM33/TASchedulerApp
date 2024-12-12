from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from TAScheduler.models import Course, Section, Lab, Lecture, TA

User = get_user_model()

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from TAScheduler.models import Course, Section, Lab, Lecture, TA

User = get_user_model()


class ManageSectionViewTests(TestCase):
    def setUp(self):
        # Create a test user and log them in
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            is_admin=True,
        )
        self.client.login(username="testuser", password="password123")

        # Create test data
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A basic course in computer science.",
            num_of_sections=2,
            modality="In-person"
        )
        self.section_lab = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="Mon-Wed 10:00 AM - 11:30 AM"
        )
        self.section_lecture = Section.objects.create(
            section_id=2,
            course=self.course,
            location="Room 102",
            meeting_time="Tue-Thu 1:00 PM - 2:30 PM"
        )
        self.lab = Lab.objects.create(section=self.section_lab)
        self.lecture = Lecture.objects.create(section=self.section_lecture)

    def test_manage_section_view_all_sections(self):
        """Test if the view returns all sections when no filter is applied."""
        response = self.client.get(reverse('manage_section'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.section_lab.location)
        self.assertContains(response, self.section_lecture.location)

    def test_manage_section_view_labs(self):
        """Test if the view returns only lab sections when 'Lab' filter is applied."""
        response = self.client.get(reverse('manage_section'), {'type': 'Lab'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.section_lab.location)
        self.assertNotContains(response, self.section_lecture.location)

    def test_manage_section_view_lectures(self):
        """Test if the view returns only lecture sections when 'Lecture' filter is applied."""
        response = self.client.get(reverse('manage_section'), {'type': 'Lecture'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.section_lecture.location)
        self.assertNotContains(response, self.section_lab.location)

    def test_manage_section_view_unauthenticated_access(self):
        """Test if unauthenticated users are redirected to the login page."""
        self.client.logout()
        response = self.client.get(reverse('manage_section'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertIn('/login/', response.url)

    def test_manage_section_view_post_create_section(self):
        """Test if the view allows the creation of a new section."""
        response = self.client.post(reverse('manage_section'), {
            'section_id': 3,
            'course': self.course.id,
            'location': 'Room 103',
            'meeting_time': 'Mon-Wed 12:00 PM - 1:30 PM'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        new_section = Section.objects.get(section_id=3)
        self.assertEqual(new_section.location, 'Room 103')

    def test_manage_section_view_post_create_section_without_location(self):
        """Test if the view handles form submission without location."""
        response = self.client.post(reverse('manage_section'), {
            'section_id': 3,
            'course': self.course.id,
            'meeting_time': 'Mon-Wed 12:00 PM - 1:30 PM'
        })
        self.assertFormError(response, 'form', 'location', 'This field is required.')

    def test_manage_section_view_post_create_section_without_time(self):
        """Test if the view handles form submission without meeting time."""
        response = self.client.post(reverse('manage_section'), {
            'section_id': 3,
            'course': self.course.id,
            'location': 'Room 103',
        })
        self.assertFormError(response, 'form', 'meeting_time', 'This field is required.')

    def test_manage_section_view_get_edit_section(self):
        """Test if the view allows editing an existing section."""
        response = self.client.get(reverse('manage_section_edit', args=[self.section_lab.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.section_lab.location)

    def test_manage_section_view_post_edit_section(self):
        """Test if the view allows saving edited section data."""
        response = self.client.post(reverse('manage_section_edit', args=[self.section_lab.id]), {
            'section_id': self.section_lab.section_id,
            'course': self.course.id,
            'location': 'Room 104',
            'meeting_time': 'Mon-Wed 9:00 AM - 10:30 AM'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after editing
        self.section_lab.refresh_from_db()
        self.assertEqual(self.section_lab.location, 'Room 104')

    def test_manage_section_view_post_delete_section(self):
        """Test if the view allows deleting a section."""
        response = self.client.post(reverse('manage_section_delete', args=[self.section_lab.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        with self.assertRaises(Section.DoesNotExist):
            Section.objects.get(id=self.section_lab.id)

    def test_manage_section_view_delete_section_nonexistent(self):
        """Test if the view properly handles trying to delete a nonexistent section."""
        response = self.client.post(reverse('manage_section_delete', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_manage_section_view_get_edit_section_nonexistent(self):
        """Test if the view properly handles trying to edit a nonexistent section."""
        response = self.client.get(reverse('manage_section_edit', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_manage_section_view_invalid_filter(self):
        """Test if the view handles invalid filters gracefully."""
        response = self.client.get(reverse('manage_section'), {'type': 'InvalidType'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.section_lab.location)
        self.assertContains(response, self.section_lecture.location)

    def test_manage_section_view_all_sections_after_creation(self):
        """Test if a newly created section shows up in the all sections view."""
        new_section = Section.objects.create(
            section_id=3,
            course=self.course,
            location="Room 103",
            meeting_time="Mon-Wed 12:00 PM - 1:30 PM"
        )
        response = self.client.get(reverse('manage_section'))
        self.assertContains(response, new_section.location)

    def test_manage_section_view_filter_by_semester(self):
        """Test if filtering by semester works."""
        self.course.semester = "Spring 2025"
        self.course.save()
        response = self.client.get(reverse('manage_section'), {'semester': 'Spring 2025'})
        self.assertContains(response, self.course.name)
        self.assertNotContains(response, "Fall 2024")

    def test_manage_section_view_filter_by_modality(self):
        """Test if filtering by modality works."""
        self.course.modality = "Online"
        self.course.save()
        response = self.client.get(reverse('manage_section'), {'modality': 'Online'})
        self.assertContains(response, self.course.name)

    def test_manage_section_view_edit_section_no_permission(self):
        """Test if a non-admin user is restricted from editing sections."""
        non_admin_user = User.objects.create_user(
            username="nonadmin",
            email="nonadmin@example.com",
            password="password123",
            is_admin=False,
        )
        self.client.login(username="nonadmin", password="password123")
        response = self.client.get(reverse('manage_section_edit', args=[self.section_lab.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_manage_section_view_filter_by_instructor(self):
        """Test if filtering by instructor works."""
        instructor = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="password123"
        )
        self.course.instructor = instructor
        self.course.save()
        response = self.client.get(reverse('manage_section'), {'instructor': instructor.id})
        self.assertContains(response, self.course.name)

    def test_manage_section_view_create_section_duplicate_id(self):
        """Test if creating a section with a duplicate ID raises an error."""
        response = self.client.post(reverse('manage_section'), {
            'section_id': 1,
            'course': self.course.id,
            'location': 'Room 103',
            'meeting_time': 'Mon-Wed 12:00 PM - 1:30 PM'
        })
        self.assertFormError(response, 'form', 'section_id', 'Section with this Section id already exists.')

    def test_manage_section_view_filter_by_time(self):
        """Test if filtering by time works."""
        response = self.client.get(reverse('manage_section'), {'meeting_time': 'Mon-Wed 10:00 AM - 11:30 AM'})
        self.assertContains(response, self.section_lab.location)
        self.assertNotContains(response, self.section_lecture.location)
