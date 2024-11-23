from django.test import TestCase, Client
from TAScheduler.models import User, Instructor, Course, Administrator


class InstructorTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create administrator for session handling
        admin_user = User.objects.create(
            email_address="admin@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            home_address="123 Admin St",
            phone_number="1234567890",
        )
        self.admin = Administrator.objects.create(user=admin_user)
        ses = self.client.session
        ses["user"] = str(self.admin)
        ses.save()

        # Create test instructor
        self.instructor_user = User.objects.create(
            email_address="instructor@example.com",
            password="instrpassword",
            first_name="Jane",
            last_name="Doe",
            home_address="456 Instructor Lane",
            phone_number="0987654321",
            is_instructor=True
        )
        self.instructor = Instructor.objects.create(user=self.instructor_user, max_assignments=3)

        # Create test courses
        self.courses = []
        for i in range(1, 4):
            course = Course.objects.create(
                course_id=f"CS10{i}",
                semester=f"Fall 202{i}",
                name=f"Course {i}",
                description=f"Description for Course {i}",
                num_of_sections=2,
                modality="In-person"
            )
            self.courses.append(course)

    def test_instructor_creation(self):
        self.assertIsNotNone(self.instructor, "Instructor should be created successfully.")
        self.assertEqual(self.instructor.user.first_name, "Jane", "Instructor's first name should match.")
        self.assertEqual(self.instructor.user.email_address, "instructor@example.com", "Instructor's email should match.")

    def test_assign_instructor_to_course(self):
        course = self.courses[0]
        self.instructor.course_assignments.create(course=course)
        self.assertIn(course, [assignment.course for assignment in self.instructor.course_assignments.all()],
                      "Instructor should be assigned to the course.")

    def test_assign_instructor_to_multiple_courses(self):
        for course in self.courses:
            self.instructor.course_assignments.create(course=course)
        assigned_courses = [assignment.course for assignment in self.instructor.course_assignments.all()]
        self.assertEqual(len(assigned_courses), len(self.courses), "Instructor should be assigned to all courses.")
        self.assertListEqual(assigned_courses, self.courses, "Assigned courses should match the created courses.")

    def test_exceed_max_assignments(self):
        for i in range(self.instructor.max_assignments + 1):
            if i < self.instructor.max_assignments:
                self.instructor.course_assignments.create(course=self.courses[i])
            else:
                with self.assertRaises(Exception, msg="Should raise an exception when exceeding max assignments"):
                    self.instructor.course_assignments.create(course=self.courses[i])

    def test_edit_instructor_details(self):
        self.instructor.user.first_name = "Updated Name"
        self.instructor.user.save()
        updated_instructor = User.objects.get(email_address="instructor@example.com")
        self.assertEqual(updated_instructor.first_name, "Updated Name", "Instructor's first name should be updated.")

    def test_delete_instructor(self):
        self.instructor.delete()
        self.assertFalse(Instructor.objects.filter(pk=self.instructor.pk).exists(),
                         "Instructor should be deleted from the database.")
