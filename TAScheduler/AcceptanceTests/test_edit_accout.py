from django.test import TestCase, Client
from TAScheduler.models import User, Instructor, Course, Administrator, Section


class InstructorTestCase(TestCase):
    def setUp(self):
        # Set up the client and an admin user for authentication
        self.client = Client()

        # Create an administrator
        admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        self.admin = Administrator.objects.create(user=admin_user)
        self.client.force_login(admin_user)  # Log in as admin

        # Create an instructor
        self.instructor_user = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="instrpassword",
            first_name="Jane",
            last_name="Doe",
            is_instructor=True
        )
        self.instructor = Instructor.objects.create(user=self.instructor_user, max_assignments=3)

        # Create some test courses
        self.courses = [
            Course.objects.create(
                course_id=f"CS10{i}",
                semester=f"Fall 202{i}",
                name=f"Course {i}",
                description=f"Description for Course {i}",
                num_of_sections=2,
                modality="In-person"
            )
            for i in range(1, 4)
        ]

    def test_instructor_creation(self):
        """Test that an instructor is created successfully."""
        self.assertIsNotNone(self.instructor, "Instructor should be created successfully.")
        self.assertEqual(self.instructor.user.first_name, "Jane", "Instructor's first name should be 'Jane'.")
        self.assertEqual(self.instructor.user.email, "instructor@example.com", "Instructor's email should match.")


    def test_edit_instructor_details(self):
        """Test that an instructor's details can be updated."""
        self.instructor.user.first_name = "Updated Name"
        self.instructor.user.save()
        updated_instructor = User.objects.get(email="instructor@example.com")
        self.assertEqual(updated_instructor.first_name, "Updated Name", "Instructor's first name should be updated.")

    def test_delete_instructor(self):
        """Test that an instructor can be deleted."""
        instructor_id = self.instructor.pk
        self.instructor.delete()
        self.assertFalse(Instructor.objects.filter(pk=instructor_id).exists(),
                         "Instructor should be deleted from the database.")