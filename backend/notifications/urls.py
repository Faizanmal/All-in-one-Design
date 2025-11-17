from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, WebhookViewSet, UserPreferenceViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'preferences', UserPreferenceViewSet, basename='preference')

urlpatterns = [
    path('', include(router.urls)),
]
