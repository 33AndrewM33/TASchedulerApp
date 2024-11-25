from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    
    username=models.CharField(max_length=50, unique=True)
    email_address = models.EmailField(unique=True, max_length=90)  # Email validation and unique constraint
    password = models.CharField(max_length=128)  # Supports hashed passwords
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    home_address = models.CharField(max_length=90, blank=True)  # Allow optional fields
    phone_number = models.CharField(max_length=15, blank=True)


    # User roles
    is_admin = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    is_ta = models.BooleanField(default=False)
    
    

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email_address})"


class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="supervisor_profile")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Supervisor"


class TA(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ta_profile")
    grader_status = models.BooleanField()
    skills = models.TextField(null=True, default="No skills listed")
    max_assignments = models.IntegerField(
        default=6,
        validators=[
            MaxValueValidator(6),
            MinValueValidator(0)
        ]
    )

    def __str__(self):
        return f"{self.user} - TA"


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="instructor_profile")
    max_assignments = models.IntegerField(
        default=6,
        validators=[
            MaxValueValidator(6),
            MinValueValidator(0)
        ]
    )

    def __str__(self):
        return f"{self.user} - Instructor"


class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True)
    semester = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField()
    num_of_sections = models.IntegerField(
        validators=[MinValueValidator(0)]  # Ensure value is 0 or greater
    )
    modality = models.CharField(max_length=50, choices=[("Online", "Online"), ("In-person", "In-person")])
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,  # If the instructor is deleted, set this field to NULL
        null=True,
        blank=True,
        related_name="courses"  # Enables reverse lookup: instructor.courses.all()
    )

    def __str__(self):
        return f"{self.course_id}: {self.name}"
    
    @classmethod
    def delete_case_insensitive(cls, course_id):
        return cls.objects.filter(course_id__iexact=course_id).delete()


    def edit_Course(self, **kwargs):
        # Validate and update basic fields
        if 'name' in kwargs:
            if not kwargs['name']:  # Check for empty values
                raise ValueError("Course name cannot be empty.")
            self.name = kwargs['name']

        if 'num_of_sections' in kwargs:
            if kwargs['num_of_sections'] < 0:  # Check for negative values
                raise ValueError("Number of sections cannot be negative.")
            self.num_of_sections = kwargs['num_of_sections']

        # Update other fields
        for field, value in kwargs.items():
            if hasattr(self, field) and field != 'instructors':  # Skip 'instructors'
                setattr(self, field, value)

        # Handle instructor assignments if provided
        if 'instructors' in kwargs:
            instructor_list = kwargs['instructors']
            if not isinstance(instructor_list, list):
                raise ValueError("Instructors should be a list of Instructor instances.")
            
            # Clear existing assignments
            InstructorToCourse.objects.filter(course=self).delete()
            
            # Add new assignments
            for instructor in instructor_list:
                if isinstance(instructor, Instructor):
                    InstructorToCourse.objects.create(instructor=instructor, course=self)
                else:
                    raise ValueError("Each instructor must be an instance of the Instructor model.")

        # Save the updated course instance
        self.save()


class Section(models.Model):
    section_id = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    location = models.CharField(max_length=30)
    meeting_time = models.TextField()

    def __str__(self):
        return f"Section {self.section_id} - {self.course}"


class Lab(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="labs")
    ta = models.ForeignKey(TA, on_delete=models.SET_NULL, null=True, related_name="assigned_labs")

    def __str__(self):
        return f"Lab: {self.section}"


class Lecture(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lectures")
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, related_name="assigned_lectures")
    ta = models.ForeignKey(TA, on_delete=models.SET_NULL, null=True, related_name="grading_lectures")

    def __str__(self):
        return f"Lecture: {self.section}"


class TAToCourse(models.Model):
    ta = models.ForeignKey(TA, on_delete=models.CASCADE, related_name="course_assignments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="ta_assignments")


class InstructorToCourse(models.Model):
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name="course_assignments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="instructor_assignments")
    
    class Meta:
        # Adds a unique constraint to ensure that each instructor-course pair is unique
        constraints = [
            models.UniqueConstraint(
                fields=["instructor", "course"],  # Specifies the combination of fields to enforce uniqueness
                name="unique_instructor_course"  # Gives a name to the constraint for easy reference
            )
        ]



class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="administrator_profile")

    def __str__(self):
        return f"{self.user} - Administrator"
