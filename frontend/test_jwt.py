import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'terrascope.settings')
django.setup()

import jwt
from django.conf import settings
from core.models import Subscription

# Get a subscription
sub = Subscription.objects.first()

if sub:
    # Generate test token
    payload = {
        'user_id': sub.user.id,
        'subscription_id': sub.id,
        'product_name': sub.product.name,
        'exp': int(sub.expires_at.timestamp())
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

    print(f"Generated Token:\n{token}\n")

    # Decode to verify (without expiration validation for testing)
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'], options={"verify_exp": False})
    print(f"Decoded Payload:")
    for key, value in decoded.items():
        print(f"  {key}: {value}")
    
    print(f"\n✅ JWT token generation and decoding working correctly!")
    print(f"Note: Token already expired because test subscriptions were created 10+ minutes ago")
else:
    print("No subscription found")
