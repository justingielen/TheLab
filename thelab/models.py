from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from PIL import Image # for re-sizing profile pictures
from phonenumber_field.modelfields import PhoneNumberField

user_types = {
    'person':'person',
    'business':'business'
}

# User accounts
class User(AbstractUser):
    image = models.ImageField(default='user_pics/default.jpg', upload_to='user_pics')
    type = models.CharField(max_length=20,choices=user_types,default="person")
    phone = PhoneNumberField(blank=True, null=True, unique=True)

    def __str__(self):
        return f"@{self.username}"

    groups = models.ManyToManyField(
        Group,
        related_name='thelab_user_set',  # Avoids clash with auth.User.groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='thelab_user_permissions',  # Avoids clash with auth.User.user_permissions
        blank=True
    )

    #  Re-defining the save User function to re-size any uploaded image to a max of 300x300
    def save(self, *args, **kwargs):
        super().save(*args,**kwargs) # args/kwargs are ensuring that any arguments expected by the original save() method are correctly handled

        if self.image: # If an image was passed to the User 
            img = Image.open(self.image.path) # opens the image of the current instance

            if img.height > 300 or img.width > 300:
                output_size = (300,300)
                img.thumbnail(output_size)
                img.save(self.image.path)
        else: # If no image was uploaded, assign them the default picture
            img= Image.open('media/user_pics/default.jpg')
            img.save(self.image.path)
    
states = {
    'AL':'AL','AK':'AK',
    'AZ':'AZ','AR':'AR',
    'CA':'CA','CO':'CO',
    'CT':'CT','DE':'DE',
    'DC':'DC','FL':'FL',
    'GA':'GA','HI':'HI',
    'ID':'ID','IL':'IL',
    'IN':'IN','IA':'IA',
    'KS':'KS','KY':'KY',
    'LA':'LA','ME':'ME', 
    'MD':'MD','MA':'MA',
    'MI':'MI','MN':'MN',
    'MS':'MS','MO':'MO',
    'MT':'MT','NE':'NE',
    'NV':'NV','NH':'NH',
    'NJ':'NJ','VA':'VA',
    'NM':'NM','VI':'VI',
    'NY':'NY','WA':'WA',
    'NC':'NC','WV':'WV',
    'ND':'ND','WI':'WI',
    'WY':'WY','OH':'OH',
    'OK':'OK','OR':'OR',
    'PA':'PA','PR':'PR',
    'RI':'RI','SC':'SC',
    'SD':'SD','TN':'TN',
    'TX':'TX','UT':'UT','VT':'VT',
}
# Profile automatically created for new personal Users
class Profile(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True, default="(last name)")
    birthday = models.DateField(help_text="Format: YYYY-MM-DD (include the dashes)", blank=True, null=True)
    city = models.CharField(max_length=40,blank=True)
    state = models.CharField(max_length=25,choices=states,blank=True)
    coach = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Notifications -------------------------------------------------------------------------------------
notif_types = {
    'profile_creation':'profile_creation',
    'coach_approval':'coach_approval',
    'event_suggestion':'event_suggestion',
}

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    type = models.CharField(max_length=50, choices=notif_types, default='profile_creation')

    def __str__(self):
        return f"@{self.user.username} - {self.type}"

    class Meta:
        ordering = ['-timestamp']
# Notifications -------------------------------------------------------------------------------------
    
control_types = {
    'personal':'personal',
    'parent':'parent',
    'business':'business',
    'boss':'boss'
}
class ProfileUser(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    control_type = models.CharField(max_length=15,choices=control_types,default='personal')

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name} - {self.user} ({self.control_type})"
    
# Application for Profiles to authenticate playing/coaching resume   
# "approved" starts out as unknown, and is edited to True or False in admin, based on a manual review of the Application    
# DO NOT DELETE APPLICATIONS
# DO NOT DELETE APPLICATIONS
# DO NOT DELETE APPLICATIONS     //// "Coach" status is set based on the existence of approved applications on file (see "check_coach" in thelab/signals.py)
class Application(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sport = models.CharField(max_length=20,help_text="(Just the sport- leave out Men's or Women's & whether College or Professional)")
    team = models.CharField(max_length=50,blank=True, help_text="(i.e., the college/university or professional organization)")
    roster = models.TextField(help_text='(Copy-and-paste the link to a roster of a college/professional team on which you are or were a player or a coach)') # unique = True (can't submit same record twice)
    approved = models.BooleanField(null=True)

    def __str__(self):
        if self.approved == True:
            result = "approved"
        elif self.approved == False:
            result = "denied"
        else:
            result = "undecided"

        return f"{self.profile.first_name} {self.profile.last_name} - {self.team} //// {self.sport} ({result})"
# ----------------------------------------------------------------------------------------------------

# Home Calendar automatically created for Profiles ---------------------------------------------------
from schedule.models import Calendar as BaseCalendar

class HomeCalendar(BaseCalendar):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    def save(self, *args, **kwargs):
        self.name = f"Home Calendar for {self.user.username}"
        # Customize slug generation to ensure uniqueness
        self.slug = f"home_calendar_{self.user.username}"
        super().save(*args, **kwargs)
              
    def __str__(self):
        return self.name
# ----------------------------------------------------------------------------------------------------

