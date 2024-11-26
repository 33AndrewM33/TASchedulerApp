from django.contrib import admin
from django.urls import path
from TAScheduler import views  # Import your custom views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('', views.custom_login, name='login'),  # Root path for login page
    path('logout/', views.custom_logout, name='logout'),  # Logout
    path('home/', views.home, name='home'),  # Home page
    path('home/managecourse/', views.manage_course, name='manage_course'),  # Manage courses
    path('home/managesection/', views.manage_section, name='manage_section'),  # Manage sections
    path('home/managesection/create/', views.create_section, name='create_section'),  # Create section
    path('forgot_password/', views.forgot_password, name='forgot_password'),  # Forgot password
]
