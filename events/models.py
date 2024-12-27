from django.db import models
from thelab.models import User
from page.models import Event
from schedule.models import Occurrence as BaseOccurrence

class EventCoach(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    coach = models.OneToOneField(User, on_delete=models.CASCADE)

class Occurrence(BaseOccurrence):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()