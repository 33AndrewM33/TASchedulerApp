from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views import View
from TAScheduler.models import Course
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator


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

    
# Utility function for role checking
def is_admin_or_instructor(user):
    return user.is_admin or user.is_instructor


@method_decorator([login_required, user_passes_test(is_admin_or_instructor)], name="dispatch")
class CourseManagement(View):
    def get(self, request):
        # Render a list of courses
        courses = Course.objects.all()
        return render(request, "course_list.html", {"courses": courses})

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