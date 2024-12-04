from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from TAScheduler.models import Course, Section, Lab, Lecture, TA, Instructor, Administrator, User
from django.core.exceptions import PermissionDenied

# ----------------------------------------
# Section Management Views
# ----------------------------------------

@login_required
def manage_section(request):
    # Restrict access to admins and instructors
    # This ensures that only users with sufficient roles (admin or instructor) can access the page.
    # TAs or unauthorized users will receive a 403 Forbidden error.
    if not (request.user.is_admin or request.user.is_instructor):
        raise PermissionDenied  # Return 403 Forbidden
        # Get the course_id from the request (assuming you pass this in POST or GET request)
    course_id = request.POST.get('course_id') or request.GET.get('course_id')
    
    # Handle course_id validation

    if course_id:
        try:
            course = Course.objects.get(course_id=course_id)
        except Course.DoesNotExist:
            messages.error(request, "Course ID does not exist.")
            return render(request, 'manage_section.html', {"user": request.user, "sections": sections})

    sections = Section.objects.select_related('course').all()
    section_type = request.GET.get('type')
    search_query = request.GET.get('search', '')

    if section_type == "Lab":
        sections = sections.filter(labs__isnull=False)
    elif section_type == "Lecture":
        sections = sections.filter(lectures__isnull=False)

    # This code provides a search filter that allows users to filter sections based on the location
    if search_query:  # Filter sections by search query
        sections = sections.filter(location__icontains=search_query)

    return render(request, 'manage_section.html', {"user": request.user, "sections": sections})

@login_required
def create_section(request):
    
    if not (request.user.is_admin or request.user.is_instructor):
        raise PermissionDenied  # Allow only admins and instructors


    if request.method == "POST":
        course_id = request.POST.get("course_id")
        section_id = request.POST.get("section_id")
        section_type = request.POST.get("section_type")
        location = request.POST.get("location")
        meeting_time = request.POST.get("meeting_time")

        # Ensure course_id is provided; avoid processing without it
        if not course_id:
            messages.error(request, "Invalid course ID. Please select a valid course.")
            return render(request, 'create_section.html', {"user": request.user, "courses": Course.objects.all()})

        # Validate all required fields to ensure no missing data
        if not course_id or not section_id or not section_type or not location or not meeting_time:
            messages.error(request, "All fields are required.")
            return render(request, 'create_section.html', {"user": request.user, "courses": Course.objects.all()})


        # Convert section_id to integer and handle invalid formats
        try:
            section_id = int(section_id)
        except ValueError:
            messages.error(request, "Section ID must be a valid number.")
            return render(request, 'create_section.html', {"user": request.user, "courses": Course.objects.all()})

        # Check if the provided course_id corresponds to an existing course
        try:
            course = Course.objects.get(course_id=course_id)
        except Course.DoesNotExist:
            messages.error(request, "Invalid course ID.")
            return render(request, 'create_section.html', {"user": request.user, "courses": Course.objects.all()})

        # Prevent duplicate section IDs for the same course
        if Section.objects.filter(section_id=section_id, course=course).exists():
            print(f"Duplicate section ID detected for section_id {section_id} in course {course.course_id}")
            messages.error(request, "Section with this ID already exists.")
            return render(request, 'create_section.html', {"user": request.user, "courses": Course.objects.all()})
        
        # Ensure the number of sections does not exceed the course's limit
        if course.sections.count() >= course.num_of_sections:
            messages.error(request, "The course has reached its maximum number of sections.")
            return render(request, 'create_section.html', {"user": request.user, "courses": Course.objects.all()})





        # Create the section and associate it with the course
        section = Section.objects.create(
            section_id=section_id,
            course=course,
            location=location,
            meeting_time=meeting_time,
        )

        # Create either a Lab or Lecture object based on the section type
        if section_type == "Lab":
            Lab.objects.create(section=section)
        elif section_type == "Lecture":
            Lecture.objects.create(section=section)

        # Notify the user of the successful section creation
        messages.success(request, f"{section_type} section created successfully.")
        return redirect('manage_section')  # Redirect to section management after success

    # Render the form with a list of all courses for selection
    courses = Course.objects.all()
    return render(request, 'create_section.html', {"user": request.user, "courses": courses})

