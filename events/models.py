from django.db import models
from django.contrib.auth.models import User
from page.models import Event

# This needs to change, User will be an optional field in the Attendee model, to allow parents to sign up their kids without necessarily making User accounts for them
# class Attendee(models.Model):
# first_name required
# last_name required
# age
# other information required for being at an event
# optional fk user

# Event Attendee will still exist, it would just be two fk fields - Attendee and Event
class EventAttendee(models.Model):
    first_name = models.CharField(max_length=50, default="(first name)")
    first_name = models.CharField(max_length=100, default = "(last name)")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'