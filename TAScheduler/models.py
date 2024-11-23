from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import BaseUserManager
from django.db import models


class User(models.Model):
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
    num_of_sections = models.IntegerField()
    modality = models.CharField(max_length=50, choices=[("Online", "Online"), ("In-person", "In-person")])
    

    def __str__(self):
        return f"{self.course_id}: {self.name}"
    
    @classmethod
    def delete_case_insensitive(cls, course_id):
        return cls.objects.filter(course_id__iexact=course_id).delete()



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


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="administrator_profile")

    def __str__(self):
        return f"{self.user} - Administrator"


class UserManager(BaseUserManager):
    def create_user(self, email_address, password=None, **extra_fields):
        """Create and return a regular user with the given email and password."""
        if not email_address:
            raise ValueError("The Email Address field must be set")
        email_address = self.normalize_email(email_address)
        user = self.model(email_address=email_address, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email_address, password=None, **extra_fields):
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_admin'):
            raise ValueError("Superuser must have is_admin=True.")
        return self.create_user(email_address, password, **extra_fields)