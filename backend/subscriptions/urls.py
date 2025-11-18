from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionTierViewSet,
    SubscriptionViewSet,
    CouponViewSet,
    billing_history
)

router = DefaultRouter()
router.register(r'tiers', SubscriptionTierViewSet, basename='subscription-tier')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
    path('billing-history/', billing_history, name='billing-history'),
]