@login_required
def edit_section(request, section_id):
    # Restrict access to only instructors and admins
    if not (request.user.is_admin or request.user.is_instructor):  # Added this check for access restriction
        raise PermissionDenied  # Return 403 Forbidden for unauthorized access

    section = get_object_or_404(Section, id=section_id)

    if request.method == "POST":
        location = request.POST.get("location", "").strip()  # Added `.strip()` to remove leading/trailing spaces
        meeting_time = request.POST.get("meeting_time", "").strip()  # Added `.strip()` for consistency

        # Validate required fields and provide specific error messages
        if not location:  # Added validation for location
            messages.error(request, "Location is required.")
        if not meeting_time:  # Added validation for meeting time
            messages.error(request, "Meeting time is required.")

        # If there are any errors, re-render the form with the current values
        if not location or not meeting_time:  # Prevent saving if fields are missing
            return render(request, 'edit_section.html', {  # Re-render the form with error messages
                "user": request.user,
                "section": section,
                "tas": TA.objects.all(),
                "instructors": Instructor.objects.all(),
            })

        # Update section fields
        section.location = location
        section.meeting_time = meeting_time
        section.save()

        # Handle optional assignments
        assigned_ta = request.POST.get("assigned_ta")
        assigned_instructor = request.POST.get("assigned_instructor")

        if assigned_ta:
            ta = get_object_or_404(TA, user__id=assigned_ta)
            section.labs.update(ta=ta)

        if assigned_instructor:
            instructor = get_object_or_404(Instructor, user__id=assigned_instructor)
            section.lectures.update(instructor=instructor)

        messages.success(request, f"Section {section.section_id} updated successfully.")
        return redirect('manage_section')

    return render(request, 'edit_section.html', {
        "user": request.user,
        "section": section,
        "tas": TA.objects.all(),
        "instructors": Instructor.objects.all()
    })

@login_required
def delete_section(request, section_id):
    if not request.user.is_admin:
        raise PermissionDenied  # Added a check to ensure only admin users can delete sections

    try:
        section = Section.objects.get(id=section_id)  # Changed from `get_object_or_404` to `Section.objects.get`
        section.delete()
        messages.success(request, f"Section {section.section_id} deleted successfully.")
    except Section.DoesNotExist:
        messages.error(request, "Section not found.")  # Added a specific error message for non-existent sections
        return redirect('manage_section')  # Added redirection to manage_section after this exception
    except Exception as e:
        messages.error(request, f"Error deleting section: {str(e)}")
        return redirect('manage_section')  # Added redirection to manage_section after catching a general exception

    return redirect('manage_section')




# ----------------------------------------
# Course Management Views
# ----------------------------------------

@login_required
def manage_course(request):
    courses = Course.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(name__icontains=search_query)
    semester_filter = request.GET.get('semester', '')
    if semester_filter:
        courses = courses.filter(semester__icontains=semester_filter)
    modality_filter = request.GET.get('modality', '')
    if modality_filter:
        courses = courses.filter(modality=modality_filter)
    return render(request, 'manage_course.html', {"courses": courses})

@login_required
def create_course(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        name = request.POST.get("name")
        semester = request.POST.get("semester")
        description = request.POST.get("description")
        modality = request.POST.get("modality")
        num_of_sections = request.POST.get("num_of_sections")
        try:
            if Course.objects.filter(course_id=course_id).exists():
                messages.error(request, "A course with this ID already exists.")
                return redirect('create_course')
            Course.objects.create(
                course_id=course_id,
                name=name,
                semester=semester,
                description=description,
                modality=modality,
                num_of_sections=num_of_sections,
            )
            messages.success(request, f"Course '{name}' created successfully.")
            return redirect('manage_course')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    return render(request, 'create_course.html')

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    if request.method == "POST":
        course.name = request.POST.get("name")
        course.semester = request.POST.get("semester")
        course.description = request.POST.get("description")
        course.modality = request.POST.get("modality")
        course.num_of_sections = request.POST.get("num_of_sections")
        course.save()
        messages.success(request, f"Course '{course.name}' updated successfully.")
        return redirect('manage_course')
    return render(request, 'edit_course.html', {"course": course})

@login_required
def delete_course(request, course_id):
    try:
        course = get_object_or_404(Course, course_id=course_id)
        course.delete()
        messages.success(request, f"Course '{course.name}' deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting course: {str(e)}")
    return redirect('manage_course')

# ----------------------------------------
# Account Management Views
# ----------------------------------------

@login_required
def account_management(request):
    editing_user = None
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            role = request.POST.get("role")
            try:
                new_user = User.objects.create(
                    username=username,
                    email=email,  # Ensure email is used
                    password=make_password(password)
                )
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
            user_id = request.POST.get("user_id")
            try:
                user_to_delete = get_object_or_404(User, id=user_id)
                user_to_delete.delete()
                messages.success(request, f"User '{user_to_delete.username}' deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting user: {str(e)}")
        elif action == "edit":
            user_id = request.POST.get("user_id")
            editing_user = get_object_or_404(User, id=user_id)
        elif action == "update":
            user_id = request.POST.get("editing_user_id")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            role = request.POST.get("role")
            try:
                user_to_update = get_object_or_404(User, id=user_id)
                user_to_update.username = username
                user_to_update.email = email  # Ensure email is updated
                if password:
                    user_to_update.password = make_password(password)
                user_to_update.is_ta = False
                user_to_update.is_instructor = False
                user_to_update.is_admin = False
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
    users = User.objects.all()
    return render(request, 'account_management.html', {"users": users, "editing_user": editing_user})
# ----------------------------------------
# Authentication Views
# ----------------------------------------

def assign_user_role(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'assign_role.html', {'user': user})

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
            return redirect('/home/')
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})

