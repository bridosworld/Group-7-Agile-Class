import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'terrascope.settings')
django.setup()

from core.models import Product, Subscription
from django.conf import settings

print("=" * 60)
print("TERRASCOPE SYSTEM CHECK")
print("=" * 60)

# Check 1: Products in database
print("\n1. CHECKING PRODUCTS:")
print("-" * 60)
products = Product.objects.all()
if products.exists():
    for product in products:
        print(f"\nProduct: {product.name}")
        print(f"  ID: {product.id}")
        print(f"  Price 1 Month: £{product.price_1_month if hasattr(product, 'price_1_month') else 'MISSING FIELD'}")
        print(f"  Price 2 Months: £{product.price_2_months if hasattr(product, 'price_2_months') else 'MISSING FIELD'}")
        print(f"  Price 1 Year: £{product.price_1_year if hasattr(product, 'price_1_year') else 'MISSING FIELD'}")
        print(f"  API Calls Limit: {product.api_calls_limit if hasattr(product, 'api_calls_limit') else 'MISSING FIELD'}")
        print(f"  Data Limit MB: {product.data_limit_mb if hasattr(product, 'data_limit_mb') else 'MISSING FIELD'}")
        print(f"  Short Description: {product.short_description if hasattr(product, 'short_description') else 'MISSING FIELD'}")
        print(f"  Active: {product.is_active if hasattr(product, 'is_active') else 'MISSING FIELD'}")
else:
    print("❌ NO PRODUCTS FOUND IN DATABASE!")

# Check 2: Product Model Fields
print("\n2. CHECKING PRODUCT MODEL FIELDS:")
print("-" * 60)
product_fields = [f.name for f in Product._meta.get_fields()]
required_fields = ['price_1_month', 'price_2_months', 'price_1_year', 'api_calls_limit', 'data_limit_mb', 'short_description']
for field in required_fields:
    if field in product_fields:
        print(f"  ✅ {field}")
    else:
        print(f"  ❌ {field} - MISSING!")

# Check 3: Subscription Model Fields
print("\n3. CHECKING SUBSCRIPTION MODEL FIELDS:")
print("-" * 60)
subscription_fields = [f.name for f in Subscription._meta.get_fields()]
important_fields = ['user', 'product', 'status', 'expires_at', 'api_calls_made', 'api_calls_limit', 'total_cost']
for field in important_fields:
    if field in subscription_fields:
        print(f"  ✅ {field}")
    else:
        print(f"  ❌ {field} - MISSING!")

# Check 4: Stripe Configuration
print("\n4. CHECKING STRIPE CONFIGURATION:")
print("-" * 60)
if hasattr(settings, 'STRIPE_PUBLIC_KEY'):
    key = settings.STRIPE_PUBLIC_KEY
    if key and key.startswith('pk_'):
        print(f"  ✅ STRIPE_PUBLIC_KEY: {key[:15]}...")
    else:
        print(f"  ❌ STRIPE_PUBLIC_KEY: Invalid or missing")
else:
    print(f"  ❌ STRIPE_PUBLIC_KEY: Not configured")

if hasattr(settings, 'STRIPE_SECRET_KEY'):
    key = settings.STRIPE_SECRET_KEY
    if key and key.startswith('sk_'):
        print(f"  ✅ STRIPE_SECRET_KEY: {key[:15]}...")
    else:
        print(f"  ❌ STRIPE_SECRET_KEY: Invalid or missing")
else:
    print(f"  ❌ STRIPE_SECRET_KEY: Not configured")

# Check 5: URLs
print("\n5. CHECKING URL PATTERNS:")
print("-" * 60)
from django.urls import get_resolver
resolver = get_resolver()
url_patterns = resolver.url_patterns
important_urls = ['product_list', 'product_detail', 'create_checkout_session', 'payment_success', 'dashboard']
for url_name in important_urls:
    try:
        from django.urls import reverse
        path = reverse(url_name) if url_name != 'product_detail' and url_name != 'create_checkout_session' else f"/{url_name}/1/"
        print(f"  ✅ {url_name}")
    except:
        print(f"  ❌ {url_name} - NOT FOUND!")

# Check 6: Template Files
print("\n6. CHECKING TEMPLATE FILES:")
print("-" * 60)
import os
template_dir = os.path.join(settings.BASE_DIR, 'templates', 'core')
required_templates = ['product_list.html', 'product_detail.html', 'payment_success.html', 'payment_cancel.html', 'dashboard.html']
for template in required_templates:
    template_path = os.path.join(template_dir, template)
    if os.path.exists(template_path):
        print(f"  ✅ {template}")
    else:
        print(f"  ❌ {template} - NOT FOUND!")

# Check 7: Active Subscriptions
print("\n7. CHECKING SUBSCRIPTIONS:")
print("-" * 60)
subscriptions = Subscription.objects.all()
if subscriptions.exists():
    print(f"  Total Subscriptions: {subscriptions.count()}")
    active = subscriptions.filter(status='active').count()
    print(f"  Active: {active}")
    print(f"  Expired: {subscriptions.filter(status='expired').count()}")
    print(f"  Cancelled: {subscriptions.filter(status='cancelled').count()}")
else:
    print("  No subscriptions found")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)