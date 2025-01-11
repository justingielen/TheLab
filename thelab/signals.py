from django.db.models.signals import post_save, post_delete # signal that gets fired after an object is saved
from django.dispatch import receiver # decorator
from django.conf import settings
from django.urls import reverse
from .models import User, Notification, Application
from page.models import Sport, CoachSport

@receiver(post_save,sender=Application) 
def application_notification(sender, instance, **kwargs):
    if instance.approved is not None:
        if instance.approved:
            user = instance.user
            page_url = reverse('page_viewing', kwargs={'pk': user.pk})
            message = (
                f"Congratulations Coach! Your Application has been Approved! "
                f"If you didn't already, you should have access to a <a class='green-link' href='{page_url}'>Page</a> button on your navigation bar."
            )        
        else:
            message = "Your Coach Application has been denied."
        
        user = instance.user
        type = 'coach_application'
        Notification.objects.create(user=user,message=message,type=type)

@receiver([post_save, post_delete], sender=Application)
def check_coach(sender, instance, **kwargs):
    user = instance.user  # Get the user related to the Application

    # Check if any Approved Applications exist for the user
    approved_applications_exist = Application.objects.filter(
        user=user,
        approved=True
    ).exists()

    # Update the coach field according to the existence of approved applications
    user.coach = approved_applications_exist
    user.save()

# The signals to update the Sport model if needed
@receiver(post_save, sender=Application)
def check_sport(sender, instance, **kwargs):
    if instance.approved:
        # Add sport if it doesn't already exist
        sport_exists = Sport.objects.filter(sport=instance.sport).exists()
        if not sport_exists:
            Sport.objects.create(sport=instance.sport)

    else: 
        # Delete sport if there are no more approved Applications for it
        sport_approved = Application.objects.filter(sport=instance.sport,approved=True).exists()
        if not sport_approved:
            Sport.objects.filter(sport=instance.sport).delete()

    # Ensure admin has access to all sports -- this needs work
    adminuser = User.objects.get(username='admin')
    adminsports = CoachSport.objects.filter(coach=adminuser)
    sports = Sport.objects.all()
    for sport in sports:
        if sport.sport not in adminsports:
            print(sport)
            CoachSport.objects.create(sport=sport,coach=adminuser)

@receiver(post_delete, sender=Application)
def check_sport_delete(sender, instance, **kwargs):
    # Delete sport if there are no more approved Applications for it
    sport_approved = Application.objects.filter(sport=instance.sport,approved=True).exists()
    if not sport_approved:
        Sport.objects.filter(sport=instance.sport).delete()

@receiver(post_save, sender=Application)
def check_coach_sport(sender, instance, **kwargs):
    # If the Application is saved with a result
    if instance.approved is not None:
        user = instance.user
        sport = Sport.objects.get(sport=instance.sport)
        
        # ...of approved
        if instance.approved:
            # Check if association exists
            associated = CoachSport.objects.filter(sport=sport,coach=user).exists()
            if not associated:
                CoachSport.objects.create(sport=sport,coach=user)

        #... of denied
        if not instance.approved:
            # Check if approved application exists
            other_approved = Application.objects.filter(sport=sport,user=user,approved=True).exists()
            if not other_approved:
                # Check if association exists
                associated = CoachSport.objects.filter(sport=sport,user=user).exists()
                if associated:
                    CoachSport.objects.filter(sport=sport,user=user).delete()
