from django.test import TestCase
from TAScheduler.models import TA, Administrator, Instructor, Course, InstructorToCourse, Lab, Lecture
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.contrib.auth import get_user_model


class UnitAdminAssignInstructorToCourseTest(TestCase):
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

class Acceptance_Admin_Creates_Instructor_TA(TestCase):
    def setUp(self):
        # Create an admin user
        User = get_user_model()
        self.admin_user = User.objects.create(
            username="admin_user",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.admin_user.set_password("adminpassword")
        self.admin_user.save()

        # Log in as admin
        self.client.login(username="admin_user", password="adminpassword")

        # URL for account creation
        self.create_account_url = reverse("create-account")

    def test_create_ta(self):
        response = self.client.post(self.create_account_url, {
            "username": "ta_user",
            "email_address": "ta@example.com",
            "password": "tapassword",
            "first_name": "TA",
            "last_name": "User",
            "is_ta": "on",
        })

        # Assert the response status code
        self.assertEqual(response.status_code, 302)  # Expect a redirect on success

        # Check the created TA user
        User = get_user_model()
        ta_user = User.objects.get(username="ta_user")
        self.assertTrue(ta_user.is_ta)
        self.assertEqual(ta_user.email_address, "ta@example.com")

    def test_create_instructor(self):
        response = self.client.post(self.create_account_url, {
            "username": "instructor_user",
            "email_address": "instructor@example.com",
            "password": "instructorpassword",
            "first_name": "Instructor",
            "last_name": "User",
            "is_instructor": "on",
        })

        # Assert the response status code
        self.assertEqual(response.status_code, 302)  # Expect a redirect on success

        # Check the created Instructor user
        User = get_user_model()
        instructor_user = User.objects.get(username="instructor_user")
        self.assertTrue(instructor_user.is_instructor)
        self.assertEqual(instructor_user.email_address, "instructor@example.com")

class Unit_Admin_Assign_TA_Tests(TestCase):
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

        # Create a TA
        self.ta = TA.objects.create(
            username="ta_user",
            email_address="ta@example.com",
            first_name="TA",
            last_name="User",
            is_ta=True,
        )

        # Create a course
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Intro to CS",
            description="Basic course on computer science",
            num_of_sections=2,
            modality="In-person",
        )

        # Create a lab and a lecture
        self.lab = Lab.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="MWF 10:00-11:00",
        )
        self.lecture = Lecture.objects.create(
            section_id=2,
            course=self.course,
            location="Room 202",
            meeting_time="TTh 1:00-2:30",
        )

    def test_assign_ta_to_lab_successfully(self):
        # Assign TA to lab
        self.lab.ta = self.ta
        self.lab.save()

        # Verify assignment
        self.assertEqual(self.lab.ta, self.ta)
        self.assertTrue(Lab.objects.filter(id=self.lab.id, ta=self.ta).exists())

    def test_assign_ta_to_lecture_successfully(self):
        # Assign TA to lecture
        self.lecture.ta = self.ta
        self.lecture.save()

        # Verify assignment
        self.assertEqual(self.lecture.ta, self.ta)
        self.assertTrue(Lecture.objects.filter(id=self.lecture.id, ta=self.ta).exists())

    def test_assign_non_ta_to_lab(self):
        # Create a non-TA user
        non_ta = Administrator.objects.create(
            username="non_ta_user",
            email_address="non_ta@example.com",
            first_name="Non",
            last_name="TA",
        )

        # Attempt to assign non-TA to lab
        with self.assertRaises(ValueError):
            self.lab.ta = non_ta
            self.lab.save()

    def test_assign_ta_to_nonexistent_lab(self):
        with self.assertRaises(Lab.DoesNotExist):
            Lab.objects.get(id=999).ta = self.ta

    def test_remove_ta_from_lab(self):
        # Assign TA to lab
        self.lab.ta = self.ta
        self.lab.save()

        # Remove TA assignment
        self.lab.ta = None
        self.lab.save()

        # Verify removal
        self.assertIsNone(self.lab.ta)
        self.assertFalse(Lab.objects.filter(id=self.lab.id, ta=self.ta).exists())

    def test_remove_ta_with_protected_constraint(self):
        # Assign TA to lab
        self.lab.ta = self.ta
        self.lab.save()

        # Attempt to delete the TA directly
        with self.assertRaises(ProtectedError):
            self.ta.delete()

        # Verify the TA and lab assignment still exist
        self.assertTrue(TA.objects.filter(id=self.ta.id).exists())
        self.assertTrue(Lab.objects.filter(id=self.lab.id, ta=self.ta).exists())


    def test_assign_ta_to_multiple_labs(self):
        # Create another lab
        another_lab = Lab.objects.create(
            section_id=3,
            course=self.course,
            location="Room 303",
            meeting_time="MW 3:00-4:00",
        )

        # Assign TA to both labs
        self.lab.ta = self.ta
        self.lab.save()

        another_lab.ta = self.ta
        another_lab.save()

        # Verify assignments
        self.assertEqual(self.lab.ta, self.ta)
        self.assertEqual(another_lab.ta, self.ta)

    def test_assign_ta_with_max_assignments_exceeded(self):
        # Simulate the TA already having the maximum number of assignments
        self.ta.max_assignments = 1
        self.ta.save()

        # Assign TA to the first lab
        self.lab.ta = self.ta
        self.lab.save()

        # Attempt to assign the TA to another lab
        another_lab = Lab.objects.create(
            section_id=3,
            course=self.course,
            location="Room 303",
            meeting_time="MW 3:00-4:00",
        )

        with self.assertRaises(ValueError):
            another_lab.assign_ta(self.ta)

