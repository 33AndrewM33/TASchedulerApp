from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from TAScheduler.models import Course, Section, Lab, Lecture, TA, Instructor, Administrator, User


@login_required
def manage_course(request):
    # Add logic for managing courses here
    return render(request, 'manage_course.html', {"user": request.user})


@login_required
def manage_section(request):
    if request.method == "POST":
        section_id = request.POST.get("section_id")
        action = request.POST.get("delete")  # Check if "delete" action is triggered

        if action == "Delete":
            try:
                # Fetch the section
                section = Section.objects.get(section_id=section_id)
                section.delete()  # Delete the section
                messages.success(request, "Successfully Deleted Section")
            except Section.DoesNotExist:
                messages.error(request, "Section not found.")
            except Exception as e:
                messages.error(request, f"Failed to delete section: {str(e)}")

    # Fetch all sections to display on the page
    sections = Section.objects.all()
    return render(request, 'manage_section.html', {"user": request.user, "sections": sections})


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


@login_required
def account_management(request):
    editing_user = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            # Handle user creation
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            role = request.POST.get("role")

            try:
                # Create the base user
                new_user = User.objects.create(
                    username=username,
                    email_address=email,
                    password=make_password(password)
                )

                # Assign role-specific attributes
                if role == "ta":
                    new_user.is_ta = True
                    TA.objects.create(user=new_user)
                elif role == "instructor":
                    new_user.is_instructor = True
                    Instructor.objects.create(user=new_user)
                elif role == "administrator":
                    new_user.is_admin = True
                    Administrator.objects.create(user=new_user)
                new_user.save()

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

        elif action == "edit":
            # Load user data for editing
            user_id = request.POST.get("user_id")
            editing_user = get_object_or_404(User, id=user_id)

        elif action == "update":
            # Handle updating user information
            user_id = request.POST.get("editing_user_id")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            role = request.POST.get("role")

            try:
                user_to_update = get_object_or_404(User, id=user_id)
                user_to_update.username = username
                user_to_update.email_address = email

                # Update password only if provided
                if password:
                    user_to_update.password = make_password(password)

                # Reset roles
                user_to_update.is_ta = False
                user_to_update.is_instructor = False
                user_to_update.is_admin = False

                # Assign new role
                if role == "ta":
                    user_to_update.is_ta = True
                    if not hasattr(user_to_update, "ta_profile"):
                        TA.objects.create(user=user_to_update)
                elif role == "instructor":
                    user_to_update.is_instructor = True
                    if not hasattr(user_to_update, "instructor_profile"):
                        Instructor.objects.create(user=user_to_update)
                elif role == "administrator":
                    user_to_update.is_admin = True
                    if not hasattr(user_to_update, "administrator_profile"):
                        Administrator.objects.create(user=user_to_update)

                user_to_update.save()
                messages.success(request, f"User '{username}' updated successfully.")
            except Exception as e:
                messages.error(request, f"Error updating user: {str(e)}")

    # Retrieve all users to display
    users = User.objects.all()
    return render(request, 'account_management.html', {"users": users, "editing_user": editing_user})


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

@login_required
def edit_user(request, user_id):
    # Fetch the user to edit
    user_to_edit = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        # Get updated data from the form
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        # Update user fields
        user_to_edit.username = username
        user_to_edit.email_address = email

        # Update the password if provided
        if password:
            user_to_edit.password = make_password(password)

        # Update roles
        user_to_edit.is_ta = role == "ta"
        user_to_edit.is_instructor = role == "instructor"
        user_to_edit.is_admin = role == "administrator"
        user_to_edit.save()

        # Update role-specific models
        if role == "ta":
            # Handle TA creation or update
            if not hasattr(user_to_edit, "ta_profile"):
                TA.objects.create(user=user_to_edit, grader_status=False)  # Default grader_status to False
            else:
                ta_profile = user_to_edit.ta_profile
                ta_profile.grader_status = ta_profile.grader_status or False  # Ensure grader_status is set
                ta_profile.save()
        elif role == "instructor":
            if not hasattr(user_to_edit, "instructor_profile"):
                Instructor.objects.create(user=user_to_edit)
        elif role == "administrator":
            if not hasattr(user_to_edit, "administrator_profile"):
                Administrator.objects.create(user=user_to_edit)

        messages.success(request, f"User '{username}' updated successfully.")
        return redirect("account_management")  # Redirect back to account management

    # Pass current user info to the template
    context = {
        "user_to_edit": user_to_edit,
        "roles": ["ta", "instructor", "administrator"],
    }
    return render(request, "edit_user.html", context)