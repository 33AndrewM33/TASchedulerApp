from django.test import TestCase, Client
from TAScheduler.models import Course, Section, User, Administrator


class AdminDeleteCourseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create an administrator
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
        ses["user"] = self.admin_user.user.email_address
        ses.save()

        # Create a course with sections
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Intro to Computer Science",
            description="Basic programming concepts.",
            num_of_sections=2,
            modality="In-person"
        )
        self.section = Section.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="Mon/Wed 10:00-11:30"
        )

    def test_delete_course_success(self):
        # Post to delete the course
        response = self.client.post('/home/managecourse/', {'course_id': self.course.course_id, 'delete': 'Delete'})

        # Fetch the course from the database after the delete request
        course_exists = Course.objects.filter(pk=self.course.pk).exists()

        # Assert the course is deleted
        self.assertFalse(course_exists, "The course was not successfully deleted.")
        self.assertEqual(response.status_code, 200, "Failed to get the correct response for delete.")