def custom_logout(request):
    logout(request)
    return redirect('/')

@login_required
def home(request):
    storage = messages.get_messages(request)
    storage.used = True

    # Check user role and display appropriate message
    if request.user.is_ta:
        message = f"Welcome TA {request.user.username}! This page will display the lab assignments that will be developed in Sprint 2."
        show_navigation = False  # Hide navigation for TA
    elif request.user.is_instructor:
        message = f"Welcome Instructor {request.user.username}! This page will display the courses assigned to you by the admin and the sections you're in."
        show_navigation = False  # Hide navigation for Instructor
    else:
        message = "Welcome Admin! You have full access to manage the system."
        show_navigation = True  # Show navigation for Admin

    return render(request, 'home.html', {
        "user": request.user,
        "message": message,
        "show_navigation": show_navigation
    })

def forgot_password(request):
    error = None
    security_questions = {
        "question_1": "university of wisconsin milwaukee",
        "question_2": "rock",
        "question_3": "django",
    }
    if request.method == "POST":
        if "username" in request.POST and "answer_1" in request.POST:
            username = request.POST.get("username", "").strip()
            answer_1 = request.POST.get("answer_1", "").strip().lower()
            answer_2 = request.POST.get("answer_2", "").strip().lower()
            answer_3 = request.POST.get("answer_3", "").strip().lower()
            if (
                answer_1 == security_questions["question_1"] and
                answer_2 == security_questions["question_2"] and
                answer_3 == security_questions["question_3"]
            ):
                request.session['valid_user'] = username
                return render(request, "reset_password.html")
            else:
                error = "One or more answers were incorrect. Please try again."
        elif "new_password" in request.POST and "confirm_password" in request.POST:
            username = request.session.get('valid_user', None)
            if username:
                new_password = request.POST.get("new_password", "")
                confirm_password = request.POST.get("confirm_password", "")
                if new_password == confirm_password:
                    try:
                        user = User.objects.get(username=username)
                        user.password = make_password(new_password)
                        user.save()
                        messages.success(request, "Password reset! Log in with your new password.")
                        return redirect('/')
                    except User.DoesNotExist:
                        error = "User not found. Please start again."
                else:
                    error = "Passwords do not match. Try again."
                    return render(request, "reset_password.html", {"error": error})
            else:
                error = "Session expired. Start again."
    return render(request, "forgot_password.html", {"error": error})

@login_required
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")
        user_to_edit.username = username
        user_to_edit.email = email
        if password:
            user_to_edit.password = make_password(password)
        user_to_edit.is_ta = role == "ta"
        user_to_edit.is_instructor = role == "instructor"
        user_to_edit.is_admin = role == "administrator"
        user_to_edit.save()
        if role == "ta":
            if not hasattr(user_to_edit, "ta_profile"):
                TA.objects.create(user=user_to_edit, grader_status=False)
            else:
                ta_profile = user_to_edit.ta_profile
                ta_profile.grader_status = ta_profile.grader_status or False
                ta_profile.save()
        elif role == "instructor":
            if not hasattr(user_to_edit, "instructor_profile"):
                Instructor.objects.create(user=user_to_edit)
        elif role == "administrator":
            if not hasattr(user_to_edit, "administrator_profile"):
                Administrator.objects.create(user=user_to_edit)
        messages.success(request, f"User '{username}' updated successfully.")
        return redirect("account_management")
    context = {
        "user_to_edit": user_to_edit,
        "roles": ["ta", "instructor", "administrator"],
    }
    return render(request, "edit_user.html", context)