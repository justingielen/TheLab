from datetime import datetime, time, timedelta
import calendar
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Event, EventSport, Location, Availability, Package, PackageLocation, Attendee, Parent


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name','type','hyperlink','street_address','city','state','zip']

class AvailabilityForm(forms.ModelForm):
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type':'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type':'time'}))

    # Restricting the available locations to those associated with the Coach (passed to this Form through the coach_locations variable in the set_availability view)
    def __init__(self, *args, **kwargs):
        locations = kwargs.pop('locations', None)
        super().__init__(*args, **kwargs)
        if locations:
            self.fields['location'].queryset = locations

    class Meta:
        model = Availability
        fields = ['day','location','start_time','end_time']

    # Changing the fields into datetime objects
    def clean(self):
        cleaned_data = super().clean()

        # get cleaned fields
        day_string = cleaned_data.get('day')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # convert the day string into day-of-week integer
        target_weekday = list(calendar.day_name).index(day_string)

        # get today's date and weekday
        today = datetime.now().date()
        today_weekday = today.weekday() # Monday = 0, ..., Sunday = 6

        # calculate difference in days to the target weekday
        days_until_target = (target_weekday - today_weekday + 7) % 7
        if days_until_target == 0:
            days_until_target = 7 # If today is the target day, use the next occurence

        # Calculate target date
        target_date = today + timedelta(days=days_until_target)

        
        # Combine target_date with start_time and end_time to create datetime objects
        start_datetime = datetime.combine(target_date, start_time)
        end_datetime = datetime.combine(target_date, end_time)

        # Ensure start_time is before end_time
        if start_datetime >= end_datetime:
          raise ValidationError("'start_time' must be earlier than 'end_time'.")

        # Here
        cleaned_data['start_time'] = start_datetime
        cleaned_data['end_time'] = end_datetime

        return cleaned_data


class PackageForm(forms.ModelForm):
    # Restricting the available sports to those associated with the Coach (passed to this Form through the create_package view)
    def __init__(self, *args, **kwargs):
        sports = kwargs.pop('sports', None)
        super().__init__(*args, **kwargs)
        self.fields['sport'].queryset = sports

    class Meta:
        model = Package
        fields = ['sport', 'type', 'price', 'duration', 'athletes', 'description']

class PackageLocationForm(forms.ModelForm):
    # Making the 
    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )

    # Restricting the available locations to those associated with the Coach (passed to this Form through the create_package view)
    def __init__(self, *args, **kwargs):
        locations = kwargs.pop('locations', None)
        super().__init__(*args, **kwargs)
        self.fields['locations'].queryset = locations
        location_help_text=(
            f"<small class='text-muted'><i>(Note: locations must be added to your Profile before they can be used in a Package. </i></small>"
            f"<small class='text-muted'><i>You can add them <a href='{reverse('location_search')}'>here</a>!)</i></small>"
        )
        self.fields['locations'].help_text = location_help_text

    class Meta:
        model = PackageLocation
        fields = ['locations']


class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['first_name','last_name','age','attendee_notes']

AttendeeFormSet = forms.modelformset_factory(Attendee, form=AttendeeForm, extra=1)

class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['first_name','last_name','email']


class EventSportForm(forms.ModelForm):
    # Restricting the available sports to those associated with the Coach (passed to this Form through the coach_locations variable in the create_event view)
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
        fields = ['title','price','location','location_notes','description','event_type'] # 'price'

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
