from django.db import models
from django.urls import reverse
from schedule.models import Event as BaseEvent
from schedule.models import Calendar as BaseCalendar
from django.conf import settings
from datetime import timedelta
    
class Sport(models.Model):
    sport = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.sport

class CoachSport(models.Model):
    coach = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.coach} - {self.sport}"
    
class PageCalendar(BaseCalendar):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        self.name = f"Page Calendar for {self.user.username}"
        # Customize slug generation to ensure uniqueness
        self.slug = f"page_calendar_{self.user.username}"
        super().save(*args, **kwargs)
              
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    LOCATION_TYPES = (
        ('in-person', 'In Person'),
        ('virtual', 'Virtual'),
    )
    type = models.CharField(max_length=20, choices=LOCATION_TYPES)
    hyperlink = models.CharField(max_length=255, blank=True, null=True)
    
    # For this, consider Django's GIS (PointField) framework or a library like Google Places
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return self.name
    
class LocationSport(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

class CoachLocation(models.Model):
    coach = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.coach} - {self.location}"
    
days_of_the_week = {
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    }

class Availability(BaseEvent):
    '''''
    From django-scheduler (thelab > lib > schedule > models > events.py):

    start, end, title, description, creator (fk --> django_settings.AUTH_USER_MODEL), created_on, updated_on, rule (fk), end_recurring_period, calendar (fk), 
    '''''
    day = models.CharField(max_length=10,choices=days_of_the_week)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.creator} ({self.day}): {self.start.time()} - {self.end.time()}"
    
package_types = {
        ('Training','Training'),
        ('P(r)ep Talk','P(r)ep Talk'),
    }

class Package(models.Model):
    type = models.CharField(max_length=20, choices=package_types)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    duration = models.DurationField(default=timedelta(minutes=60))
    athletes = models.IntegerField(default=1)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, default=1)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner} - {self.type} ({self.athletes}): ${self.price}"
    
class PackageLocation(models.Model):
    package =  models.ForeignKey(Package, on_delete=models.CASCADE)   
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.package} @ {self.location}"

# Attendee model, to let parents sign their kids up for events without making accounts for them
class Attendee(models.Model):
    first_name = models.CharField(max_length=50, help_text="(athlete's first name)")
    last_name = models.CharField(max_length=100, help_text="(athlete's last name)")
    age = models.IntegerField()
    attendee_notes = models.TextField(blank=True)

    def __str__(self):
        try:
            return f'{self.user.first_name} {self.user.last_name}'
        except: 
            return f'{self.first_name} {self.last_name}'

class Parent(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    # phone = models.ForeignKey

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Event(BaseEvent):
    '''''
    From django-scheduler (thelab > lib > schedule > models > events.py):

    start, end, title, description, creator (fk --> django_settings.AUTH_USER_MODEL), created_on, updated_on, rule (fk), end_recurring_period, calendar (fk), 
    '''''
    EVENT_TYPES = (
        ('camp', 'Camp'),
        ('clinic', 'Clinic'),
        ('training', 'Training'),
    )
    event_type = models.CharField(max_length=255, choices=EVENT_TYPES)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, help_text="(Note: locations must be added to your Profile before they can be used in an Event)")
    location_notes = models.CharField(max_length=255,blank=True, help_text="(e.g., 'Field 3', or 'Auxiliary Gym')")
    is_accepted = models.BooleanField(default=True)
    max_attendance = models.IntegerField(default=100)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,help_text='(optional)') # maybe IntegerField(1000),null=True,blank=True... in order to deal with Stripe's API better

    def __str__(self):
        return f'{self.title} - {self.location} - ({self.price})'
    
    def get_absolute_url(self):
        return reverse('view_event', kwargs={'pk':self.pk})
    
class EventSport(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.event.title} - {self.sport}"
    
class EventAttendee(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.attendee} -- {self.event.title}'
    
class AttendeeParent(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.parent} : {self.attendee}"