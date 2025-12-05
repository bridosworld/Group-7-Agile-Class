from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Subscription

class Command(BaseCommand):
    help = 'Update expired subscriptions and deactivate their tokens'
    
    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find active subscriptions that have expired
        expired = Subscription.objects.filter(
            status='active',
            expires_at__lte=now
        )
        
        count = expired.count()
        
        if count > 0:
            # Update status to expired
            expired.update(status='expired')
            
            # Deactivate associated tokens
            from core.models import UserToken
            UserToken.objects.filter(
                subscription__in=expired,
                is_active=True
            ).update(is_active=False)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Updated {count} expired subscription(s) and deactivated their tokens'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ No expired subscriptions found')
            )
