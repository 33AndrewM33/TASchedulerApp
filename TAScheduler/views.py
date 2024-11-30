from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages  # Import messages framework
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from TAScheduler.models import Course, Section, Lab, Lecture

# Utility function for role checking
def is_admin_or_instructor(user):
    return user.is_admin or user.is_instructor


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


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
            return redirect('/home/')  # Redirect after successful login
        return render(request, "login.html", {"error": "Invalid username or password"})


class LogoutManagement(View):
    def get(self, request):
        logout(request)
        return redirect('/')


@method_decorator([login_required, user_passes_test(lambda user: user.is_admin)], name="dispatch")
class AccountCreation(View):
    def get(self, request):
        return render(request, "create_account.html")  # Ensure the template exists

    def post(self, request):
        username = request.POST.get("username")
        email_address = request.POST.get("email_address")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        home_address = request.POST.get("home_address", "")
        phone_number = request.POST.get("phone_number", "")
        is_admin = request.POST.get("is_admin", False) == "on"
        is_instructor = request.POST.get("is_instructor", False) == "on"
        is_ta = request.POST.get("is_ta", False) == "on"

        if not all([username, email_address, password, first_name, last_name]):
            return HttpResponseBadRequest("Missing required fields")

        User.objects.create_user(
            username=username,
            email=email_address,
            password=password,
            first_name=first_name,
            last_name=last_name,
            home_address=home_address,
            phone_number=phone_number,
            is_admin=is_admin,
            is_instructor=is_instructor,
            is_ta=is_ta
        )
        return redirect("home")  # Redirect after success


@method_decorator([login_required, user_passes_test(is_admin_or_instructor)], name="dispatch")
class EditCourse(View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)

        # Check user permissions explicitly
        if request.user.is_admin or request.user.is_instructor:
            # Update course fields only if permission is granted
            course.name = request.POST.get("name", course.name)
            course.description = request.POST.get("description", course.description)
            course.num_of_sections = request.POST.get("num_of_sections", course.num_of_sections)
            course.save()
            return redirect("course-list")  # Redirect after editing
        else:
            return HttpResponseForbidden("You do not have permission to edit this course.")


@method_decorator([login_required, user_passes_test(is_admin_or_instructor)], name="dispatch")
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


@login_required
def manage_course(request):
    return render(request, 'manage_course.html', {"user": request.user})


@login_required
def manage_section(request):
    return render(request, 'manage_section.html', {"user": request.user})


@login_required
def create_section(request):
    if request.method == "POST":
        # Extract data from the POST request
        course_id = request.POST.get("course_id")
        section_id = request.POST.get("section_id")
        section_type = request.POST.get("section_type")
        location = request.POST.get("location")
        meeting_time = request.POST.get("meeting_time")

        # Validate input and handle section creation
        try:
            # Ensure the course exists
            course = Course.objects.get(course_id=course_id)
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

                if section_type.lower() == "lab":
                    Lab.objects.create(section=section)
                elif section_type.lower() == "lecture":
                    Lecture.objects.create(section=section)

                messages.success(request, f"{section_type} section created successfully.")
        except Course.DoesNotExist:
            messages.error(request, "Course ID does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'create_section.html', {"user": request.user})


def forgot_password(request):
    error = None

    # Hardcoded answers for security questions
    security_questions = {
        "question_1": "university of wisconsin milwaukee",
        "question_2": "rock",
        "question_3": "django",
    }

    if request.method == "POST":
        if "username" in request.POST and "answer_1" in request.POST:
            # Step 1: Validate security questions
            username = request.POST.get("username", "").strip()
            answer_1 = request.POST.get("answer_1", "").strip().lower()
            answer_2 = request.POST.get("answer_2", "").strip().lower()
            answer_3 = request.POST.get("answer_3", "").strip().lower()

            if (
                answer_1 == security_questions["question_1"] and
                answer_2 == security_questions["question_2"] and
                answer_3 == security_questions["question_3"]
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
