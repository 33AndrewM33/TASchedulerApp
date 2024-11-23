from django.db import IntegrityError
from django.forms import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from TAScheduler.models import Administrator, Course, Section, User
from django.core.exceptions import PermissionDenied
from django.db.models.deletion import ProtectedError

class CourseModelTestCase(TestCase):

    def setUp(self):
        # Set up any necessary data for the test
        self.course_data = {
            "course_id": "CS101",
            "semester": "Fall 2024",
            "name": "Introduction to Computer Science",
            "description": "A beginner's course in computer science.",
            "num_of_sections": 3,
            "modality": "In-person",
        }

    'Unit Tests'

    # Create Course Tests #
    
    def test_create_course(self):
        # Create a course instance
        course = Course.objects.create(**self.course_data)

        # Assertions to ensure the course was created successfully
        self.assertIsNotNone(course.id, "Course ID should not be None after creation.")
        self.assertEqual(course.course_id, self.course_data["course_id"])
        self.assertEqual(course.semester, self.course_data["semester"])
        self.assertEqual(course.name, self.course_data["name"])
        self.assertEqual(course.description, self.course_data["description"])
        self.assertEqual(course.num_of_sections, self.course_data["num_of_sections"])
        self.assertEqual(course.modality, self.course_data["modality"])
    


    def test_create_course_missing_required_fields(self):
        with self.assertRaises(IntegrityError):  # Expecting an error due to missing 'num_of_sections'
            Course.objects.create(  
                modality="In-person"
            )


    def test_create_course_invalid_field_length(self):
        long_course_id = "C" * 21  # Exceeds max_length
        course_data_override = {**self.course_data, "course_id": long_course_id}

        with self.assertRaises(ValidationError):  # ValidationError is Django's field-level validation
            course = Course(**course_data_override)
            course.full_clean()  # By calling course.full_clean(), you ensured that Django performed the validation before attempting to save the instance to the database. This validation is what raised the error and allowed your test to pass.
            course.save()           
            

    def test_create_course_duplicate_course_id(self):
        Course.objects.create(**self.course_data)
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            Course.objects.create(**self.course_data)
          
    def test_create_course_with_special_characters(self):
        course = Course.objects.create(
            course_id="CS-101!",
            semester="Fall 2024",
            name="Intro to CS @2024",
            description="A beginner's course with symbols.",
            num_of_sections=3,
            modality="Online"
        )
        self.assertEqual(course.course_id, "CS-101!")
        self.assertEqual(course.name, "Intro to CS @2024")


    def test_create_course_with_empty_description(self):
        course = Course.objects.create(
            course_id="CS107",
            semester="Fall 2024",
            name="Intro to CS",
            description="",  # Optional empty description
            num_of_sections=3,
            modality="Online"
        )
        self.assertEqual(course.description, "")
        
    def test_case_insensitive_course_id(self):
        Course.objects.create(**self.course_data)
        course = Course.objects.get(course_id="cs101".upper())
        self.assertEqual(course.name, "Introduction to Computer Science")
        



    
    # Create Course Database Tests 
            
    def test_save_and_retrieve_course(self):
        course = Course.objects.create(**self.course_data)
        saved_course = Course.objects.get(course_id=self.course_data["course_id"])
        self.assertEqual(saved_course.name, self.course_data["name"])
    
    
    def test_create_course_and_save_to_database(self):
        # Create a course instance
        course = Course.objects.create(**self.course_data)

        # Check that the course was saved in the database
        self.assertIsNotNone(course.id, "Course ID should not be None after saving to the database.")

        # Verify the course details in the database
        saved_course = Course.objects.get(course_id="CS101")
        self.assertEqual(saved_course.name, self.course_data["name"])
        self.assertEqual(saved_course.semester, self.course_data["semester"])
        self.assertEqual(saved_course.description, self.course_data["description"])
        self.assertEqual(saved_course.num_of_sections, self.course_data["num_of_sections"])
        self.assertEqual(saved_course.modality, self.course_data["modality"])

        # Confirm that only one course exists in the database
        self.assertEqual(Course.objects.count(), 1, "There should be exactly one course in the database.")
    
    
    # Remove Course Tests 
        
    def test_remove_course_from_database(self):
        # Create a course
        course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person",
        )

        # Ensure the course exists in the database
        self.assertTrue(Course.objects.filter(id=course.id).exists(), "Course should exist in the database.")

        # Delete the course
        course.delete()

        # Ensure the course no longer exists in the database
        self.assertFalse(Course.objects.filter(id=course.id).exists(), "Course should not exist in the database after deletion.")


    def test_remove_nonexistent_course(self):
    # Attempt to delete a course that does not exist
        with self.assertRaises(Course.DoesNotExist):
            course = Course.objects.get(id=999)
            course.delete()

    def test_remove_course_cascade_delete(self):
        # Create a course and related sections
        course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description="A beginner's course in computer science.",
            num_of_sections=3,
            modality="In-person",
        )
        section = Section.objects.create(
            section_id=1,
            course=course,
            location="Room 101",
            meeting_time="Monday 10AM",
        )

        # Ensure both the course and the section exist
        self.assertTrue(Course.objects.filter(id=course.id).exists(), "Course should exist in the database.")
        self.assertTrue(Section.objects.filter(id=section.id).exists(), "Section should exist in the database.")

        # Delete the course
        course.delete()

        # Ensure the course and its related sections no longer exist
        self.assertFalse(Course.objects.filter(id=course.id).exists(), "Course should not exist in the database after deletion.")
        self.assertFalse(Section.objects.filter(id=section.id).exists(), "Section should not exist in the database after course deletion.")


    def test_remove_all_courses(self):
        # Create multiple courses
        Course.objects.bulk_create([
            Course(
                course_id=f"CS10{i}",
                semester="Fall 2024",
                name=f"Course {i}",
                description="A sample course.",
                num_of_sections=i,
                modality="Online" if i % 2 == 0 else "In-person",
            ) for i in range(1, 6)
        ])

        # Ensure all courses are in the database
        self.assertEqual(Course.objects.count(), 5, "There should be 5 courses in the database.")

        # Delete all courses
        Course.objects.all().delete()

        # Ensure no courses remain in the database
        self.assertEqual(Course.objects.count(), 0, "No courses should remain in the database.")
    
    def test_remove_course_with_long_description(self):
        long_description = "A" * 1000  # Long description
        course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            description=long_description,
            num_of_sections=3,
            modality="In-person",
        )

        # Ensure the course exists
        self.assertTrue(Course.objects.filter(id=course.id).exists(), "Course should exist in the database.")

        # Delete the course
        course.delete()

        # Ensure the course no longer exists
        self.assertFalse(Course.objects.filter(id=course.id).exists(), "Course should not exist in the database after deletion.")

    def test_remove_case_insensitive_exact_match(self):
        course = Course.objects.create(
            course_id="cs101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            num_of_sections=3,
            modality="In-person",
        )
        deleted_rows, _ = Course.delete_case_insensitive("CS101")
        self.assertEqual(deleted_rows, 1, "One course should be deleted with the exact case.")
        self.assertFalse(Course.objects.filter(course_id="CS101").exists(), "The course should no longer exist.")

    def test_remove_case_insensitive_lowercase(self):
        course = Course.objects.create(
            course_id="CS101",
            semester="Fall 2024",
            name="Introduction to Computer Science",
            num_of_sections=3,
            modality="In-person",
        )
        deleted_rows, _ = Course.delete_case_insensitive("cs101")
        self.assertEqual(deleted_rows, 1, "One course should be deleted with a lowercase query.")
        self.assertFalse(Course.objects.filter(course_id="CS101").exists(), "The course should no longer exist.")

    def test_remove_case_insensitive_no_match(self):
        deleted_rows, _ = Course.delete_case_insensitive("MATH101")
        self.assertEqual(deleted_rows, 0, "No course should be deleted for a non-existent course_id.")
        
        
        
        
        
        
  