from datetime import datetime
from django.test import TestCase, Client
from TAScheduler.models import Section, Course, Lecture, Lab, Administrator, User


class CreateSectionTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create administrator account
        self.admin_user = Administrator.objects.create(
            user=User.objects.create(
                email_address="admin@example.com",
                password="adminpassword",
                first_name="Admin",
                last_name="User",
                home_address="123 Admin St",
                phone_number="1234567890"
            )
        )
        ses = self.client.session
        ses["user"] = str(self.admin_user)
        ses.save()

        # Create test courses
        self.courses = []
        self.sections = []
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
        for i in range(1, 4):
            section = Section.objects.create(
                section_id=i,
                course=self.courses[i - 1],
                location=f"Location {i}",
                meeting_time=datetime(2023, 1, 1, 1, i, i)
            )
            self.sections.append(section)

        # Section creation data
        self.valid_lecture_data = {
            "course_id": self.courses[0].course_id,
            "section_id": 4,
            "section_type": "Lecture",
            "meeting_time": datetime(2023, 1, 1, 1, 1, 1),
            "location": "Lecture Hall"
        }
        self.valid_lab_data = {
            "course_id": self.courses[0].course_id,
            "section_id": 5,
            "section_type": "Lab",
            "meeting_time": datetime(2023, 1, 1, 2, 2, 2),
            "location": "Lab Room"
        }
        self.invalid_data = {
            "course_id": 999,  # Nonexistent course
            "section_id": 6,
            "section_type": "Lecture",
            "meeting_time": "",
            "location": ""
        }

    def test_successful_lecture_creation(self):
        response = self.client.post("/home/managesection/create/", data=self.valid_lecture_data)
        section = Section.objects.filter(section_id=4).first()
        lecture = Lecture.objects.filter(section=section).first()

        self.assertIsNotNone(section, "The lecture section should exist in the database.")
        self.assertIsNotNone(lecture, "The lecture should exist in the database.")

    def test_successful_lab_creation(self):
        response = self.client.post("/home/managesection/create/", data=self.valid_lab_data)
        section = Section.objects.filter(section_id=5).first()
        lab = Lab.objects.filter(section=section).first()

        self.assertIsNotNone(section, "The lab section should exist in the database.")
        self.assertIsNotNone(lab, "The lab should exist in the database.")

    def test_duplicate_section_id(self):
        duplicate_data = self.valid_lecture_data.copy()
        duplicate_data["section_id"] = self.sections[0].section_id

        response = self.client.post("/home/managesection/create/", data=duplicate_data)
        self.assertContains(response, "Section with this ID already exists", status_code=400)

    def test_nonexistent_course(self):
        response = self.client.post("/home/managesection/create/", data=self.invalid_data)
        self.assertContains(response, "Course ID does not exist", status_code=400)

    def test_no_additional_sections_on_failure(self):
        initial_count = Section.objects.count()
        self.client.post("/home/managesection/create/", data=self.invalid_data)
        final_count = Section.objects.count()

        self.assertEqual(initial_count, final_count, "No new section should be added on failure.")
