from django.contrib import admin
from .models import User, Profile, ProfileUser, Notification, HomeCalendar, Application

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(ProfileUser)
admin.site.register(HomeCalendar)
admin.site.register(Notification)
admin.site.register(Application)