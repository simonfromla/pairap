from user_profile.models import Profile


def notifications_unread(request):
    try:
        profile = Profile.objects.get(user__username=request.user)
        return {'notifyme': profile.user.notifications.unread()}
    except Profile.DoesNotExist:
        return {}
