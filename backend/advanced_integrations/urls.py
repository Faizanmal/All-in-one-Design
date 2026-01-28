from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IntegrationProviderViewSet, UserIntegrationViewSet,
    SlackIntegrationViewSet, JiraIntegrationViewSet, AdobeIntegrationViewSet,
    GoogleDriveIntegrationViewSet, DropboxIntegrationViewSet,
    NotionIntegrationViewSet, WordPressIntegrationViewSet,
    WebhookEndpointViewSet, ZapierIntegrationViewSet, IntegrationSyncViewSet,
    oauth_callback, webhook_receiver
)

router = DefaultRouter()
router.register(r'providers', IntegrationProviderViewSet, basename='provider')
router.register(r'connections', UserIntegrationViewSet, basename='user-integration')
router.register(r'slack', SlackIntegrationViewSet, basename='slack')
router.register(r'jira', JiraIntegrationViewSet, basename='jira')
router.register(r'adobe', AdobeIntegrationViewSet, basename='adobe')
router.register(r'google-drive', GoogleDriveIntegrationViewSet, basename='google-drive')
router.register(r'dropbox', DropboxIntegrationViewSet, basename='dropbox')
router.register(r'notion', NotionIntegrationViewSet, basename='notion')
router.register(r'wordpress', WordPressIntegrationViewSet, basename='wordpress')
router.register(r'webhooks', WebhookEndpointViewSet, basename='webhook')
router.register(r'zapier', ZapierIntegrationViewSet, basename='zapier')
router.register(r'syncs', IntegrationSyncViewSet, basename='sync')

urlpatterns = [
    path('', include(router.urls)),
    path('oauth/callback/<str:provider>/', oauth_callback, name='oauth-callback'),
    path('webhook/<uuid:webhook_id>/receive/', webhook_receiver, name='webhook-receiver'),
]
