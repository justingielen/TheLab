from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegistrationForm, UserUpdateForm, ApplicationForm
from .models import User, Notification, HomeCalendar
from django.contrib.auth.decorators import login_required # Decorator-- adds functionality to an existing function
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail


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

# FIRST VIEW THAT CALLS A TEMPLATE W/ A FORM
def createprofile(request):
    context = {
        'title': "Create Profile",
    }

    if request.method == "POST":
        form = UserRegistrationForm(request.POST) # passes in data from form when the POST request was sent
        if form.is_valid():
            user = form.save()  # Save the user, username is automatically set
            message = (
                "Welcome to The Lab! Welcome to the future of youth sports development. "
                "If you've played or coached at the collegiate level or above, "
                "submit an <strong><a class='green-link' href='/application'>Application</a></strong> to join the coaching team! "
                'For those looking to enhance an athletic career, explore our roster of experienced '
                "<strong><a class='green-link' href='/page/browsing'>Coaches</a></strong> who are ready to guide you or your athlete's journey "
                'to the next level! You can also discover and sign up for upcoming developmental '
                "<strong><a class='green-link' href='/events/browsing'>Events</a></strong> (e.g., camps & Clinics). "
                "Stay tuned for more features and updates as we continue building The Lab!"
            )
            Notification.objects.create(user=user,message=message)

            
            # Send welcome email
            html_message = render_to_string(
                'emails/profile_creation.html',
                {
                    'username': user.username,
                    'message': message
                }
            )
            # (include both html and plain text versions to avoid being marked as spam)
            plain_message = strip_tags(html_message)
            send_mail(
                subject='Welcome to the Lab!',
                message=plain_message,
                html_message=html_message,
                from_email=settings.FROM_EMAIL_JUSTIN,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            
            # Create a home calendar for the user
            HomeCalendar.objects.create(user=user)

            username = user.username  # For success message
            messages.success(request, f'Profile created for {username}! You should now be able to log in:')
            return redirect('home')
        else:
            print(form.errors) # for debugging
    else:
        try:
            # Get query parameters from the URL
            first_name = request.GET.get('first_name', '')
            last_name = request.GET.get('last_name', '')
            email = request.GET.get('email', '')
            parent = request.GET.get('parent')
            form = UserRegistrationForm(initial={
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
        })
            context.update({'parent':parent})
        except:
            form = UserRegistrationForm()
        
    context.update({'form':form})
    return render(request, 'main/createprofile.html',context)

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