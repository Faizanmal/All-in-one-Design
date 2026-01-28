from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SlackWorkspaceViewSet, MicrosoftTeamsWorkspaceViewSet,
    SlackChannelViewSet, TeamsChannelViewSet,
    ShareDesignView, SlackCommandWebhookView, SlackEventWebhookView,
    NotificationPreferenceViewSet, IntegrationMessageViewSet,
    IntegrationStatsView
)

router = DefaultRouter()
router.register(r'slack/workspaces', SlackWorkspaceViewSet, basename='slack-workspace')
router.register(r'slack/channels', SlackChannelViewSet, basename='slack-channel')
router.register(r'teams/workspaces', MicrosoftTeamsWorkspaceViewSet, basename='teams-workspace')
router.register(r'teams/channels', TeamsChannelViewSet, basename='teams-channel')
router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'messages', IntegrationMessageViewSet, basename='integration-message')

urlpatterns = [
    path('', include(router.urls)),
    path('share/', ShareDesignView.as_view(), name='share-design'),
    path('webhooks/slack/commands/', SlackCommandWebhookView.as_view(), name='slack-commands'),
    path('webhooks/slack/events/', SlackEventWebhookView.as_view(), name='slack-events'),
    path('stats/', IntegrationStatsView.as_view(), name='integration-stats'),
]
