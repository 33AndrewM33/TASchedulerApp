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
from django.urls import path
from TAScheduler import views  # Import your custom views
from TAScheduler.views import Edit_Course, LoginManagement, LogoutManagement, CourseCreation


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginManagement.as_view(), name='login'),  # Class-based login view
    path('logout/', LogoutManagement.as_view(), name='logout'),  # Class-based logout view
    path('home/', lambda request: None, name='manage_account'),
    path('home/managecourse/', lambda request: None, name='manage_course'),
    path('home/managesection/', lambda request: None, name='manage_section'),
    path('home/managesection/create/', lambda request: None, name='create_section'),
    path('home/managecourse/create/', CourseCreation.as_view(), name='course-create'),
    path('home/managecourse/list/', CourseCreation.as_view(), name='course-list'),
    path("courses/<str:course_id>/edit/", Edit_Course.as_view(), name="edit-course"),
]
