"""
Subscriptions Tests
"""
from django.test import TestCase
from django.contrib.auth.models import User
from subscriptions.models import SubscriptionTier, Subscription


class SubscriptionTierTestCase(TestCase):
    def setUp(self):
        self.tier = SubscriptionTier.objects.create(
            name='Test Tier',
            slug='test',
            description='Test description',
            price_monthly=9.99,
            price_yearly=99.99,
            max_projects=10,
            max_ai_requests_per_month=100,
            max_storage_mb=1024
        )
    
    def test_tier_creation(self):
        """Test subscription tier creation"""
        self.assertEqual(self.tier.name, 'Test Tier')
        self.assertEqual(self.tier.max_projects, 10)
    
    def test_tier_features(self):
        """Test tier features JSON field"""
        self.tier.features = {'advanced_ai': True}
        self.tier.save()
        self.assertTrue(self.tier.features.get('advanced_ai'))


class SubscriptionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.tier = SubscriptionTier.objects.create(
            name='Pro',
            slug='pro',
            description='Pro tier',
            price_monthly=29.99,
            price_yearly=299.99,
            max_projects=50,
            max_ai_requests_per_month=500,
            max_storage_mb=10240
        )
    
    def test_subscription_creation(self):
        """Test creating a subscription"""
        subscription = Subscription.objects.create(
            user=self.user,
            tier=self.tier,
            status='active'
        )
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.tier.name, 'Pro')
        self.assertTrue(subscription.is_active())
    
    def test_check_limits(self):
        """Test checking resource limits"""
        subscription = Subscription.objects.create(
            user=self.user,
            tier=self.tier,
            status='active'
        )
        # Should be within limits initially
        self.assertTrue(subscription.check_limit('projects'))
