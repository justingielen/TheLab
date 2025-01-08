from django.db.models.signals import post_save, post_delete # signal that gets fired after an object is saved
from django.dispatch import receiver # decorator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from .models import User, Profile, ProfileUser, Notification, Application
from .models import HomeCalendar
from page.models import Sport, ProfileSport

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile for the user
        Profile.objects.create(first_name=instance.username)

        # Create 'personal' profile-user association
        profile = Profile.objects.get(first_name=instance.username)
        ProfileUser.objects.create(profile=profile,user=instance)

        # Create a notification for the user
        user = instance
        message = (
        "Welcome to The Lab! We're excited to help you be part of the future of sports development. "
        "If you've played or coached at the collegiate level or above, "
        "submit an <a class='green-link' href='/application'>Application</a> to join the coaching team! "
        'For those looking to enhance an athletic career, explore our roster of experienced '
        "<a class='green-link' href='/page/browsing'>Coaches</a> who are ready to guide you or your athlete's journey "
        'to the next level! You can also discover and sign up for upcoming developmental '
        "<a class='green-link' href='/events/browsing'>Events</a> (e.g., camps & Clinics). "
        "Stay tuned for more features and updates as we continue building The Lab!"
    )
        Notification.objects.create(user=user,message=message)

        
        # Send welcome email
        html_message = render_to_string(
            'emails/profile_creation.html',
            {
                'username': instance.username,
                'message': message
            }
        )
        # (include both html and plain text versions to void being marked as spam)
        plain_message = strip_tags(html_message)
        print(settings.DEFAULT_FROM_EMAIL)
        print(settings.EMAIL_HOST_PASSWORD)
        send_mail(
            subject='Welcome to the Lab!',
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )
        
        
        # Create a home calendar for the user
        HomeCalendar.objects.create(user=instance)
                
# This might be unnecessary -- Not having a Profile model could make this obsolete
@receiver(post_save, sender=Profile)
def user_name(sender, instance, **kwargs):
    profile = instance
    try:
        user = ProfileUser.objects.get(profile=profile, control_type='personal').user
        if profile.first_name is not None:
            user.first_name = profile.first_name
            user.last_name = profile.last_name
            user.save()
    except ProfileUser.DoesNotExist:
        pass


# Delete profile if personal User account is deleted
@receiver(post_delete, sender=ProfileUser)
def delete_profile(sender, instance, **kwargs):
    if instance.control_type == 'personal':
        profile = instance.profile
        profile.delete()
    

@receiver(post_save,sender=Application) 
def application_notification(sender, instance, **kwargs):
    if instance.approved is not None:
        if instance.approved:
            profile = instance.profile
            user = ProfileUser.objects.get(profile=profile, control_type='personal').user
            page_url = reverse('page_viewing', kwargs={'pk': user.pk})
            message = (
                f"Congratulations Coach! Your Application has been Approved! "
                f"If you didn't already, you should have access to a <a class='green-link' href='{page_url}'>Page</a> button on your navigation bar."
            )        
        else:
            message = "Your Coach Application has been denied."
        
        profile_user = ProfileUser.objects.get(profile=instance.profile)
        user = profile_user.user

        type = 'coach_application'
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

    # Ensure admin has access to all sports -- this needs work
    adminuser = User.objects.get(username='admin')
    adminprofile = ProfileUser.objects.get(user=adminuser).profile
    adminsports = ProfileSport.objects.filter(profile=adminprofile)
    sports = Sport.objects.all()
    for sport in sports:
        if sport.sport not in adminsports:
            ProfileSport.objects.create(sport=sport,profile=adminprofile)

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
