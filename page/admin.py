from django.contrib import admin
from .models import Sport, ProfileSport, PageCalendar, Location, CoachLocation, Availability, Package, Attendee, Event, EventAttendee, AttendeeParent

# Register your models here.
admin.site.register(Sport)
admin.site.register(ProfileSport)
admin.site.register(PageCalendar)
admin.site.register(Location)
admin.site.register(CoachLocation)
admin.site.register(Availability)
admin.site.register(Package)
admin.site.register(Attendee)
admin.site.register(Event)
admin.site.register(EventAttendee)
admin.site.register(AttendeeParent)