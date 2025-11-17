from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification, Webhook, WebhookDelivery, UserPreference
from .serializers import (
    NotificationSerializer, WebhookSerializer, 
    WebhookDeliverySerializer, UserPreferenceSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = self.get_queryset().filter(read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response({
            'count': notifications.count(),
            'notifications': serializer.data
        })

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        updated = self.get_queryset().filter(read=False).update(read=True)
        return Response({
            'message': f'{updated} notifications marked as read',
            'count': updated
        })

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Delete all notifications"""
        deleted = self.get_queryset().delete()[0]
        return Response({
            'message': f'{deleted} notifications deleted',
            'count': deleted
        })


class WebhookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing webhooks
    """
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Webhook.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send a test webhook"""
        webhook = self.get_object()
        from .tasks import send_webhook
        
        test_payload = {
            'event': 'webhook.test',
            'timestamp': timezone.now().isoformat(),
            'data': {
                'message': 'This is a test webhook'
            }
        }
        
        # Send webhook asynchronously
        send_webhook.delay(webhook.id, 'webhook.test', test_payload)
        
        return Response({
            'message': 'Test webhook queued for delivery',
            'webhook': webhook.name
        })

    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        """Get webhook delivery history"""
        webhook = self.get_object()
        deliveries = WebhookDelivery.objects.filter(webhook=webhook)[:50]
        serializer = WebhookDeliverySerializer(deliveries, many=True)
        return Response(serializer.data)


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notification preferences
    """
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create user preferences"""
        obj, created = UserPreference.objects.get_or_create(user=self.request.user)
        return obj

    def list(self, request, *args, **kwargs):
        """Return single preference object instead of list"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
