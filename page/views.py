from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # Decorator-- adds functionality to an existing function
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.urls import reverse

from thelab.models import User, UserRelation, Notification
from .models import PageCalendar, Sport, CoachSport, Location, CoachLocation, Availability, Package, PackageLocation, Attendee, AttendeeParent, Event, EventAttendee
from .forms import LocationForm, PackageForm, PackageLocationForm, AvailabilityForm, AttendeeForm, ParentForm, EventSportForm, EventDetailsForm, EventTimelineForm, EventRecurrenceForm
from datetime import datetime, timedelta
import calendar
from schedule.models import Rule
from .signals import coach_location

# emails
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail
import base64

def page_browsing(request):
    # Find all coaches
    coaches = User.objects.filter(coach=True)
    # Create a list of tuples containing coach's information
    coach_data = []
    for coach in coaches:
        sports = []
        coachsports = CoachSport.objects.filter(coach=coach)
        for coachsport in coachsports:
            sports.append(coachsport.sport)
        
        packages = Package.objects.filter(owner=coach)
        prices = [package.price for package in packages]
        try:
            lowest_price = min(prices)
        except ValueError:
            lowest_price = 0

        if lowest_price and sports:
            coach_data.append((coach, sports, lowest_price))

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
    sports = []
    coachsports = CoachSport.objects.filter(coach=coach)
    for coachsport in coachsports:
        sports.append(coachsport.sport)

    # Combine and order suggested and upcoming events
    # Fetch all events for the coach
    all_events = Event.objects.filter(
        creator=coach
    ).order_by('start')

    # Filter EventAttendees based on the specific events the coach owns
    event_ids = [event.id for event in all_events]  # Get the IDs of the coach's events

    # Fetch the attendees for only the relevant events
    event_attendees = EventAttendee.objects.filter(event_id__in=event_ids).select_related('attendee')

    # Create a mapping of event IDs to their attendees
    attendees_mapping = {}
    for attendee in event_attendees:
        if attendee.event.id not in attendees_mapping:
            attendees_mapping[attendee.event.id] = []
        attendees_mapping[attendee.event.id].append(attendee.attendee)

    # Attach the attendees to the corresponding events in all_events
    for event in all_events:
        event.attendees = attendees_mapping.get(event.id, [])

    # Add calculated location info and per-athlete pricing
    package_locations = {}
    for package in coach_packages:
        # Calculate package price per athlete
        if package.type == "Training":
            if package.athletes == 1:
                package.price_per_athlete = package.price // 1
            if package.athletes == 2:
                package.price_per_athlete = package.price // 2
            elif package.athletes == 3:
                package.price_per_athlete = package.price // 3
        # Map location info to the packages 
        locations = PackageLocation.objects.filter(package=package)
        if locations.count() == 1:
            package.location_name = locations.first().location.name
        else:
            package.location_name = "Multiple Locations"

    context = {
        'is_owner':is_owner,
        'coach':coach,
        'sports':sports,
        'all_events':all_events,
        'event_attendees':event_attendees,
        'locations':coach_locations,
        'availabilities':coach_availability,
        'packages':coach_packages,
        'package_locations':package_locations,
    }
    return render(request, 'page/viewing.html',context=context)

@login_required
def create_location(request):
    if request.method == 'POST':
        location_form = LocationForm(request.POST)
        if location_form.is_valid():
            # handle the data
            location = Location()
            location.name = location_form.cleaned_data['name']
            location.type = location_form.cleaned_data['type']
            location.hyperlink = location_form.cleaned_data['hyperlink']
            location.street_address = location_form.cleaned_data['street_address']
            location.city = location_form.cleaned_data['city']
            location.state = location_form.cleaned_data['state']
            location.zip = location_form.cleaned_data['zip']
            
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
    locations = Location.objects.filter(name__icontains=query)
    
    context = {'locations': locations, 'query': query}
    
    return render(request, 'page/location_search.html', context)

@login_required
def add_location(request, name):
    location = get_object_or_404(Location, name=name)

    coach_location(sender=Location, instance=location, location=location, user=request.user)

    messages.success(request, 'Location added!')
    return redirect('page_viewing', pk=request.user.pk)

@login_required
def remove_location(request, name):
    location = Location.objects.filter(name=name).get()
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
    
