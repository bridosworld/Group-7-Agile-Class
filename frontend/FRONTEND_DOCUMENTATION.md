# TerraScope Frontend Documentation

## Overview

TerraScope is a Django-based web application that provides a comprehensive subscription management platform for geospatial observation data services. Users can register, purchase subscriptions, manage API tokens, and access premium features through an intuitive web interface.

## Table of Contents

- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Models](#database-models)
- [Views & URLs](#views--urls)
- [Authentication](#authentication)
- [Payment Integration](#payment-integration)
- [API Token Management](#api-token-management)
- [Testing](#testing)
- [Deployment](#deployment)

---

## Technology Stack

- **Framework**: Django 5.2.8
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Authentication**: Django Auth + django-two-factor-auth + django-otp
- **Payment**: Stripe
- **Templates**: Django Templates with Bootstrap CSS
- **Python**: 3.14+

### Key Dependencies

```
django==5.2.8
django-two-factor-auth
django-otp
stripe
PyJWT
Pillow (for image handling)
```

---

## Project Structure

```
frontend/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
│
├── terrascope/              # Main project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Root URL configuration
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
│
├── core/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # URL patterns
│   ├── admin.py            # Admin interface config
│   ├── middleware.py       # Custom middleware
│   ├── context_processors.py  # Template context
│   ├── management/         # Custom management commands
│   ├── migrations/         # Database migrations
│   └── tests/              # Test suite
│
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   └── core/               # App-specific templates
│       ├── home.html
│       ├── dashboard.html
│       ├── product_list.html
│       ├── product_detail.html
│       ├── subscription_detail.html
│       ├── profile.html
│       └── ...
│
└── media/                   # User-uploaded files
    ├── products/           # Product images
    └── avatars/            # User avatars
```

---

## Features

### 1. User Management
- ✅ User registration with email validation
- ✅ Login/Logout functionality
- ✅ Two-Factor Authentication (2FA) via TOTP
- ✅ User profile management with avatar upload
- ✅ Password reset functionality

### 2. Product & Subscription Management
- ✅ Browse available products/services
- ✅ View detailed product information
- ✅ Multiple subscription durations (10 minutes, 2 hours, 1 week)
- ✅ Subscription status tracking (active, paused, cancelled, expired)
- ✅ Usage analytics and monitoring
- ✅ Automatic subscription expiry handling

### 3. Payment Processing
- ✅ Stripe integration for secure payments
- ✅ Multiple payment options
- ✅ Payment success/failure handling
- ✅ Subscription history tracking

### 4. API Token Management
- ✅ Generate JWT tokens for API access
- ✅ Token expiration based on subscription period
- ✅ Token revocation
- ✅ Token refresh functionality
- ✅ Maximum 5 tokens per subscription
- ✅ Token usage tracking

### 5. Dashboard & Analytics
- ✅ User dashboard with subscription overview
- ✅ API usage charts (30-day trends)
- ✅ Data usage monitoring
- ✅ Success rate analytics
- ✅ Subscription statistics

### 6. Security Features
- ✅ Two-Factor Authentication (2FA)
- ✅ JWT token-based API authentication
- ✅ CSRF protection
- ✅ Session security
- ✅ Password hashing
- ✅ Subscription expiry middleware

---

## Installation

### Prerequisites

- Python 3.14 or higher
- pip (Python package manager)
- Git

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   cd frontend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   
   **Windows (Git Bash):**
   ```bash
   source .venv/Scripts/activate
   ```
   
   **Windows (CMD):**
   ```cmd
   .venv\\Scripts\\activate.bat
   ```
   
   **Linux/Mac:**
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   
   Create `.env` file in frontend directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   STRIPE_PUBLIC_KEY=pk_test_your_key
   STRIPE_SECRET_KEY=sk_test_your_key
   JWT_SECRET_KEY=your-jwt-secret-key
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Create initial products**
   ```bash
   python manage.py create_products
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Website: http://127.0.0.1:8000
    - Admin: http://127.0.0.1:8000/admin

---

## Configuration

### Settings (`terrascope/settings.py`)

#### Database Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Stripe Configuration
```python
STRIPE_PUBLIC_KEY = 'pk_test_...'
STRIPE_SECRET_KEY = 'sk_test_...'
PAYMENT_SUCCESS_URL = 'http://127.0.0.1:8000/payment/success/'
PAYMENT_CANCEL_URL = 'http://127.0.0.1:8000/payment/cancel/'
```

#### JWT Configuration
```python
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key')
JWT_ALGORITHM = 'HS256'
JWT_TOKEN_LIMIT_PER_SUBSCRIPTION = 5
```

#### Two-Factor Authentication
```python
TWO_FACTOR_PATCH_ADMIN = True
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
OTP_TOTP_TOLERANCE = 2
```

#### Middleware Configuration
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.SubscriptionExpiryMiddleware',  # Custom
    'core.middleware.Enforce2FAMiddleware',          # Custom
]
```

---

## Database Models

### UserProfile
Extended user profile with additional information.

**Fields:**
- `user` - OneToOne relationship with Django User
- `phone_number`, `company`, `job_title`, `bio` - Personal info
- `address_line1/2`, `city`, `state`, `country`, `postal_code` - Address
- `avatar` - Profile picture
- `timezone`, `language` - Preferences
- `email_notifications`, `usage_alerts`, `marketing_emails` - Settings

**Properties:**
- `full_name` - Returns formatted full name
- `full_address` - Returns formatted address

### Product
Represents subscription products/services.

**Fields:**
- `name`, `description`, `short_description` - Product info
- `image` - Product image
- `price_10_minutes`, `price_2_hours`, `price_1_week` - Pricing tiers
- `api_calls_limit` - API call quota
- `data_limit_mb` - Data download quota
- `is_active` - Product availability status

### Subscription
Tracks user subscriptions to products.

**Fields:**
- `user` - ForeignKey to User
- `product` - ForeignKey to Product
- `status` - active, paused, cancelled, expired
- `subscribed_at`, `expires_at`, `cancelled_at`, `paused_at` - Timestamps
- `duration_months`, `total_cost` - Subscription details
- `api_calls_made`, `api_calls_limit` - Usage tracking
- `data_downloaded_mb`, `data_limit_mb` - Data usage

**Properties:**
- `days_until_expiry` - Remaining days
- `usage_percentage` - API usage %
- `data_usage_percentage` - Data usage %

### SubscriptionUsage
Daily usage logs for analytics.

**Fields:**
- `subscription` - ForeignKey to Subscription
- `date` - Log date
- `api_calls`, `data_downloaded_mb` - Usage metrics
- `requests_successful`, `requests_failed` - Success tracking
- `avg_response_time_ms` - Performance metric

**Properties:**
- `success_rate` - Success percentage

### UserToken
API tokens for Flask integration.

**Fields:**
- `user`, `subscription` - Relationships
- `name` - User-friendly token name
- `token` - JWT token string
- `token_id` - Unique UUID
- `created_at`, `expires_at` - Timestamps
- `is_active`, `last_used` - Status tracking

**Properties:**
- `is_expired` - Check if expired
- `days_until_expiry` - Remaining days

**Methods:**
- `mark_as_used()` - Update last_used timestamp

---

## Views & URLs

### Public Views

#### Home Page
- **URL**: `/`
- **View**: `views.home`
- **Description**: Landing page with featured products
- **Template**: `core/home.html`

#### Product List
- **URL**: `/products/`
- **View**: `views.product_list`
- **Description**: Display all active products
- **Template**: `core/product_list.html`

#### Product Detail
- **URL**: `/products/<id>/`
- **View**: `views.product_detail`
- **Description**: Detailed product information
- **Template**: `core/product_detail.html`

### Authentication Views

#### Register
- **URL**: `/register/`
- **View**: `views.register`
- **Authentication**: Not required
- **Description**: User registration form

#### Login
- **URL**: `/account/login/`
- **View**: Two-factor login
- **Description**: 2FA login with TOTP

#### Logout
- **URL**: `/logout/`
- **View**: Django LogoutView
- **Redirect**: Home page

### Protected Views (Login Required)

#### Dashboard
- **URL**: `/dashboard/`
- **View**: `views.dashboard`
- **Authentication**: Required
- **Description**: User dashboard with subscriptions and analytics
- **Features**:
  - Active/expired subscription counts
  - Usage statistics
  - 30-day usage charts
  - Subscription management

#### Subscription Detail
- **URL**: `/subscription/<id>/`
- **View**: `views.subscription_detail`
- **Authentication**: Required + Owner check
- **Description**: Detailed subscription view
- **Features**:
  - Subscription info
  - API token management
  - Usage metrics
  - Actions (pause, resume, cancel)

#### Profile Management
- **URL**: `/profile/`
- **View**: `views.profile`
- **Authentication**: Required
- **Description**: User profile editing
- **Features**:
  - Personal information
  - Address management
  - Avatar upload
  - Notification preferences

### Payment Views

#### Create Checkout Session
- **URL**: `/checkout/<product_id>/`
- **View**: `views.create_checkout_session`
- **Method**: POST
- **Authentication**: Required
- **Description**: Creates Stripe checkout session
- **Parameters**:
  - `product_id` - Product to purchase
  - `duration` - 10_minutes, 2_hours, or 1_week

#### Payment Success
- **URL**: `/payment/success/`
- **View**: `views.payment_success`
- **Authentication**: Required
- **Description**: Handles successful payment callback
- **Actions**:
  - Creates subscription record
  - Sets expiry date
  - Copies product limits to subscription

#### Payment Cancel
- **URL**: `/payment/cancel/`
- **View**: `views.payment_cancel`
- **Authentication**: Required
- **Description**: Handles payment cancellation

### Token Management Views

#### Generate Token
- **URL**: `/subscription/<id>/generate-token/`
- **View**: `views.generate_token`
- **Method**: POST
- **Authentication**: Required
- **Description**: Generates new JWT token for subscription
- **Validation**:
  - Subscription must be active
  - Not expired
  - Token limit not reached (max 5)

#### Revoke Token
- **URL**: `/token/<id>/revoke/`
- **View**: `views.revoke_token`
- **Method**: POST
- **Authentication**: Required
- **Description**: Deactivates a token

#### Refresh Token
- **URL**: `/token/<id>/refresh/`
- **View**: `views.refresh_token`
- **Method**: POST
- **Authentication**: Required
- **Description**: Generates new token with same expiry

### Subscription Actions

#### Pause Subscription
- **URL**: `/subscription/<id>/pause/`
- **View**: `views.pause_subscription`
- **Method**: POST
- **Status**: active → paused

#### Resume Subscription
- **URL**: `/subscription/<id>/resume/`
- **View**: `views.resume_subscription`
- **Method**: POST
- **Status**: paused → active

#### Cancel Subscription
- **URL**: `/subscription/<id>/cancel/`
- **View**: `views.cancel_subscription`
- **Method**: POST
- **Status**: active/paused → cancelled

---

## Authentication

### Two-Factor Authentication (2FA)

TerraScope uses TOTP (Time-based One-Time Password) for enhanced security.

#### Setup Process:
1. User registers/logs in
2. Prompted to set up 2FA
3. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
4. Enter 6-digit code to verify
5. Save backup codes

#### Login Flow:
1. Enter username & password
2. Enter 6-digit TOTP code
3. Access granted

#### Middleware:
`Enforce2FAMiddleware` ensures all users enable 2FA before accessing protected pages.

### Session Management
- Session timeout: Default Django settings
- Secure cookies in production
- CSRF protection enabled

---

## Payment Integration

### Stripe Setup

1. **Get API Keys**
   - Sign up at https://stripe.com
   - Get test keys from Dashboard
   - Add to `.env` file

2. **Test Cards**
   ```
   Success: 4242 4242 4242 4242
   Decline: 4000 0000 0000 0002
   3D Secure: 4000 0025 0000 3155
   ```

### Payment Flow

```
User clicks "Subscribe" on product
        ↓
Django creates Stripe checkout session
        ↓
User redirected to Stripe payment page
        ↓
User completes payment
        ↓
Stripe redirects to success/cancel URL
        ↓
Django processes webhook/callback
        ↓
Subscription created in database
```

### Checkout Session Creation

```python
checkout_session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {
            'currency': 'gbp',
            'unit_amount': int(amount * 100),
            'product_data': {
                'name': f'{product.name} - {duration_text}',
                'description': product.short_description,
            },
        },
        'quantity': 1,
    }],
    mode='payment',
    success_url=success_url,
    cancel_url=cancel_url,
    metadata={
        'product_id': product_id,
        'duration': duration,
        'user_id': user.id,
    }
)
```

---

## API Token Management

### Token Generation

When a user generates a token:

1. **Validation**:
   - Subscription is active
   - Not expired
   - Token limit not reached (5 max)

2. **JWT Payload**:
```python
{
    'jti': 'unique-token-id',
    'user_id': user.id,
    'username': user.username,
    'email': user.email,
    'subscription_id': subscription.id,
    'product_id': product.id,
    'product_name': product.name,
    'api_calls_limit': product.api_calls_limit,
    'data_limit_mb': product.data_limit_mb,
    'tier': product.name.lower(),
    'iat': issued_timestamp,
    'exp': subscription.expires_at
}
```

3. **Token Encoding**:
```python
token = jwt.encode(
    payload,
    settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM
)
```

4. **Storage**:
   - Token saved to `UserToken` model
   - Linked to user and subscription
   - One-time display to user

### Token Usage

Tokens are used with the Flask API (backend):

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:5000/api/observations
```

See `DJANGO_FLASK_INTEGRATION.md` for Flask integration details.

### Token Security

- ✅ Tokens expire with subscription
- ✅ Can be revoked anytime
- ✅ Limited to 5 per subscription
- ✅ Tied to specific user and subscription
- ✅ Tracked usage (last_used timestamp)

---

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test core.tests.test_new_user_registration

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Files

Located in `core/tests/`:

- `test_new_user_registration.py` - User registration tests
- `test_product_listing_detail.py` - Product view tests
- `test_purchase_flow.py` - Payment and subscription tests
- `test_us15_integration.py` - 2FA integration tests

### Test Structure

```python
from django.test import TestCase, Client
from django.urls import reverse
from core.models import Product, Subscription

class ProductTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(...)
    
    def test_product_list(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
```

---

## Deployment

### Production Checklist

1. **Security Settings**
   ```python
   DEBUG = False
   SECRET_KEY = os.environ['SECRET_KEY']
   ALLOWED_HOSTS = ['yourdomain.com']
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

2. **Database**
   - Use PostgreSQL instead of SQLite
   - Set up database backups
   - Configure connection pooling

3. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

4. **Media Files**
   - Use S3 or similar for storage
   - Configure proper permissions

5. **Environment Variables**
   - Never commit `.env` to git
   - Use secure secret generation
   - Rotate keys regularly

6. **HTTPS**
   - Obtain SSL certificate
   - Configure web server (Nginx/Apache)
   - Enable HSTS

7. **Monitoring**
   - Set up error logging (Sentry)
   - Monitor performance
   - Track usage metrics

### Deployment Platforms

#### Heroku
```bash
heroku create terrascope-app
git push heroku main
heroku run python manage.py migrate
```

#### AWS/DigitalOcean
- Use Gunicorn/uWSGI as WSGI server
- Nginx as reverse proxy
- Supervisor for process management

---

## Common Tasks

### Create New Products
```bash
python manage.py create_products
```

### Update Product Prices
```bash
python manage.py shell
from core.models import Product
product = Product.objects.get(id=1)
product.price_1_month = 29.99
product.save()
```

### Expire Old Subscriptions Manually
```bash
python manage.py shell
from core.models import Subscription
from django.utils import timezone
Subscription.objects.filter(
    expires_at__lte=timezone.now(),
    status='active'
).update(status='expired')
```

### Generate Test Token
```bash
python test_jwt.py
```

---

## Troubleshooting

### Issue: 2FA Not Working
**Solution**: Check OTP_TOTP_TOLERANCE setting, ensure device time is synchronized

### Issue: Stripe Payments Failing
**Solution**: Verify API keys are correct, check Stripe dashboard for errors

### Issue: Tokens Not Validating in Flask
**Solution**: Ensure JWT_SECRET_KEY matches between Django and Flask

### Issue: Static Files Not Loading
**Solution**: Run `python manage.py collectstatic`, check STATIC_URL setting

### Issue: Database Migrations Failed
**Solution**: 
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

---

## Support & Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Review error logs
   - Check subscription expiry updates
   - Monitor API token usage

2. **Monthly**:
   - Database backup
   - Update dependencies
   - Review security patches

3. **Quarterly**:
   - Rotate JWT secrets
   - Review and optimize queries
   - Update documentation

---

## API Integration

The Django frontend generates JWT tokens that are used to authenticate with the Flask backend API. See `DJANGO_FLASK_INTEGRATION.md` for complete integration documentation.

---

## Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Stripe API Docs**: https://stripe.com/docs/api
- **django-two-factor-auth**: https://github.com/jazzband/django-two-factor-auth
- **JWT Docs**: https://pyjwt.readthedocs.io/

---

## Contributing

1. Create feature branch
2. Make changes
3. Write/update tests
4. Submit pull request

---

## License

[Your License Here]

---

## Contact

For support: [your-email@example.com]
