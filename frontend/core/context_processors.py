from django.conf import settings

def products_context(request):
    """Add products to all templates"""
    from .models import Product
    return {
        'products': Product.objects.filter(is_active=True)[:6]
    }

def stripe_context(request):
    """Add Stripe public key to all templates - ADD THIS FUNCTION"""
    return {
        'STRIPE_PUBLIC_KEY': getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    }