from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # Decorator-- adds functionality to an existing function
from django.contrib import messages
from django.utils import timezone
from thelab.models import Profile, ProfileUser, User
from .models import PageCalendar, Sport, ProfileSport, Location, CoachLocation, Availability, Package, Event
from .forms import LocationForm, PackageForm, AvailabilityForm, EventSportForm, EventDetailsForm, EventTimelineForm, EventRecurrenceForm
from datetime import datetime, timedelta
import calendar
from schedule.models import Rule
from .signals import coach_location

def page_browsing(request):
    # Find all coach profiles
    coach_profiles = Profile.objects.filter(coach=True)
    # Find all ProfileUser objects associated with those coaches
    coach_profile_users = ProfileUser.objects.filter(profile__in=coach_profiles)
    # Create list of just the Coach User accounts
    coaches = [cpu.user for cpu in coach_profile_users]
    # Create a list of tuples containing coach's information
    coach_data = []
    for coach in coaches:
        profile = ProfileUser.objects.get(user=coach, control_type='personal').profile
        sport = ProfileSport.objects.get(profile=profile).sport
        
        packages = Package.objects.filter(owner=coach)
        prices = [package.price for package in packages]
        lowest_price = min(prices)

        if lowest_price and sport:
            coach_data.append((coach, sport, lowest_price))

    context = {
        'coach_data': coach_data,
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
    coach = User.objects.get(pk=pk)
    coach_locations = CoachLocation.objects.filter(coach=coach)
    coach_availability = Availability.objects.filter(creator=coach)
    coach_packages = Package.objects.filter(owner=coach)

    coach_profile = ProfileUser.objects.filter(user=coach, control_type='personal').first().profile
    coach_sport = ProfileSport.objects.filter(profile=coach_profile).first().sport

    # Add calculated fields for group pricing
    for package in coach_packages:
        if package.type == "Training":
            if package.athletes == 2:
                package.price_per_athlete_2 = package.price // 2
            elif package.athletes == 3:
                package.price_per_athlete_3 = package.price // 3

    context = {
        'is_owner':is_owner,
        'coach':coach,
        'locations':coach_locations,
        'availabilities':coach_availability,
        'packages':coach_packages,
        'sport':coach_sport,
    }
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
            # Sending the save request's User to the CoachLocation creation signal (because Coaches adding a location will always want that to be one of their locations)
            coach_location(sender=Location, instance=location, location=location, user=request.user)
            ## ^^ PRETTY COOL!! This is using a signal as a function inside of a view. 
            return redirect('page_viewing', pk=request.user.pk)
    else:
        location_form = LocationForm()

    context = {
        'location_form':location_form,
    }

    return render(request, 'page/location_form.html',context)

@login_required
def search_location(request):
    # Don't know the details here
    query = request.GET.get('query', '')
    locations = Location.objects.filter(location_name__icontains=query)
    
    context = {'locations': locations, 'query': query}
    
    return render(request, 'page/location_search.html', context)

@login_required
def add_location(request, location_name):
    location = get_object_or_404(Location, location_name=location_name)

    coach_location(sender=Location, instance=location, location=location, user=request.user)

    messages.success(request, 'Location added!')
    return redirect('page_viewing', pk=request.user.pk)

@login_required
def remove_location(request, location_name):
    location = Location.objects.filter(location_name=location_name).get()
    coach_location = CoachLocation.objects.filter(location=location, coach=request.user)
    coach_location.delete()
    messages.success(request, 'Location removed!')
    return redirect('page_viewing', pk=request.user.pk)

@login_required
def set_availability(request):
    if request.method == "POST":
        availability_form = AvailabilityForm(request.POST)
        if availability_form.is_valid():
            # Straightforward inputs
            availability = Availability()
            availability.day = availability_form.cleaned_data['day']
            availability.creator = request.user
            availability.calendar = PageCalendar.objects.filter(user=request.user).first()
            availability.location = availability_form.cleaned_data['location']

            # First day
            availability.start = availability_form.cleaned_data['start_time']
            availability.end = availability_form.cleaned_data['end_time']

            # Recurrence
            availability.rule = Rule.objects.filter(name="Weekly").first()
            first_day = availability_form.cleaned_data['start_time'].date()
            availability.end_recurring_period = first_day + timedelta(days=2*365)

            # Save the availability
            availability.save()

            messages.success(request, 'Availability added!')
            return redirect('page_viewing', pk=request.user.pk)
    else:
        # Get applicable locations
        cls_on_file = CoachLocation.objects.filter(coach=request.user)
        coach_locations = [coach_location.location.id for coach_location in cls_on_file]
        locations_queryset = Location.objects.filter(pk__in=coach_locations)
        availability_form = AvailabilityForm(locations=locations_queryset)

    context = {
        'availability':availability_form,
    }
    
    return render(request, 'page/availability_form.html', context) # Current availability will need to be passed as context

@login_required
def remove_availability(request, availability_id):
    availability = Availability.objects.filter(id=availability_id)
    availability.delete()
    messages.success(request, 'Availability removed!')
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

# View for showing potential clients a Coach's still-available time slots
def check_availability(request, pk, week):
    week = int(week)
    coach = User.objects.get(pk=pk)

    # Get a coach's posted availability
    avails = Availability.objects.filter(creator=coach)
    # Break each availability down into 1 hour time slots
    slots = []
    date = datetime.now().date() + timedelta(days=7*week)
    for avail in avails:
        # 1: Find difference between today's weekday and availability's weekday
        today_index = date.weekday()
        avail_day_index = list(calendar.day_name).index(avail.day)
        day_diff = (avail_day_index - today_index)

        print(day_diff)

        # 2: Get the specific date of the availability
        specific_date = date + timedelta(days=day_diff)

        print(specific_date)

        # 3: Combine this date with the start and end times of the availability
        start_datetime = datetime.combine(specific_date, avail.start.time())
        end_datetime = datetime.combine(specific_date, avail.end.time())

        # 4: Generate 1-hour time slots within this range - [)
        current_time = start_datetime
        while current_time < end_datetime:
            slots.append(current_time)  # Add the current time slot to the list
            current_time += timedelta(hours=1)  # Increment by 1 hour

    # get coach's events for the applicable window (2 weeks long extending back and forwards a week from the current day)
    events = Event.objects.filter(creator=coach, start__gte=date-timedelta(weeks=1), end__lt=date+timedelta(weeks=1))

    # delete time slots if they're in the past or if the coach has an event during that time
    for slot in slots[:]:  # Iterating over a copy of slots to safely modify the original list
        # Check if the slot is in the past
        if slot < datetime.now():
            slots.remove(slot)
            continue  # Skip to the next slot
        
        # Check if the slot conflicts with any of the coach's events
        for event in events:
            if event.start <= slot < event.end:
                slots.remove(slot)
                continue  # Skip to the next slot once a conflict is found
    
    formatted_slots = []
    for slot in slots:
        formatted_slots.append({
            'date': slot.date(),  # Extract the date part
            'time': slot.time()   # Extract the time part
        })

    # Create a dictionary mapping days of the week to their corresponding dates (of the appropriate week)
    days_of_week = list(calendar.day_name)
    dates = {}
    for i, day in enumerate(days_of_week):
        day_date = date + timedelta(days=(i - date.weekday()))
        dates[day.lower()] = {
            'display': day_date.strftime('%m/%d'),  # For display (MM/DD)
            'compare': day_date             # For comparison (datetime.date object)
        }

    context = {
        'coach':coach,
        'week':week,
        'slots':formatted_slots,
        'dates':dates,
    }
    
    return render(request, 'page/partials/time_slots.html', context)


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
