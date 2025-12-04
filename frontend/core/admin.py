from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Subscription

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'image_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'status', 'duration_display', 'expires_at', 'days_left', 'subscribed_at']
    list_filter = ['status', 'duration_months', 'subscribed_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['subscribed_at']
    
    def duration_display(self, obj):
        return dict(obj.DURATION_CHOICES).get(obj.duration_months, 'Unknown')
    duration_display.short_description = 'Duration'
    
    def days_left(self, obj):
        if obj.status == 'active' and obj.expires_at:
            days = obj.days_remaining()
            if days > 0:
                color = 'green' if days > 7 else 'orange' if days > 3 else 'red'
                return format_html('<span style="color: {}; font-weight: bold;">{} days</span>', color, days)
            return format_html('<span style="color: red; font-weight: bold;">Expired</span>')
        return '-'
    days_left.short_description = 'Days Remaining'
