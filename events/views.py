from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.contrib import messages
from page.models import Event
from page import forms
from .models import *
from page.models import Attendee

# ----------- # Class-based views (List)
class EventListView(ListView):
    model = Event
    template_name = 'events/browse_events.html' 
    context_object_name = 'events'

    # adding the title of the page to the context passed (in addition to the events)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Find Events'
        return context

    def get_queryset(self):
        return Event.objects.filter(is_accepted=True)
# ---------- # Class-based views (Detail)
class EventDetailView(DetailView):
    model = Event
    template_name='events/view_event.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Event Details"
        return context

# View to handle initial 'Sign Up' click & EventAttendee formset submission
def create_attendee(request, pk):
    event = Event.objects.get(pk=pk)

    if request.method == 'POST': 
        formset = forms.AttendeeFormSet(request.POST)
        if formset.is_valid():
            # Process the formset data (creating EventAttendees)
            instances = formset.save(commit=False)
            for instance in instances:
                instance.event = event
                instance.save()
            formset.save_m2m()  # Include this for completeness
            messages.success(request, 'Attendee(s) created!')
            response = HttpResponse()
            response['HX-Redirect'] = redirect('browse_events').url
            return response
    
    formset = forms.AttendeeFormSet(queryset=Attendee.objects.none())
    return render(request, 'events/partials/attendee_formset.html',{'formset':formset, 'event':event})

# View to add empty attendee form to the end of the current attendee formset
def add_attendee(request, pk):
    # Get the current count of forms from the HTMX request's form_count parameter (which is defined in attendee_formset.html using JavaScript's document query selector on ".attendee-form" elements)
    total_forms = int(request.GET.get('form_count', 0))

    # Create additional form from Django's special formset property (.empty_form)
    empty_form = forms.AttendeeFormSet().empty_form
    
    # Replace the empty form's default index (stored in __prefix__) with the appropriate index (the count of the formset)
    empty_form.prefix = empty_form.prefix.replace('__prefix__', str(total_forms))

    # Return the rendered empty form
    return render(request, 'events/partials/attendee_form.html', {'form':empty_form})