from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from TAScheduler.models import Course

def custom_login(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/home/manageaccount/')  # Redirect to a placeholder after successful login
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})

def custom_logout(request):
    logout(request)
    return redirect('/')


@login_required
def course_create(request):
    # Check if the logged-in user is an admin or instructor
    if not (request.user.is_admin or request.user.is_instructor):
        return HttpResponseForbidden("You do not have permission to create a course.")

    if request.method == "POST":
        # Extract data from the POST request
        course_id = request.POST.get("course_id")
        semester = request.POST.get("semester")
        name = request.POST.get("name")
        description = request.POST.get("description")
        num_of_sections = request.POST.get("num_of_sections")
        modality = request.POST.get("modality")

        # Create the course
        course = Course.objects.create(
            course_id=course_id,
            semester=semester,
            name=name,
            description=description,
            num_of_sections=num_of_sections,
            modality=modality,
        )

        # Redirect or render a success message
        return redirect("course-list")  # Replace with your actual course list view

    return render(request, "course_create.html")