from django import forms
from allauth.account.forms import SignupForm
from .models import User, Application

# User (Profile) registration
class UserRegistrationForm(SignupForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name','last_name','email','password1','password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password help text to simplify form
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    # Set the username as first_name + last_name in lowercase
    def save(self, request):
        # First, let allauth create the user instance
        user = super().save(request)

        # Set first and last name
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # set base username
        base_username = (self.cleaned_data['first_name'] + self.cleaned_data['last_name']).lower()
        user.username = base_username

        # Ensure the username is unique (add numbers to end if not)
        if User.objects.filter(username=user.username).exists():
            n = 2
            while True:
                new_username = f"{base_username}{n}"
                if not User.objects.filter(username=new_username).exists():
                    user.username = new_username
                    break
                n += 1

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