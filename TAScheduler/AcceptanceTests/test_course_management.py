from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from TAScheduler.models import Course, User, Administrator


class CourseManagementTestCase(TestCase):
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

        # Log in the admin user
        self.client.login(username="admin", password="adminpassword")

        # Create some test courses
        self.course1 = Course.objects.create(
            course_id="CS101",
            name="Intro to Programming",
            semester="Fall 2024",
            description="Basic programming concepts",
            num_of_sections=2,
            modality="Online"
        )

        self.course2 = Course.objects.create(
            course_id="CS102",
            name="Data Structures",
            semester="Spring 2024",
            description="Advanced programming concepts",
            num_of_sections=3,
            modality="In-person"
        )

    def test_view_course_list(self):
        """Test viewing the list of courses"""
        response = self.client.get(reverse('manage_course'))

        # Check that response is successful
        self.assertEqual(response.status_code, 200)

        # Check that courses are in context
        self.assertIn('courses', response.context)
        courses = response.context['courses']
        self.assertEqual(len(courses), 2)

        # Verify course details are present
        self.assertTrue(any(c.course_id == "CS101" for c in courses))
        self.assertTrue(any(c.course_id == "CS102" for c in courses))

    def test_create_course_success(self):
        """Test successful course creation"""
        course_data = {
            'course_id': 'CS103',
            'name': 'Software Engineering',
            'semester': 'Fall 2024',
            'description': 'Software development principles',
            'num_of_sections': 2,
            'modality': 'Online'
        }

        response = self.client.post(reverse('create_course'), course_data)

        # Check that course was created
        self.assertTrue(Course.objects.filter(course_id='CS103').exists())

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Course 'Software Engineering' created successfully" in str(m) for m in messages))

    def test_create_duplicate_course(self):
        """Test creating a course with existing course ID"""
        course_data = {
            'course_id': 'CS101',  # Already exists
            'name': 'New Course',
            'semester': 'Fall 2024',
            'description': 'Test description',
            'num_of_sections': 1,
            'modality': 'Online'
        }

        response = self.client.post(reverse('create_course'), course_data)

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("A course with this ID already exists" in str(m) for m in messages))

    def test_edit_course(self):
        """Test editing an existing course"""
        edit_data = {
            'name': 'Updated Course Name',
            'semester': 'Spring 2025',
            'description': 'Updated description',
            'num_of_sections': 4,
            'modality': 'In-person'
        }

        response = self.client.post(
            reverse('edit_course', args=[self.course1.course_id]),
            edit_data
        )

        # Refresh course from database
        updated_course = Course.objects.get(course_id=self.course1.course_id)

        # Check that course was updated
        self.assertEqual(updated_course.name, 'Updated Course Name')
        self.assertEqual(updated_course.semester, 'Spring 2025')

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Course 'Updated Course Name' updated successfully" in str(m) for m in messages))

    def test_search_course(self):
        """Test searching for courses"""
        # Search by name
        response = self.client.get(reverse('manage_course'), {'search': 'Data'})
        self.assertEqual(len(response.context['courses']), 1)
        self.assertEqual(response.context['courses'][0].course_id, 'CS102')

        # Search by semester
        response = self.client.get(reverse('manage_course'), {'semester': 'Spring 2024'})
        self.assertEqual(len(response.context['courses']), 1)
        self.assertEqual(response.context['courses'][0].course_id, 'CS102')

    def test_filter_by_modality(self):
        """Test filtering courses by modality"""
        # Filter Online courses
        response = self.client.get(reverse('manage_course'), {'modality': 'Online'})
        self.assertEqual(len(response.context['courses']), 1)
        self.assertEqual(response.context['courses'][0].course_id, 'CS101')

        # Filter In-person courses
        response = self.client.get(reverse('manage_course'), {'modality': 'In-person'})
        self.assertEqual(len(response.context['courses']), 1)
        self.assertEqual(response.context['courses'][0].course_id, 'CS102')