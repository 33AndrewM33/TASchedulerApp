from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from TAScheduler.models import Course, Lab, Lecture, Section, User


class TestAccountManagement(TestCase):
        def setUp(self):
            self.admin_user = User.objects.create(username="admin", email_address="admin@example.com", is_admin=True)
            self.admin_user.set_password("password123")
            self.admin_user.save()
            self.client.login(username="admin", password="password123")

        def test_access_account_management_as_non_admin(self):
            """Verify non-admin users cannot access the account management view"""
            self.client.logout()
            # Create a non-admin user
            non_admin_user = User.objects.create(
                username="nonadmin",
                email_address="nonadmin@example.com",  # Use email_address instead of email
                is_admin=False
            )
            non_admin_user.set_password("password123")
            non_admin_user.save()

            self.client.login(username="nonadmin", password="password123")

            response = self.client.get(reverse("account_management"))
            self.assertEqual(response.status_code, 403, "Non-admin users should be forbidden from accessing this view.")



        def test_create_user_for_each_role(self):
            """Ensure users are created with correct roles (TA, Instructor, Administrator)"""
            roles = ["ta", "instructor", "administrator"]
            for role in roles:
                response = self.client.post(reverse("account_management"), {
                    "action": "create",
                    "username": f"{role}_user",
                    "email": f"{role}@example.com",
                    "password": "password123",
                    "role": role,
                })
                self.assertEqual(response.status_code, 302, f"Failed to create user for role: {role}")
                user = User.objects.get(username=f"{role}_user")
                self.assertTrue(
                    getattr(user, f"is_{role}" if role != "administrator" else "is_admin"),
                    f"User role assignment for {role} failed."
                )

        def test_create_user_with_invalid_email(self):
            """Verify users cannot be created with an invalid email format"""
            response = self.client.post(reverse("account_management"), {
                "action": "create",
                "username": "invalidemailuser",
                "email": "not-an-email",
                "password": "password123",
                "role": "ta",
            })
            self.assertEqual(response.status_code, 302, "Invalid email input should redirect.")
            messages = [msg.message for msg in response.wsgi_request._messages]
            self.assertIn("Invalid email format.", messages, "Expected invalid email format message.")

        def test_create_user_with_invalid_role(self):
            """Verify users cannot be created with an invalid role"""
            response = self.client.post(reverse("account_management"), {
                "action": "create",
                "username": "invalidroleuser",
                "email": "role@example.com",
                "password": "password123",
                "role": "invalid_role",
            })
            self.assertEqual(response.status_code, 302, "Invalid role input should redirect.")
            self.assertFalse(
                User.objects.filter(username="invalidroleuser").exists(),
                "User should not be created with an invalid role."
            )
            messages = [msg.message for msg in response.wsgi_request._messages]
            self.assertIn("Invalid role selected.", messages, "Expected invalid role message.")

        def test_delete_nonexistent_user(self):
            """Verify attempting to delete a nonexistent user produces an error"""
            response = self.client.post(reverse("account_management"), {
                "action": "delete",
                "user_id": 9999,  # Nonexistent user ID
            })
            self.assertEqual(response.status_code, 302, "Nonexistent user deletion should redirect.")
            messages = [msg.message for msg in response.wsgi_request._messages]
            self.assertIn(
                "Error deleting user: No User matches the given query.",
                messages,
                "Expected error message for nonexistent user deletion."
            )

        def test_delete_user_with_invalid_id(self):
            """Verify attempting to delete a user with an invalid ID format produces an error"""
            response = self.client.post(reverse("account_management"), {
                "action": "delete",
                "user_id": "invalid_id",  # Invalid ID
            })
            self.assertEqual(response.status_code, 302, "Invalid ID input should redirect.")
            messages = [msg.message for msg in response.wsgi_request._messages]
            self.assertIn(
                "Invalid user ID.",
                messages,
                "Expected error message for invalid ID."
            )

        def test_create_user_with_duplicate_username(self):
            """Ensure duplicate usernames are not allowed."""
            User.objects.create(username="duplicateuser", email_address="duplicate@example.com")
            response = self.client.post(reverse("account_management"), {
                "action": "create",
                "username": "duplicateuser",
                "email": "newduplicate@example.com",
                "password": "password123",
                "role": "ta",
            })
            self.assertEqual(response.status_code, 302)
            messages = [msg.message for msg in response.wsgi_request._messages]
            self.assertIn("Username already exists.", messages)

        def test_create_user_with_duplicate_email(self):
            """Ensure duplicate emails are not allowed."""
            User.objects.create(username="uniqueuser", email_address="duplicate@example.com")
            response = self.client.post(reverse("account_management"), {
                "action": "create",
                "username": "newuniqueuser",
                "email": "duplicate@example.com",
                "password": "password123",
                "role": "ta",
            })
            self.assertEqual(response.status_code, 302)
            messages = [msg.message for msg in response.wsgi_request._messages]
            self.assertIn("Email address already exists.", messages)

        def test_update_user_details(self):
            """Ensure user details can be updated correctly."""
            user = User.objects.create(username="updateuser", email_address="update@example.com", is_ta=True)
            user.set_password("oldpassword")
            user.save()

            response = self.client.post(reverse("edit_user", kwargs={"user_id": user.id}), {
                "username": "updateduser",
                "email": "updated@example.com",
                "password": "newpassword",
                "role": "instructor",
            })
            user.refresh_from_db()
            self.assertEqual(user.username, "updateduser")
            self.assertEqual(user.email_address, "updated@example.com")
            self.assertTrue(user.is_instructor)
            self.assertFalse(user.is_ta)
            self.assertTrue(user.check_password("newpassword"))

        def test_delete_existing_user(self):
            """Ensure an existing user can be deleted."""
            user = User.objects.create(username="deleteuser", email_address="delete@example.com")
            response = self.client.post(reverse("account_management"), {
                "action": "delete",
                "user_id": user.id,
            })
            self.assertEqual(response.status_code, 302)
            self.assertFalse(User.objects.filter(username="deleteuser").exists())

