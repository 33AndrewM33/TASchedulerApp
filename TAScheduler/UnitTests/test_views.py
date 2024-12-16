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

    # Break down the test for rendering the account management page
    def test_render_account_management_page_status_code(self):
        response = self.client.get(reverse('account_management'))
        self.assertEqual(response.status_code, 200)

    def test_render_account_management_page_template_used(self):
        response = self.client.get(reverse('account_management'))
        self.assertTemplateUsed(response, 'account_management.html')

    def test_render_account_management_page_contains_users(self):
        response = self.client.get(reverse('account_management'))
        self.assertContains(response, "Users")

    # Break down the test for deleting an existing user
    def test_delete_user_status_code(self):
        user_to_delete = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            is_ta=True,
        )
        data = {"action": "delete", "user_id": user_to_delete.id}
        response = self.client.post(reverse('account_management'), data)
        self.assertEqual(response.status_code, 200)

    def test_delete_user_removed(self):
        user_to_delete = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            is_ta=True,
        )
        data = {"action": "delete", "user_id": user_to_delete.id}
        self.client.post(reverse('account_management'), data)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_to_delete.id)

    # Break down the test for editing a user
    def test_edit_user_status_code(self):
        user_to_edit = User.objects.create_user(
            username="edituser",
            email="edituser@example.com",
            password="password123",
            is_ta=True,
        )
        data = {"action": "edit", "user_id": user_to_edit.id}
        response = self.client.post(reverse('account_management'), data)
        self.assertEqual(response.status_code, 200)

    def test_edit_user_contains_username(self):
        user_to_edit = User.objects.create_user(
            username="edituser",
            email="edituser@example.com",
            password="password123",
            is_ta=True,
        )
        data = {"action": "edit", "user_id": user_to_edit.id}
        response = self.client.post(reverse('account_management'), data)
        self.assertContains(response, "edituser")

    # Break down the test for updating a user
    def test_update_user_status_code(self):
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

    def test_create_section_duplicate_section_id(self):
        """Test that duplicate section IDs cannot be created for the same course"""
        Section.objects.create(
            section_id=1, 
            course=self.course_1, 
            location="Room 101", 
            meeting_time="10:00 AM"
        )

        data = {
            'course_id': self.course_1.course_id,
            'section_id': 1,  # Duplicate ID
            'section_type': 'Lab',
            'location': 'Room 104',
            'meeting_time': '4:00 PM'
        }
        response = self.client.post(reverse('create_section'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Section with this ID already exists.")

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

    def test_get_edit_section_form(self):
        """Test rendering the edit section form."""
        response = self.client.get(reverse('edit_section', args=[self.section.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_section.html')
        self.assertContains(response, 'Room 101')  # Ensure current location is in the form
        self.assertContains(response, '10:00 AM')  # Ensure current meeting time is in the form

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


class ManageSectionViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test admin user
        cls.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="password123",
            is_admin=True,
        )

        # Create test courses
        cls.course_1 = Course.objects.create(
            course_id="CS101",
            name="Intro to CS",
            semester="Fall 2024",
            num_of_sections=2,
            modality="Online",
        )
        cls.course_2 = Course.objects.create(
            course_id="CS102",
            name="Data Structures",
            semester="Fall 2024",
            num_of_sections=2,
            modality="In-person",
        )

        # Create sections for the first course
        cls.section_lab = Section.objects.create(
            section_id=1,
            course=cls.course_1,
            location="Room 101",
            meeting_time="Mon-Wed 10:00 AM - 11:30 AM",
        )
        cls.section_lecture = Section.objects.create(
            section_id=2,
            course=cls.course_1,
            location="Room 102",
            meeting_time="Tue-Thu 1:00 PM - 2:30 PM",
        )

        # Create associated Lab and Lecture objects
        cls.lab = Lab.objects.create(section=cls.section_lab)
        cls.lecture = Lecture.objects.create(section=cls.section_lecture)

    def setUp(self):
        # Log in the admin user
        self.client.login(username="adminuser", password="password123")

    def test_manage_section_view_all_sections(self):
        """Test if the view returns all sections without any filter."""
        response = self.client.get(reverse('manage_section'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.section_lab.location)
        self.assertContains(response, self.section_lecture.location)

    def test_manage_section_view_labs_only(self):
        """Test if the view returns only lab sections when 'Lab' filter is applied."""
        response = self.client.get(reverse('manage_section'), {'type': 'Lab'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.section_lab.location)
        self.assertNotContains(response, self.section_lecture.location)

    def test_manage_section_view_lectures_only(self):
        """Test if the view returns only lecture sections when 'Lecture' filter is applied."""
        response = self.client.get(reverse('manage_section'), {'type': 'Lecture'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.section_lecture.location)
        self.assertNotContains(response, self.section_lab.location)

    def test_manage_section_no_sections(self):
        """Test if the view handles the case where no sections exist."""
        Section.objects.all().delete()  # Remove all sections
        response = self.client.get(reverse('manage_section'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No sections found.")

    def test_create_section_duplicate_section_id(self):
        """Test that a section with a duplicate section ID cannot be created."""
        data = {
            'course_id': self.course_1.course_id,
            'section_id': 1,  # Duplicate ID
            'section_type': 'Lab',
            'location': 'Room 104',
            'meeting_time': '10:00 AM',
        }
        response = self.client.post(reverse('create_section'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Section with this ID already exists.")


class DeleteSectionViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user with admin privileges
        cls.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password",
            is_admin=True
        )
        
        # Create a course
        cls.course = Course.objects.create(
            course_id="CS101",
            name="Intro to Computer Science",
            num_of_sections=10
        )
            # Create TA user
        cls.ta_user = User.objects.create_user(
        username="tauser",
        email="ta@example.com",
        password="tapass",
        is_ta=True,  # Assuming your User model has an is_ta field
    )
        cls.instructor_user = User.objects.create_user(
        username="instructoruser",
        email="instructor@example.com",
        password="instructorpass",
        is_instructor=True,  # Assuming your User model has an is_instructor field
    )
        # Create a section
        cls.section = Section.objects.create(
            section_id=1,
            course=cls.course,
            location="Room 101",
            meeting_time="Mon-Wed 10:00 AM"
        )

    def setUp(self):
        # Log in the admin user for each test
        self.client.login(username="admin", password="password")

    def test_delete_section_success(self):
        """Test that a section is successfully deleted."""
        response = self.client.post(reverse('delete_section', args=[self.section.id]))
        self.assertRedirects(response, reverse('manage_section'))
        self.assertFalse(Section.objects.filter(id=self.section.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Section 1 deleted successfully." in str(msg) for msg in messages))

    def test_delete_section_successful(self):
            """Test that an admin can delete a section successfully."""
            self.client.login(username='admin_user', password='adminpassword')
            response = self.client.post(reverse('delete_section', args=[self.section.id]))
            self.assertRedirects(response, reverse('manage_section'))
            self.assertFalse(Section.objects.filter(id=self.section.id).exists())  # Ensure the section is deleted

    def test_delete_section_not_logged_in(self):
        # Log out the user to simulate unauthenticated access
        self.client.logout()

        # Attempt to access the delete_section view
        response = self.client.get(reverse('delete_section', args=[self.section.id]))

        # Expected URL for login redirection
        expected_url = f"/login/?next={reverse('delete_section', args=[self.section.id])}"

        # Assert redirection to the login page
        self.assertRedirects(response, expected_url)

    def test_section_removed_from_database(self):
        self.client.login(username=self.admin_user.username, password="adminpass")
        section_id = self.section.id
        response = self.client.post(reverse('delete_section', args=[section_id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(Section.objects.filter(id=section_id).exists())  # Verify deletion

    def test_delete_section_with_dependencies(self):
        # Create a TA instance
        ta = TA.objects.create(user=self.ta_user)

        # Create a Lab linked to the section
        lab = Lab.objects.create(section=self.section, ta=ta)

        # Delete the section
        response = self.client.post(reverse('delete_section', args=[self.section.id]), follow=True)
        self.assertRedirects(response, reverse('manage_section'))

        # Check if the success message appears
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(f"Section {self.section.section_id} deleted successfully." in str(msg) for msg in messages))



    def test_success_message_on_delete(self):
        self.client.login(username=self.admin_user.username, password="adminpass")
        response = self.client.post(reverse('delete_section', args=[self.section.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Section {self.section.section_id} deleted successfully.")