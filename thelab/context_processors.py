from .models import ProfileUser

def user_profile_processor(request):
    profile = None
    user = None
    if request.user.is_authenticated:
        try:
            profile_user = ProfileUser.objects.get(user=request.user, control_type='personal')
            profile = profile_user.profile
            user = profile_user.user
        except ProfileUser.DoesNotExist:
            pass
    
    return {
        'profile': profile,
        'user': user,
    }