from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from TAScheduler.models import Course, Instructor, Section, Lab, Lecture, TA
from django.contrib.messages import get_messages

User = get_user_model()

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

    def test_create_section_invalid_user_permissions(self):
        """Test that non-admin users cannot create sections"""
        # Log in as a TA user
        self.client.logout()
        self.client.login(username='tauser', password='tapassword')

        data = {
            'course_id': self.course_1.course_id,
            'section_id': 2,
            'section_type': 'Lab',
            'location': 'Room 102',
            'meeting_time': '11:00 AM'
        }
        response = self.client.post(reverse('create_section'), data)
        self.assertEqual(response.status_code, 403)


    def test_create_section_with_empty_field(self):
        """Test that the form rejects missing required fields"""
        data = {
            'course_id': self.course_1.course_id,
            'section_id': '',  # Empty section_id
            'section_type': 'Lab',
            'location': 'Room 103',
            'meeting_time': '12:00 PM'
        }
        response = self.client.post(reverse('create_section'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All fields are required.")



    def test_create_section_exceed_maximum_sections(self):
        """Test that creating sections beyond the course limit is disallowed"""
        # Create maximum allowed sections
        Section.objects.create(section_id=1, course=self.course_1, location="Room 201", meeting_time="1:00 PM")
        Section.objects.create(section_id=2, course=self.course_1, location="Room 202", meeting_time="2:00 PM")

        data = {
            'course_id': self.course_1.course_id,
            'section_id': 3,
            'section_type': 'Lab',
            'location': 'Room 203',
            'meeting_time': '3:00 PM'
        }
        response = self.client.post(reverse('create_section'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The course has reached its maximum number of sections.")


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


        
    def test_create_section_missing_course_id(self):
        """Test that a missing course ID is rejected"""
        data = {
            'course_id': '',  # Missing course_id
            'section_id': 4,
            'section_type': 'Lab',
            'location': 'Room 106',
            'meeting_time': '4:00 PM'
        }
        response = self.client.post(reverse('create_section'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid course ID. Please select a valid course.")
        
    def test_create_section_valid_lecture(self):
        """Test the creation of a valid Lecture section."""
        data = {
            'course_id': self.course_1.course_id,
            'section_id': 5,
            'section_type': 'Lecture',
            'location': 'Room 107',
            'meeting_time': '5:00 PM'
        }
        response = self.client.post(reverse('create_section'), data, follow=True)
        
        # Assert that the response redirects to manage_section
        self.assertRedirects(response, reverse('manage_section'))

        # Assert that the success message is displayed on the redirected page
        self.assertContains(response, "Lecture section created successfully.")

        # Validate that the section and lecture are created
        section = Section.objects.get(section_id=5, course=self.course_1)
        self.assertEqual(section.location, 'Room 107')
        self.assertEqual(section.meeting_time, '5:00 PM')
        lecture = Lecture.objects.get(section=section)
        self.assertIsNotNone(lecture)

        
                
    def test_create_section_non_integer_section_id(self):
        """Test that non-integer section IDs are rejected"""
        data = {
            'course_id': self.course_1.course_id,
            'section_id': 'abc',  # Non-integer section_id
            'section_type': 'Lab',
            'location': 'Room 108',
            'meeting_time': '6:00 PM'
        }
        response = self.client.post(reverse('create_section'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Section ID must be a valid number.")

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
            
    def test_edit_section_unauthorized_access(self):
        """Ensure non-admin and non-instructor users cannot access the edit_section view."""
        self.client.login(username='tauser', password='tapassword')  # Log in as TA
        response = self.client.get(reverse('edit_section', args=[self.section.id]))
        self.assertEqual(response.status_code, 403)  # Access should be forbidden

    def test_edit_section_with_missing_data(self):
        """Test that missing data does not update the section."""
        response = self.client.post(reverse('edit_section', args=[self.section_lab.id]), {
            "location": "",  # Missing location
            "meeting_time": "Mon-Wed 2:00 PM",
        })

        # Check that the response indicates an error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Location is required.")  # Validate the error message

        # Ensure the section location has not been updated
        section = Section.objects.get(id=self.section_lab.id)
        self.assertNotEqual(section.location, "")  # Location should remain unchanged


        


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

    def test_manage_section_search(self):
        """Test searching for sections by location."""
        response = self.client.get(reverse('manage_section'), {'search': 'Room 101'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Room 101")
        self.assertNotContains(response, "Room 102")

    def test_manage_section_unauthorized_access(self):
        """Test if unauthorized users (non-admin, non-instructor) are denied access."""
        ta_user = User.objects.create_user(
            username="tauser",
            email="tauser@example.com",
            password="password",
            is_ta=True,
        )
        self.client.login(username="tauser", password="password")
        response = self.client.get(reverse('manage_section'))
        self.assertEqual(response.status_code, 403)

    def test_create_section_valid(self):
        """Test creating a valid section."""
        # Create a test user and log them in
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            is_admin=True,
        )
        self.client.login(username="testuser", password="password123")
        
        # Create a course directly in the test
        course = Course.objects.create(
            course_id="CS141",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A basic course in computer science.",
            num_of_sections=2,
            modality="In-person",
        )
        
        # POST request to create a section
        data = {
            'course_id': course.course_id,
            'section_id': 1,
            'section_type': 'Lab',
            'location': 'Room 101',
            'meeting_time': '9:00 AM',
        }
        response = self.client.post(reverse('create_section'), data)

        # Check if the response is a redirect (302)
        self.assertEqual(response.status_code, 302)

        # Check if the user is redirected to the 'manage_section' page
        self.assertRedirects(response, reverse('manage_section'))

        # Check if the section is created
        section = Section.objects.get(section_id=1, course=course)
        self.assertEqual(section.location, 'Room 101')
        self.assertEqual(section.meeting_time, '9:00 AM')



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

    def test_create_section_invalid_course(self):
        """Test creating a section with an invalid course ID."""
        data = {
            'course_id': 'INVALID',
            'section_id': 3,
            'section_type': 'Lab',
            'location': 'Room 103',
            'meeting_time': '9:00 AM',
        }
        response = self.client.post(reverse('create_section'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid course ID.")

    def test_create_section_maximum_limit(self):
        """Test creating a section when the maximum number of sections is exceeded."""
        Section.objects.create(
            section_id=3,
            course=self.course_1,
            location="Room 105",
            meeting_time="10:00 AM",
        )
        data = {
            'course_id': self.course_1.course_id,
            'section_id': 4,
            'section_type': 'Lab',
            'location': 'Room 106',
            'meeting_time': '11:00 AM',
        }
        response = self.client.post(reverse('create_section'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The course has reached its maximum number of sections.")

    def test_create_section_missing_data(self):
        """Test creating a section with missing required fields."""
        data = {
            'course_id': self.course_1.course_id,
            'section_id': '',  # Missing section_id
            'section_type': 'Lab',
            'location': 'Room 103',
            'meeting_time': '9:00 AM',
        }
        response = self.client.post(reverse('create_section'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All fields are required.")
 
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

    def test_delete_section_invalid_id(self):
        """Test deleting a non-existent section."""
        response = self.client.post(reverse('delete_section', args=[999]))
        self.assertRedirects(response, reverse('manage_section'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Error deleting section:" in str(msg) for msg in messages))

    def test_delete_section_unauthorized_access(self):
        """Test that a non-admin user cannot delete a section."""
        # Log out admin user
        self.client.logout()
        
        # Create a regular user
        User.objects.create_user(username="regularuser", password="password")
        self.client.login(username="regularuser", password="password")
        
        response = self.client.post(reverse('delete_section', args=[self.section.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden access        
        
    def test_delete_section_successful(self):
            """Test that an admin can delete a section successfully."""
            self.client.login(username='admin_user', password='adminpassword')
            response = self.client.post(reverse('delete_section', args=[self.section.id]))
            self.assertRedirects(response, reverse('manage_section'))
            self.assertFalse(Section.objects.filter(id=self.section.id).exists())  # Ensure the section is deleted

    def test_delete_nonexistent_section(self):
        """Test attempting to delete a nonexistent section redirects with an error."""
        response = self.client.post(reverse('delete_section', args=[9999]), follow=True)
        self.assertRedirects(response, reverse('manage_section'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Section not found." in str(msg) for msg in messages))





    def test_delete_section_not_logged_in(self):
        # Log out the user to simulate unauthenticated access
        self.client.logout()

        # Attempt to access the delete_section view
        response = self.client.get(reverse('delete_section', args=[self.section.id]))

        # Expected URL for login redirection
        expected_url = f"/login/?next={reverse('delete_section', args=[self.section.id])}"

        # Assert redirection to the login page
        self.assertRedirects(response, expected_url)

    def test_delete_section_invalid_id(self):
        """Test deleting a section with an invalid ID redirects with an error message."""
        response = self.client.post(reverse('delete_section', args=[9999]), follow=True)
        self.assertRedirects(response, reverse('manage_section'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Section not found." in str(msg) for msg in messages))



    def test_delete_section_as_ta(self):
        self.client.login(username=self.ta_user.username, password="tapass")
        response = self.client.post(reverse('delete_section', args=[self.section.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden for TA users

    def test_delete_section_as_instructor(self):
        self.client.login(username=self.instructor_user.username, password="instructorpass")
        response = self.client.post(reverse('delete_section', args=[self.section.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden for Instructor users

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
        response = self.client.post(reverse('delete_section', args=[self.section.id]), follow=True)
        self.assertContains(response, f"Section {self.section.section_id} deleted successfully.")