from django.test import TestCase
from django.contrib.auth.models import User
from .models import Notification, Webhook


class NotificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            notification_type='info',
            title='Test Notification',
            message='This is a test'
        )
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.read)

    def test_mark_as_read(self):
        notification = Notification.objects.create(
            user=self.user,
            notification_type='info',
            title='Test',
            message='Test'
        )
        notification.mark_as_read()
        self.assertTrue(notification.read)
        self.assertIsNotNone(notification.read_at)


class WebhookTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_webhook(self):
        webhook = Webhook.objects.create(
            user=self.user,
            name='Test Webhook',
            url='https://example.com/webhook',
            events=['project.created', 'project.updated']
        )
        self.assertEqual(webhook.user, self.user)
        self.assertTrue(webhook.active)
        self.assertEqual(webhook.total_deliveries, 0)


class UserPreferenceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_auto_create_preferences(self):
        # Preferences should be auto-created via signal
        self.assertTrue(hasattr(self.user, 'notification_preferences'))
        preferences = self.user.notification_preferences
        self.assertTrue(preferences.email_on_project_shared)
        self.assertTrue(preferences.notify_project_updates)
