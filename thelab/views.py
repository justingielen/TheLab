from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, TeamApplicationForm
from page.models import Event
from .models import ProfileUser, Profile, Notification
from django.contrib.auth.decorators import login_required # Decorator-- adds functionality to an existing function

title = 'The Lab - '

# Mainly for aesthetics (don't worry about this at this stage)
def discover_drills(request):
    context = {
        'title': title+ 'Discover Drills',
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
            form.save() # Creates the User ('profile' is misleading-- the user is actually creating a User account, which automatically signals the creation of a profile)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Profile created for {username}! You should now be able to log in:')
            return redirect('login')
        else:
            print(form.errors) # for debugging
    else:
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
    notifications = Notification.objects.filter(user=request.user)
    try:
        profile_user = ProfileUser.objects.get(user=request.user)
        profile = profile_user.profile
    except:
        profile = None

    context = {
        'title': title + 'Alerts',
        'notifications': notifications,
        'profile':profile
    }
    return render(request, 'main/alerts.html', context)

# ----------------------------------------------------------------------------------------------------------------------
@login_required
def profile_edit(request):
    try:
        profile_user = ProfileUser.objects.get(user=request.user,control_type='personal')
        profile = profile_user.profile
        user = profile_user.user
    except ProfileUser.DoesNotExist:
        profile = None

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated!')
            return redirect('home')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form':u_form,
        'p_form':p_form,
        'profile':profile,
        'user':user
    }

    return render(request, 'main/profile_edit.html', context)
# ----------- # Class-based views (different types): List, Detail, Create, Update, Delete (this is a List)
#class TeamApprovalListView(ListView):

# ---------------------------------------------------------------------------------------------------------------------------
@login_required
def team_application(request):
    if request.method == "POST":
        application = TeamApplicationForm(request.POST)
        if application.is_valid():
            profile_user = ProfileUser.objects.get(user=request.user,control_type='personal')
            profile = profile_user.profile
            
            application_instance = application.save(commit=False)
            application_instance.profile = profile
            application_instance.save()
            messages.success(request, 'Team Application submitted! You should get an Alert once a decision is reached.')
            return redirect('profile_edit')
    else:
        application = TeamApplicationForm()

    return render(request, 'main/team_application.html',{'application':application})