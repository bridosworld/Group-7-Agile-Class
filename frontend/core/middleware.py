from django.utils import timezone
from core.models import Subscription

class SubscriptionExpiryMiddleware:
    """Automatically update expired subscriptions on each request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check for expired subscriptions if user is authenticated
        if request.user.is_authenticated:
            now = timezone.now()
            Subscription.objects.filter(
                user=request.user,
                status='active',
                expires_at__lte=now
            ).update(status='expired')
        
        response = self.get_response(request)
        return response
