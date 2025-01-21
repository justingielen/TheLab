from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse
from allauth.account.views import SignupView, LoginView
from google.oauth2 import id_token
from google.auth.transport import requests
import json
from .forms import UserRegistrationForm, UserUpdateForm, ApplicationForm
from .models import User, Notification
from django.contrib.auth.decorators import login_required # Decorator-- adds functionality to an existing function
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# emails 
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail
import base64
import os

title = 'The Lab - '

def discover_drills(request):
    context = {
        'title': title + 'Discover Drills',
    }

    return render(request, 'main/discover_drills.html',context)

# Page shown when you click 'The Lab' on the main toolbar
def welcome(request):
    context = {
        'title': title + "Welcome!",
    }

    return render(request,'main/welcome.html',context)

def whatisthelab(request):
    context = {
        'title': title + "What is it?",
    }

    return render(request, 'main/whatisthelab.html',context)

def about(request):
    context = {
        'title': "About LevelUp Sports",
    }

    return render(request, 'main/about.html',context)

class CustomSignupView(SignupView):
    template_name = 'main/createprofile.html'
    form_class = UserRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create Profile"
        context.update({
            'google_config': {
                'apiKey': settings.GOOGLE_IDENTITY_PLATFORM['API_KEY'],
                'authDomain': settings.GOOGLE_IDENTITY_PLATFORM['AUTH_DOMAIN'],
                'projectId': settings.GOOGLE_IDENTITY_PLATFORM['PROJECT_ID'],
            }
        })
        
        # Handle NPU parameters (from signup)
        parent = self.request.GET.get('parent')
        if parent:
            context['parent'] = parent
            
        return context

    def get_initial(self):
        # Handle pre-filling form fields for NPUs
        initial = super().get_initial()
        initial.update({
            'first_name': self.request.GET.get('first_name', ''),
            'last_name': self.request.GET.get('last_name', ''),
            'email': self.request.GET.get('email', ''),
        })
        return initial

    def _create_welcome_notification(self, user):
        message = (
            "Welcome to The Lab, the future of youth sports development! "
            'For those looking to enhance an athletic career, explore our roster of experienced '
            "<strong><a class='green-link' href='/page/browsing'>Coaches</a></strong> "
            "who are ready to guide you or your athlete's journey to the next level! "
            "If you've played or coached at the collegiate level or above, "
            "submit an <strong><a class='green-link' href='/application'>Application</a></strong> "
            "to join the coaching team and start making money while making a difference! "
            "Stay tuned for more features and updates as we continue building The Lab!"
        )
        Notification.objects.create(user=user, message=message)
    
    def _send_welcome_email(self, user):
        # Handle static files based on environment
        static_root = ('staticfiles' if settings.DJANGO_ENV != 'development' 
                      else os.path.join('thelab', 'static'))
        logo_path = os.path.join(
            settings.BASE_DIR, 
            static_root, 
            'images', 
            'green_logo.png'
        )
        
        with open(logo_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Set up domain-specific links
        domain = ('https://justingielen.pythonanywhere.com' 
                 if settings.DJANGO_ENV == 'staging' 
                 else 'http://localhost:8000')
        
        links = {
            'coaches': f"{domain}/page/browsing",
            'application': f"{domain}/application",
            'get_started': f"{domain}/home",
        }

        html_message = render_to_string(
            'emails/profile_created.html',
            {
                'username': user.username,
                'encoded_image': encoded_image,
                'links': links,
            }
        )
        
        plain_message = strip_tags(html_message)
        send_mail(
            subject='Welcome to The Lab!',
            message=plain_message,
            html_message=html_message,
            from_email=settings.FROM_EMAIL_JUSTIN,
            recipient_list=[user.email],
            auth_user=settings.FROM_EMAIL_JUSTIN,
            auth_password=settings.EMAIL_JUSTIN_PASSWORD,
            fail_silently=False,
        )
    
    def form_valid(self, form):
        # First, let allauth handle the basic user creation
        response = super().form_valid(form)
        user = self.user  # allauth sets this after successful signup

        # Create notification
        self._create_welcome_notification(user)
        
        # Send welcome email
        self._send_welcome_email(user)
        
        messages.success(
            self.request, 
            f'Profile created for {user.username}! You should now be able to log in:'
        )
        
        return response
    
@csrf_exempt
def google_auth_callback(request):
    """Handle Google Identity Platform authentication callback"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        id_token_str = data.get('idToken')
        
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_IDENTITY_PLATFORM['CLIENT_ID']
        )

        # Get user info from token
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')

        # Get or create user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Generate username
            base_username = (first_name + last_name).lower()
            username = base_username
            
            if User.objects.filter(username=username).exists():
                n = 2
                while True:
                    new_username = f"{base_username}{n}"
                    if not User.objects.filter(username=new_username).exists():
                        username = new_username
                        break
                    n += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # Create associated objects
            Notification.objects.create(
                user=user,
                message="Welcome to The Lab! [...]"  # Your welcome message
            )

            # Send welcome email (reuse the email sending logic)
            CustomSignupView()._send_welcome_email(user)

        return JsonResponse({
            'success': True,
            'redirect': reverse('home')
        })

    except ValueError:
        return JsonResponse({'error': 'Invalid token'}, status=400)

# defining a Home screen function
@login_required
def home(request):

    context = {
        'title': title + 'Home',
    }
    return render(request, 'main/home.html', context)

@login_required
def alerts(request):
    notifications = request.user.notifications.all()
    
    context = {
        'title': title + 'Alerts',
        'notifications': notifications,
    }
    return render(request, 'main/alerts.html', context)

@csrf_exempt
def read_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    response = HttpResponse(render_to_string("main/partials/single_alert.html", {"notification": notification}))
    response["HX-Trigger"] = "notificationRead"
    return response

# ----------------------------------------------------------------------------------------------------------------------
@login_required
def profile_edit(request):
    try:
        user = request.user
    except user.DoesNotExist:
        user = None

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=user)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Profile updated!')
            return redirect('home')
    else:
        u_form = UserUpdateForm(instance=request.user)

    context = {
        'u_form':u_form,
        'user':user
    }

    return render(request, 'main/profile_edit.html', context)
# ----------- # Class-based views (different types): List, Detail, Create, Update, Delete (this is a List)
#class TeamApprovalListView(ListView):

# ---------------------------------------------------------------------------------------------------------------------------
@login_required
def application(request):
    if request.method == "POST":
        application = ApplicationForm(request.POST)
        if application.is_valid():
            application_instance = application.save(commit=False)
            application_instance.user = request.user
            application_instance.save()
            messages.success(request, 'Coach Application submitted! You should get an Alert once a decision is reached.')
            return redirect('profile_edit')
    else:
        application = ApplicationForm()

    return render(request, 'main/application.html',{'application':application})