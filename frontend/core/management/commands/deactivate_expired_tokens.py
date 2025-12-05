from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import UserToken

class Command(BaseCommand):
    help = 'Deactivate expired API tokens'
    
    def handle(self, *args, **options):
        # Find all active tokens that have expired
        expired_tokens = UserToken.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )
        
        count = expired_tokens.count()
        
        if count > 0:
            # Deactivate them
            expired_tokens.update(is_active=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Deactivated {count} expired token(s)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ No expired tokens found')
            )
