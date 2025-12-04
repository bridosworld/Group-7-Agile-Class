from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Changed from URLField to ImageField for file uploads
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), 
        ('active', 'Active'), 
        ('expired', 'Expired')
    ]
    
    DURATION_CHOICES = [
        (1, '1 Month'),
        (2, '2 Months'),
        (12, '1 Year'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Customer selects duration
    duration_months = models.IntegerField(choices=DURATION_CHOICES, default=1)
    
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    # Auto-calculated expiration date
    expires_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate expiration when status becomes active
        if self.status == 'active' and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30 * self.duration_months)
        
        # Auto-expire if past expiration date
        if self.expires_at and timezone.now() > self.expires_at and self.status == 'active':
            self.status = 'expired'
        
        super().save(*args, **kwargs)
    
    def days_remaining(self):
        """Calculate days remaining in subscription"""
        if self.expires_at and self.status == 'active':
            remaining = self.expires_at - timezone.now()
            return max(0, remaining.days)
        return 0
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-subscribed_at']