class Unit_Admin_Assigns_TA_Lab_Lecture(TestCase):
    def setUp(self):
        # Create an admin user
        self.admin = Administrator.objects.create(
            username="admin_user",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.admin.set_password("adminpassword")
        self.admin.save()

        # Log in as admin
        self.client.login(username="admin_user", password="adminpassword")

        # Create a TA
        self.ta = TA.objects.create(
            username="ta_user",
            email_address="ta@example.com",
            first_name="Test",
            last_name="TA",
            is_ta=True,
            grader_status=True,
        )

        # Create a course
        self.course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person",
        )

        # Create a lab
        self.lab = Lab.objects.create(
            section_id=1,
            course=self.course,
            location="Room 101",
            meeting_time="Monday 10AM",
        )

        # Create a lecture
        self.lecture = Lecture.objects.create(
            section_id=2,
            course=self.course,
            location="Room 102",
            meeting_time="Tuesday 2PM",
        )

    def test_admin_assign_ta_to_lab(self):
        response = self.client.post(reverse("assign-ta-to-lab", args=[self.lab.id]), {
            "ta": self.ta.id,
        })
        self.lab.refresh_from_db()
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(self.lab.ta, self.ta)  # Ensure the TA was assigned

    def test_admin_assign_ta_to_lecture(self):
        response = self.client.post(reverse("assign-ta-to-lecture", args=[self.lecture.id]), {
            "ta": self.ta.id,
        })
        self.lecture.refresh_from_db()
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(self.lecture.ta, self.ta)  # Ensure the TA was assigned

    def test_assign_invalid_ta_to_lab(self):
        response = self.client.post(reverse("assign-ta-to-lab", args=[self.lab.id]), {
            "ta": 999,  # Non-existent TA ID
        })
        self.assertEqual(response.status_code, 404)  # Expect a 404 error

    def test_assign_invalid_ta_to_lecture(self):
        response = self.client.post(reverse("assign-ta-to-lecture", args=[self.lecture.id]), {
            "ta": 999,  # Non-existent TA ID
        })
        self.assertEqual(response.status_code, 404)  # Expect a 404 error

    def test_admin_assign_ta_to_nonexistent_lab(self):
        response = self.client.post(reverse("assign-ta-to-lab", args=[999]), {
            "ta": self.ta.id,
        })
        self.assertEqual(response.status_code, 404)  # Expect a 404 error

    def test_admin_assign_ta_to_nonexistent_lecture(self):
        response = self.client.post(reverse("assign-ta-to-lecture", args=[999]), {
            "ta": self.ta.id,
        })
        self.assertEqual(response.status_code, 404)  # Expect a 404 error

