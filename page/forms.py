from datetime import datetime, time
from django import forms
from django.contrib.auth.models import User
from .models import Event, EventSport, Location, Package

class LocationForm(forms.ModelForm):

    class Meta:
        model = Location
        fields = ['location_name','location_type','hyperlink','street_address','location_city','location_state','location_zip']

class PackageForm(forms.ModelForm):

    class Meta:
        model = Package
        fields = ['type', 'price', 'duration', 'number_of_sessions', 'location', 'description']

class EventSportForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        sports = kwargs.pop('sports', None)
        super().__init__(*args, **kwargs)
        if sports:
            self.fields['sport'].queryset = sports

    class Meta:
        model = EventSport
        fields = ['sport']

class EventDetailsForm(forms.ModelForm):
    
    # Restricting the available locations to those associated with the Coach (passed to this Form through the coach_locations variable in the create_event view)
    def __init__(self, *args, **kwargs):
        locations = kwargs.pop('locations', None)
        super().__init__(*args, **kwargs)
        if locations:
            self.fields['location'].queryset = locations

    class Meta:
        model = Event
        fields = ['title','location','location_notes','description','event_type'] # 'price'

class EventTimelineForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type':'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type':'time'}))

    class Meta:
        model = Event
        fields = ['date','start_time','end_time']

    # Changing the fields into datetime objects
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Here
        start_datetime = datetime.combine(date, start_time)
        cleaned_data['start_time'] = start_datetime
        end_datetime = datetime.combine(date, end_time)
        cleaned_data['end_time'] = end_datetime

        return cleaned_data

class EventRecurrenceForm(forms.ModelForm):
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))

    class Meta:
        model = Event
        fields = ['rule','end_date']

    def clean(self):
        cleaned_data = super().clean()
        end_date = cleaned_data.get('end_date')
        if end_date:
            cleaned_data['end_time'] = time(23, 59)
        return cleaned_data
