from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandKitEnforcementViewSet, BrandViolationLogViewSet

router = DefaultRouter()
router.register(r'enforcement', BrandKitEnforcementViewSet, basename='enforcement')
router.register(r'violations', BrandViolationLogViewSet, basename='violation')

urlpatterns = [
    path('', include(router.urls)),
]
