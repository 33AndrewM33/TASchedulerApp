from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from TAScheduler.models import User, Course, Instructor, Administrator, Notification


class InstructorAssignmentTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
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

        # Create test course
        self.course = Course.objects.create(
            course_id="CS101",
            name="Test Course",
            semester="Fall 2024",
            description="Test Description",
            num_of_sections=2,
            modality="Online"
        )

        # Log in as admin
        self.client.login(username="admin", password="adminpassword")

    def test_assign_instructor_to_course(self):
        """Test assigning an instructor to a course from account management"""
        data = {
            'course_id': self.course.id
        }

        response = self.client.post(
            reverse('assign_instructor_to_course', args=[self.instructor_user.id]),
            data
        )

        # Check redirect
        self.assertRedirects(response, reverse('account_management'))

        # Verify instructor was assigned
        self.assertTrue(
            self.course.instructors.filter(id=self.instructor.id).exists(),
            "Instructor should be assigned to course"
        )

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(f"Instructor {self.instructor_user.first_name}" in str(m) for m in messages)
        )

    def test_assign_multiple_instructors(self):
        """Test assigning multiple instructors to a course"""
        # Create another instructor
        instructor2_user = User.objects.create_user(
            username="instructor2",
            email="instructor2@example.com",
            password="instructor2pass",
            first_name="Test2",
            last_name="Instructor2",
            is_instructor=True
        )
        instructor2 = Instructor.objects.create(user=instructor2_user)

        data = {
            'instructors': [self.instructor.id, instructor2.id]
        }

        response = self.client.post(
            reverse('assign_instructors_to_course', args=[self.course.course_id]),
            data
        )

        # Verify both instructors were assigned
        self.assertTrue(
            self.course.instructors.filter(id=self.instructor.id).exists(),
            "First instructor should be assigned"
        )
        self.assertTrue(
            self.course.instructors.filter(id=instructor2.id).exists(),
            "Second instructor should be assigned"
        )

    def test_instructor_notification(self):
        """Test that instructors receive notifications when assigned"""
        data = {
            'instructors': [self.instructor.id]
        }

        self.client.post(
            reverse('assign_instructors_to_course', args=[self.course.course_id]),
            data
        )

        # Check for notification
        notification = Notification.objects.filter(
            recipient=self.instructor_user,
            subject="Course Assignment Notification"
        ).first()

        self.assertIsNotNone(notification, "Instructor should receive notification")
        self.assertIn(self.course.name, notification.message)

    def test_invalid_course_id(self):
        """Test assignment with invalid course ID"""
        data = {
            'course_id': 9999  # Non-existent course ID
        }

        response = self.client.post(
            reverse('assign_instructor_to_course', args=[self.instructor_user.id]),
            data
        )

        # Check that assignment failed
        self.assertEqual(
            self.course.instructors.count(), 0,
            "No instructor should be assigned with invalid course ID"
        )

    def test_invalid_instructor(self):
        """Test assignment with invalid instructor"""
        # Create non-instructor user
        regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="regularpass",
            first_name="Regular",
            last_name="User"
        )

        # Attempt to assign non-instructor
        response = self.client.post(
            reverse('assign_instructor_to_course', args=[regular_user.id]),
            {'course_id': self.course.id}
        )

        # Verify response is 404
        self.assertEqual(response.status_code, 404)