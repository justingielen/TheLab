from django.db.models.signals import post_save, post_delete # signal that gets fired after an object is saved
from django.dispatch import receiver # decorator
from .models import User, Profile, ProfileUser, HomeCalendar, Notification, Application
from page.models import Sport, ProfileSport

@receiver(post_save, sender=User)
def create_personal_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile for the user
        Profile.objects.create(first_name=instance.username)

        # Create 'personal' profile-user association
        profile = Profile.objects.get(first_name=instance.username)
        ProfileUser.objects.create(profile=profile,user=instance)

        # Create a notification for the user
        user = instance.user
        message = "Welcome to your personal profile in the Lab!! The Lab aims to be a platform where aspiring athletes can connect with and learn from successful players and coaches. You can look for a Coach that suits your (or your child's) aspirations in the 'Coaches' tab of your main navigation bar. You can also find upcoming developmental sports Events in the 'Events' tab. Or, you can discover Drills to fill your Workout at home! (under the 'Drills' tab)."
        Notification.objects.create(user=user,message=message)

        # Create a home calendar for the user
        HomeCalendar.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_home_calendar(sender, instance, **kwargs):
    instance.homecalendar.save()


@receiver(post_save,sender=Application) 
def application_notification(sender, instance, **kwargs):
    if instance.approved is not None:
        if instance.approved:
            message = "Congratulations Coach! Your Team Application has been Approved! If you didn't already, you should have access to a 'Page' button on your main navigation bar."
        else:
            message = "Your Team Application has been denied."
        
        profile_user = ProfileUser.objects.get(profile=instance.profile)
        user = profile_user.user

        type = 'Team Approval'
        Notification.objects.create(user=user,message=message,type=type)

@receiver([post_save, post_delete], sender=Application)
def check_coach(sender, instance, **kwargs):
    profile = instance.profile  # Get the profile related to the Application

    # Check if any Approved Applications exist for the related profile
    approved_applications_exist = Application.objects.filter(
        profile=profile,
        approved=True
    ).exists()

    # Update the coach field according to the existence of approved applications
    profile.coach = approved_applications_exist
    profile.save()

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

@receiver(post_delete, sender=Application)
def check_sport_delete(sender, instance, **kwargs):
    # Delete sport if there are no more approved Applications for it
    sport_approved = Application.objects.filter(sport=instance.sport,approved=True).exists()
    if not sport_approved:
        Sport.objects.filter(sport=instance.sport).delete()

@receiver(post_save, sender=Application)
def check_profile_sport(sender, instance, **kwargs):
    # If the Application is saved with a result
    if instance.approved is not None:
        profile = instance.profile
        sport = Sport.objects.get(sport=instance.sport)
        
        # ...of approved
        if instance.approved:
            # Check if association exists
            associated = ProfileSport.objects.filter(sport=sport,profile=profile).exists()
            if not associated:
                ProfileSport.objects.create(sport=sport,profile=profile)

        #... of denied
        if not instance.approved:
            # Check if approved application exists
            other_approved = Application.objects.filter(sport=sport,profile=profile,approved=True).exists()
            if not other_approved:
                # Check if association exists
                associated = ProfileSport.objects.filter(sport=sport,profile=profile).exists()
                if associated:
                    ProfileSport.objects.filter(sport=sport,profile=profile).delete()