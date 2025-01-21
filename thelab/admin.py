from django.contrib import admin
from .models import User, UserRelation, Notification, Application 

admin.site.register(User)
admin.site.register(UserRelation)
admin.site.register(Notification)
admin.site.register(Application)