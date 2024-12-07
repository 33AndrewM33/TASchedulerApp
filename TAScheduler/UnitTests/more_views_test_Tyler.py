from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from TAScheduler.models import Course, Instructor, Section, Lab, Lecture, TA
from django.contrib.messages import get_messages
from django.contrib.auth.hashers import check_password

User = get_user_model()


class AccountManagementViewTests(TestCase):
    def setUp(self):
        # Create an admin user for testing
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            is_admin=True,
        )
        self.client.login(username="admin", password="password123")

    def test_render_account_management_page(self):
        """Test rendering the account management page."""
        response = self.client.get(reverse('account_management'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account_management.html')
        self.assertContains(response, "Users")

    def test_create_user(self):
        """Test creating a new user."""
        data = {
            "action": "create",
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "role": "ta",
        }
        response = self.client.post(reverse('account_management'), data)
        self.assertEqual(response.status_code, 200)

        # Check if the user was created
        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(check_password("securepassword", user.password))
        self.assertTrue(user.is_ta)
        self.assertTrue(hasattr(user, "ta_profile"))

    def test_delete_user(self):
        """Test deleting an existing user."""
        user_to_delete = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            is_ta=True,
        )
        data = {
            "action": "delete",
            "user_id": user_to_delete.id,
        }
        response = self.client.post(reverse('account_management'), data)
        self.assertEqual(response.status_code, 200)

        # Check if the user was deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_to_delete.id)

    def test_edit_user(self):
        """Test initiating an edit action for a user."""
        user_to_edit = User.objects.create_user(
            username="edituser",
            email="edituser@example.com",
            password="password123",
            is_ta=True,
        )
        data = {
            "action": "edit",
            "user_id": user_to_edit.id,
        }
        response = self.client.post(reverse('account_management'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "edituser")

    def test_update_user(self):
        """Test updating an existing user."""
        user_to_update = User.objects.create_user(
            username="updateuser",
            email="updateuser@example.com",
            password="password123",
            is_ta=True,
        )
        data = {
            "action": "update",
            "editing_user_id": user_to_update.id,
            "username": "updateduser",
            "email": "updateduser@example.com",
            "password": "newpassword",
            "role": "instructor",
        }
        response = self.client.post(reverse('account_management'), data)
        self.assertEqual(response.status_code, 200)

        # Check if the user details were updated
        user_to_update.refresh_from_db()
        self.assertEqual(user_to_update.username, "updateduser")
        self.assertEqual(user_to_update.email, "updateduser@example.com")
        self.assertTrue(check_password("newpassword", user_to_update.password))
        self.assertTrue(user_to_update.is_instructor)
        self.assertTrue(hasattr(user_to_update, "instructor_profile"))

    def test_update_user_without_password(self):
        """Test updating a user without changing the password."""
        user_to_update = User.objects.create_user(
            username="updateuser",
            email="updateuser@example.com",
            password="password123",
            is_ta=True,
        )
        data = {
            "action": "update",
            "editing_user_id": user_to_update.id,
            "username": "updateduser",
            "email": "updateduser@example.com",
            "password": "",
            "role": "administrator",
        }
        response = self.client.post(reverse('account_management'), data)
        self.assertEqual(response.status_code, 200)

        # Check if the user details were updated without changing the password
        user_to_update.refresh_from_db()
        self.assertEqual(user_to_update.username, "updateduser")
        self.assertEqual(user_to_update.email, "updateduser@example.com")
        self.assertTrue(check_password("password123", user_to_update.password))
        self.assertTrue(user_to_update.is_admin)
        self.assertTrue(hasattr(user_to_update, "administrator_profile"))


class CreateSectionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an admin user
        cls.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpassword',
            email='admin@example.com',
            is_admin=True
        )
        # Create a non-admin TA user
        cls.ta_user = User.objects.create_user(
            username='tauser',
            password='tapassword',
            email='tauser@example.com',
            is_ta=True
        )
        # Create test courses
        cls.course_1 = Course.objects.create(
            course_id="CS101",
            name="Intro to CS",
            semester="Fall 2024",
            num_of_sections=2,
            modality="Online"
        )

    def setUp(self):
        # Log in as the admin user by default
        self.client.login(username='adminuser', password='adminpassword')

    def test_create_section_lab_creation(self):
        """Test the creation of a Lab section by an admin user"""
        data = {
            'course_id': self.course_1.course_id,
            'section_id': 1,
            'section_type': 'Lab',
            'location': 'Room 101',
            'meeting_time': '10:00 AM'
        }
        response = self.client.post(reverse('create_section'), data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check if the Lab section is created
        section = Section.objects.get(section_id=1, course=self.course_1)
        self.assertEqual(section.location, 'Room 101')
        self.assertEqual(section.meeting_time, '10:00 AM')
        lab = Lab.objects.get(section=section)
        self.assertIsNotNone(lab)








class EditSectionViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create unique email addresses for each user to avoid IntegrityError
        cls.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_admin=True
        )
        cls.ta_user = User.objects.create_user(
            username='tauser',
            email='tauser@example.com',  # Ensure this email is unique
            password='tapassword',
            is_ta=True
        )
        cls.instructor_user = User.objects.create_user(
            username='instructoruser',
            email='instructor@example.com',  # Ensure this email is unique
            password='instructorpassword',
            is_instructor=True
        )

        cls.ta = TA.objects.create(user=cls.ta_user)
        cls.instructor = Instructor.objects.create(user=cls.instructor_user)

        # Create a course and section
        cls.course = Course.objects.create(
            course_id="CS101",
            name="Intro to CS",
            semester="Fall 2024",
            num_of_sections=2,
            modality="Online"
        )
        cls.section = Section.objects.create(
            section_id=1,
            course=cls.course,
            location="Room 101",
            meeting_time="10:00 AM"
        )
        cls.section_lab = Section.objects.create(
            section_id=1,
            course=cls.course,
            location="Room 101",
            meeting_time="Mon-Wed 10:00 AM"
        )
        cls.lab = Lab.objects.create(section=cls.section)
        cls.lecture = Lecture.objects.create(section=cls.section)

    def setUp(self):
        # Log in as the admin user
        self.client.login(username='adminuser', password='adminpassword')

    def test_edit_section_update_location_and_time(self):
        """Test updating section location and meeting time."""
        response = self.client.post(reverse('edit_section', args=[self.section.id]), {
            'location': 'Room 202',
            'meeting_time': '2:00 PM'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.section.refresh_from_db()
        self.assertEqual(self.section.location, 'Room 202')
        self.assertEqual(self.section.meeting_time, '2:00 PM')

    def test_edit_section_assign_ta(self):
        """Test assigning a TA to the section."""
        response = self.client.post(reverse('edit_section', args=[self.section.id]), {
            'location': self.section.location,
            'meeting_time': self.section.meeting_time,
            'assigned_ta': self.ta.user.id
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.lab.refresh_from_db()
        self.assertEqual(self.lab.ta, self.ta)

    def test_edit_section_assign_instructor(self):
        """Test assigning an instructor to the section."""
        response = self.client.post(reverse('edit_section', args=[self.section.id]), {
            'location': self.section.location,
            'meeting_time': self.section.meeting_time,
            'assigned_instructor': self.instructor.user.id
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.lecture.refresh_from_db()
        self.assertEqual(self.lecture.instructor, self.instructor)

    def test_edit_section_invalid_ta(self):
        """Test assigning a non-existent TA raises a 404 error."""
        response = self.client.post(reverse('edit_section', args=[self.section.id]), {
            'location': self.section.location,
            'meeting_time': self.section.meeting_time,
            'assigned_ta': 999  # Non-existent TA ID
        })
        self.assertEqual(response.status_code, 404)

    def test_edit_section_invalid_instructor(self):
        """Test assigning a non-existent instructor raises a 404 error."""
        response = self.client.post(reverse('edit_section', args=[self.section.id]), {
            'location': self.section.location,
            'meeting_time': self.section.meeting_time,
            'assigned_instructor': 999  # Non-existent Instructor ID
        })
        self.assertEqual(response.status_code, 404)



    def test_no_changes_submitted(self):
        """Test that submitting the form without changes does not alter the section."""
        self.client.login(username='adminuser', password='adminpassword')
        data = {
            "location": self.section.location,
            "meeting_time": self.section.meeting_time,
        }
        response = self.client.post(reverse('edit_section', args=[self.section.id]), data)
        self.assertEqual(response.status_code, 302)
        section = Section.objects.get(id=self.section.id)
        self.assertEqual(section.location, self.section.location)
        self.assertEqual(section.meeting_time, self.section.meeting_time)
