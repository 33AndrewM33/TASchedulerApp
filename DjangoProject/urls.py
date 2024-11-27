"""
URL configuration for DjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from TAScheduler import views  # Import your custom views
from TAScheduler.views import Edit_Course, LoginManagement, LogoutManagement, CourseCreation


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginManagement.as_view(), name='login'),  # Login page
    path('logout/', LogoutManagement.as_view(), name='logout'),  # Logout page

    # Home and Dashboard
    path('home/', lambda request: render(request, 'home.html'), name='home'),  # Proper view for home
    path('home/managecourse/', CourseCreation.as_view(), name='manage_course'),
    path('home/managecourse/create/', CourseCreation.as_view(), name='course-create'),
    path('home/managesection/', lambda request: render(request, 'section_list.html'), name='manage_section'),
    path('home/managesection/create/', lambda request: render(request, 'create_section.html'), name='create_section'),

    # Course Editing and Creation
    path("courses/<str:course_id>/edit/", Edit_Course.as_view(), name="edit-course"),
    path('courses/create/', CourseCreation.as_view(), name='course-create'),  # Alias for course creation
    path('courses/', CourseCreation.as_view(), name='course-list'),  # List of courses
]
    

