from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from TAScheduler.models import Course, Section, Lab, Lecture, TA, Instructor, Administrator, User

# ----------------------------------------
# Section Management Views
# ----------------------------------------


@login_required
def manage_section(request):
    sections = Section.objects.select_related('course').all()
    section_type = request.GET.get('type')
    if section_type == "Lab":
        sections = sections.filter(labs__isnull=False)
    elif section_type == "Lecture":
        sections = sections.filter(lectures__isnull=False)
    return render(request, 'manage_section.html', {"user": request.user, "sections": sections})

@login_required
def create_section(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        section_id = request.POST.get("section_id")
        section_type = request.POST.get("section_type")
        location = request.POST.get("location")
        meeting_time = request.POST.get("meeting_time")
        try:
            course = Course.objects.get(course_id=course_id)
            if Section.objects.filter(section_id=section_id, course=course).exists():
                messages.error(request, "Section with this ID already exists.")
            else:
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
    courses = Course.objects.all()
    return render(request, 'create_section.html', {"user": request.user, "courses": courses})

@login_required
def edit_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    if request.method == "POST":
        section.location = request.POST.get("location")
        section.meeting_time = request.POST.get("meeting_time")
        section.save()
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
    tas = TA.objects.all()
    instructors = Instructor.objects.all()
    return render(request, 'edit_section.html', {
        "user": request.user,
        "section": section,
        "tas": tas,
        "instructors": instructors
    })

@login_required
def delete_section(request, section_id):
    try:
        section = get_object_or_404(Section, id=section_id)
        section.delete()
        messages.success(request, f"Section {section.section_id} deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting section: {str(e)}")
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
                    email_address=email,
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
                user_to_update.email_address = email
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
    return render(request, 'home.html', {"user": request.user})

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
        user_to_edit.email_address = email
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
