from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import secrets
import hmac
import hashlib

from .models import (
    IntegrationProvider, UserIntegration, SlackIntegration, JiraIntegration,
    AdobeIntegration, GoogleDriveIntegration, DropboxIntegration,
    NotionIntegration, WordPressIntegration, WebhookEndpoint, WebhookLog,
    ZapierIntegration, IntegrationSync
)
from .serializers import (
    IntegrationProviderSerializer, UserIntegrationSerializer,
    SlackIntegrationSerializer, JiraIntegrationSerializer,
    AdobeIntegrationSerializer, GoogleDriveIntegrationSerializer,
    DropboxIntegrationSerializer, NotionIntegrationSerializer,
    WordPressIntegrationSerializer, WebhookEndpointSerializer,
    WebhookLogSerializer, ZapierIntegrationSerializer, IntegrationSyncSerializer
)


class IntegrationProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for available integration providers"""
    queryset = IntegrationProvider.objects.filter(is_active=True)
    serializer_class = IntegrationProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get providers grouped by type"""
        providers = {}
        for provider_type, _ in IntegrationProvider.PROVIDER_TYPES:
            providers[provider_type] = IntegrationProviderSerializer(
                self.queryset.filter(provider_type=provider_type),
                many=True
            ).data
        return Response(providers)


class UserIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for user's connected integrations"""
    serializer_class = UserIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserIntegration.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def connected(self, request):
        """Get all connected integrations"""
        integrations = self.get_queryset().filter(status='connected')
        return Response(UserIntegrationSerializer(integrations, many=True).data)
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """Disconnect an integration"""
        integration = self.get_object()
        integration.status = 'disconnected'
        integration.access_token = ''
        integration.refresh_token = ''
        integration.save()
        return Response({'status': 'disconnected'})
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh OAuth token"""
        integration = self.get_object()
        
        # In production, use OAuth library to refresh token
        # This is a placeholder
        integration.token_expires = timezone.now() + timezone.timedelta(hours=1)
        integration.save()
        
        return Response({'status': 'refreshed', 'expires': integration.token_expires})
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Trigger manual sync"""
        integration = self.get_object()
        
        sync = IntegrationSync.objects.create(
            user_integration=integration,
            sync_type=request.data.get('sync_type', 'two_way'),
            status='in_progress',
            started_at=timezone.now()
        )
        
        # In production, trigger async sync task
        # For now, simulate completion
        sync.status = 'completed'
        sync.items_synced = 10
        sync.completed_at = timezone.now()
        sync.save()
        
        integration.last_sync = timezone.now()
        integration.save()
        
        return Response(IntegrationSyncSerializer(sync).data)


class SlackIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Slack integration settings"""
    serializer_class = SlackIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SlackIntegration.objects.filter(
            user_integration__user=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def send_test_message(self, request, pk=None):
        """Send a test message to Slack"""
        slack = self.get_object()
        
        # In production, use Slack API
        return Response({
            'status': 'sent',
            'channel': slack.notification_channel,
            'message': 'Test notification from Design Platform'
        })
    
    @action(detail=True, methods=['get'])
    def channels(self, request, pk=None):
        """Get available Slack channels"""
        # In production, fetch from Slack API
        return Response({
            'channels': [
                {'id': 'C1234567890', 'name': 'general'},
                {'id': 'C0987654321', 'name': 'design-team'},
            ]
        })


class JiraIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Jira integration settings"""
    serializer_class = JiraIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JiraIntegration.objects.filter(
            user_integration__user=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """Get available Jira projects"""
        # In production, fetch from Jira API
        return Response({
            'projects': [
                {'key': 'DESIGN', 'name': 'Design Project'},
                {'key': 'WEB', 'name': 'Website Redesign'},
            ]
        })
    
    @action(detail=True, methods=['post'])
    def create_issue(self, request, pk=None):
        """Create a Jira issue"""
        jira = self.get_object()
        
        # In production, create issue via Jira API
        return Response({
            'issue_key': f"{jira.default_project_key}-123",
            'summary': request.data.get('summary'),
            'url': f"{jira.site_url}/browse/{jira.default_project_key}-123"
        })


class AdobeIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Adobe CC integration"""
    serializer_class = AdobeIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AdobeIntegration.objects.filter(
            user_integration__user=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def libraries(self, request, pk=None):
        """Get CC Libraries"""
        # In production, fetch from Adobe API
        return Response({
            'libraries': [
                {'id': 'lib1', 'name': 'Brand Assets'},
                {'id': 'lib2', 'name': 'Icon Library'},
            ]
        })
    
    @action(detail=True, methods=['post'])
    def export_to_library(self, request, pk=None):
        """Export asset to CC Library"""
        return Response({
            'status': 'exported',
            'library_id': request.data.get('library_id'),
            'asset_id': request.data.get('asset_id')
        })


class GoogleDriveIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Google Drive integration"""
    serializer_class = GoogleDriveIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return GoogleDriveIntegration.objects.filter(
            user_integration__user=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def folders(self, request, pk=None):
        """Get Drive folders"""
        return Response({
            'folders': [
                {'id': 'folder1', 'name': 'Design Projects'},
                {'id': 'folder2', 'name': 'Exports'},
            ]
        })
    
    @action(detail=True, methods=['post'])
    def upload(self, request, pk=None):
        """Upload file to Drive"""
        return Response({
            'status': 'uploaded',
            'file_id': 'gdrive_file_123',
            'web_view_link': 'https://drive.google.com/file/...'
        })


class DropboxIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Dropbox integration"""
    serializer_class = DropboxIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DropboxIntegration.objects.filter(
            user_integration__user=self.request.user
        )


class NotionIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notion integration"""
    serializer_class = NotionIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NotionIntegration.objects.filter(
            user_integration__user=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def databases(self, request, pk=None):
        """Get Notion databases"""
        return Response({
            'databases': [
                {'id': 'db1', 'title': 'Project Tracker'},
                {'id': 'db2', 'title': 'Asset Library'},
            ]
        })
    
    @action(detail=True, methods=['post'])
    def create_page(self, request, pk=None):
        """Create a Notion page"""
        return Response({
            'page_id': 'notion_page_123',
            'url': 'https://notion.so/page/...'
        })


class WordPressIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for WordPress integration"""
    serializer_class = WordPressIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WordPressIntegration.objects.filter(
            user_integration__user=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish design to WordPress"""
        wp = self.get_object()
        
        return Response({
            'post_id': 123,
            'url': f"{wp.site_url}/?p=123",
            'status': wp.default_status
        })


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """ViewSet for webhook management"""
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WebhookEndpoint.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Generate webhook secret
        secret = secrets.token_hex(32)
        serializer.save(user=self.request.user, secret=secret)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send a test webhook"""
        webhook = self.get_object()
        
        # Create test payload
        payload = {
            'event': 'test',
            'timestamp': timezone.now().isoformat(),
            'message': 'This is a test webhook'
        }
        
        # In production, actually send the webhook
        log = WebhookLog.objects.create(
            webhook=webhook,
            event_type='test',
            payload=payload,
            status='success',
            response_code=200,
            completed_at=timezone.now()
        )
        
        webhook.last_triggered = timezone.now()
        webhook.save()
        
        return Response(WebhookLogSerializer(log).data)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get webhook logs"""
        webhook = self.get_object()
        logs = webhook.logs.all()[:50]
        return Response(WebhookLogSerializer(logs, many=True).data)
    
    @action(detail=True, methods=['post'])
    def regenerate_secret(self, request, pk=None):
        """Regenerate webhook secret"""
        webhook = self.get_object()
        webhook.secret = secrets.token_hex(32)
        webhook.save()
        
        return Response({'secret': webhook.secret})


class ZapierIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Zapier hooks"""
    serializer_class = ZapierIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ZapierIntegration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IntegrationSyncViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for sync history"""
    serializer_class = IntegrationSyncSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return IntegrationSync.objects.filter(
            user_integration__user=self.request.user
        )


# OAuth callback handlers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_callback(request, provider):
    """Handle OAuth callbacks from providers"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code:
        return Response({'error': 'No authorization code'}, status=400)
    
    # In production:
    # 1. Validate state parameter
    # 2. Exchange code for access token
    # 3. Get user info from provider
    # 4. Create/update UserIntegration
    
    return Response({
        'status': 'success',
        'provider': provider,
        'message': 'Integration connected successfully'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_receiver(request, webhook_id):
    """Receive incoming webhooks from external services"""
    try:
        webhook = WebhookEndpoint.objects.get(id=webhook_id, is_active=True)
    except WebhookEndpoint.DoesNotExist:
        return Response({'error': 'Webhook not found'}, status=404)
    
    # Verify signature if secret is set
    if webhook.secret:
        signature = request.headers.get('X-Webhook-Signature')
        if signature:
            expected = hmac.new(
                webhook.secret.encode(),
                request.body,
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return Response({'error': 'Invalid signature'}, status=401)
    
    # Log the received webhook
    WebhookLog.objects.create(
        webhook=webhook,
        event_type='received',
        payload=request.data,
        status='success'
    )
    
    return Response({'status': 'received'})
