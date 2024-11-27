from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from TAScheduler import views  # Import your custom views
from TAScheduler.views import Edit_Course, LoginManagement, LogoutManagement, CourseCreation


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.custom_login, name='login'),  # Root path for login page
    path('logout/', views.custom_logout, name='logout'),  # Optional custom logout
    path('home/', lambda request: None, name='manage_account'), #Changed from /home/manage_account
    path('home/managecourse/', lambda request: None, name='manage_course'),
    path('home/managesection/', lambda request: None, name='manage_section'),
    path('home/managesection/create/', lambda request: None, name='create_section'),
]
