from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F
from django.urls import reverse
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import json
import jwt
import uuid
import stripe
from django.conf import settings
from .models import Product, Subscription, SubscriptionUsage, UserToken

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    """Home page view"""
    products = Product.objects.filter(is_active=True)[:6]
    return render(request, 'core/home.html', {'products': products})

def product_list(request):
    """Display all active products"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'core/product_list.html', {'products': products})

def product_detail(request, pk):
    """Display product details"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'core/product_detail.html', {'product': product})

@login_required
def create_checkout_session(request, product_id):
    """Create Stripe checkout session for product purchase"""
    if request.method != 'POST':
        return redirect('product_detail', pk=product_id)
    
    try:
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        duration = request.POST.get('duration', '10_minutes')
        
        # Check if Stripe is configured
        if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == '':
            messages.error(
                request, 
                'Payment system is not configured. Please contact the administrator.'
            )
            return redirect('product_detail', pk=product_id)
        
        # Calculate price based on duration
        if duration == '10_minutes':
            amount = float(product.price_10_minutes)
            duration_text = "10 Minutes"
        elif duration == '2_hours':
            amount = float(product.price_2_hours)
            duration_text = "2 Hours"
        elif duration == '1_week':
            amount = float(product.price_1_week)
            duration_text = "1 Week"
        else:
            amount = float(product.price_10_minutes)
            duration = '10_minutes'
            duration_text = "10 Minutes"
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'unit_amount': int(amount * 100),
                    'product_data': {
                        'name': f'{product.name} - {duration_text}',
                        'description': product.short_description or product.description[:100],
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('payment_success')
            ) + f'?session_id={{CHECKOUT_SESSION_ID}}&product_id={product_id}&duration={duration}',
            cancel_url=request.build_absolute_uri(
                reverse('payment_cancel')
            ) + f'?product_id={product_id}',
            client_reference_id=str(request.user.id),
            metadata={
                'product_id': str(product_id),
                'duration': str(duration),
                'user_id': str(request.user.id),
                'user_email': request.user.email,
            }
        )
        
        return redirect(checkout_session.url)
        
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('product_detail', pk=product_id)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('product_detail', pk=product_id)

@login_required
def payment_success(request):
    """Handle successful payment and create subscription"""
    session_id = request.GET.get('session_id')
    product_id = request.GET.get('product_id')
    duration = request.GET.get('duration', '10_minutes')
    
    if not product_id:
        messages.error(request, 'Invalid payment session')
        return redirect('product_list')
    
    try:
        # Verify Stripe session if session_id is provided
        if session_id:
            if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == '':
                messages.error(request, 'Payment system not configured')
                return redirect('product_list')
            
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status != 'paid':
                messages.error(request, 'Payment was not completed successfully')
                return redirect('product_detail', pk=product_id)
        
        # Create subscription (works for both Stripe payments and demo mode)
        if True:  # Always create subscription if we reach here
            product = get_object_or_404(Product, pk=product_id)
            
            # Duration map
            duration_map = {
                '10_minutes': timedelta(minutes=10),
                '2_hours': timedelta(hours=2),
                '1_week': timedelta(weeks=1)
            }
            
            price_map = {
                '10_minutes': product.price_10_minutes,
                '2_hours': product.price_2_hours,
                '1_week': product.price_1_week
            }
            
            if duration in duration_map:
                expires_at = timezone.now() + duration_map[duration]
                total_cost = price_map[duration]
            else:
                expires_at = timezone.now() + timedelta(minutes=10)
                total_cost = product.price_10_minutes
            
            subscription = Subscription.objects.create(
                user=request.user,
                product=product,
                status='active',
                subscribed_at=timezone.now(),
                expires_at=expires_at,
                duration_months=1,  # Default to 1 for compatibility
                total_cost=total_cost,
                api_calls_limit=product.api_calls_limit,
                data_limit_mb=product.data_limit_mb,
                api_calls_made=0,
                data_downloaded_mb=0,
            )
            
            SubscriptionUsage.objects.create(
                subscription=subscription,
                date=timezone.now().date(),
                api_calls=0,
                data_downloaded_mb=0,
                requests_successful=0,
                requests_failed=0,
                avg_response_time_ms=0,  # ✅ ADD THIS LINE
            )
            
            messages.success(request, f'Successfully subscribed to {product.name}!')
            
            return render(request, 'core/payment_success.html', {
                'subscription': subscription,
                'product': product,
            })
    
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment verification error: {str(e)}')
        return redirect('product_list')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('product_list')

