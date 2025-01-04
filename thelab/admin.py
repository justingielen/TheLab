from django.contrib import admin
from .models import User, Profile, ProfileUser, Notification, Application 
from .models import HomeCalendar

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(ProfileUser)
admin.site.register(Notification)
admin.site.register(Application)
admin.site.register(HomeCalendar)