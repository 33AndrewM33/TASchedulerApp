from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages  # Import messages framework
from django.contrib.auth.decorators import login_required
from TAScheduler.models import Course, Section, Lab, Lecture  # Import your models


@login_required
def manage_course(request):
    # Add logic for managing courses here.
    return render(request, 'manage_course.html', {"user": request.user})


@login_required
def manage_section(request):
    # Add logic for managing sections here.
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


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('/home/')
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/home/')  # Redirect to home page after successful login
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})


def custom_logout(request):
    logout(request)
    return redirect('/')  # Redirect to login page


@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect('/')  # Redirect to login page if user is not authenticated

    # Clear any lingering messages
    messages.get_messages(request)

    return render(request, 'home.html', {"user": request.user})


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