# 
@login_required
def create_package(request):
    # Helper function to get the required querysets
    def get_querysets():
        # Get applicable locations
        cls_on_file = CoachLocation.objects.filter(coach=request.user)
        coach_locations = [coach_location.location.id for coach_location in cls_on_file]
        locations_queryset = Location.objects.filter(pk__in=coach_locations)

        # Get applicable sports
        coach_sport_objects = CoachSport.objects.filter(coach=request.user)
        coach_sports = [profile_sport.sport.id for profile_sport in coach_sport_objects]
        sports_queryset = Sport.objects.filter(pk__in=coach_sports)
        
        return sports_queryset, locations_queryset

    # Get the querysets regardless of request method
    sports_queryset, locations_queryset = get_querysets()

    if request.method == 'POST':
        # handle form info
        package_form = PackageForm(
            request.POST,
            sports=sports_queryset,
        )
        package_location_form = PackageLocationForm(
            request.POST,
            locations=locations_queryset

        )
        if package_form.is_valid() and package_location_form.is_valid():
            package = package_form.save(commit=False)
            package.owner = request.user
            package.save()

            # Create PackageLocation objects for each selected location
            selected_locations = package_location_form.cleaned_data['locations']
            for location in selected_locations:
                PackageLocation.objects.create(
                    package=package,
                    location=location
                )

            messages.success(request, 'Package added!')
            return redirect('page_viewing', pk=request.user.pk)
    
    else:
        package_form = PackageForm(sports=sports_queryset)
        package_location_form = PackageLocationForm(locations=locations_queryset)

    context = {
        'package':package_form,
        'package_location':package_location_form,
    }

    return render(request, 'page/package_form.html', context)

def select_location(request, pk):
    """
    Intermediate view between package selection and availability checking.
    Handles location selection for multi-location packages.
    """
    # Fetch the package based on package_id from the GET parameter
    package_id = request.GET.get('package_id')
    package = get_object_or_404(Package, id=package_id)

     # Get all locations associated with this package
    package_locations = PackageLocation.objects.filter(package=package)
    locations = [package_location.location for package_location in package_locations]
    selected_location = request.GET.get('selected_location')

    context = {
        'package': package,
        'locations': locations,
        'selected_location':selected_location,
        'pk':pk,
    }

    return render(request, 'page/partials/select_location.html', context)

# View for showing potential clients a Coach's still-available time slots
def check_availability(request, pk, week):
    week = int(week)
    coach = User.objects.get(pk=pk)
    package_id = request.GET.get('package_id')
    location_id = request.GET.get('location_id')

    package = get_object_or_404(Package, id=package_id)
    location = get_object_or_404(Location, id=location_id)
    print(location)

    # Get a coach's posted availability
    avails = Availability.objects.filter(creator=coach, location=location)

    # Break each availability down into 1 hour time slots
    slots = []
    date = datetime.now().date() + timedelta(days=7*week)
    for avail in avails:
        # 1: Find difference between today's weekday and availability's weekday
        today_index = date.weekday()
        avail_day_index = list(calendar.day_name).index(avail.day)
        day_diff = (avail_day_index - today_index)

        # 2: Get the specific date of the availability
        specific_date = date + timedelta(days=day_diff)

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
                if slot in slots:
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
        'package':package,
        'slots':formatted_slots,
        'dates':dates,
        'location':location,
    }
    
    return render(request, 'page/partials/time_slots.html', context)

