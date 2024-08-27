from django.contrib import admin
from .models import Sport, ProfileSport, Location, CoachLocation, Package, Event, PageCalendar, Occurrence

# Register your models here.
admin.site.register(Sport)
admin.site.register(ProfileSport)
admin.site.register(Location)
admin.site.register(CoachLocation)
admin.site.register(Package)
admin.site.register(Event)
admin.site.register(PageCalendar)
admin.site.register(Occurrence)