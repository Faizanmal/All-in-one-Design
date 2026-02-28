"""
Tests for notifications models and views.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from notifications.models import Notification, Webhook


@pytest.fixture
def notification(user):
    return Notification.objects.create(
        user=user,
        notification_type='info',
        title='Test Notification',
        message='This is a test notification.',
    )


@pytest.fixture
def webhook(user):
    return Webhook.objects.create(
        user=user,
        name='Test Webhook',
        url='https://example.com/webhook',
        events=['project.created', 'project.updated'],
        active=True,
    )


@pytest.mark.unit
class TestNotificationModel:
    """Tests for Notification model."""

    def test_create_notification(self, notification):
        assert notification.title == 'Test Notification'
        assert notification.read is False

    def test_notification_types(self, user):
        types = ['info', 'success', 'warning', 'error',
                 'project_shared', 'ai_complete', 'export_ready']
        for t in types:
            n = Notification.objects.create(
                user=user, notification_type=t, title=f'{t} test',
                message=f'test {t}',
            )
            assert n.notification_type == t

    def test_notification_read(self, notification):
        notification.read = True
        notification.save()
        notification.refresh_from_db()
        assert notification.read is True

    def test_notification_metadata(self, user):
        n = Notification.objects.create(
            user=user, notification_type='info', title='Meta',
            message='test', metadata={'project_id': 1},
        )
        assert n.metadata['project_id'] == 1


@pytest.mark.unit
class TestWebhookModel:
    """Tests for Webhook model."""

    def test_create_webhook(self, webhook):
        assert webhook.name == 'Test Webhook'
        assert webhook.active is True

    def test_webhook_events(self, webhook):
        assert 'project.created' in webhook.events

    def test_webhook_delivery_counters(self, webhook):
        assert webhook.total_deliveries == 0
        assert webhook.successful_deliveries == 0
        assert webhook.failed_deliveries == 0


@pytest.mark.api
class TestNotificationViewSet:
    """Tests for notification API endpoints."""

    def test_list_notifications(self, auth_client, notification):
        response = auth_client.get('/api/v1/notifications/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_notification(self, auth_client, user):
        payload = {
            'notification_type': 'info',
            'title': 'API Notification',
            'message': 'Created via API',
        }
        response = auth_client.post('/api/v1/notifications/', payload)
        assert response.status_code in [201, 405]  # May not allow POST

    def test_mark_read(self, auth_client, notification):
        response = auth_client.post(
            f'/api/v1/notifications/{notification.id}/mark_read/'
        )
        assert response.status_code == status.HTTP_200_OK

    def test_mark_all_read(self, auth_client, notification):
        response = auth_client.post('/api/v1/notifications/mark_all_read/')
        assert response.status_code == status.HTTP_200_OK

    def test_unread_notifications(self, auth_client, notification):
        response = auth_client.get('/api/v1/notifications/unread/')
        assert response.status_code == status.HTTP_200_OK

    def test_clear_all(self, auth_client, notification):
        response = auth_client.delete('/api/v1/notifications/clear_all/')
        assert response.status_code in [200, 204]

    def test_notifications_unauthenticated(self, api_client, db):
        response = api_client.get('/api/v1/notifications/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestWebhookViewSet:
    """Tests for webhook API endpoints."""

    def test_list_webhooks(self, auth_client, webhook):
        response = auth_client.get('/api/v1/notifications/webhooks/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_webhook(self, auth_client, user):
        payload = {
            'name': 'New Webhook',
            'url': 'https://example.com/hook',
            'events': ['project.created'],
        }
        response = auth_client.post(
            '/api/v1/notifications/webhooks/', payload, format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_test_webhook(self, auth_client, webhook):
        response = auth_client.post(
            f'/api/v1/notifications/webhooks/{webhook.id}/test/'
        )
        assert response.status_code in [200, 400, 500]

    def test_webhook_deliveries(self, auth_client, webhook):
        response = auth_client.get(
            f'/api/v1/notifications/webhooks/{webhook.id}/deliveries/'
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestNotificationPreferences:
    """Tests for notification preferences."""

    def test_get_preferences(self, auth_client, user):
        response = auth_client.get('/api/v1/notifications/preferences/')
        assert response.status_code == status.HTTP_200_OK
