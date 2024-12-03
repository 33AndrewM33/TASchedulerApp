from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth import get_user_model
from TAScheduler.models import TA, Course, Section, Lab, Lecture, Instructor, Administrator, User
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.validators import validate_email


# Utility functions

class UtilityFunctions:
    @staticmethod
    def is_admin_or_instructor(user):
        return user.is_admin or user.is_instructor

    @staticmethod
    def is_admin(user):
        return user.is_admin

# Account Controls 

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name="dispatch")
class AccountManagement(View):
    def get(self, request):
        # Display all users
        users = User.objects.all()
        return render(request, "account_management.html", {"users": users})

    def post(self, request):
        action = request.POST.get("action")

        if action == "create":
            # Handle user creation
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            role = request.POST.get("role")

            if not all([username, email, password, role]):
                messages.error(request, "All fields are required.")
                return redirect("account_management")

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect("account_management")

            if User.objects.filter(email_address=email).exists():
                messages.error(request, "Email address already exists.")
                return redirect("account_management")

            # Assign role
            is_admin = role == "administrator"
            is_instructor = role == "instructor"
            is_ta = role == "ta"

            try:
                user = User.objects.create(
                    username=username,
                    email_address=email,
                    is_admin=is_admin,
                    is_instructor=is_instructor,
                    is_ta=is_ta,
                )
                user.set_password(password)
                user.save()

                # Create role-specific object
                if is_admin:
                    Administrator.objects.create(user=user)
                elif is_instructor:
                    Instructor.objects.create(user=user)
                elif is_ta:
                    TA.objects.create(user=user)

                messages.success(request, f"User '{username}' created successfully.")
            except Exception as e:
                messages.error(request, f"Error creating user: {str(e)}")

        elif action == "delete":
            # Handle user deletion
            user_id = request.POST.get("user_id")
            try:
                user_to_delete = get_object_or_404(User, id=user_id)
                user_to_delete.delete()
                messages.success(request, f"User '{user_to_delete.username}' deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting user: {str(e)}")

        return redirect("account_management")

