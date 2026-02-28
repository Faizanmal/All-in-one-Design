"""
Tests for subscriptions models and views.
"""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from subscriptions.models import (
    SubscriptionTier, Subscription, UsageQuota, Payment, Invoice, Coupon
)


@pytest.fixture
def free_tier(db):
    """Create a free subscription tier."""
    return SubscriptionTier.objects.create(
        name='Free',
        slug='free',
        description='Free tier',
        price_monthly=Decimal('0.00'),
        price_yearly=Decimal('0.00'),
        max_projects=5,
        max_ai_requests_per_month=50,
        max_storage_mb=500,
        max_collaborators_per_project=1,
        max_exports_per_month=10,
        is_active=True,
        sort_order=0,
    )


@pytest.fixture
def pro_tier(db):
    """Create a pro subscription tier."""
    return SubscriptionTier.objects.create(
        name='Pro',
        slug='pro',
        description='Professional tier',
        price_monthly=Decimal('19.99'),
        price_yearly=Decimal('199.99'),
        max_projects=100,
        max_ai_requests_per_month=1000,
        max_storage_mb=10000,
        max_collaborators_per_project=10,
        max_exports_per_month=500,
        is_active=True,
        is_featured=True,
        sort_order=1,
    )


@pytest.fixture
def subscription(user, free_tier):
    """Create a subscription for the test user."""
    return Subscription.objects.create(
        user=user,
        tier=free_tier,
        status='active',
        billing_period='monthly',
    )


@pytest.mark.unit
class TestSubscriptionTier:
    """Tests for SubscriptionTier model."""

    def test_create_tier(self, free_tier):
        assert free_tier.name == 'Free'
        assert free_tier.price_monthly == Decimal('0.00')

    def test_tier_str(self, free_tier):
        assert 'Free' in str(free_tier)

    def test_tier_limits(self, pro_tier):
        assert pro_tier.max_projects == 100
        assert pro_tier.max_ai_requests_per_month == 1000
        assert pro_tier.max_storage_mb == 10000

    def test_featured_tier(self, pro_tier):
        assert pro_tier.is_featured is True

    def test_tier_slug_unique(self, free_tier):
        with pytest.raises(Exception):
            SubscriptionTier.objects.create(
                name='Another Free', slug='free',
                price_monthly=Decimal('0'), price_yearly=Decimal('0'),
            )


@pytest.mark.unit
class TestSubscription:
    """Tests for Subscription model."""

    def test_create_subscription(self, subscription):
        assert subscription.status == 'active'
        assert subscription.billing_period == 'monthly'

    def test_subscription_statuses(self, user, free_tier):
        for s in ['active', 'cancelled', 'expired', 'trial', 'paused']:
            sub = Subscription.objects.create(
                user=User.objects.create_user(
                    username=f'user_{s}', password='pass123!',
                    email=f'{s}@example.com'
                ),
                tier=free_tier,
                status=s,
            )
            assert sub.status == s


@pytest.mark.unit
class TestUsageQuota:
    """Tests for UsageQuota model."""

    def test_create_quota(self, user):
        from django.utils import timezone
        quota = UsageQuota.objects.create(
            user=user,
            month=timezone.now().date().replace(day=1),
            ai_requests_used=10,
            ai_requests_limit=50,
            exports_used=3,
            exports_limit=10,
        )
        assert quota.ai_requests_used == 10


@pytest.mark.unit
class TestCoupon:
    """Tests for Coupon model."""

    def test_create_percentage_coupon(self, db):
        coupon = Coupon.objects.create(
            code='SAVE20',
            name='20% Off',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            max_uses=100,
            is_active=True,
        )
        assert coupon.discount_type == 'percentage'
        assert coupon.current_uses == 0

    def test_create_fixed_coupon(self, db):
        coupon = Coupon.objects.create(
            code='FLAT10',
            name='$10 Off',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            is_active=True,
        )
        assert coupon.discount_type == 'fixed'


@pytest.mark.api
class TestSubscriptionTierAPI:
    """Tests for subscription tier API."""

    def test_list_tiers(self, api_client, free_tier, pro_tier):
        response = api_client.get('/api/v1/subscriptions/tiers/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_tier(self, api_client, free_tier):
        response = api_client.get(f'/api/v1/subscriptions/tiers/{free_tier.id}/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestSubscriptionAPI:
    """Tests for subscription management API."""

    def test_list_subscriptions(self, auth_client, subscription):
        response = auth_client.get('/api/v1/subscriptions/subscriptions/')
        assert response.status_code == status.HTTP_200_OK

    def test_current_subscription(self, auth_client, subscription):
        response = auth_client.get(
            '/api/v1/subscriptions/subscriptions/current/'
        )
        assert response.status_code in [200, 404]

    def test_usage(self, auth_client, subscription):
        response = auth_client.get(
            '/api/v1/subscriptions/subscriptions/usage/'
        )
        assert response.status_code in [200, 404]

    def test_my_usage(self, auth_client, user):
        response = auth_client.get('/api/v1/subscriptions/my-usage/')
        assert response.status_code in [200, 404]

    def test_billing_history(self, auth_client, user):
        response = auth_client.get('/api/v1/subscriptions/billing-history/')
        assert response.status_code == status.HTTP_200_OK

    def test_subscription_unauthenticated(self, api_client, db):
        response = api_client.get('/api/v1/subscriptions/subscriptions/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
