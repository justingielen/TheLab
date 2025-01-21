from django.contrib import admin
from .models import Sport, CoachSport, Location, CoachLocation, Package, PackageLocation, Availability, Attendee, Parent, Event, EventAttendee, AttendeeParent

# Register your models here.
admin.site.register(Sport)
admin.site.register(CoachSport)
admin.site.register(Location)
admin.site.register(CoachLocation)
admin.site.register(Package)
admin.site.register(PackageLocation)
admin.site.register(Availability)
admin.site.register(Attendee)
admin.site.register(Parent)
admin.site.register(Event)
admin.site.register(EventAttendee)
admin.site.register(AttendeeParent)