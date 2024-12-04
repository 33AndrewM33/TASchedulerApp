from django.contrib.messages import get_messages
from django.test import TestCase, Client
from TAScheduler.models import Section, Course, Lecture, Lab, User, Administrator


class CreateSectionTestCase(TestCase):
    def setUp(self):
        # Initialize the client
        self.client = Client()

        # Create an administrator account with hashed password
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            home_address = "1234 Bayside Way",
            phone_number = "000-000-0000",
            password="adminpassword",
            is_admin=True
        )
        self.Administrator = Administrator.objects.create(user=self.admin_user)

        # Log in the admin user
        self.client.login(username="admin", password="adminpassword")

        # Create test courses
        self.courses = []
        for i in range(1, 4):
            course = Course.objects.create(
                course_id=f"CS10{i}",
                semester=f"Fall 202{i}",
                name=f"Course {i}",
                description=f"Description for Course {i}",
                num_of_sections=2,
                modality="Remote"
            )
            self.courses.append(course)

        # Create test sections
        self.sections = []
        for i in range(1, 4):
            section = Section.objects.create(
                section_id=i,
                course=self.courses[i - 1],  # Associate with corresponding course
                location=f"Location {i}",
                meeting_time="Mon/Wed 10:00-11:30"
            )
            self.sections.append(section)

        # Valid lecture creation data
        self.valid_lecture_data = {
            "course_id": self.courses[0].course_id,  # Associate with the first course
            "section_id": 10,  # Ensure unique section_id for the course
            "section_type": "Lecture",
            "meeting_time": "Mon/Wed 12:00-1:30",
            "location": "Lecture Hall"
        }

        # Valid lab creation data
        self.valid_lab_data = {
            "course_id": self.courses[0].course_id,  # Associate with the first course
            "section_id": 11,  # Ensure unique section_id for the course
            "section_type": "Lab",
            "meeting_time": "Tue/Thu 2:00-3:30",
            "location": "Lab Room"
        }

        # Invalid creation data
        self.invalid_data = {
            "course_id": "CS999",  # Nonexistent course
            "section_id": 6,
            "section_type": "Lecture",
            "meeting_time": "",  # Missing meeting time
            "location": ""  # Missing location
        }

    def test_successful_lecture_creation(self):
        # Send a POST request to create a lecture section
        response = self.client.post("/home/managesection/create/", data=self.valid_lecture_data)

        # Assert that the request redirects after processing
        self.assertEqual(response.status_code,
        200, "Expected a redirect after successful section creation.")

        # Query the Section object
        section = Section.objects.filter(section_id=self.valid_lecture_data["section_id"]).first()
        self.assertIsNotNone(section, "The lecture section should exist in the database.")

        # Verify Section details
        self.assertEqual(section.course.course_id, self.valid_lecture_data["course_id"],
                         "The section's course ID should match.")
        self.assertEqual(section.location, self.valid_lecture_data["location"], "The section's location should match.")
        self.assertEqual(section.meeting_time, self.valid_lecture_data["meeting_time"],
                         "The section's meeting time should match.")

        # Query the Lecture object
        lecture = Lecture.objects.filter(section=section).first()
        self.assertIsNotNone(lecture, "The lecture should exist in the database.")

        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(f"{self.valid_lecture_data['section_type']} section created successfully." in str(message) for message
                in messages),
            "Expected success message not found in flash messages."
        )

    def test_successful_lab_creation(self):
        response = self.client.post("/home/managesection/create/", data=self.valid_lab_data)

        # Check for redirect after successful creation
        self.assertEqual(response.status_code, 200, "Expected a redirect after successful section creation.")

        # Check if the section exists
        section = Section.objects.filter(section_id=self.valid_lab_data["section_id"]).first()
        self.assertIsNotNone(section, "The lab section should exist in the database.")

        # Check if the lab is linked to the section
        lab = Lab.objects.filter(section=section).first()
        self.assertIsNotNone(lab, "The lab should exist in the database.")

    def test_duplicate_section_id(self):
        # Create an initial section
        Section.objects.create(
            section_id=self.valid_lecture_data["section_id"],
            course=self.courses[0],  # Ensure this matches the course in the test data
            location="Duplicate Location",
            meeting_time="Duplicate Time"
        )

        # Attempt to create a section with the same section_id
        response = self.client.post("/home/managesection/create/", data=self.valid_lecture_data)
        self.assertEqual(response.status_code, 200, "Expected the page to render with status 200 on error.")
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Section with this ID already exists." in str(message) for message in messages),
            "Expected error message not found in messages."
        )

    def test_nonexistent_course(self):
        response = self.client.post("/home/managesection/create/", data=self.invalid_data)

        # Check for redirect after processing
        self.assertEqual(response.status_code, 200,
                         "Expected a redirect after processing creation with invalid course ID.")

        # Verify the flash message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Course ID does not exist" in str(message) for message in messages),
                        "Expected error message not found in flash messages.")

        # Ensure no new section is created
        section = Section.objects.filter(section_id=self.invalid_data["section_id"]).first()
        self.assertIsNone(section, "No section should be created for a nonexistent course.")

    def test_no_additional_sections_on_failure(self):
        initial_count = Section.objects.count()
        self.client.post("/home/managesection/create/", data=self.invalid_data)
        final_count = Section.objects.count()

        self.assertEqual(initial_count, final_count, "No new section should be added on failure.")