def signup(request, date, time, week):
    # get the selected package & location
    package = Package.objects.get(pk=request.GET.get('package_id'))
    coach = User.objects.get(pk=request.GET.get('coach_id'))
    location = Location.objects.get(pk=request.GET.get('location_id'))


    # convert date and time (strings) to start_time and end_time (datetimes)
    date = datetime.strptime(date, "%Y-%m-%d").date()  # Convert to a date object
    start_time = datetime.strptime(time, "%H:%M:%S").time()  # Convert to a time object
    start_time = datetime.combine(date, start_time)
    end_time = start_time + timedelta(hours=1)

    # Create the AttendeeFormSet with a dynamic number of forms based on `package.athletes`
    AttendeeFormSet = modelformset_factory(Attendee, form=AttendeeForm, extra=package.athletes)

    if request.method == 'POST':
        # Capture attendee and parent info from the form 
        formset = AttendeeFormSet(request.POST)
        parent_form = ParentForm(request.POST or None)

        if formset.is_valid() and parent_form.is_valid():
            # Save attendee(s) & parent
            attendees = formset.save()
            parent = parent_form.save()
            
            # Get coach's calendar
            page_calendar = PageCalendar.objects.get(user=coach)
            
            # Create a suggested event (is_accepted = False) that's private (max_attendance = package.athletes)
            event = Event(
                title=f"{package.sport} {package.type}",
                location=location,
                start=start_time,
                end=end_time,
                type=package.type,
                creator=coach,
                is_accepted=False,  # Needs coach approval
                max_attendance=package.athletes, 
                calendar=page_calendar
            )
            event.save()
            
            # Add attendees to suggested event
            for attendee in attendees:
                EventAttendee.objects.create(
                    event=event,
                    attendee=attendee
                )
                # Create parent relation to attendees
                AttendeeParent.objects.create(
                    attendee=attendee,
                    parent=parent,
                )
            
            # Send email to Coach
            with open('C:/Users/Justin/.virtualenvs/TheLab1_0/thelab/static/images/green_logo.png', 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Send welcome email
            html_message = render_to_string(
                'emails/event_suggested.html',
                {
                    'encoded_image':encoded_image,
                    'package': package,
                    'location': location,
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'attendees': attendees,
                }
            )
            # (include both html and plain text versions to avoid being marked as spam)
            plain_message = strip_tags(html_message)
            send_mail(
                subject='An event has been requested!',
                message=plain_message,
                html_message=html_message,
                from_email=settings.FROM_EMAIL_ADMIN,  # From admin email
                recipient_list=[coach.email],
                auth_user=settings.FROM_EMAIL_ADMIN,
                auth_password=settings.EMAIL_ADMIN_PASSWORD,
                fail_silently=False,
            )

            # Handle payment choice
            payment_type = request.POST.get('payment_type')
            
            if payment_type == 'online':
                # add this with Stripe (don't worry about this section yet)
                pass
            else:  # in_person payment
                messages.success(
                    request, 
                    'Your session has been requested. We will notify you when your coach has accepted!'
                )
                # Notify coach about new event suggestion
                notification = Notification(
                    user=coach,
                    message="A new event has been suggested! Please Accept or Deny it as soon as possible.",
                    type='event_suggestion'
                )
                notification.save()

                # For HTMX, we need to send a response that includes HX-Redirect
                response = HttpResponse()
                redirect_url = reverse('createprofile')
                passed = True

                # Add query parameters for pre-filling the form
                redirect_url_with_params = f"{redirect_url}?first_name={parent.first_name}&last_name={parent.last_name}&email={parent.email}&parent={passed}"


                response['HX-Redirect'] = redirect_url_with_params
                return response
        
    else:
        formset = AttendeeFormSet(queryset=Attendee.objects.none())
        parent_form = ParentForm()

    context = {
        'package':package, 
        'week':week,
        'coach':coach,
        'date':date, 
        'start_time':start_time, 
        'end_time':end_time, 
        'formset':formset,
        'parent_form':parent_form,
        'location':location,
    }
    
    return render(request, 'page/partials/signup.html', context)

def accept_event(request, pk):
    event = Event.objects.get(pk=request.GET.get('event_id'))
    event.is_accepted = True
    event.save()

    coach = User.objects.get(pk=pk)

    context = {
        'coach':coach,
        'event':event,
    }

    return render(request, 'page/partials/list_event_item.html', context)

@login_required
def create_event(request):
    if request.method == 'POST':
        event_details = EventDetailsForm(request.POST)
        event_timeline = EventTimelineForm(request.POST)
        event_recurrence = EventRecurrenceForm(request.POST)
        
        if all([event_details.is_valid(), event_timeline.is_valid(), event_recurrence.is_valid()]):
            event = Event()
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
        
    else:
        # Get applicable locations
        cls_on_file = CoachLocation.objects.filter(coach=request.user)
        coach_locations = [coach_location.location.id for coach_location in cls_on_file]
        locations_queryset = Location.objects.filter(pk__in=coach_locations)

        # Get applicable sports
        coach_sport_objects = CoachSport.objects.filter(coach=request.user)
        coach_sports = [profile_sport.sport.id for profile_sport in coach_sport_objects]
        sports_queryset = Sport.objects.filter(pk__in=coach_sports)

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
