from django.test import TestCase
from TAScheduler.models import Administrator, Instructor, Course, InstructorToCourse
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError


class AdminAssignInstructorToCourseTest(TestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = Administrator.objects.create(
            username="admin_user",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.admin_user.set_password("adminpassword")
        self.admin_user.save()

        # Create two instructors
        self.instructor1 = Instructor.objects.create(
            username="instructor1",
            email_address="instructor1@example.com",
            first_name="John",
            last_name="Doe",
            is_instructor=True,
        )
        self.instructor1.set_password("password123")
        self.instructor1.save()

        self.instructor2 = Instructor.objects.create(
            username="instructor2",
            email_address="instructor2@example.com",
            first_name="Jane",
            last_name="Smith",
            is_instructor=True,
        )
        self.instructor2.set_password("password123")
        self.instructor2.save()

        # Create a course
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person",
        )

    def test_admin_can_assign_instructor_to_course(self):
        # Log in as admin
        self.client.login(username="admin_user", password="adminpassword")

        # Assign the instructor to the course
        assignment = InstructorToCourse.objects.create(
            instructor=self.instructor1,
            course=self.course,
        )

        # Assertions
        self.assertEqual(assignment.instructor, self.instructor1)
        self.assertEqual(assignment.course, self.course)
        self.assertTrue(InstructorToCourse.objects.filter(
            instructor=self.instructor1,
            course=self.course
        ).exists())

    def test_admin_can_reassign_instructor_to_course(self):
        # Assign the first instructor to the course
        InstructorToCourse.objects.create(
            instructor=self.instructor1,
            course=self.course,
        )

        # Reassign by deleting the old assignment and adding a new one
        InstructorToCourse.objects.filter(course=self.course).delete()
        new_assignment = InstructorToCourse.objects.create(
            instructor=self.instructor2,
            course=self.course,
        )

        # Assertions
        self.assertEqual(new_assignment.instructor, self.instructor2)
        self.assertEqual(new_assignment.course, self.course)
        self.assertTrue(InstructorToCourse.objects.filter(
            instructor=self.instructor2,
            course=self.course
        ).exists())
        self.assertFalse(InstructorToCourse.objects.filter(
            instructor=self.instructor1,
            course=self.course
        ).exists())

    def test_admin_cannot_assign_non_instructor_to_course(self):
        # Create a non-instructor user
        non_instructor = Administrator.objects.create(
            username="not_an_instructor",
            email_address="notinstructor@example.com",
            first_name="Non",
            last_name="Instructor",
        )
        with self.assertRaises(ValueError):
            InstructorToCourse.objects.create(
                instructor=non_instructor,
                course=self.course,
            )

    def test_admin_cannot_duplicate_assignment(self):
        # Assign the instructor to the course
        InstructorToCourse.objects.create(
            instructor=self.instructor1,
            course=self.course,
        )

        # Attempt to assign the same instructor again
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                InstructorToCourse.objects.create(
                    instructor=self.instructor1,
                    course=self.course,
                )

        # Assertions
        assignments = InstructorToCourse.objects.filter(course=self.course)
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().instructor, self.instructor1)


    def test_admin_can_remove_instructor_from_course(self):
        # Assign the instructor to the course
        assignment = InstructorToCourse.objects.create(
            instructor=self.instructor1,
            course=self.course,
        )

        # Verify the assignment exists
        self.assertTrue(InstructorToCourse.objects.filter(
            instructor=self.instructor1,
            course=self.course
        ).exists())

        # Remove the assignment
        assignment.delete()

        # Verify the assignment no longer exists
        self.assertFalse(InstructorToCourse.objects.filter(
            instructor=self.instructor1,
            course=self.course
        ).exists())

    def test_admin_removal_of_nonexistent_assignment(self):
        # Attempt to remove a non-existent assignment
        with self.assertRaises(InstructorToCourse.DoesNotExist):
            InstructorToCourse.objects.get(
                instructor=self.instructor1,
                course=self.course
            ).delete()

        # Verify the database is unaffected
        self.assertEqual(InstructorToCourse.objects.count(), 0)


    def test_admin_can_remove_all_instructors_from_course(self):
        # Assign multiple instructors to the course
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)
        InstructorToCourse.objects.create(instructor=self.instructor2, course=self.course)

        # Verify the assignments exist
        self.assertEqual(InstructorToCourse.objects.filter(course=self.course).count(), 2)

        # Remove all assignments for the course
        InstructorToCourse.objects.filter(course=self.course).delete()

        # Verify all assignments are removed
        self.assertEqual(InstructorToCourse.objects.filter(course=self.course).count(), 0)


    def test_admin_reassigns_instructor_after_removal(self):
        # Assign and then remove the first instructor
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)
        InstructorToCourse.objects.filter(instructor=self.instructor1, course=self.course).delete()

        # Verify the first instructor is no longer assigned
        self.assertFalse(InstructorToCourse.objects.filter(
            instructor=self.instructor1,
            course=self.course
        ).exists())

        # Assign a new instructor
        new_assignment = InstructorToCourse.objects.create(
            instructor=self.instructor2,
            course=self.course,
        )

        # Verify the new assignment
        self.assertEqual(new_assignment.instructor, self.instructor2)
        self.assertTrue(InstructorToCourse.objects.filter(
            instructor=self.instructor2,
            course=self.course
        ).exists())



    def test_admin_cannot_remove_instructor_due_to_protected_constraint(self):
        # Assign the instructor to the course
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)

        # Attempt to delete the instructor directly
        with self.assertRaises(ProtectedError):
            self.instructor1.delete()

        # Verify the instructor and assignment still exist
        self.assertTrue(Instructor.objects.filter(id=self.instructor1.id).exists())
        self.assertTrue(InstructorToCourse.objects.filter(
            instructor=self.instructor1,
            course=self.course
        ).exists())


    def test_admin_removes_course_and_cascade_deletes_assignments(self):
        # Assign the instructor to the course
        InstructorToCourse.objects.create(instructor=self.instructor1, course=self.course)

        # Verify the assignment exists
        self.assertTrue(InstructorToCourse.objects.filter(
            instructor=self.instructor1,
            course=self.course
        ).exists())

        # Delete the course
        self.course.delete()

        # Verify the assignment is also removed
        self.assertFalse(InstructorToCourse.objects.filter(
            instructor=self.instructor1
        ).exists())
