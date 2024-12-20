from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from thelab.models import ProfileUser
from page.models import Event
from . import forms
from .models import EventAttendee

# not sure how to define the request on a List based view
def get_profile_user(request):
    try:
        profile_user = ProfileUser.objects.get(user=request.user,control_type='personal')
        profile = profile_user.profile
        user = profile_user.user
    except:
        profile= None
        user=None
    context = {
        'profile':profile,
        'user':user
    }
    return profile, user, context

# ----------- # Class-based views (different types): List, Detail, Create, Update, Delete (this is a List)
class EventListView(ListView):
    model = Event
    template_name = 'events/browse_events.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'events'

    # adding the title of the page to the context passed (in addition to the events)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Find Events'
        #profile_user = ProfileUser.objects.get(user=request.user)
        #profile = profile_user.profile
        #context['profile'] = profile
        return context

    def get_queryset(self): # I'm assuming 'querysets' can be effected by recommendation algorithms
        return Event.objects.all()
# ----------------------------------------------------------------------------------------- # Class-based views (different types): List, Detail, Create, Update, Delete (this is a Detail)
class EventDetailView(DetailView):
    model = Event
    template_name='events/view_event.html'


def create_attendee(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        # Current handling of registration --> save attendee(s) and redirect to event browsing
        
        formset = forms.AttendeeFormSet(request.POST, queryset=EventAttendee.objects.none())
        if formset.is_valid():
            # Process the formset data (create, update, or delete attendees)
            instances = formset.save(commit=False)
            for instance in instances:
                instance.event = event
                instance.save()
            print(instances)
            formset.save_m2m()  # Include this for completeness
            messages.success(request, f'Attendee(s) created!')
            return redirect('browse_events') # Redirect to a success page
    else:
        formset = forms.AttendeeFormSet(queryset=EventAttendee.objects.none())

    return render(request, 'events/attendee_form.html',{'formset':formset, 'event':event})

# regular view function // is going to have to be modified // this is the precursor to the Stripe integration (step 1 is to make the EventAttendee a Stripe Product, step 2 is to make the Attendee model the input for shopping cart quantity)
def signup(request):
    context = {
        'event' : Event.objects.all()
    }
    return render(request, 'events/signup.html', context)