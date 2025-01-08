from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, Application

# User (Profile) registration
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username','email','password1','password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

# User updating
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','image'] # changing your password will be a separate process

# Profile Updating
class ProfileUpdateForm(forms.ModelForm):
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), required=False)

    class Meta:
        model = Profile
        fields = ['first_name','last_name','city','state','birthday']

# Applications are manually approved/denied in Admin
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields  = ['sport','team','roster']