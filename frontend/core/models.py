from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
import jwt
from django.conf import settings
import uuid


class UserProfile(models.Model):
    """Extended user profile with additional information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    phone_number = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, help_text="Brief description about yourself")
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Profile Settings
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    usage_alerts = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_name(self):
        """Get user's full name or username"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join([p for p in parts if p])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile whenever the user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Pricing
    price_10_minutes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="10 Minutes Plan")
    price_2_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="2 Hours Plan")
    price_1_week = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="1 Week Plan")
    
    # API Limits
    api_calls_limit = models.IntegerField(default=10000)
    data_limit_mb = models.IntegerField(default=100)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Dates
    subscribed_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Subscription details
    duration_months = models.IntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Usage tracking
    api_calls_made = models.IntegerField(default=0)
    api_calls_limit = models.IntegerField()
    data_downloaded_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_limit_mb = models.IntegerField()
    
    class Meta:
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    @property
    def days_until_expiry(self):
        """Calculate days until subscription expires"""
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return max(0, delta.days)
        return 0
    
    @property
    def usage_percentage(self):
        """Calculate API usage percentage"""
        if self.api_calls_limit > 0:
            return min(100, (self.api_calls_made / self.api_calls_limit) * 100)
        return 0
    
    @property
    def data_usage_percentage(self):
        """Calculate data usage percentage"""
        if self.data_limit_mb > 0:
            return min(100, (float(self.data_downloaded_mb) / self.data_limit_mb) * 100)
        return 0


class SubscriptionUsage(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='usage_logs')
    date = models.DateField()
    api_calls = models.IntegerField(default=0)
    data_downloaded_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    requests_successful = models.IntegerField(default=0)
    requests_failed = models.IntegerField(default=0)
    avg_response_time_ms = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ ADD THIS LINE
    
    class Meta:
        ordering = ['-date']
        unique_together = ['subscription', 'date']
        indexes = [
            models.Index(fields=['subscription', 'date']),
        ]

    def __str__(self):
        return f"{self.subscription} - {self.date}"
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        total = self.requests_successful + self.requests_failed
        if total > 0:
            return round((self.requests_successful / total) * 100, 2)
        return 100.0


class UserToken(models.Model):
    """API tokens linked to specific subscriptions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_tokens')
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE, related_name='tokens')
    
    name = models.CharField(
        max_length=100, 
        default="API Token",
        help_text="User-friendly name for this token"
    )
    token = models.TextField(unique=True)
    token_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['subscription', 'name'], 
                name='unique_token_name_per_subscription'
            )
        ]
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['subscription', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subscription.product.name}"
    
    @property
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() > self.expires_at if self.expires_at else False
    
    @property
    def days_until_expiry(self):
        """Calculate days until token expires"""
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return delta.days if delta.days > 0 else 0
        return 0
    
    def mark_as_used(self):
        """Update last_used timestamp"""
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])