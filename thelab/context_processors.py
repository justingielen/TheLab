from .models import ProfileUser

def user_profile_processor(request):
    profile = None
    user = None
    alerts = None
    if request.user.is_authenticated:
        try:
            profile_user = ProfileUser.objects.get(user=request.user, control_type='personal')
            profile = profile_user.profile
            user = profile_user.user
            alerts = bool(user.notifications.filter(is_read=False))
        except ProfileUser.DoesNotExist:
            pass
    
    return {
        'profile': profile,
        'user': user,
        'alerts':alerts,
    }