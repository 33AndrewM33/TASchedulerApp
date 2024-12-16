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

    def test_manage_section_view_filter_by_modality(self):
        """Test if filtering by modality works."""
        self.course.modality = "Online"
        self.course.save()
        response = self.client.get(reverse('manage_section'), {'modality': 'Online'})
        self.assertContains(response, self.course.name)

    def test_manage_section_view_filter_by_semester(self):
        """Test if filtering by semester works."""
        self.course.semester = "Spring 2025"
        self.course.save()
        response = self.client.get(reverse('manage_section'), {'semester': 'Spring 2025'})
        self.assertContains(response, self.course.name)
        self.assertNotContains(response, "Fall 2024")

    def test_manage_section_view_invalid_filter(self):
        """Test if the view handles invalid filters gracefully."""
        response = self.client.get(reverse('manage_section'), {'type': 'InvalidType'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.section_lab.location)
        self.assertContains(response, self.section_lecture.location)

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
