from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from schedule.models import Event as BaseEvent
from schedule.models import Calendar as BaseCalendar
from schedule.models import Occurrence as BaseOccurrence
from thelab.models import Profile
from datetime import timedelta
    

class Sport(models.Model):
    sport = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.sport

class ProfileSport(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.profile} - {self.sport}"

class Location(models.Model):
    location_name = models.CharField(max_length=255, unique=True)
    LOCATION_TYPES = (
        ('in-person', 'In Person'),
        ('virtual', 'Virtual'),
    )
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES)
    hyperlink = models.CharField(max_length=255, blank=True, null=True)
    
    # All of this should eventually incorporate some sort of searching for actual address, in order to compare proposed additions to existing locations
    # ^^ For this, consider Django's GIS (PointField) framework or a library like Google Places
    street_address = models.CharField(max_length=255, blank=True)
    location_city = models.CharField(max_length=255, blank=True)
    location_state = models.CharField(max_length=2, blank=True)
    location_zip = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return self.location_name

class CoachLocation(models.Model):
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.coach} - {self.location}"

class Availability(BaseEvent):
    '''''
    From django-scheduler (thelab > lib > schedule > models > events.py):

    start, end, title, description, creator (fk --> django_settings.AUTH_USER_MODEL), created_on, updated_on, rule (fk), end_recurring_period, calendar (fk), 
    '''''
    day = models.CharField(max_length=10,choices= {
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    })
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"@{self.creator} ({self.day}): {self.start.time()} - {self.end.time()}"
    
class Package(models.Model):
    package_types = {
        ('Training','Training'),
        ('P(r)ep Talk','P(r)ep Talk'),
    }
    type = models.CharField(max_length=20, choices=package_types)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    duration = models.DurationField(default=timedelta(minutes=60))
    athletes = models.IntegerField(default=1)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, help_text="(Note: locations must be added to your Profile before they can be used in an Event)", blank=True, null=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"@{self.owner} - {self.type} ({self.athletes}): ${self.price}"

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
    # price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,help_text='(optional)') # maybe IntegerField(1000),null=True,blank=True... in order to deal with Stripe's API better

    def __str__(self):
        return f'{self.title} - {self.location} - ({self.event_type})'
    
    def get_absolute_url(self):
        return reverse('view_event', kwargs={'pk':self.pk})
    
class EventSport(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.event.title} - {self.sport}"

class Occurrence(BaseOccurrence):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

class PageCalendar(BaseCalendar):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        self.name = f"Page Calendar for {self.user.username}"
        # Customize slug generation to ensure uniqueness
        self.slug = f"page_calendar_{self.user.username}"
        super().save(*args, **kwargs)
              
    def __str__(self):
        return self.name
    
class EventCoach(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    coach = models.OneToOneField(User, on_delete=models.CASCADE)