from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from PIL import Image # for re-sizing profile pictures
from phonenumber_field.modelfields import PhoneNumberField

user_types = {
    'person':'person',
    'business':'business'
}

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

# User accounts
class User(AbstractUser):
    image = models.ImageField(default='user_pics/default.jpg', upload_to='user_pics')
    type = models.CharField(max_length=20,choices=user_types,default="person")
    phone = PhoneNumberField(blank=True, null=True, unique=True)
    birthday = models.DateField(help_text="Format: YYYY-MM-DD (include the dashes)", blank=True, null=True)
    city = models.CharField(max_length=40,blank=True)
    state = models.CharField(max_length=25,choices=states,blank=True)
    coach = models.BooleanField(default=False)

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

        if self.image and self.image.name != 'user_pics/default.jpg': # If a user-uploaded image was passed to the User 
            img = Image.open(self.image.path) # opens the image of the current instance

            if img.height > 300 or img.width > 300:
                output_size = (300,300)
                img.thumbnail(output_size)
                img.save(self.image.path)
        else: # If no image was uploaded, assign them the default picture
            img= Image.open('media/user_pics/default.jpg')
            img.save(self.image.path)

# Notifications -------------------------------------------------------------------------------------
notif_types = {
    'profile_creation':'profile_creation',
    'coach_application':'coach_application',
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
    'parent':'parent',
    'admin':'admin',
    'boss':'boss'
}
class UserRelation(models.Model):
    controller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='controllers')
    controlled = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='controlled_by')
    control_type = models.CharField(max_length=15,choices=control_types,default='parent')

    def __str__(self):
        return f"{self.controller.first_name} {self.controller.last_name} - @{self.controlled.username} ({self.control_type})"
    
# Application for Users to authenticate playing/coaching resume   
# "approved" starts out as unknown, and is edited to True or False in admin, based on a manual review of the Application    
# DO NOT DELETE APPLICATIONS
# DO NOT DELETE APPLICATIONS
# DO NOT DELETE APPLICATIONS     //// "Coach" status is set based on the existence of approved applications on file (see "check_coach" in thelab/signals.py)
class Application(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sport = models.CharField(max_length=20,help_text="(Just the sport- leave out Men's or Women's & whether College or Professional)")
    team = models.CharField(max_length=50,blank=True, help_text="(i.e., the college/university or professional organization)")
    roster = models.TextField(help_text='(Copy-and-paste the link to the roster of any college/professional team on which you are or were a player or a coach)') # unique = True (can't submit same record twice)
    approved = models.BooleanField(null=True)

    def __str__(self):
        if self.approved == True:
            result = "approved"
        elif self.approved == False:
            result = "denied"
        else:
            result = "undecided"

        return f"{self.user.first_name} {self.user.last_name} - {self.team} //// {self.sport} ({result})"
