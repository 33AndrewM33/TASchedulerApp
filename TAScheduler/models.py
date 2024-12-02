from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


# ----------------------------------------
# User Model
# ----------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email_address = models.EmailField(unique=True, max_length=90)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    home_address = models.CharField(max_length=90, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    # Roles
    is_admin = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    is_ta = models.BooleanField(default=False)

    # Required for authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()  # Use Django's built-in manager

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email_address']

    def get_role(self):
        if self.is_admin:
            return "Administrator"
        elif self.is_instructor:
            return "Instructor"
        elif self.is_ta:
            return "TA"
        return "No Role"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email_address})"


# ----------------------------------------
# Administrator Model
# ----------------------------------------
class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="administrator_profile")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Administrator"


# ----------------------------------------
# Teaching Assistant Model
# ----------------------------------------
class TA(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ta_profile")
    grader_status = models.BooleanField(default=False)
    skills = models.TextField(null=True, blank=True, default="No skills listed")
    max_assignments = models.IntegerField(
        default=6,
        validators=[
            MaxValueValidator(6),
            MinValueValidator(0)
        ]
    )

    def __str__(self):
        return f"{self.user.first_name} - TA"


# ----------------------------------------
# Instructor Model
# ----------------------------------------
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
        return f"{self.user.first_name} - Instructor"


# ----------------------------------------
# Course Model
# ----------------------------------------
class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True)
    semester = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField()
    num_of_sections = models.IntegerField()
    modality = models.CharField(max_length=50, choices=[("Online", "Online"), ("In-person", "In-person")])

    def __str__(self):
        return f"{self.course_id}: {self.name}"


# ----------------------------------------
# Section Model
# ----------------------------------------
class Section(models.Model):
    section_id = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    location = models.CharField(max_length=30)
    meeting_time = models.TextField()

    def __str__(self):
        return f"Section {self.section_id} - {self.course}"


# ----------------------------------------
# Lab Model
# ----------------------------------------
class Lab(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="labs")
    ta = models.ForeignKey(TA, on_delete=models.SET_NULL, null=True, related_name="assigned_labs")

    def __str__(self):
        return f"Lab in {self.section}"


# ----------------------------------------
# Lecture Model
# ----------------------------------------
class Lecture(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lectures")
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, related_name="assigned_lectures")
    ta = models.ForeignKey(TA, on_delete=models.SET_NULL, null=True, related_name="grading_lectures")

    def __str__(self):
        return f"Lecture in {self.section}"
