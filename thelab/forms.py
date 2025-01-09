from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Application

# User (Profile) registration
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name','last_name','email','password1','password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def save(self, commit=True):
        # Call the parent save method, but don't commit yet
        user = super().save(commit=False)
       # Set the username as first_name + last_name in lowercase
        base_username = (self.cleaned_data['first_name'] + self.cleaned_data['last_name']).lower()
        user.username = base_username

        # Ensure the username is unique
        if User.objects.filter(username=user.username).exists():
            n = 2
            while True:
                new_username = f"{base_username}{n}"
                if not User.objects.filter(username=new_username).exists():
                    user.username = new_username
                    break
                n += 1

        if commit:
            user.save()

        return user

# User updating
class UserUpdateForm(forms.ModelForm):
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), required=False)

    class Meta:
        model = User
        fields = ['username','email','image','first_name','last_name','city','state','birthday'] # changing your password will be a separate process

# Applications are manually approved/denied in Admin
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields  = ['sport','team','roster']