def payment_cancel(request):
    """Handle cancelled payment"""
    product_id = request.GET.get('product_id')
    messages.warning(request, 'Payment was cancelled')
    
    if product_id:
        return redirect('product_detail', pk=product_id)
    return redirect('product_list')

@login_required
def dashboard(request):
    """User dashboard with subscriptions and usage analytics"""
    user = request.user
    
    subscriptions = Subscription.objects.filter(user=user).select_related('product').order_by('-subscribed_at')
    
    # Auto-update expired subscriptions (middleware does this too, but double-check here)
    now = timezone.now()
    Subscription.objects.filter(
        user=user,
        status='active',
        expires_at__lte=now
    ).update(status='expired')
    
    # Refresh subscriptions after update
    subscriptions = Subscription.objects.filter(user=user).select_related('product').order_by('-subscribed_at')
    
    total_spent = subscriptions.aggregate(total=Sum('total_cost'))['total'] or 0
    active_subscriptions = subscriptions.filter(status='active', expires_at__gt=now).count()
    expired_subscriptions = subscriptions.filter(status='expired').count()
    paused_subscriptions = subscriptions.filter(status='paused').count()
    total_api_calls = subscriptions.aggregate(total=Sum('api_calls_made'))['total'] or 0
    total_data_used = subscriptions.aggregate(total=Sum('data_downloaded_mb'))['total'] or 0
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=29)
    
    chart_labels = []
    api_calls_data = []
    data_usage_data = []
    success_rate_data = []
    
    current_date = start_date
    while current_date <= end_date:
        chart_labels.append(current_date.strftime('%b %d'))
        
        daily_usage = SubscriptionUsage.objects.filter(
            subscription__user=user,
            date=current_date
        ).aggregate(
            total_calls=Sum('api_calls'),
            total_data=Sum('data_downloaded_mb'),
            total_successful=Sum('requests_successful'),
            total_failed=Sum('requests_failed')
        )
        
        calls = daily_usage['total_calls'] or 0
        api_calls_data.append(calls)
        
        data = float(daily_usage['total_data'] or 0)
        data_usage_data.append(round(data, 2))
        
        successful = daily_usage['total_successful'] or 0
        failed = daily_usage['total_failed'] or 0
        total_requests = successful + failed
        success_rate = (successful / total_requests * 100) if total_requests > 0 else 100
        success_rate_data.append(round(success_rate, 2))
        
        current_date += timedelta(days=1)
    
    context = {
        'subscriptions': subscriptions,
        'total_spent': total_spent,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'paused_subscriptions': paused_subscriptions,
        'total_subscriptions': subscriptions.count(),
        'total_api_calls': total_api_calls,
        'total_data_used': total_data_used,
        'now': now,
        'chart_labels': json.dumps(chart_labels),
        'api_calls_data': json.dumps(api_calls_data),
        'data_usage_data': json.dumps(data_usage_data),
        'success_rate_data': json.dumps(success_rate_data),
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def subscription_detail(request, pk):
    """Display subscription details with token management"""
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    
    # Check actual subscription status based on expiry
    now = timezone.now()
    if subscription.expires_at <= now and subscription.status == 'active':
        # Auto-update expired subscriptions
        subscription.status = 'expired'
        subscription.save()
    
    # Check if user can generate tokens
    can_generate_token = (
        subscription.status == 'active' and 
        subscription.expires_at > now
    )
    
    # Get all tokens for this subscription
    tokens = UserToken.objects.filter(
        subscription=subscription,
        is_active=True
    ).order_by('-created_at')
    
    # Check token limit
    max_tokens = settings.JWT_TOKEN_LIMIT_PER_SUBSCRIPTION
    can_create_more = tokens.count() < max_tokens
    
    context = {
        'subscription': subscription,
        'tokens': tokens,
        'can_generate_token': can_generate_token,
        'can_create_more': can_create_more,
        'max_tokens': max_tokens,
        'tokens_used': tokens.count(),
        'now': timezone.now(),
    }
    
    return render(request, 'core/subscription_detail.html', context)

@login_required
def generate_token(request, subscription_id):
    """Generate API token for specific subscription"""
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        user=request.user,
        status='active'
    )
    
    # Verify subscription is still valid
    if subscription.expires_at <= timezone.now():
        messages.error(request, 'Cannot generate token: Subscription has expired.')
        return redirect('subscription_detail', pk=subscription_id)
    
    # Check token limit
    active_tokens_count = UserToken.objects.filter(
        subscription=subscription,
        is_active=True
    ).count()
    
    if active_tokens_count >= settings.JWT_TOKEN_LIMIT_PER_SUBSCRIPTION:
        messages.error(
            request, 
            f'Maximum token limit reached ({settings.JWT_TOKEN_LIMIT_PER_SUBSCRIPTION}). '
            'Please revoke an existing token first.'
        )
        return redirect('subscription_detail', pk=subscription_id)
    
    if request.method == 'POST':
        token_name = request.POST.get('name', f'Token {active_tokens_count + 1}')
        
        # Create unique token ID
        token_id = str(uuid.uuid4())
        
        # Build JWT payload
        payload = {
            'jti': token_id,  # JWT ID (unique identifier)
            'user_id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'subscription_id': subscription.id,
            'product_id': subscription.product.id,
            'product_name': subscription.product.name,
            'api_calls_limit': subscription.product.api_calls_limit,
            'data_limit_mb': subscription.product.data_limit_mb,
            'tier': subscription.product.name.lower(),
            'iat': int(datetime.utcnow().timestamp()),  # Issued at
            'exp': int(subscription.expires_at.timestamp()),  # Expires with subscription
        }
        
        # Generate JWT token
        token_string = jwt.encode(
            payload, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Save to database
        UserToken.objects.create(
            user=request.user,
            subscription=subscription,
            name=token_name,
            token=token_string,
            token_id=token_id,
            expires_at=subscription.expires_at
        )
        
        messages.success(
            request, 
            f'✅ Token "{token_name}" generated successfully! '
            f'Valid until {subscription.expires_at.strftime("%B %d, %Y at %I:%M %p")}'
        )
        
        # Redirect back to subscription detail with token section in view
        return redirect('subscription_detail', pk=subscription_id)
    
    # GET request - show generation form
    context = {
        'subscription': subscription,
        'active_tokens_count': active_tokens_count,
        'max_tokens': settings.JWT_TOKEN_LIMIT_PER_SUBSCRIPTION,
    }
    return render(request, 'core/generate_token.html', context)

@login_required
def revoke_token(request, token_id):
    """Revoke (deactivate) a specific token"""
    token = get_object_or_404(
        UserToken,
        id=token_id,
        user=request.user,
        is_active=True
    )
    
    if request.method == 'POST':
        token.is_active = False
        token.save()
        
        messages.success(
            request,
            f'🗑️ Token "{token.name}" has been revoked and can no longer be used.'
        )
        
        return redirect('subscription_detail', pk=token.subscription.id)
    
    # Show confirmation page
    context = {'token': token}
    return render(request, 'core/revoke_token_confirm.html', context)

@login_required
def refresh_token(request, token_id):
    """Refresh an existing token (deactivate old, create new)"""
    old_token = get_object_or_404(
        UserToken,
        id=token_id,
        user=request.user
    )
    
    subscription = old_token.subscription
    
    # Verify subscription is still active
    if subscription.status != 'active' or subscription.expires_at <= timezone.now():
        messages.error(request, 'Cannot refresh token: Subscription is no longer active.')
        return redirect('subscription_detail', pk=subscription.id)
    
    if request.method == 'POST':
        # Deactivate old token
        old_token.is_active = False
        old_token.save()
        
        # Generate new token with same name
        token_id_new = str(uuid.uuid4())
        
        payload = {
            'jti': token_id_new,
            'user_id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'subscription_id': subscription.id,
            'product_id': subscription.product.id,
            'product_name': subscription.product.name,
            'api_calls_limit': subscription.product.api_calls_limit,
            'data_limit_mb': subscription.product.data_limit_mb,
            'tier': subscription.product.name.lower(),
            'iat': int(datetime.utcnow().timestamp()),
            'exp': int(subscription.expires_at.timestamp()),
        }
        
        token_string = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Create new token
        UserToken.objects.create(
            user=request.user,
            subscription=subscription,
            name=old_token.name,  # Keep same name
            token=token_string,
            token_id=token_id_new,
            expires_at=subscription.expires_at
        )
        
        messages.success(
            request,
            f'🔄 Token "{old_token.name}" has been refreshed successfully!'
        )
        
        return redirect('subscription_detail', pk=subscription.id)
    
    context = {'token': old_token}
    return render(request, 'core/refresh_token_confirm.html', context)

@login_required
def pause_subscription(request, pk):
    """Pause a subscription"""
    if request.method == 'POST':
        subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
        if subscription.status == 'active':
            subscription.status = 'paused'
            subscription.paused_at = timezone.now()
            subscription.save()
            messages.success(request, f'Subscription to {subscription.product.name} has been paused')
        else:
            messages.warning(request, 'Only active subscriptions can be paused')
    return redirect('subscription_detail', pk=pk)

@login_required
def resume_subscription(request, pk):
    """Resume a paused subscription"""
    if request.method == 'POST':
        subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
        if subscription.status == 'paused':
            subscription.status = 'active'
            subscription.paused_at = None
            subscription.save()
            messages.success(request, f'Subscription to {subscription.product.name} has been resumed')
        else:
            messages.warning(request, 'Only paused subscriptions can be resumed')
    return redirect('subscription_detail', pk=pk)

@login_required
def cancel_subscription(request, pk):
    """Cancel a subscription"""
    if request.method == 'POST':
        subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
        if subscription.status in ['active', 'paused']:
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
            messages.success(request, f'Subscription to {subscription.product.name} has been cancelled')
        else:
            messages.warning(request, 'This subscription is already cancelled or expired')
    return redirect('dashboard')

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def api_tokens(request):
    """Display user's API tokens"""
    tokens = UserToken.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'tokens': tokens,
    }
    
    return render(request, 'core/api_tokens.html', context)


@login_required
def profile(request):
    """View and edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update profile info
        profile.phone_number = request.POST.get('phone_number', '')
        profile.company = request.POST.get('company', '')
        profile.job_title = request.POST.get('job_title', '')
        profile.bio = request.POST.get('bio', '')
        
        # Address
        profile.address_line1 = request.POST.get('address_line1', '')
        profile.address_line2 = request.POST.get('address_line2', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.country = request.POST.get('country', '')
        profile.postal_code = request.POST.get('postal_code', '')
        
        # Settings
        profile.timezone = request.POST.get('timezone', 'UTC')
        profile.language = request.POST.get('language', 'en')
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.usage_alerts = request.POST.get('usage_alerts') == 'on'
        profile.marketing_emails = request.POST.get('marketing_emails') == 'on'
        
        # Handle avatar upload - check if file was actually uploaded
        if request.FILES.get('avatar'):
            # Delete old avatar if exists
            if profile.avatar:
                try:
                    profile.avatar.delete(save=False)
                except:
                    pass
            profile.avatar = request.FILES['avatar']
            messages.success(request, 'Profile picture updated successfully!')
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    
    return render(request, 'core/profile.html', context)
