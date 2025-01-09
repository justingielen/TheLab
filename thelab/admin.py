from django.contrib import admin
from .models import User, UserRelation, Notification, Application 
from .models import HomeCalendar

admin.site.register(User)
admin.site.register(UserRelation)
admin.site.register(Notification)
admin.site.register(Application)
admin.site.register(HomeCalendar)