from django.contrib import admin
from TAScheduler.models import User, TA, Instructor, Course, Section, Lab, Lecture, Administrator

# Registering models for the admin interface
admin.site.register(User)
admin.site.register(TA)
admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Lab)
admin.site.register(Lecture)
admin.site.register(Administrator)
