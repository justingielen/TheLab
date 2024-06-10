from django import forms
from .models import EventAttendee

class EventAttendeeCreateForm(forms.ModelForm):
    class Meta:
        model = EventAttendee
        fields = ['first_name','last_name','age','attendee_notes']

AttendeeFormSet = forms.modelformset_factory(EventAttendee, form=EventAttendeeCreateForm, extra=1)