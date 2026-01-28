from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import (
    AgencyViewSet, ClientViewSet, ClientPortalViewSet, ClientFeedbackViewSet,
    APIKeyViewSet, AgencyBillingViewSet, AgencyInvoiceViewSet, BrandLibraryViewSet,
    client_portal_access, submit_client_feedback
)

router = DefaultRouter()
router.register(r'agencies', AgencyViewSet, basename='agency')

# Nested routes for agency resources
agency_router = nested_routers.NestedDefaultRouter(router, r'agencies', lookup='agency')
agency_router.register(r'clients', ClientViewSet, basename='client')
agency_router.register(r'portals', ClientPortalViewSet, basename='client-portal')
agency_router.register(r'feedback', ClientFeedbackViewSet, basename='client-feedback')
agency_router.register(r'api-keys', APIKeyViewSet, basename='api-key')
agency_router.register(r'billing', AgencyBillingViewSet, basename='agency-billing')
agency_router.register(r'invoices', AgencyInvoiceViewSet, basename='agency-invoice')
agency_router.register(r'brand-libraries', BrandLibraryViewSet, basename='brand-library')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(agency_router.urls)),
    path('portal/<str:token>/', client_portal_access, name='client-portal-access'),
    path('portal/<str:token>/feedback/', submit_client_feedback, name='client-portal-feedback'),
]
