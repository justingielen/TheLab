from django.db.models.signals import post_save, post_delete # signal that gets fired after an object is saved
from django.dispatch import receiver # decorator
from django.conf import settings
from django.urls import reverse
from allauth.socialaccount.models import SocialAccount
from .models import User, Notification, Application
from page.models import Sport, CoachSport

# emails 
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail
import base64
import os

@receiver(post_save, sender=SocialAccount)
def create_social_user_profile(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        # Get name from social account
        first_name = instance.extra_data.get('given_name', '')
        last_name = instance.extra_data.get('family_name', '')
        
        # Update user info
        user.first_name = first_name
        user.last_name = last_name
        
        # Generate username as per Registration Form
        base_username = (first_name + last_name).lower()
        username = base_username
        
        # Ensure username uniqueness
        if User.objects.filter(username=username).exists():
            n = 2
            while True:
                new_username = f"{base_username}{n}"
                if not User.objects.filter(username=new_username).exists():
                    username = new_username
                    break
                n += 1
        
        user.username = username
        user.save()

@receiver(post_save,sender=Application) 
def application_notification(sender, instance, **kwargs):
    if instance.approved is not None:
        if instance.approved:
            user = instance.user
            page_url = reverse('page_viewing', kwargs={'pk': user.pk})
            # Create a notification
            message = (
                f"Congratulations Coach! Your Application has been Approved! "
                f"If you didn't already, you should have access to a <a class='green-link' href='{page_url}'>Page</a> button on your navigation bar."
            )        

            # For the email: ensuring static files are obtained from the correct root
            if settings.DJANGO_ENV == 'development':
                static_root = os.path.join('thelab', 'static')
            else:
                static_root = 'staticfiles'
            logo_path = os.path.join(settings.BASE_DIR, static_root, 'images', 'green_logo.png')
            with open(logo_path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Ensuring email links point to the right domain
            if settings.DJANGO_ENV == 'staging':
                domain = 'https://justingielen.pythonanywhere.com'
            else:
                domain = 'http://localhost:8000'
            links = {
                'page': str(domain + "/page/" + str(user.pk) + "/viewing"),
                'availability': str(domain + "/page/set/availability"),
                'package': str(domain + "/page/create/package")
            }

            # Constructing welcome email
            html_message = render_to_string(
                'emails/application_decision.html',
                {
                    'encoded_image': encoded_image,
                    'links': links,
                }
            )

            # Send the email (including both html and plain text versions to avoid being marked as spam)
            plain_message = strip_tags(html_message)
            send_mail(
                subject='Welcome, Coach!',
                message=plain_message,
                html_message=html_message,
                from_email=settings.FROM_EMAIL_JUSTIN,  # From justin email
                recipient_list=[user.email],
                auth_user=settings.FROM_EMAIL_JUSTIN,
                auth_password=settings.EMAIL_JUSTIN_PASSWORD,
                fail_silently=False,
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
