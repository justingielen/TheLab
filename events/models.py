from django.db import models
from django.contrib.auth.models import User
from page.models import Event

# This needs to change, User will be an optional field in the Attendee model, to allow parents to sign up their kids without necessarily making User accounts for them
# Event Attendee will still exist
class EventAttendee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    event = models.OneToOneField(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'