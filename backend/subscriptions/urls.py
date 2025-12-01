from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionTierViewSet,
    SubscriptionViewSet,
    CouponViewSet,
    billing_history,
    create_checkout_session,
    create_billing_portal,
)
from .webhooks import stripe_webhook
from .marketplace_views import (
    MarketplaceTemplateViewSet,
    TemplateReviewViewSet,
    CreatorProfileViewSet,
    WhiteLabelConfigViewSet,
    my_purchases,
    my_sales
)
from .quota_views import (
    AIUsageQuotaViewSet,
    AIUsageRecordViewSet,
    BudgetAlertViewSet,
    usage_summary,
    quota_dashboard,
    cost_estimate,
    ai_model_pricing,
)

router = DefaultRouter()
router.register(r'tiers', SubscriptionTierViewSet, basename='subscription-tier')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'coupons', CouponViewSet, basename='coupon')

# Marketplace routers
router.register(r'marketplace/templates', MarketplaceTemplateViewSet, basename='marketplace-template')
router.register(r'marketplace/reviews', TemplateReviewViewSet, basename='template-review')
router.register(r'marketplace/creators', CreatorProfileViewSet, basename='creator-profile')
router.register(r'white-label', WhiteLabelConfigViewSet, basename='white-label')

# Quota routers
router.register(r'quotas', AIUsageQuotaViewSet, basename='ai-quota')
router.register(r'usage-records', AIUsageRecordViewSet, basename='usage-record')
router.register(r'budget-alerts', BudgetAlertViewSet, basename='budget-alert')

urlpatterns = [
    path('', include(router.urls)),
    path('billing-history/', billing_history, name='billing-history'),
    
    # Stripe endpoints
    path('create-checkout-session/', create_checkout_session, name='create-checkout-session'),
    path('billing-portal/', create_billing_portal, name='billing-portal'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    
    # Marketplace endpoints
    path('marketplace/my-purchases/', my_purchases, name='my-purchases'),
    path('marketplace/my-sales/', my_sales, name='my-sales'),
    
    # Quota & Usage endpoints
    path('quota/usage-summary/', usage_summary, name='usage-summary'),
    path('quota/dashboard/', quota_dashboard, name='quota-dashboard'),
    path('quota/estimate/', cost_estimate, name='cost-estimate'),
    path('quota/pricing/', ai_model_pricing, name='ai-model-pricing'),
]
