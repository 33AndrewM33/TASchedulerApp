from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings  # Added

import random
import string

from TAScheduler.models import Course, Section, Lab, Lecture, TA, Instructor, Administrator, User, Notification


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

                # Notify admins about the new section
                Notification.notify_admin_on_section_creation(section, request.user)

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
            course = Course.objects.create(
                course_id=course_id,
                name=name,
                semester=semester,
                description=description,
                modality=modality,
                num_of_sections=num_of_sections,
            )
            # Notify admins about the new course
            Notification.notify_admin_on_course_creation(course, request.user)

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
            first_name = request.POST.get("first_name")  # Added first name
            last_name = request.POST.get("last_name")    # Added last name
            try:
                new_user = User.objects.create(
                    username=username,
                    email=email,

                    password=make_password(password),
                    first_name=first_name,  # Assigning first name
                    last_name=last_name,    # Assigning last name


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

                # Notify admins about the new account
                Notification.notify_admin_on_account_creation(new_user, request.user)

                messages.success(request, f"User '{username}' created successfully.")
            except Exception as e:
                messages.error(request, f"Error creating user: {str(e)}")
        elif action == "delete":
            user_id = request.POST.get("user_id")
            try:
                user_to_delete = get_object_or_404(User, id=user_id)

                # Notify admins about the account deletion
                Notification.notify_admin_on_account_deletion(user_to_delete, request.user)

                user_to_delete.delete()
                messages.success(request, f"User '{user_to_delete.username}' deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting user: {str(e)}")
    users = User.objects.all()
    courses = Course.objects.all()  # Fetch all courses for assignment dropdown
    return render(request, "account_management.html", {
        "users": users,
        "courses": courses,
    })
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
    if request.user.is_admin:
        # Admin-specific home page
        unread_notifications_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()

        notifications = Notification.objects.filter(recipient=request.user, is_read=False)

        return render(request, 'home_admin.html', {
            "user": request.user,
            "notifications": notifications,
            "unread_notifications_count": unread_notifications_count  # Add count here
        })
    elif request.user.is_instructor:
        # Redirect to instructor home page
        return redirect('home_instructor')
    elif request.user.is_ta:
        # Redirect to TA home page
        return redirect('home_ta')
    else:
        # If no role is assigned, redirect to login with an error
        messages.error(request, "Invalid user role.")
        return redirect('login')


def clear_notifications(request):
    if request.method == "POST":
        # Clear notifications for the current admin
        Notification.objects.filter(recipient=request.user).delete()
        messages.success(request, "All notifications cleared successfully.")
    return redirect('home')

@login_required
def home_instructor(request):
    return render(request, 'home_instructor.html', {
        "user": request.user,
        "message": "Welcome to the Instructor Dashboard! Placeholder content here.",
    })



def clear_notifications(request):
    if request.method == "POST":
        # Clear notifications for the current admin
        Notification.objects.filter(recipient=request.user).delete()
        messages.success(request, "All notifications cleared successfully.")
    return redirect('home')

@login_required
def home_instructor(request):
    if not request.user.is_instructor:
        return redirect('home')  # Redirect if the user is not an instructor

    # Fetch notifications for the instructor
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    unread_notifications_count = unread_notifications.count()

    return render(request, 'home_instructor.html', {
        "user": request.user,
        "notifications": unread_notifications,
        "unread_notifications_count": unread_notifications_count,
        "message": "Welcome to the Instructor Dashboard!",
    })


@login_required
def home_ta(request):
    return render(request, 'home_ta.html', {
        "user": request.user,
        "message": "Welcome to the TA Dashboard! Placeholder content here.",
    })

def forgot_password(request):
    error = None
    success_message = None  # Added to store the success message
    security_questions = {
        "question_1": "university of wisconsin milwaukee",
        "question_2": "rock",
        "question_3": "django",
    }

    if request.method == "POST":
        # Handle temporary password request
        if "temp_password" in request.POST:
            username = request.POST.get("temp_username", "")
            email = request.POST.get("temp_email", "")
            try:
                print(username, email)
                user = User.objects.get(username=username, email=email)
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                user.set_password(temp_password)
                user.is_temporary_password = True
                user.save()
                success_message = "Temporary password sent to your email!"
                send_mail(
                    subject="Your Temporary Password",
                    message=f"Your temporary password is: {temp_password}\nPlease change your password after logging in.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                )

            except(User.DoesNotExist):
                error = "User not found or email does not match."

        # Handle reset password via security questions
        elif "username" in request.POST and "answer_1" in request.POST:
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

    # Handle actual password reset
    if request.method == "POST" and "new_password" in request.POST:
        username = request.session.get('valid_user')
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if username and new_password == confirm_password:
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.is_temporary_password = False  # Reset the flag
                user.save()
                del request.session['valid_user']  # Clear session after success

                # Notify admins about the password reset
                admins = User.objects.filter(is_admin=True)
                for admin in admins:
                    Notification.objects.create(
                        sender=user,
                        recipient=admin,
                        subject="User Password Reset",
                        message=f"The user {user.first_name} {user.last_name} ({user.email}) has successfully reset their password.",
                    )

                success_message = "Password reset successfully! Redirecting to login page..."
                return render(request, "reset_password.html", {"success_message": success_message})
            except User.DoesNotExist:
                error = "User not found. Please start the process again."
        else:
            error = "Passwords do not match. Please try again."

    return render(request, "forgot_password.html", {
        "error": error,
        "success_message": success_message,
    })
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

def send_temp_password(request):
    if request.method == "POST":
        username = request.POST.get("temp-username")
        email = request.POST.get("temp-email")

        user = User.objects.filter(username=username, email=email).first()
        if user:
            # Generate a temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.set_password(temp_password)
            user.save()

            # Send email
            send_mail(
                "Your Temporary Password",
                f"Your temporary password is: {temp_password}\nPlease change your password after logging in.",
                "no-reply@example.com",
                [email],
            )
            return JsonResponse({"message": "Temporary password sent to your email!"}, status=200)
        else:
            return JsonResponse({"message": "User not found or email does not match."}, status=404)

    return JsonResponse({"message": "Invalid request."}, status=400)

@login_required
def assign_instructor_to_course_account_dashboard(request, user_id):
    instructor = get_object_or_404(User, id=user_id, is_instructor=True)

    if request.method == "POST":
        course_id = request.POST.get("course_id")
        if not course_id:
            messages.error(request, "Please select a course.")
            return redirect("account_management")

        course = get_object_or_404(Course, id=course_id)

        # Assign the instructor to the course
        course.instructors.add(instructor.instructor_profile)
        course.save()

        messages.success(request, f"Instructor {instructor.first_name} {instructor.last_name} assigned to course {course.name}.")
        return redirect("account_management")
    return redirect("account_management")

@login_required
def assign_instructors_to_course(request, course_id):
    # Get the course by ID
    course = get_object_or_404(Course, course_id=course_id)

    # Fetch all instructors from the database
    instructors = Instructor.objects.all()

    if request.method == "POST":
        # Get selected instructor IDs from the form
        selected_instructors = request.POST.getlist("instructors")

        # Assign instructors to the course
        new_instructors = Instructor.objects.filter(id__in=selected_instructors)
        course.instructors.set(new_instructors)  # Update course instructors
        course.save()

        # Send notifications to the assigned instructors
        for instructor in new_instructors:
            Notification.objects.create(
                sender=request.user,  # The user assigning the instructors
                recipient=instructor.user,  # The instructor receiving the notification
                subject="Course Assignment Notification",
                message=f"You have been assigned to the course '{course.name}' ({course.course_id})."
            )

        # Add a success message
        messages.success(request, f"Instructors updated for course '{course.name}'. Notifications sent to the assigned instructors.")
        return redirect("manage_course")

    # Render the template with course and instructor data
    return render(request, "assign_instructors.html", {
        "course": course,
        "instructors": instructors,
    })



@login_required
def edit_contact_info(request):
    if not request.user.is_instructor:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        home_address = request.POST.get('home_address')

        # Update user fields
        request.user.email = email
        request.user.phone_number = phone_number
        request.user.home_address = home_address
        request.user.save()

        messages.success(request, "Your contact information has been updated successfully.")
        return redirect('edit_contact_info')

    return render(request, 'edit_contact_info.html', {
        'user': request.user,
    })

@login_required
def view_courses(request):
    if not request.user.is_instructor:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')

    courses = request.user.instructor_profile.courses.all()

    return render(request, 'view_courses.html', {
        'user': request.user,
        'courses': courses,
    })


@login_required
def assign_ta_to_section(request):
    if not request.user.is_instructor:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')

    # Get sections taught by the instructor
    instructor = request.user.instructor_profile
    sections = Section.objects.filter(course__instructors=instructor)

    # Get all TAs
    tas = TA.objects.all()

    # Handle assignment
    if request.method == "POST":
        ta_id = request.POST.get('ta_id')
        section_id = request.POST.get('section_id')

        # Get the TA and Section
        ta = get_object_or_404(TA, id=ta_id)
        section = get_object_or_404(Section, id=section_id)

        # Assign the TA to the section
        section.assigned_tas.add(ta)
        section.save()

        messages.success(request, f"TA {ta.user.first_name} {ta.user.last_name} has been assigned to Section {section.section_id}.")
        return redirect('assign_ta_to_section')

    return render(request, 'assign_ta_to_section.html', {
        'tas': tas,
        'sections': sections,
    })

@login_required
def unassign_ta(request, section_id, ta_id):
    # Check if the user is an instructor
    if not request.user.is_instructor:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')

    # Fetch the section and TA
    section = get_object_or_404(Section, id=section_id)
    ta = get_object_or_404(TA, id=ta_id)

    # Remove the TA from the section's assigned TAs
    section.assigned_tas.remove(ta)
    section.save()

    # Notify the instructor
    messages.success(request, f"TA {ta.user.first_name} {ta.user.last_name} has been unassigned from Section {section.section_id}.")
    return redirect('assign_ta_to_section')

@login_required
def view_public_users(request):
    if not request.user.is_instructor:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')

    # Fetch all users' public information
    users = User.objects.values('first_name', 'last_name', 'email', 'phone_number')

    return render(request, 'view_public_users.html', {
        'users': users,
    })
    
@login_required
def unassign_instructor(request, course_id, instructor_id):
    # Get the course and instructor objects
    course = get_object_or_404(Course, id=course_id)
    instructor = get_object_or_404(Instructor, id=instructor_id)

    if request.method == "POST":  # Ensure it only processes POST requests
        # Remove the instructor from the course
        course.instructors.remove(instructor)
        course.save()

        # Send a notification to the instructor
        Notification.objects.create(
            recipient=instructor.user,
            subject="Unassigned from Course",
            message=f"You have been unassigned from the course '{course.name}' (ID: {course.course_id}).",
            sender=request.user
        )

        # Add a success message
        messages.success(request, f"Instructor {instructor.user.first_name} {instructor.user.last_name} has been unassigned from course {course.name}.")
        return redirect('manage_course')

    # Redirect back if not a POST request
    messages.error(request, "Invalid request method.")
    return redirect('manage_course')
