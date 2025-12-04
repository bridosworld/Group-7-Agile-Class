from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Subscription, SubscriptionUsage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_1_month', 'api_calls_limit', 'data_limit_mb', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_description', 'description', 'image', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_1_month', 'price_2_months', 'price_1_year'),
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
