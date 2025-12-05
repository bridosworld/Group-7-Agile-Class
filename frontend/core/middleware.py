from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse
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


class Enforce2FAMiddleware:
    """Enforce 2FA setup for all authenticated users"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that should be accessible without 2FA setup
        self.exempt_urls = [
            '/account/',  # All 2FA URLs
            '/login/',
            '/logout/',
            '/register/',
            '/static/',
            '/media/',
            '/admin/',
            '/',  # Home page
            '/products/',  # Product listing
        ]
    
    def __call__(self, request):
        # Check if user is authenticated and verified with OTP
        if request.user.is_authenticated and hasattr(request.user, 'is_verified'):
            # Only enforce if user has passed OTP verification
            if request.user.is_verified():
                # Check if any exempt URL matches
                path = request.path
                is_exempt = any(path.startswith(url) for url in self.exempt_urls)
                
                if not is_exempt:
                    # Check if user has 2FA device configured
                    if not request.user.totpdevice_set.filter(confirmed=True).exists():
                        # Redirect to 2FA setup
                        setup_url = reverse('two_factor:setup')
                        if path != setup_url:
                            return redirect(setup_url)
        
        response = self.get_response(request)
        return response