@method_decorator([login_required, user_passes_test(UtilityFunctions.is_admin)], name="dispatch")
class AccountCreation(View):
    def get(self, request):
        return render(request, "create_account.html")

    def post(self, request):
        username = request.POST.get("username")
        email_address = request.POST.get("email_address")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        home_address = request.POST.get("home_address", "")
        phone_number = request.POST.get("phone_number", "")
        role = request.POST.get("role")

        if not all([username, email_address, password, first_name, last_name, role]):
            messages.error(request, "All fields are required.")
            return redirect("create-account")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("create-account")
        if User.objects.filter(email_address=email_address).exists():
            messages.error(request, "Email address already exists.")
            return redirect("create-account")

        # Role assignment
        is_admin = role == "administrator"
        is_instructor = role == "instructor"
        is_ta = role == "ta"

        try:
            user = User.objects.create(
                username=username,
                email_address=email_address,
                first_name=first_name,
                last_name=last_name,
                home_address=home_address,
                phone_number=phone_number,
                is_admin=is_admin,
                is_instructor=is_instructor,
                is_ta=is_ta
            )
            user.set_password(password)
            user.save()

            # Create role-specific object
            if is_admin:
                Administrator.objects.create(user=user)
            elif is_instructor:
                Instructor.objects.create(user=user)
            elif is_ta:
                TA.objects.create(user=user)

            messages.success(request, "Account created successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect("home")


# Logging in and out controls

class LoginManagement(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/home/')
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/home/')  # Redirect to home page after successful login
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

@method_decorator(require_http_methods(["GET", "POST"]), name="dispatch")
class LogoutManagement(View):
    def get(self, request):
        logout(request)
        return redirect('/')

    def post(self, request):
        logout(request)
        return redirect('/')


# TA Views

@method_decorator([login_required, user_passes_test(UtilityFunctions.is_admin)], name="dispatch")
class AssignTAToLabView(View):
    def get(self, request, lab_id):
        lab = get_object_or_404(Lab, id=lab_id)
        tas = TA.objects.all()
        return render(request, "assign_ta_to_lab.html", {"lab": lab, "tas": tas})

    def post(self, request, lab_id):
        lab = get_object_or_404(Lab, id=lab_id)
        ta_id = request.POST.get("ta")
        ta = get_object_or_404(TA, id=ta_id)

        # Assign the TA to the lab
        lab.ta = ta
        lab.save()
        messages.success(request, f"TA {ta.first_name} {ta.last_name} assigned to lab {lab_id}.")
        return redirect("lab-list")

@method_decorator([login_required, user_passes_test(UtilityFunctions.is_admin)], name="dispatch")
class AssignTAToLectureView(View):
    def get(self, request, lecture_id):
        lecture = get_object_or_404(Lecture, id=lecture_id)
        tas = TA.objects.all()
        return render(request, "assign_ta_to_lecture.html", {"lecture": lecture, "tas": tas})

    def post(self, request, lecture_id):
        lecture = get_object_or_404(Lecture, id=lecture_id)
        ta_id = request.POST.get("ta")
        ta = get_object_or_404(TA, id=ta_id)

        # Assign the TA to the lecture
        lecture.ta = ta
        lecture.save()
        messages.success(request, f"TA {ta.first_name} {ta.last_name} assigned to lecture {lecture_id}.")
        return redirect("lecture-list")


# Course Views

@method_decorator([login_required, user_passes_test(UtilityFunctions.is_admin_or_instructor)], name="dispatch")
class CourseCreation(View):
    def get(self, request):
        return render(request, "create_course.html")  # Ensure this template exists

    def post(self, request):
        # Handle course creation
        course_id = request.POST.get("course_id")
        semester = request.POST.get("semester")
        name = request.POST.get("name")
        description = request.POST.get("description")
        num_of_sections = request.POST.get("num_of_sections")
        modality = request.POST.get("modality")

        if not all([course_id, semester, name, num_of_sections, modality]):
            return HttpResponseBadRequest("Missing required fields")

        Course.objects.create(
            course_id=course_id,
            semester=semester,
            name=name,
            description=description,
            num_of_sections=num_of_sections,
            modality=modality,
        )
        return redirect("course-list")  # Redirect after success

@method_decorator(login_required, name="dispatch")
class EditCourse(View):
    def get(self, request, course_id):
        # Fetch the course to edit
        course = get_object_or_404(Course, course_id=course_id)
        return render(request, "edit_course.html", {"course": course})

    def post(self, request, course_id):
        # Handle course update
        course = get_object_or_404(Course, course_id=course_id)
        name = request.POST.get("name")
        semester = request.POST.get("semester")
        modality = request.POST.get("modality")
        num_of_sections = request.POST.get("num_of_sections")
        description = request.POST.get("description")

        # Update course details
        try:
            course.name = name
            course.semester = semester
            course.modality = modality
            course.num_of_sections = num_of_sections
            course.description = description
            course.save()
            messages.success(request, f"Course {course.course_id} updated successfully!")
            return redirect("manage_course")  # Redirect back to course management
        except Exception as e:
            messages.error(request, f"An error occurred while updating the course: {str(e)}")
            return render(request, "edit_course.html", {"course": course})
        
@method_decorator([login_required, user_passes_test(UtilityFunctions.is_admin)], name="dispatch")
class DeleteCourseView(View):
    def post(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        course.delete()
        messages.success(request, f"Course {course.name} has been successfully deleted.")
        return redirect('course-list')  # Adjust the redirect URL as necessary        

@method_decorator(login_required, name="dispatch")
class CourseManagement(View):
    def get(self, request):
        # Fetch all courses and pass them to the template
        courses = Course.objects.all()
        return render(request, "manage_course.html", {"courses": courses})

    def post(self, request):
        # Determine the action based on the form
        action = request.POST.get("action")

        if action == "create":
            # Extract form data for course creation
            course_id = request.POST.get("course_id")
            name = request.POST.get("name")
            description = request.POST.get("description")
            semester = request.POST.get("semester")
            modality = request.POST.get("modality")

            # Validate required fields
            if not all([course_id, name, semester, modality]):
                messages.error(request, "All fields are required.")
                return redirect("manage_course")

            try:
                # Create the new course
                Course.objects.create(
                    course_id=course_id,
                    name=name,
                    description=description,
                    semester=semester,
                    modality=modality,
                )
                messages.success(request, "Course created successfully.")
            except Exception as e:
                messages.error(request, f"An error occurred while creating the course: {e}")

        elif action == "delete":
            # Handle course deletion
            course_id = request.POST.get("course_id")
            try:
                # Fetch and delete the course
                course = Course.objects.get(course_id=course_id)
                course.delete()
                messages.success(request, "Course deleted successfully.")
            except Course.DoesNotExist:
                messages.error(request, "Course not found.")
            except Exception as e:
                messages.error(request, f"An error occurred while deleting the course: {e}")

        return redirect("manage_course")




# Section Views

@method_decorator(login_required, name='dispatch')
class CreateSectionView(View):
    def get(self, request):
        # Fetch all courses to pass to the template
        courses = Course.objects.all()
        return render(request, "create_section.html", {"courses": courses})

    def post(self, request):
        # Extract data from the POST request
        course_id = request.POST.get("course_id")
        section_id = request.POST.get("section_id")
        section_type = request.POST.get("section_type")
        location = request.POST.get("location")
        meeting_time = request.POST.get("meeting_time")

        try:
            # Ensure the course exists
            course = get_object_or_404(Course, course_id=course_id)
            if Section.objects.filter(section_id=section_id, course=course).exists():
                messages.error(request, "Section with this ID already exists for the course.")
            else:
                # Create the section
                section = Section.objects.create(
                    section_id=section_id,
                    course=course,
                    location=location,
                    meeting_time=meeting_time,
                )

                # Add Lab or Lecture
                if section_type.lower() == "lab":
                    Lab.objects.create(section=section)
                elif section_type.lower() == "lecture":
                    Lecture.objects.create(section=section)

                messages.success(request, f"{section_type.capitalize()} section created successfully.")
                return redirect("manage_section")
        except Course.DoesNotExist:
            messages.error(request, "Course does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        # Fetch all courses to pass to the template again in case of errors
        courses = Course.objects.all()
        return render(request, "create_section.html", {"courses": courses})
    
@method_decorator(login_required, name='dispatch')
class EditSectionView(View):
    def get(self, request, section_id):
        # Fetch the section and available courses
        section = get_object_or_404(Section, id=section_id)
        courses = Course.objects.all()

        # Pass the section and courses to the template
        return render(request, "edit_section.html", {"section": section, "courses": courses})

    def post(self, request, section_id):
        # Fetch the section
        section = get_object_or_404(Section, id=section_id)

        # Extract data from the POST request
        course_id = request.POST.get("course_id")
        section_identifier = request.POST.get("section_id")
        meeting_time = request.POST.get("meeting_time")
        location = request.POST.get("location")

        try:
            # Fetch the course and update section details
            course = get_object_or_404(Course, id=course_id)
            section.course = course
            section.section_id = section_identifier
            section.meeting_time = meeting_time
            section.location = location
            section.save()
            messages.success(request, "Section updated successfully.")
            return redirect("manage_section")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        # Fetch all courses to pass to the template in case of an error
        courses = Course.objects.all()
        return render(request, "edit_section.html", {"section": section, "courses": courses})

@method_decorator(login_required, name="dispatch")
class SectionManagement(View):
    def get(self, request):
        # Display all sections
        sections = Section.objects.all()
        return render(request, "manage_section.html", {"sections": sections, "user": request.user})

    def post(self, request):
        action = request.POST.get("action")
        if action == "delete":
            section_id = request.POST.get("section_id")
            try:
                section = get_object_or_404(Section, section_id=section_id)
                section.delete()
                messages.success(request, "Section deleted successfully.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        return redirect("manage_section")

@method_decorator(login_required, name="dispatch")
class DeleteSectionView(View):
    def get(self, request, section_id):
        return self.delete_section(request, section_id)

    def post(self, request, section_id):
        return self.delete_section(request, section_id)

    def delete_section(self, request, section_id):
        try:
            section = get_object_or_404(Section, id=section_id)
            section.delete()
            messages.success(request, "Section deleted successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the section: {e}")
        return redirect("manage_section")


# Home webpage

@method_decorator(login_required, name='dispatch')
class HomeView(View):
    def get(self, request):
        # Clear any lingering messages
        messages.get_messages(request)

        # Render the home page
        return render(request, 'home.html', {"user": request.user})


# Password Management 

class ForgotPasswordView(View):
    security_questions = {
        "question_1": "university of wisconsin milwaukee",
        "question_2": "rock",
        "question_3": "django",
    }

    def get(self, request):
        # Render the forgot password form
        return render(request, "forgot_password.html", {"error": None})

    def post(self, request):
        error = None
        User = get_user_model()  # Get the user model

        if "username" in request.POST and "answer_1" in request.POST:
            # Step 1: Validate security questions
            username = request.POST.get("username", "").strip()
            answer_1 = request.POST.get("answer_1", "").strip().lower()
            answer_2 = request.POST.get("answer_2", "").strip().lower()
            answer_3 = request.POST.get("answer_3", "").strip().lower()

            if (
                answer_1 == self.security_questions["question_1"] and
                answer_2 == self.security_questions["question_2"] and
                answer_3 == self.security_questions["question_3"]
            ):
                # Valid answers, proceed to password reset
                request.session['valid_user'] = username  # Store valid user in session
                return render(request, "reset_password.html")  # Render reset password page
            else:
                error = "One or more answers were incorrect. Please try again."

        elif "new_password" in request.POST and "confirm_password" in request.POST:
            # Step 2: Reset the password
            username = request.session.get('valid_user', None)
            if username:
                new_password = request.POST.get("new_password", "")
                confirm_password = request.POST.get("confirm_password", "")

                if new_password == confirm_password:
                    try:
                        user = User.objects.get(username=username)
                        user.password = make_password(new_password)
                        user.save()
                        # Redirect to login page with a success message
                        messages.success(request, "Password successfully reset! Please log in with your new password.")
                        return redirect('/')  # Redirect to login page
                    except User.DoesNotExist:
                        error = "User not found. Please start the process again."
                else:
                    error = "Passwords do not match. Please try again."
                    return render(request, "reset_password.html", {"error": error})  # Stay on the reset_password page
            else:
                error = "Session expired. Please start the process again."

        return render(request, "forgot_password.html", {"error": error})
    
@method_decorator(login_required, name='dispatch')
class EditUserView(View):
    def get(self, request, user_id):
        user_to_edit = get_object_or_404(User, id=user_id)
        roles = ["ta", "instructor", "administrator"]
        return render(request, "edit_user.html", {"user_to_edit": user_to_edit, "roles": roles})

    def post(self, request, user_id):
        user_to_edit = get_object_or_404(User, id=user_id)

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        # Validate unique username
        if User.objects.filter(username=username).exclude(id=user_to_edit.id).exists():
            messages.error(request, "Username already exists.")
            return render(request, "edit_user.html", {"user_to_edit": user_to_edit, "roles": ["ta", "instructor", "administrator"]})

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return render(request, "edit_user.html", {"user_to_edit": user_to_edit, "roles": ["ta", "instructor", "administrator"]})

        # Update user fields
        user_to_edit.username = username
        user_to_edit.email_address = email
        if password:
            user_to_edit.set_password(password)

        user_to_edit.is_ta = role == "ta"
        user_to_edit.is_instructor = role == "instructor"
        user_to_edit.is_admin = role == "administrator"
        user_to_edit.save()

        # Handle role-specific objects
        if role == "ta":
            TA.objects.get_or_create(user=user_to_edit)
        elif role == "instructor":
            Instructor.objects.get_or_create(user=user_to_edit)
        elif role == "administrator":
            Administrator.objects.get_or_create(user=user_to_edit)

        # Remove other roles' objects
        if role != "ta" and hasattr(user_to_edit, "ta_profile"):
            user_to_edit.ta_profile.delete()
        if role != "instructor" and hasattr(user_to_edit, "instructor_profile"):
            user_to_edit.instructor_profile.delete()
        if role != "administrator" and hasattr(user_to_edit, "administrator_profile"):
            user_to_edit.administrator_profile.delete()

        messages.success(request, f"User '{username}' updated successfully.")
        return redirect("account_management")
