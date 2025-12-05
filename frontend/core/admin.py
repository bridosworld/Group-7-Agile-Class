from django.contrib import admin
from django.utils.html import format_html

from .models import Product, Subscription, SubscriptionUsage, UserToken, UserProfile

from .models import Product, Subscription, SubscriptionUsage, UserToken


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_10_minutes', 'price_2_hours', 'price_1_week', 'api_calls_limit', 'data_limit_mb', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_description', 'description', 'image', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_10_minutes', 'price_2_hours', 'price_1_week'),
            'description': 'Set pricing for different subscription durations'
        }),
        ('API Limits', {
            'fields': ('api_calls_limit', 'data_limit_mb'),
            'description': 'Define usage limits for this product'
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    # Use only fields that exist in your model
    list_display = ['user', 'product', 'status', 'expires_at', 'api_calls_made']
    list_filter = ['status']
    search_fields = ['user__username', 'user__email', 'product__name']
    # Don't include any readonly_fields for now
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'product', 'status', 'expires_at')
        }),
        ('Usage Statistics', {
            'fields': ('api_calls_made', 'api_calls_limit', 'data_downloaded_mb', 'data_limit_mb')
        }),
        ('Payment Information', {
            'fields': ('total_cost',)
        }),
    )


@admin.register(SubscriptionUsage)
class SubscriptionUsageAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'date', 'api_calls', 'data_downloaded_mb']
    list_filter = ['date']
    search_fields = ['subscription__user__username']
    date_hierarchy = 'date'


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'subscription', 'created_at', 'expires_at', 'is_active', 'last_used']
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['user__username', 'name', 'subscription__product__name']
    readonly_fields = ['token', 'token_id', 'created_at', 'last_used']
    
    fieldsets = (
        ('Token Information', {
            'fields': ('name', 'token', 'token_id')
        }),
        ('Associations', {
            'fields': ('user', 'subscription')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'expires_at', 'last_used')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'job_title', 'phone_number', 'email_notifications']
    list_filter = ['email_notifications', 'usage_alerts', 'marketing_emails', 'created_at']
    search_fields = ['user__username', 'user__email', 'company', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'company', 'job_title', 'bio', 'avatar')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('timezone', 'language')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'usage_alerts', 'marketing_emails')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
