from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # Decorator-- adds functionality to an existing function
from django.contrib import messages
from django.utils import timezone
from thelab.models import Profile, ProfileUser, User
from .models import PageCalendar, Sport, ProfileSport, Location, CoachLocation, Package, Event
from .forms import LocationForm, PackageForm, EventSportForm, EventDetailsForm, EventTimelineForm, EventRecurrenceForm
from datetime import datetime
from .signals import coach_location

def page_browsing(request):
    # Find all coach profiles
    coach_profiles = Profile.objects.filter(coach=True)
    # Find all ProfileUser objects associated with those coaches
    coach_profile_users = ProfileUser.objects.filter(profile__in=coach_profiles)
    # Create list of just the Coach User accounts
    coaches = [cpu.user for cpu in coach_profile_users]
    # Create a dictionary that maps all packages to their (owner) User accounts
    packages_by_coach = {coach: Package.objects.filter(owner=coach) for coach in coaches}

    context = {
        'coaches': coaches,
        'packages_by_coach': packages_by_coach,
    }

    return render(request, 'page/browsing.html', context)

# Page Viewing ------
def page_viewing(request, pk):
    # if the viewer is the owner of the page,
    is_owner = request.user.pk == int(pk)
    if is_owner:
        # assign profile/user data based on the requesting user
        context = {
            'is_owner':is_owner,
        }
    # if not,
    else:
        # assign profile/user data based on the private key (id) of the Page's owner, which is defined when the view is called
        user = User.objects.get(pk=pk)
        profile_user = ProfileUser.objects.get(user=user, control_type='personal')
        profile = profile_user.profile
        context = {
            'user':user,
            'coach':profile,
        }

    coach = User.objects.get(pk=pk)
    coach_events = Event.objects.filter(creator=coach) # I feel like this will become expensive with more events, probably much better to go through Calendars rather than searching through the entire Event table
    coach_locations = CoachLocation.objects.filter(coach=coach)

    context.update({
        'is_owner':is_owner,
        'coach_locations':coach_locations,
        'coach_events':coach_events
    })
    return render(request, 'page/viewing.html',context=context)

@login_required
def create_location(request):
    if request.method == 'POST':
        location_form = LocationForm(request.POST)
        if location_form.is_valid():
            # handle the data
            location = Location()
            location.location_name = location_form.cleaned_data['location_name']
            location.location_type = location_form.cleaned_data['location_type']
            location.hyperlink = location_form.cleaned_data['hyperlink']
            location.street_address = location_form.cleaned_data['street_address']
            location.location_city = location_form.cleaned_data['location_city']
            location.location_state = location_form.cleaned_data['location_state']
            location.location_zip = location_form.cleaned_data['location_zip']
            
            location.save()
            messages.success(request, 'Location added!')
            # Sending the save request's User to the CoachLocation creation signal
            coach_location(sender=Location, instance=location, location=location, user=request.user)
            ## ^^ PRETTY COOL!! This is using a signal as a function inside of a view. 
            return redirect('page_viewing', pk=request.user.pk)
    else:
        location_form = LocationForm()

    context = {
        'location_form':location_form,
    }

    return render(request, 'page/location_form.html',context)

def search_location(request):
    # Don't know the details here
    query = request.GET.get('query', '')
    locations = Location.objects.filter(location_name__icontains=query)
    
    context = {'locations': locations, 'query': query}
    
    return render(request, 'page/location_search.html', context)

def add_location(request, location_name):
    location = get_object_or_404(Location, location_name=location_name)

    coach_location(sender=Location, instance=location, location=location, user=request.user)

    messages.success(request, 'Location added!')
    return redirect('page_viewing', pk=request.user.pk)

def remove_location(request, location_name):
    location = Location.objects.filter(location_name=location_name).get()
    coach_location = CoachLocation.objects.filter(location=location, coach=request.user)
    coach_location.delete()
    messages.success(request, 'Location removed!')
    return redirect('page_viewing', pk=request.user.pk)

@login_required
def create_package(request):
    if request.method == 'POST':
        # handle form info
        package_form = PackageForm(request.POST)
        if package_form.is_valid:
            package = Package()
            package = package_form.save(commit=False)
            package.owner = request.user
            package.save()

            messages.success(request, 'Package added!')
            return redirect('page_viewing', pk=request.user.pk)
    
    else:
        package_form = PackageForm()

    context = {
        'package':package_form
    }

    return render(request, 'page/package_form.html', context)

@login_required
def create_event(request):
    if request.method == 'POST':
        event_details = EventDetailsForm(request.POST)
        event_timeline = EventTimelineForm(request.POST)
        event_recurrence = EventRecurrenceForm(request.POST)
        
        if all([event_details.is_valid(), event_timeline.is_valid(), event_recurrence.is_valid()]):
            event = Event()
            event.creator = request.user
            event.calendar = PageCalendar.objects.get(user=request.user)
            print(event.calendar)

            # Details
            event.title = event_details.cleaned_data['title']
            event.location = event_details.cleaned_data['location']
            event.description = event_details.cleaned_data['description']
            # event.price = event_details.cleaned_data['price']
            event.event_type = event_details.cleaned_data['event_type']

            # Timeline
            event.start = event_timeline.cleaned_data['start_time']
            event.end = event_timeline.cleaned_data['end_time']

            # Recurrence
            event.rule = event_recurrence.cleaned_data['rule']
            event.end_recurring_period = datetime.combine(event_recurrence.cleaned_data['end_date'], event_recurrence.cleaned_data['end_time'])

            event.save()
            messages.success(request, 'Event created!')
            return redirect('page_viewing', pk=request.user.pk)
        
    else:
        # Get applicable locations
        cls_on_file = CoachLocation.objects.filter(coach=request.user)
        coach_locations = [coach_location.location.id for coach_location in cls_on_file]
        locations_queryset = Location.objects.filter(pk__in=coach_locations)

        # Get applicable sports
        profile_user = ProfileUser.objects.filter(user=request.user, control_type='personal').get()
        profile_sport_objects = ProfileSport.objects.filter(profile=profile_user.profile)
        profile_sports = [profile_sport.sport.id for profile_sport in profile_sport_objects]
        sports_queryset = Sport.objects.filter(pk__in=profile_sports)

        event_sports = EventSportForm(sports=sports_queryset)

        event_details = EventDetailsForm(locations=locations_queryset)
        event_timeline = EventTimelineForm()
        event_recurrence = EventRecurrenceForm()

    context= {
            'sports':event_sports,
            'details':event_details,
            'timeline':event_timeline,
            'recurrence':event_recurrence
        }

    return render(request, 'page/event_form.html', context)


# Old EventCreate View
#class EventCreateView(CreateView):
#    model = Event
#    fields = ['title','location','description','price','worker','start','end','rule']
#    template_name='page/event_form.html'
#
#    def form_valid(self, form):
#        form.instance.creator = self.request.user
#        form.instance.calendar_id = PageCalendar.objects.get(user=self.request.user).id
#        return super().form_valid(form)
