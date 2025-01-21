from django.db import models
from django.conf import settings
from django.urls import reverse
from schedule.models import Event as BaseEvent
from datetime import datetime, timedelta

# Locations
import googlemaps
from functools import lru_cache
from django.core.exceptions import ValidationError
from django.core.exceptions import ImproperlyConfigured
from decimal import Decimal
import logging

class Sport(models.Model):
    sport = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.sport

class CoachSport(models.Model):
    coach = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.coach} - {self.sport}"

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

    # Cached geocoding results for performance
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Cached latitude from Google Maps geocoding"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Cached longitude from Google Maps geocoding"
    )
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Before saving, geocode the address for in-person locations.
        This ensures we always have coordinates for travel time calculations.
        """
        if self.type == 'in-person' and not self.latitude and all([
            self.street_address, self.city, self.state, self.zip
        ]):
            self._geocode_address()
        super().save(*args, **kwargs)
    
    def _geocode_address(self):
        """
        Convert the physical address to latitude and longitude using Google Maps API.
        Called automatically when saving new in-person locations or when addresses change.
        """
        logger = logging.getLogger(__name__)

        if not hasattr(settings, 'GOOGLE_MAPS_API_KEY'):
            raise ImproperlyConfigured(
                "GOOGLE_MAPS_API_KEY setting is required. Please configure key."
            )
            
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        address = f"{self.street_address}, {self.city}, {self.state} {self.zip}"
        
        try:
            result = gmaps.geocode(address)
            if not result:
                logger.error(f"No geocoding results found for address: {address}")
                return
                
            location = result[0]['geometry']['location']
            self.latitude = Decimal(str(location['lat']))
            self.longitude = Decimal(str(location['lng']))
            
            logger.info(f"Successfully geocoded address: {address}")
            
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Google Maps API error for {address}: {str(e)}")
            raise ValidationError(f"Unable to geocode address: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error geocoding {address}: {str(e)}")
            raise ValidationError("An unexpected error occurred while geocoding the address")

    @lru_cache(maxsize=100)
    def get_travel_time(self, other_location, departure_time=None):
        """
        Calculate travel time to another location considering traffic at departure_time.
        Results are cached to minimize API calls for frequently calculated routes.
        
        Args:
            other_location: Destination Location instance (always the location of the event being compared to the time slot)
            departure_time: When the journey will start (for traffic estimation)
        
        Returns:
            int or None: Travel time in minutes, or None if calculation fails
        """ 
        logger = logging.getLogger(__name__)

        if not all([self.latitude, self.longitude, 
                   other_location.latitude, other_location.longitude]):
            logger.warning(
                f"Cannot calculate travel time: missing coordinates for {self.name} "
                f"or {other_location.name}"
            )
            return None
            
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        try:
            result = gmaps.distance_matrix(
                origins=[(float(self.latitude), float(self.longitude))],
                destinations=[(float(other_location.latitude), float(other_location.longitude))],
                mode="driving",
                departure_time=departure_time or datetime.now(), # departure time provided in check_availability views
                traffic_model="best_guess"
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                # Convert seconds to minutes
                return result['rows'][0]['elements'][0]['duration']['value'] // 60
            return None
        except Exception as e:
            print(f"Error calculating travel time: {str(e)}")
            return None

class CoachLocation(models.Model):
    coach = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.coach} - {self.location}"
    
days_of_the_week = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
]

class Availability(BaseEvent):
    '''''
    From django-scheduler (thelab > lib > schedule > models > events.py):

    start, end, title, description, creator (fk --> django_settings.AUTH_USER_MODEL), created_on, updated_on, rule (fk), end_recurring_period, calendar (fk), 
    '''''
    day = models.CharField(max_length=10,choices=days_of_the_week)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.creator} ({self.day}): {self.start.time()} - {self.end.time()}"

class Package(models.Model):
    type = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    duration = models.DurationField(default=timedelta(minutes=60))
    athletes = models.IntegerField(default=1)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, default=1)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner} - {self.sport} {self.type} (${self.price} {self.athletes} athlete(s)/{self.duration})"
    
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
    
class AttendeeParent(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.parent} : {self.attendee}"

class Event(BaseEvent):
    '''''
    From django-scheduler (thelab > lib > schedule > models > events.py):

    start, end, title, description, creator (fk --> django_settings.AUTH_USER_MODEL), created_on, updated_on, rule (fk), end_recurring_period, calendar (fk), 
    '''''
    type = models.CharField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, help_text="(Note: locations must be added to your Profile before they can be used in an Event)")
    location_notes = models.CharField(max_length=255,blank=True, help_text="(e.g., 'Field 3', or 'Auxiliary Gym')")
    is_accepted = models.BooleanField(default=True)
    max_attendance = models.IntegerField(default=100)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,help_text='(optional)') # maybe IntegerField(1000),null=True,blank=True... in order to deal with Stripe's API better
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.title} - {self.location} - ({self.price})'
    
    def get_absolute_url(self):
        return reverse('view_event', kwargs={'pk':self.pk})
    
class EventAttendee(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.attendee} -- {self.event.title}'