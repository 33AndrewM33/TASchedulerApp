from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from TAScheduler import views
from TAScheduler.views import (
    AccountCreation, AssignTAToLabView, AssignTAToLectureView, CourseCreation, 
    CourseManagement, CreateSectionView, DeleteCourseView, EditCourse, EditSectionView, LoginManagement, 
    LogoutManagement, SectionCreation, SectionManagement, AccountManagement
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginManagement.as_view(), name='login'),  # Login page
    path('logout/', LogoutManagement.as_view(), name='logout'),  # Logout page

    # Home and Dashboard
    path('home/', lambda request: render(request, 'home.html'), name='home'),  # Home page
    path('home/managecourse/', CourseManagement.as_view(), name='manage_course'),  # Course management
    path('home/managesection/', SectionManagement.as_view(), name='manage_section'),  # Section management
    path("home/managesection/create/", CreateSectionView.as_view(), name="create_section"),

    path("edit_section/<int:section_id>/", EditSectionView.as_view(), name="edit_section"),
    path("delete_section/<int:section_id>/", views.delete_section, name="delete_section"),

    # Course Editing and Creation
    path("home/managecourse/edit/<str:course_id>/", EditCourse.as_view(), name="edit_course"),
    path('courses/create/', CourseCreation.as_view(), name='course-create'),  # Create course
    path('courses/', CourseCreation.as_view(), name='course-list'),  # List courses
    path('courses/<int:pk>/delete/', DeleteCourseView.as_view(), name='course-delete'),  # Delete course

    # TA and Lecture Management
    path("labs/<int:lab_id>/assign-ta/", AssignTAToLabView.as_view(), name="assign-ta-to-lab"),
    path("lectures/<int:lecture_id>/assign-ta/", AssignTAToLectureView.as_view(), name="assign-ta-to-lecture"),
    path("labs/", lambda request: render(request, "lab_list.html"), name="lab-list"),
    path("lectures/", lambda request: render(request, "lecture_list.html"), name="lecture-list"),

    # Account Management
    path("create-account/", AccountCreation.as_view(), name="create-account"),
    path('home/accountmanagement/', AccountManagement.as_view(), name='account_management'),
    path("home/accountmanagement/edit/<int:user_id>/", views.edit_user, name="edit_user"),  # Edit user

    # Forgot Password
    path('forgot_password/', views.forgot_password, name='forgot_password'),
]
