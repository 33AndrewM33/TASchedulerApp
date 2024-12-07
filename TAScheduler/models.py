from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


# ----------------------------------------
# User Model
# ----------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True, max_length=90)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    home_address = models.CharField(max_length=90, blank=True)  # Private information
    phone_number = models.CharField(max_length=15, blank=True)  # Private information
    is_temporary_password = models.BooleanField(default=False)  # New field to track temporary passwords

    # Roles
    is_admin = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    is_ta = models.BooleanField(default=False)

    # Required for authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_role(self):
        if self.is_admin:
            return "Administrator"
        elif self.is_instructor:
            return "Instructor"
        elif self.is_ta:
            return "TA"
        return "No Role"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

# ----------------------------------------
# Notification Model
# ----------------------------------------
class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_notifications")
    subject = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification from {self.sender} to {self.recipient} - {self.subject}"

    @staticmethod
    def notify_admin_on_reset(user):
        """Send a notification to all administrators when a user resets their account."""
        admins = User.objects.filter(is_admin=True)
        for admin in admins:
            Notification.objects.create(
                sender=user,
                recipient=admin,
                subject="User Account Reset",
                message=f"The user {user.first_name} {user.last_name} ({user.email}) has reset their account."
            )

    @staticmethod
    def notify_admin_on_course_creation(course, creator):
        """Send a notification to all administrators when a new course is created."""
        admins = User.objects.filter(is_admin=True)
        for admin in admins:
            Notification.objects.create(
                sender=creator,
                recipient=admin,
                subject="New Course Created",
                message=f"A new course '{course.name}' (ID: {course.course_id}) has been created by {creator.username}."
            )

    @staticmethod
    def notify_admin_on_section_creation(section, creator):
        """Send a notification to all administrators when a new section is created."""
        admins = User.objects.filter(is_admin=True)
        for admin in admins:
            Notification.objects.create(
                sender=creator,
                recipient=admin,
                subject="New Section Created",
                message=f"A new section (ID: {section.section_id}) for course '{section.course.name}' "
                        f"has been created by {creator.username}."
            )

    @staticmethod
    def notify_admin_on_account_creation(account, creator):
        """Send a notification to all administrators when a new account is created."""
        admins = User.objects.filter(is_admin=True)
        for admin in admins:
            Notification.objects.create(
                sender=creator,
                recipient=admin,
                subject="New Account Created",
                message=f"A new account for {account.first_name} {account.last_name} ({account.username}) "
                        f"has been created by {creator.username}."
            )

    @staticmethod
    def notify_admin_on_account_deletion(account, deleter):
        """Send a notification to all administrators when an account is deleted."""
        admins = User.objects.filter(is_admin=True)
        for admin in admins:
            Notification.objects.create(
                sender=deleter,
                recipient=admin,
                subject="Account Deleted",
                message=f"The account of {account.first_name} {account.last_name} ({account.username}) "
                        f"has been deleted by {deleter.username}."
            )

    @staticmethod
    def notify_admin_on_password_change(user):
        """Notify all admins when a user changes their password."""
        admins = User.objects.filter(is_admin=True)
        for admin in admins:
            Notification.objects.create(
                sender=user,
                recipient=admin,
                subject="Password Changed",
                message=f"The user {user.username} has changed their password.",
            )
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
    grader_status = models.BooleanField(default=False)  # Grader status
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

    instructors = models.ManyToManyField(Instructor, related_name="courses")


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
    assigned_tas = models.ManyToManyField(TA, related_name="sections")  # Assign TAs to sections

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