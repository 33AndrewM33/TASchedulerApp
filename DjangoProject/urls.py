from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from TAScheduler import views  # Import your custom views
from TAScheduler.views import AccountCreation, AssignTAToLabView, AssignTAToLectureView, DeleteCourseView, EditCourse, LoginManagement, LogoutManagement, CourseCreation


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
    path("courses/<str:course_id>/edit/", EditCourse.as_view(), name="edit-course"),
    path('courses/create/', CourseCreation.as_view(), name='course-create'),  # Alias for course creation
    path('courses/', CourseCreation.as_view(), name='course-list'),  # List of courses


    path("create-account/", AccountCreation.as_view(), name="create-account"),
    path("labs/<int:lab_id>/assign-ta/", AssignTAToLabView.as_view(), name="assign-ta-to-lab"),
    path("lectures/<int:lecture_id>/assign-ta/", AssignTAToLectureView.as_view(), name="assign-ta-to-lecture"),
    path("labs/", lambda request: render(request, "lab_list.html"), name="lab-list"),
    path("lectures/", lambda request: render(request, "lecture_list.html"), name="lecture-list"),
    path('courses/<int:pk>/delete/', DeleteCourseView.as_view(), name='course-delete'),
]

    

