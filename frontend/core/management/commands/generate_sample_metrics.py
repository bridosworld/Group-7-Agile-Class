from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal  # ✅ ADD THIS IMPORT
import random
from core.models import Subscription, SubscriptionUsage

class Command(BaseCommand):
    help = 'Generate sample usage data for active subscriptions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating sample metrics data...')
        
        active_subscriptions = Subscription.objects.filter(status='active')
        
        if not active_subscriptions.exists():
            self.stdout.write(self.style.WARNING('No active subscriptions found'))
            return
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        
        self.stdout.write(f'Generating usage data for {active_subscriptions.count()} subscriptions...')
        
        total_created = 0
        
        for subscription in active_subscriptions:
            current_date = start_date
            
            while current_date <= end_date:
                usage, created = SubscriptionUsage.objects.get_or_create(
                    subscription=subscription,
                    date=current_date,
                    defaults={
                        'api_calls': random.randint(50, 500),
                        'data_downloaded_mb': round(random.uniform(5, 50), 2),
                        'requests_successful': random.randint(45, 480),
                        'requests_failed': random.randint(0, 20),
                        'avg_response_time_ms': round(random.uniform(100, 500), 2),
                    }
                )
                
                if created:
                    total_created += 1
                    subscription.api_calls_made += usage.api_calls
                    subscription.data_downloaded_mb += Decimal(str(usage.data_downloaded_mb))  # ✅ CONVERT TO DECIMAL
                
                current_date += timedelta(days=1)
            
            subscription.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Generated data for {subscription.product.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully created {total_created} usage records'))