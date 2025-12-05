# Generated migration for UserToken model updates
import uuid
from django.db import migrations, models
import django.db.models.deletion


def populate_subscription_field(apps, schema_editor):
    """Populate subscription field for existing tokens"""
    UserToken = apps.get_model('core', 'UserToken')
    Subscription = apps.get_model('core', 'Subscription')
    
    # Get all tokens
    tokens = UserToken.objects.all()
    
    for token in tokens:
        # Try to find an active subscription for this user
        subscription = Subscription.objects.filter(
            user=token.user,
            status='active'
        ).order_by('-subscribed_at').first()
        
        # If no active subscription, get the most recent one
        if not subscription:
            subscription = Subscription.objects.filter(
                user=token.user
            ).order_by('-subscribed_at').first()
        
        # If still no subscription, skip (will be handled manually)
        if subscription:
            token.subscription = subscription
            token.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_product_price_1_month_and_more'),
    ]

    operations = [
        # Step 1: Add subscription field as nullable
        migrations.AddField(
            model_name='usertoken',
            name='subscription',
            field=models.ForeignKey(
                null=True, 
                blank=True,
                on_delete=django.db.models.deletion.CASCADE, 
                related_name='tokens', 
                to='core.subscription'
            ),
        ),
        
        # Step 2: Add token_id field
        migrations.AddField(
            model_name='usertoken',
            name='token_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        
        # Step 3: Update name field
        migrations.AlterField(
            model_name='usertoken',
            name='name',
            field=models.CharField(
                default='API Token', 
                help_text='User-friendly name for this token', 
                max_length=100
            ),
        ),
        
        # Step 4: Populate subscription field with data
        migrations.RunPython(populate_subscription_field, migrations.RunPython.noop),
        
        # Step 5: Make subscription field non-nullable
        migrations.AlterField(
            model_name='usertoken',
            name='subscription',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, 
                related_name='tokens', 
                to='core.subscription'
            ),
        ),
        
        # Step 6: Add indexes
        migrations.AddIndex(
            model_name='usertoken',
            index=models.Index(fields=['token'], name='core_userto_token_6a5e92_idx'),
        ),
        migrations.AddIndex(
            model_name='usertoken',
            index=models.Index(fields=['subscription', 'is_active'], name='core_userto_subscri_1047e3_idx'),
        ),
        
        # Step 7: Add constraint
        migrations.AddConstraint(
            model_name='usertoken',
            constraint=models.UniqueConstraint(
                fields=('subscription', 'name'), 
                name='unique_token_name_per_subscription'
            ),
        ),
    ]
