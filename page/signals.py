from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from thelab.models import User
from .models import Location, CoachLocation, Event
from django.apps import apps
from django.utils import timezone

@receiver(post_save, sender=Location)
def coach_location(sender, instance, **kwargs):
    location = instance
    user = kwargs.get('user', None)
    if user:
        if not CoachLocation.objects.filter(location=location, coach=user).exists():
            CoachLocation.objects.create(location=location, coach=user)

@receiver(post_save, sender=Event)
def create_d_on(sender, instance, **kwargs):
    base_event_model = apps.get_model(app_label='schedule',model_name='Event')

    # check if associated BaseEvent exists
    try:
        base_event = base_event_model.objects.get(event=instance)
    except base_event_model.DoesNotExist:
        # create it if it doesn't
        base_event = base_event_model(event=instance)

    if not base_event.created_on:
        base_event.created_on = timezone.now()
        print(base_event.created_on)
    
        base_event.save()