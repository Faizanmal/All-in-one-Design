"""
Management command to initialize default subscription tiers
"""
from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionTier


class Command(BaseCommand):
    help = 'Initialize default subscription tiers'
    
    def handle(self, *args, **options):
        tiers = [
            {
                'name': 'Free',
                'slug': 'free',
                'description': 'Perfect for trying out our platform',
                'price_monthly': 0,
                'price_yearly': 0,
                'max_projects': 3,
                'max_ai_requests_per_month': 10,
                'max_storage_mb': 100,
                'max_collaborators_per_project': 0,
                'max_exports_per_month': 10,
                'features': {
                    'advanced_ai': False,
                    'priority_support': False,
                    'custom_branding': False,
                    'api_access': False,
                    'white_label': False,
                    'version_history': False,
                    'advanced_export': False,
                },
                'sort_order': 1,
            },
            {
                'name': 'Pro',
                'slug': 'pro',
                'description': 'For professional designers and small teams',
                'price_monthly': 29.99,
                'price_yearly': 299.99,
                'max_projects': 50,
                'max_ai_requests_per_month': 500,
                'max_storage_mb': 10240,  # 10 GB
                'max_collaborators_per_project': 5,
                'max_exports_per_month': 1000,
                'features': {
                    'advanced_ai': True,
                    'priority_support': True,
                    'custom_branding': True,
                    'api_access': True,
                    'white_label': False,
                    'version_history': True,
                    'advanced_export': True,
                },
                'is_featured': True,
                'sort_order': 2,
            },
            {
                'name': 'Enterprise',
                'slug': 'enterprise',
                'description': 'For large teams and organizations',
                'price_monthly': 99.99,
                'price_yearly': 999.99,
                'max_projects': -1,  # Unlimited
                'max_ai_requests_per_month': -1,  # Unlimited
                'max_storage_mb': -1,  # Unlimited
                'max_collaborators_per_project': -1,  # Unlimited
                'max_exports_per_month': -1,  # Unlimited
                'features': {
                    'advanced_ai': True,
                    'priority_support': True,
                    'custom_branding': True,
                    'api_access': True,
                    'white_label': True,
                    'version_history': True,
                    'advanced_export': True,
                    'dedicated_support': True,
                    'sso': True,
                    'audit_logs': True,
                },
                'sort_order': 3,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for tier_data in tiers:
            tier, created = SubscriptionTier.objects.update_or_create(
                slug=tier_data['slug'],
                defaults=tier_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created tier: {tier.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated tier: {tier.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nInitialization complete: {created_count} created, {updated_count} updated'
            )
        )
