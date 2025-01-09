def user_profile_processor(request):
    user = None
    alerts = None
    if request.user.is_authenticated:
        try:
            user = request.user
            alerts = bool(user.notifications.filter(is_read=False))
        except request.user.DoesNotExist:
            pass
    
    return {
        'user': user,
        'alerts':alerts,
    }