class AccountCreationViewTest(TestCase):
    def setUp(self):
        # Create an admin user for authentication
        self.admin_user = User.objects.create(
            username="admin",
            email_address="admin@example.com",
            is_admin=True
        )
        self.admin_user.set_password("password123")
        self.admin_user.save()

        self.client.login(username="admin", password="password123")

        # URL for account creation
        self.create_url = reverse("create-account")

    def test_create_account_successful(self):
        """Ensure accounts can be successfully created with all required fields."""
        response = self.client.post(self.create_url, {
            "username": "newuser",
            "email_address": "newuser@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
            "home_address": "123 Test St",
            "phone_number": "555-1234",
            "role": "ta",
        })
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertTrue(User.objects.filter(username="newuser").exists(), "User was not created.")
        user = User.objects.get(username="newuser")
        self.assertEqual(user.home_address, "123 Test St")
        self.assertEqual(user.phone_number, "555-1234")
        self.assertTrue(user.is_ta)
        self.assertFalse(user.is_instructor)
        self.assertFalse(user.is_admin)

    def test_create_account_missing_required_fields(self):
        """Verify error handling for missing required fields."""
        response = self.client.post(self.create_url, {
            "username": "",
            "email_address": "missing@example.com",
            "password": "password123",
            "first_name": "",
            "last_name": "",
            "role": "ta",
        })
        self.assertEqual(response.status_code, 302)
        messages = [msg.message for msg in response.wsgi_request._messages]
        self.assertIn("All fields are required.", messages, "Expected error message for missing fields.")
        self.assertFalse(User.objects.filter(email_address="missing@example.com").exists(), "User should not be created.")

    def test_create_account_duplicate_username(self):
        """Verify error handling for duplicate username."""
        response = self.client.post(self.create_url, {
            "username": "admin",
            "email_address": "unique@example.com",
            "password": "password123",
            "first_name": "Duplicate",
            "last_name": "Username",
            "role": "ta",
        })
        self.assertEqual(response.status_code, 302)
        messages = [msg.message for msg in response.wsgi_request._messages]
        self.assertIn("Username already exists.", messages, "Expected error message for duplicate username.")

    def test_create_account_duplicate_email(self):
        """Verify error handling for duplicate email address."""
        response = self.client.post(self.create_url, {
            "username": "uniqueuser",
            "email_address": "admin@example.com",
            "password": "password123",
            "first_name": "Duplicate",
            "last_name": "Email",
            "role": "ta",
        })
        self.assertEqual(response.status_code, 302)
        messages = [msg.message for msg in response.wsgi_request._messages]
        self.assertIn("Email address already exists.", messages, "Expected error message for duplicate email.")

    def test_create_account_invalid_email_format(self):
        """Verify error handling for invalid email format."""
        response = self.client.post(self.create_url, {
            "username": "invalidemailuser",
            "email_address": "not-an-email",
            "password": "password123",
            "first_name": "Invalid",
            "last_name": "Email",
            "role": "ta",
        })
        self.assertEqual(response.status_code, 302)
        messages = [msg.message for msg in response.wsgi_request._messages]
        self.assertIn("Invalid email format.", messages, "Expected error message for invalid email format.")


    def test_create_account_optional_fields_blank(self):
        """Ensure users can be created without optional fields."""
        response = self.client.post(self.create_url, {
            "username": "optionalfieldsuser",
            "email_address": "optional@example.com",
            "password": "password123",
            "first_name": "Optional",
            "last_name": "Fields",
            "role": "ta",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="optionalfieldsuser")
        self.assertEqual(user.home_address, "", "Optional field home_address should be blank.")
        self.assertEqual(user.phone_number, "", "Optional field phone_number should be blank.")
        
        
    def test_create_account_over_max_length_fields(self):
        """Ensure overly long inputs are rejected."""
        response = self.client.post(self.create_url, {
            "username": "u" * 51,  # Exceeds max length
            "email_address": "e" * 81 + "@example.com",  # Exceeds max length
            "password": "password123",
            "first_name": "f" * 31,  # Exceeds max length
            "last_name": "l" * 31,  # Exceeds max length
            "role": "ta",
        })
        self.assertEqual(response.status_code, 302)
        messages = [msg.message for msg in response.wsgi_request._messages]
        self.assertIn("Username cannot exceed 50 characters.", "".join(messages), "Expected error message for exceeding max length.")

    def test_create_account_special_characters(self):
        """Ensure special characters are accepted where appropriate."""
        response = self.client.post(self.create_url, {
            "username": "user!@#$",
            "email_address": "special@example.com",
            "password": "password123",
            "first_name": "Special",
            "last_name": "Characters",
            "role": "ta",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="user!@#$").exists(), "User should be created with special characters.")

    def test_create_account_empty_password(self):
        """Ensure users cannot be created with an empty password."""
        response = self.client.post(self.create_url, {
            "username": "emptyuser",
            "email_address": "empty@example.com",
            "password": "",
            "first_name": "Empty",
            "last_name": "Password",
            "role": "ta",
        })
        self.assertEqual(response.status_code, 302)
        messages = [msg.message for msg in response.wsgi_request._messages]
        self.assertIn("All fields are required.", messages, "Expected error message for empty password.")
        self.assertFalse(User.objects.filter(username="emptyuser").exists(), "User should not be created with an empty password.")

class CreateSectionViewTest(TestCase):
    def setUp(self):
        # Initialize the test client
        self.client = Client()

        # Create an admin user directly since we're using a custom User model
        self.user = User.objects.create(
            username="admin",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.user.set_password("password123")  # Manually set the password
        self.user.save()

        # Log in the test client
        self.client.login(username="admin", password="password123")

        # Create a sample course
        self.course = Course.objects.create(
            course_id="CS101",
            name="Intro to Computer Science",
            description="A basic computer science course",
            semester="Fall 2024",
            modality="In-person",
            num_of_sections=3,  # Add num_of_sections
        )

        # Define the URL for the view
        self.url = reverse("create_section")

    def test_get_request_renders_form(self):
        # Test that the GET request renders the form template
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_section.html")
        self.assertIn("courses", response.context)
        self.assertIn(self.course, response.context["courses"])

    def test_post_valid_lab_section(self):
        # Test creating a valid lab section
        data = {
            "course_id": self.course.course_id,
            "section_id": "101",
            "section_type": "lab",
            "location": "Room 101",
            "meeting_time": "MWF 10-11am",
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse("manage_section"))
        self.assertTrue(Section.objects.filter(section_id="101").exists())
        self.assertTrue(Lab.objects.filter(section__section_id="101").exists())

    def test_post_valid_lecture_section(self):
        # Test creating a valid lecture section
        data = {
            "course_id": self.course.course_id,
            "section_id": "102",
            "section_type": "lecture",
            "location": "Room 202",
            "meeting_time": "TTh 2-3pm",
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse("manage_section"))
        self.assertTrue(Section.objects.filter(section_id="102").exists())
        self.assertTrue(Lecture.objects.filter(section__section_id="102").exists())

    def test_post_invalid_section_type(self):
        # Test submitting an invalid section type
        data = {
            "course_id": self.course.course_id,
            "section_id": "103",
            "section_type": "invalid_type",
            "location": "Room 303",
            "meeting_time": "MWF 3-4pm",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_section.html")
        self.assertFalse(Section.objects.filter(section_id="103").exists())

    def test_post_nonexistent_course(self):
        # Test creating a section for a nonexistent course
        data = {
            "course_id": "NONEXISTENT",
            "section_id": "104",
            "section_type": "lab",
            "location": "Room 404",
            "meeting_time": "TTh 1-2pm",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_section.html")
        self.assertFalse(Section.objects.filter(section_id="104").exists())

    def test_post_duplicate_section(self):
        # Create an initial section to test duplication
        Section.objects.create(
            section_id="105",
            course=self.course,
            location="Room 505",
            meeting_time="MWF 5-6pm",
        )
        data = {
            "course_id": self.course.course_id,
            "section_id": "105",
            "section_type": "lab",
            "location": "Room 505",
            "meeting_time": "MWF 5-6pm",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_section.html")
        self.assertEqual(Section.objects.filter(section_id="105").count(), 1)
        
        
    def test_post_missing_required_fields(self):
        # Missing `meeting_time`
        data = {
            "course_id": self.course.course_id,
            "section_id": "106",
            "section_type": "lab",
            "location": "Room 606",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_section.html")
        self.assertFalse(Section.objects.filter(section_id="106").exists())


    def test_post_section_id_exceeds_max_length(self):
        data = {
            "course_id": self.course.course_id,
            "section_id": "A" * 256,  # Assuming max length is less than 256
            "section_type": "lab",
            "location": "Room 707",
            "meeting_time": "MWF 7-8pm",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_section.html")
        self.assertFalse(Section.objects.filter(location="Room 707").exists())
        
        
    def test_post_section_id_with_invalid_characters(self):
        data = {
            "course_id": self.course.course_id,
            "section_id": "INVALID@ID!",  # Invalid characters
            "section_type": "lab",
            "location": "Room 808",
            "meeting_time": "MWF 8-9pm",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_section.html")
        self.assertFalse(Section.objects.filter(location="Room 808").exists())


    def test_unauthorized_access(self):
        self.client.logout()  # Ensure the user is logged out
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertRedirects(response, reverse("login") + f"?next={self.url}")

    def test_post_case_insensitive_section_id(self):
        Section.objects.create(
            section_id="109",
            course=self.course,
            location="Room 909",
            meeting_time="MWF 9-10pm",
        )
        data = {
            "course_id": self.course.course_id,
            "section_id": "109".lower(),  # Lowercase version of the same ID
            "section_type": "lab",
            "location": "Room 909",
            "meeting_time": "MWF 9-10pm",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_section.html")
        self.assertEqual(Section.objects.filter(section_id="109").count(), 1)
        
    def test_post_edge_case_meeting_time(self):
        data = {
            "course_id": self.course.course_id,
            "section_id": "110",
            "section_type": "lab",
            "location": "Room 1010",
            "meeting_time": "F 1-2pm",  # Single day with valid time
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse("manage_section"))
        self.assertTrue(Section.objects.filter(section_id="110").exists())

class EditSectionViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.admin_user = User.objects.create(
            username="admin",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.admin_user.set_password("password123")  # Set password
        self.admin_user.save()

        # Login as admin user
        self.client.login(username="admin", password="password123")

        # Create a test course
        self.course = Course.objects.create(
            course_id="CS101",
            name="Intro to Computer Science",
            description="Test course description",
            semester="Fall 2024",
            modality="In-Person",
            num_of_sections=5,
        )

        # Create another course for updates
        self.new_course = Course.objects.create(
            course_id="CS102",
            name="Data Structures",
            description="Advanced course",
            semester="Spring 2025",
            modality="Online",
            num_of_sections=3,
        )

        # Create a test section
        self.section = Section.objects.create(
            section_id="1",
            course=self.course,
            meeting_time="MWF 10:00AM",
            location="Room 101",
        )

        # URL for edit section
        self.edit_url = reverse("edit_section", args=[self.section.id])

    def test_get_edit_section_view(self):
        """Test that the edit section view loads correctly."""
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_section.html")
        self.assertContains(response, self.section.section_id)
        self.assertContains(response, self.course.name)

    def test_post_valid_edit_section(self):
        response = self.client.post(self.edit_url, {
            "course_id": self.new_course.id,
            "section_id": "2",
            "meeting_time": "TTh 2:00PM",
            "location": "Room 202",
        })

        self.section.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.section.section_id, 2)  # Compare as an integer
        self.assertEqual(self.section.course, self.new_course)



    def test_post_invalid_course(self):
        response = self.client.post(self.edit_url, {
            "course_id": 999,  # Invalid course ID
            "section_id": "2",
            "meeting_time": "TTh 2:00PM",
            "location": "Room 202",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid course selected.")

    def test_post_missing_fields(self):
        response = self.client.post(self.edit_url, {
            "course_id": self.course.id,
            "section_id": "",
            "meeting_time": "",
            "location": "Room 202",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All fields are required.")

    def test_access_denied_for_non_authenticated_user(self):
        """Test that unauthenticated users cannot access the view."""
        self.client.logout()  # Log out the user

        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertRedirects(response, reverse("login") + f"?next={self.edit_url}")

        response = self.client.post(self.edit_url, {
            "course_id": self.course.id,
            "section_id": "2",
            "meeting_time": "TTh 2:00PM",
            "location": "Room 202",
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertRedirects(response, reverse("login") + f"?next={self.edit_url}")

    def test_post_duplicate_section_id_in_course(self):
        """Test that editing a section to a duplicate section_id in the same course is not allowed."""
        # Create another section in the same course with a different ID
        Section.objects.create(
            section_id=2,
            course=self.course,
            meeting_time="MWF 2:00PM",
            location="Room 202",
        )

        # Attempt to update the current section to have the same section_id as the other section
        response = self.client.post(self.edit_url, {
            "course_id": self.course.id,
            "section_id": "2",  # Duplicate section ID
            "meeting_time": "TTh 3:00PM",
            "location": "Room 303",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A section with this ID already exists in the selected course.")

        # Ensure the section was not updated
        self.section.refresh_from_db()
        self.assertNotEqual(self.section.section_id, 2)
        self.assertNotEqual(self.section.meeting_time, "TTh 3:00PM")
        self.assertNotEqual(self.section.location, "Room 303")


    def test_post_update_with_same_section_id(self):
        """Test that updating a section without changing the section_id is allowed."""
        response = self.client.post(self.edit_url, {
            "course_id": self.course.id,
            "section_id": self.section.section_id,  # Same section ID
            "meeting_time": "TTh 11:00AM",
            "location": "Room 105",
        })

        self.section.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.section.section_id, int(self.section.section_id))  # Ensure no change
        self.assertEqual(self.section.meeting_time, "TTh 11:00AM")
        self.assertEqual(self.section.location, "Room 105")

    def test_post_move_section_to_different_course(self):
        """Test that a section can be moved to a different course without conflicts."""
        response = self.client.post(self.edit_url, {
            "course_id": self.new_course.id,
            "section_id": "1",  # Valid section ID in the new course
            "meeting_time": "MWF 9:00AM",
            "location": "Room 204",
        })

        self.section.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.section.course, self.new_course)
        self.assertEqual(self.section.section_id, 1)
        self.assertEqual(self.section.meeting_time, "MWF 9:00AM")
        self.assertEqual(self.section.location, "Room 204")

    def test_post_invalid_section_id_format(self):
        """Test that a non-numeric or excessively long section_id is not accepted."""
        # Non-numeric section_id
        response = self.client.post(self.edit_url, {
            "course_id": self.course.id,
            "section_id": "invalid_id",  # Invalid format
            "meeting_time": "MWF 10:00AM",
            "location": "Room 101",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Section ID must be a numeric value.")

        # Excessively long section_id
        response = self.client.post(self.edit_url, {
            "course_id": self.course.id,
            "section_id": "1" * 256,  # Exceeds acceptable length
            "meeting_time": "MWF 10:00AM",
            "location": "Room 101",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Section ID is too long.")


    def test_post_whitespace_fields(self):
        """Test that fields with only whitespace are rejected."""
        response = self.client.post(self.edit_url, {
            "course_id": "   ",
            "section_id": "   ",
            "meeting_time": "   ",
            "location": "   ",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All fields are required.")


    def test_post_invalid_meeting_time(self):
        """Test that invalid meeting time formats are not accepted."""
        response = self.client.post(self.edit_url, {
            "course_id": self.course.id,
            "section_id": "2",
            "meeting_time": "InvalidTimeFormat!",
            "location": "Room 101",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid meeting time format.")


    def test_post_access_denied_for_non_admin_user(self):
        """Test that non-admin users cannot edit sections."""
        non_admin_user = User.objects.create(
            username="nonadmin",
            email_address="nonadmin@example.com",
            first_name="Non",
            last_name="Admin",
            is_admin=False,
        )
        non_admin_user.set_password("password123")
        non_admin_user.save()

        self.client.logout()
        self.client.login(username="nonadmin", password="password123")

        response = self.client.post(self.edit_url, {
            "course_id": self.course.id,
            "section_id": "2",
            "meeting_time": "TTh 2:00PM",
            "location": "Room 202",
        })

        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_post_invalid_location(self):
        """Test that an invalid or excessively long location is rejected."""
        response = self.client.post(self.edit_url, {
            "course_id": self.course.id,
            "section_id": "2",
            "meeting_time": "MWF 10:00AM",
            "location": "A" * 256,  # Excessively long location
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Location is too long.")

class DeleteSectionViewTests(TestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create(
            username="admin",
            email_address="admin@example.com",
            is_admin=True
        )
        self.admin_user.set_password("password123")
        self.admin_user.save()

        # Create a non-admin user
        self.non_admin_user = User.objects.create(
            username="nonadmin",
            email_address="nonadmin@example.com",
            is_admin=False
        )
        self.non_admin_user.set_password("password123")
        self.non_admin_user.save()

        # Create a test course
        self.course = Course.objects.create(
            course_id="CS101",
            name="Intro to Computer Science",
            description="Basic introduction to CS",
            semester="Fall 2024",
            modality="In-Person",
            num_of_sections=5,
        )

        # Create a test section associated with the course
        self.section = Section.objects.create(
            section_id="101",
            course=self.course,
            meeting_time="MWF 10:00AM",
            location="Room 101",
        )

        # URL for delete section
        self.delete_section_url = reverse("delete_section", args=[self.section.id])

    def test_admin_can_delete_section(self):
        """Test that an admin user can successfully delete a section."""
        self.client.login(username="admin", password="password123")
        response = self.client.post(self.delete_section_url)

        # Check redirection to manage section
        self.assertRedirects(response, reverse("manage_section"))

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Section deleted successfully.", str(messages[0]))

        # Verify the section no longer exists
        self.assertFalse(Section.objects.filter(id=self.section.id).exists())

    def test_non_admin_cannot_delete_section(self):
        """Test that a non-admin user cannot delete a section."""
        self.client.login(username="nonadmin", password="password123")
        response = self.client.post(self.delete_section_url)

        # Check redirection to "manage_section"
        self.assertRedirects(response, reverse("manage_section"))

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("You do not have permission to delete sections.", str(messages[0]))

        # Verify the section still exists
        self.assertTrue(Section.objects.filter(id=self.section.id).exists())



    def test_delete_nonexistent_section(self):
        """Test that attempting to delete a non-existent section results in an error."""
        self.client.login(username="admin", password="password123")
        nonexistent_section_url = reverse("delete_section", args=[9999])
        response = self.client.post(nonexistent_section_url)

        # Check redirection to manage section
        self.assertRedirects(response, reverse("manage_section"))

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("An error occurred while deleting the section:", str(messages[0]))
        
    def test_unauthenticated_user_cannot_delete_section(self):
        """Test that unauthenticated users cannot delete a section."""
        response = self.client.post(self.delete_section_url)

        # Check redirection to the login page
        self.assertRedirects(response, f"{reverse('login')}?next={self.delete_section_url}")

        # Verify the section still exists
        self.assertTrue(Section.objects.filter(id=self.section.id).exists())
        
    def test_admin_can_delete_multiple_sections(self):
        """Test that an admin user can delete multiple sections."""
        # Create additional sections
        section2 = Section.objects.create(
            section_id="102",
            course=self.course,
            meeting_time="TTh 2:00PM",
            location="Room 202",
        )
        section3 = Section.objects.create(
            section_id="103",
            course=self.course,
            meeting_time="MWF 3:00PM",
            location="Room 303",
        )

        self.client.login(username="admin", password="password123")

        # Delete the first section
        response1 = self.client.post(reverse("delete_section", args=[self.section.id]))
        self.assertRedirects(response1, reverse("manage_section"))
        self.assertFalse(Section.objects.filter(id=self.section.id).exists())

        # Delete the second section
        response2 = self.client.post(reverse("delete_section", args=[section2.id]))
        self.assertRedirects(response2, reverse("manage_section"))
        self.assertFalse(Section.objects.filter(id=section2.id).exists())

        # Delete the third section
        response3 = self.client.post(reverse("delete_section", args=[section3.id]))
        self.assertRedirects(response3, reverse("manage_section"))
        self.assertFalse(Section.objects.filter(id=section3.id).exists())

    def test_invalid_http_method(self):
        """Test that using an invalid HTTP method for delete returns a proper response."""
        self.client.login(username="admin", password="password123")
        response = self.client.get(self.delete_section_url)

        # Check for method not allowed (405 status code)
        self.assertEqual(response.status_code, 405)

        # Verify the section still exists
        self.assertTrue(Section.objects.filter(id=self.section.id).exists())

class SectionManagementTests(TestCase):
    def setUp(self):
        # Initialize test client
        self.client = Client()

        # Create an admin user
        self.admin_user = User.objects.create(
            username="admin",
            email_address="admin@example.com",
            is_admin=True
        )
        self.admin_user.set_password("password123")
        self.admin_user.save()

        # Log in the test client as admin
        self.client.login(username="admin", password="password123")

        # Create a course
        self.course = Course.objects.create(
            course_id="CS101",
            name="Intro to Computer Science",
            description="A basic computer science course",
            semester="Fall 2024",
            modality="In-person",
            num_of_sections=5,
        )

        # Create sections
        self.section1 = Section.objects.create(
            section_id="1",
            course=self.course,
            meeting_time="MWF 10:00AM",
            location="Room 101"
        )
        self.section2 = Section.objects.create(
            section_id="2",
            course=self.course,
            meeting_time="TTh 2:00PM",
            location="Room 202"
        )

        # Define the manage section URL
        self.manage_section_url = reverse("manage_section")

    def test_get_manage_sections(self):
        """Test that the GET request renders the section management page with all sections."""
        response = self.client.get(self.manage_section_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manage_section.html")
        self.assertContains(response, self.section1.section_id)
        self.assertContains(response, self.section2.section_id)
        self.assertContains(response, self.course.name)

    def test_post_delete_section(self):
        """Test that a section can be deleted using a POST request."""
        response = self.client.post(self.manage_section_url, {
            "action": "delete",
            "section_id": self.section1.section_id,
        })

        self.assertRedirects(response, self.manage_section_url)
        self.assertFalse(Section.objects.filter(section_id=self.section1.section_id).exists())

    def test_post_delete_nonexistent_section(self):
        """Test that attempting to delete a nonexistent section returns an error."""
        response = self.client.post(self.manage_section_url, {
            "action": "delete",
            "section_id": "999",  # Nonexistent section_id
        })

        self.assertRedirects(response, self.manage_section_url)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn("An error occurred", str(messages[0]))

    def test_post_invalid_action(self):
        """Test that an invalid action does nothing."""
        response = self.client.post(self.manage_section_url, {
            "action": "invalid_action",
            "section_id": self.section1.section_id,
        })

        self.assertRedirects(response, self.manage_section_url)
        self.assertTrue(Section.objects.filter(section_id=self.section1.section_id).exists())

    def test_access_denied_for_non_authenticated_user(self):
        """Test that non-authenticated users cannot access section management."""
        self.client.logout()
        response = self.client.get(self.manage_section_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        response = self.client.post(self.manage_section_url, {
            "action": "delete",
            "section_id": self.section1.section_id,
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_post_delete_section_no_permission(self):
        """Test that non-admin users cannot delete sections."""
        # Create a non-admin user
        self.client.logout()
        non_admin_user = User.objects.create(
            username="nonadmin",
            email_address="nonadmin@example.com",
            is_admin=False
        )
        non_admin_user.set_password("password123")
        non_admin_user.save()
        self.client.login(username="nonadmin", password="password123")

        response = self.client.post(self.manage_section_url, {
            "action": "delete",
            "section_id": self.section1.section_id,
        })

        self.assertRedirects(response, self.manage_section_url)
        self.assertTrue(Section.objects.filter(section_id=self.section1.section_id).exists())