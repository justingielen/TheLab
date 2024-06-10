from django.contrib import admin
from .models import EventAttendee, AttendeeParent

# Register your models here.
admin.site.register(EventAttendee)
admin.site.register(AttendeeParent)