class AcceptanceAdminCourseTests(TestCase):
    def setUp(self):
        # Create an admin user
        User = get_user_model()
        self.admin_user = User.objects.create(
            username="admin_user",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.admin_user.set_password("adminpassword")
        self.admin_user.save()

        # Log in as admin
        self.client.login(username="admin_user", password="adminpassword")

        # URL for course creation, editing, and deletion
        self.create_course_url = reverse("course-create")
        self.course_list_url = reverse("course-list")
        self.edit_course_url = lambda course_id: reverse("edit_course", args=[course_id])

        # Sample course data
        self.course_data = {
            "course_id": "CS101",
            "semester": "Fall 2024",
            "name": "Introduction to Computer Science",
            "description": "A beginner's course in computer science.",
            "num_of_sections": 3,
            "modality": "In-person",
        }

    def test_admin_can_create_course_via_view(self):
        response = self.client.post(self.create_course_url, self.course_data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(Course.objects.filter(course_id="CS101").exists())

    def test_admin_can_edit_course_via_view(self):
        # Create a course
        Course.objects.create(**self.course_data)

        # Edit the course via POST request
        edit_data = {
            "name": "Updated Course Name",
            "description": "Updated description.",
            "num_of_sections": 5,
            "semester": "Fall 2024",  # Include the semester field
            "modality": "In-person",  # Include other required fields if necessary
        }
        response = self.client.post(self.edit_course_url("CS101"), edit_data)

        # Assertions
        self.assertEqual(response.status_code, 302)  # Redirect on success
        updated_course = Course.objects.get(course_id="CS101")
        self.assertEqual(updated_course.name, "Updated Course Name")
        self.assertEqual(updated_course.num_of_sections, 5)
        self.assertEqual(updated_course.semester, "Fall 2024")


    def test_admin_can_remove_course_via_view(self):
        # Create a course
        course = Course.objects.create(**self.course_data)

        # Remove the course via DELETE request or a dedicated endpoint
        response = self.client.post(reverse("course-delete", args=[course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(Course.objects.filter(course_id="CS101").exists())



class UnitAdminCourseTests(TestCase):
    def setUp(self):
        # Create an admin user
        User = get_user_model()
        self.admin_user = User.objects.create(
            username="admin_user",
            email_address="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        self.admin_user.set_password("adminpassword")
        self.admin_user.save()

        # Log in as admin
        self.client.login(username="admin_user", password="adminpassword")

        # Sample course data
        self.course_data = {
            "course_id": "CS101",
            "semester": "Fall 2024",
            "name": "Introduction to Computer Science",
            "description": "A beginner's course in computer science.",
            "num_of_sections": 3,
            "modality": "In-person",
        }

    def test_admin_can_create_course(self):
        course = Course.objects.create(**self.course_data)
        self.assertEqual(course.course_id, "CS101")
        self.assertEqual(course.name, "Introduction to Computer Science")

    def test_admin_can_edit_course(self):
        # Create a course
        course = Course.objects.create(**self.course_data)

        # Edit the course
        course.name = "Updated Course Name"
        course.num_of_sections = 5
        course.save()

        updated_course = Course.objects.get(course_id="CS101")
        self.assertEqual(updated_course.name, "Updated Course Name")
        self.assertEqual(updated_course.num_of_sections, 5)

    def test_admin_can_remove_course(self):
        # Create a course
        course = Course.objects.create(**self.course_data)

        # Remove the course
        course.delete()

        self.assertFalse(Course.objects.filter(course_id="CS101").exists())    