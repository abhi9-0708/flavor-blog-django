from datetime import date
from django.utils.deprecation import MiddlewareMixin
from .models import Profile

class SubscriptionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=request.user)
            request.is_premium_user = (
                profile.is_subscribed and
                (profile.subscription_end_date is None or profile.subscription_end_date >= date.today())
            )
        else:
            request.is_premium_user = False