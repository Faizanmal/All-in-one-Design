from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
import requests

from projects.models import Project
from .models import (
    SlackWorkspace, SlackChannel, MicrosoftTeamsWorkspace, TeamsChannel,
    IntegrationMessage, BotCommand, NotificationPreference
)
from .serializers import (
    SlackWorkspaceSerializer, SlackChannelSerializer,
    MicrosoftTeamsWorkspaceSerializer, TeamsChannelSerializer,
    IntegrationMessageSerializer, NotificationPreferenceSerializer, ShareDesignSerializer,
    SlackOAuthSerializer, TeamsOAuthSerializer, SlackCommandSerializer,
    ChannelListSerializer, LinkChannelSerializer
)
from .services import (
    SlackService, TeamsService, BotCommandHandler,
    IntegrationNotificationService, verify_slack_signature
)


class SlackWorkspaceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Slack workspace integrations"""
    serializer_class = SlackWorkspaceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SlackWorkspace.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def auth_url(self, request):
        """Get Slack OAuth URL"""
        client_id = getattr(settings, 'SLACK_CLIENT_ID', '')
        redirect_uri = getattr(settings, 'SLACK_REDIRECT_URI', '')
        
        scopes = [
            'channels:read', 'channels:join', 'chat:write',
            'files:write', 'users:read', 'commands'
        ]
        
        url = (
            f"https://slack.com/oauth/v2/authorize?"
            f"client_id={client_id}&"
            f"scope={','.join(scopes)}&"
            f"redirect_uri={redirect_uri}&"
            f"state={request.user.id}"
        )
        
        return Response({'auth_url': url})
    
    @action(detail=False, methods=['post'])
    def callback(self, request):
        """Handle Slack OAuth callback"""
        serializer = SlackOAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        
        # Exchange code for token
        response = requests.post('https://slack.com/api/oauth.v2.access', data={
            'client_id': getattr(settings, 'SLACK_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'SLACK_CLIENT_SECRET', ''),
            'code': code,
            'redirect_uri': getattr(settings, 'SLACK_REDIRECT_URI', ''),
        })
        
        data = response.json()
        
        if not data.get('ok'):
            return Response(
                {'error': data.get('error', 'OAuth failed')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or update workspace
        workspace, created = SlackWorkspace.objects.update_or_create(
            workspace_id=data['team']['id'],
            defaults={
                'user': request.user,
                'workspace_name': data['team']['name'],
                'access_token': data['access_token'],
                'bot_token': data.get('access_token', ''),
                'bot_user_id': data.get('bot_user_id', ''),
            }
        )
        
        return Response(SlackWorkspaceSerializer(workspace).data)
    
    @action(detail=True, methods=['get'])
    def channels(self, request, pk=None):
        """Get available channels in workspace"""
        workspace = self.get_object()
        service = SlackService(workspace)
        channels = service.get_channels()
        
        return Response(ChannelListSerializer(channels, many=True).data)
    
    @action(detail=True, methods=['post'])
    def link_channel(self, request, pk=None):
        """Link a channel to a project"""
        workspace = self.get_object()
        serializer = LinkChannelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        project = get_object_or_404(
            Project.objects.filter(user=request.user),
            id=serializer.validated_data['project_id']
        )
        
        channel, created = SlackChannel.objects.update_or_create(
            workspace=workspace,
            channel_id=serializer.validated_data['channel_id'],
            defaults={
                'project': project,
                'channel_name': serializer.validated_data['channel_name'],
                'notify_on_comment': serializer.validated_data.get('notify_on_comment', True),
                'notify_on_update': serializer.validated_data.get('notify_on_update', True),
                'notify_on_export': serializer.validated_data.get('notify_on_export', False),
                'notify_on_share': serializer.validated_data.get('notify_on_share', True),
            }
        )
        
        return Response(SlackChannelSerializer(channel).data)
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """Disconnect Slack workspace"""
        workspace = self.get_object()
        workspace.is_active = False
        workspace.save()
        return Response({'status': 'disconnected'})


class MicrosoftTeamsWorkspaceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Microsoft Teams workspace integrations"""
    serializer_class = MicrosoftTeamsWorkspaceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MicrosoftTeamsWorkspace.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def auth_url(self, request):
        """Get Microsoft OAuth URL"""
        client_id = getattr(settings, 'MICROSOFT_CLIENT_ID', '')
        redirect_uri = getattr(settings, 'MICROSOFT_REDIRECT_URI', '')
        
        scopes = [
            'https://graph.microsoft.com/Team.ReadBasic.All',
            'https://graph.microsoft.com/Channel.ReadBasic.All',
            'https://graph.microsoft.com/ChannelMessage.Send',
            'offline_access'
        ]
        
        url = (
            f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
            f"client_id={client_id}&"
            f"response_type=code&"
            f"redirect_uri={redirect_uri}&"
            f"scope={' '.join(scopes)}&"
            f"state={request.user.id}"
        )
        
        return Response({'auth_url': url})
    
    @action(detail=False, methods=['post'])
    def callback(self, request):
        """Handle Microsoft OAuth callback"""
        serializer = TeamsOAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        tenant = serializer.validated_data.get('tenant', 'common')
        
        # Exchange code for token
        response = requests.post(
            f'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token',
            data={
                'client_id': getattr(settings, 'MICROSOFT_CLIENT_ID', ''),
                'client_secret': getattr(settings, 'MICROSOFT_CLIENT_SECRET', ''),
                'code': code,
                'redirect_uri': getattr(settings, 'MICROSOFT_REDIRECT_URI', ''),
                'grant_type': 'authorization_code',
                'scope': 'https://graph.microsoft.com/.default offline_access',
            }
        )
        
        data = response.json()
        
        if 'error' in data:
            return Response(
                {'error': data.get('error_description', 'OAuth failed')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get team info
        headers = {'Authorization': f'Bearer {data["access_token"]}'}
        teams_response = requests.get(
            'https://graph.microsoft.com/v1.0/me/joinedTeams',
            headers=headers
        )
        teams_data = teams_response.json()
        
        if not teams_data.get('value'):
            return Response(
                {'error': 'No Teams found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use first team for now
        team_info = teams_data['value'][0]
        
        workspace, created = MicrosoftTeamsWorkspace.objects.update_or_create(
            team_id=team_info['id'],
            defaults={
                'user': request.user,
                'tenant_id': tenant,
                'team_name': team_info['displayName'],
                'access_token': data['access_token'],
                'refresh_token': data.get('refresh_token', ''),
                'token_expires_at': timezone.now() + timezone.timedelta(
                    seconds=data.get('expires_in', 3600)
                ),
            }
        )
        
        return Response(MicrosoftTeamsWorkspaceSerializer(workspace).data)
    
    @action(detail=True, methods=['get'])
    def channels(self, request, pk=None):
        """Get available channels in team"""
        workspace = self.get_object()
        service = TeamsService(workspace)
        channels = service.get_channels()
        
        formatted_channels = [
            {
                'id': c.get('id'),
                'name': c.get('displayName'),
                'type': c.get('membershipType', 'standard'),
                'is_private': c.get('membershipType') == 'private'
            }
            for c in channels
        ]
        
        return Response(formatted_channels)
    
    @action(detail=True, methods=['post'])
    def link_channel(self, request, pk=None):
        """Link a channel to a project"""
        workspace = self.get_object()
        serializer = LinkChannelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        project = get_object_or_404(
            Project.objects.filter(user=request.user),
            id=serializer.validated_data['project_id']
        )
        
        channel, created = TeamsChannel.objects.update_or_create(
            workspace=workspace,
            channel_id=serializer.validated_data['channel_id'],
            defaults={
                'project': project,
                'channel_name': serializer.validated_data['channel_name'],
                'notify_on_comment': serializer.validated_data.get('notify_on_comment', True),
                'notify_on_update': serializer.validated_data.get('notify_on_update', True),
                'notify_on_export': serializer.validated_data.get('notify_on_export', False),
                'notify_on_share': serializer.validated_data.get('notify_on_share', True),
            }
        )
        
        return Response(TeamsChannelSerializer(channel).data)


class SlackChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Slack channels"""
    serializer_class = SlackChannelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SlackChannel.objects.filter(
            workspace__user=self.request.user
        ).select_related('workspace', 'project')


class TeamsChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Teams channels"""
    serializer_class = TeamsChannelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TeamsChannel.objects.filter(
            workspace__user=self.request.user
        ).select_related('workspace', 'project')


class ShareDesignView(APIView):
    """Share a design to Slack or Teams"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(request=ShareDesignSerializer)
    def post(self, request):
        serializer = ShareDesignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        project = get_object_or_404(
            Project.objects.filter(user=request.user) |
            Project.objects.filter(collaborators=request.user),
            id=serializer.validated_data['project_id']
        )
        
        channel_type = serializer.validated_data['channel_type']
        channel_id = serializer.validated_data['channel_id']
        message = serializer.validated_data.get('message', '')
        
        if channel_type == 'slack':
            channel = get_object_or_404(
                SlackChannel.objects.filter(workspace__user=request.user),
                id=channel_id
            )
        else:
            channel = get_object_or_404(
                TeamsChannel.objects.filter(workspace__user=request.user),
                id=channel_id
            )
        
        result = IntegrationNotificationService.share_design(project, channel, message)
        
        return Response(IntegrationMessageSerializer(result).data)


class SlackCommandWebhookView(APIView):
    """Handle incoming Slack slash commands"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Verify request signature
        if not verify_slack_signature(request):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = SlackCommandSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'text': 'Invalid command format'})
        
        data = serializer.validated_data
        
        # Parse command
        command = data.get('command', '').replace('/design', '').strip()
        text = data.get('text', '')
        
        # Split text into command and arguments
        parts = text.split(' ', 1)
        sub_command = parts[0] if parts else 'help'
        args = parts[1] if len(parts) > 1 else ''
        
        # Find linked user
        try:
            workspace = SlackWorkspace.objects.get(workspace_id=data['team_id'])
            user = workspace.user
        except SlackWorkspace.DoesNotExist:
            user = None
        
        # Record command
        bot_command = BotCommand.objects.create(
            platform='slack',
            command=sub_command,
            arguments=args,
            workspace_id=data['team_id'],
            channel_id=data['channel_id'],
            user_external_id=data['user_id'],
            user=user,
        )
        
        # Handle command
        handler = BotCommandHandler('slack', user)
        response = handler.handle_command(sub_command, args)
        
        # Update command record
        bot_command.response_sent = True
        bot_command.response_content = response
        bot_command.processed_at = timezone.now()
        bot_command.save()
        
        return Response(response)


class SlackEventWebhookView(APIView):
    """Handle Slack events (interactive components, etc.)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Handle URL verification
        if request.data.get('type') == 'url_verification':
            return Response({'challenge': request.data.get('challenge')})
        
        # Verify request
        if not verify_slack_signature(request):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        event = request.data.get('event', {})
        event_type = event.get('type')
        
        # Handle different event types
        if event_type == 'app_mention':
            # Handle app mentions
            pass
        elif event_type == 'message':
            # Handle messages
            pass
        
        return Response({'ok': True})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj, created = NotificationPreference.objects.get_or_create(user=self.request.user)
        return obj
    
    def list(self, request):
        obj = self.get_object()
        return Response(NotificationPreferenceSerializer(obj).data)
    
    def create(self, request):
        return self.update(request)
    
    def update(self, request, pk=None):
        obj = self.get_object()
        serializer = NotificationPreferenceSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class IntegrationMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing integration messages"""
    serializer_class = IntegrationMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = IntegrationMessage.objects.filter(
            user=self.request.user
        ).select_related('project')
        
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(platform=platform)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.order_by('-created_at')


class IntegrationStatsView(APIView):
    """Get integration statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        slack_workspaces = SlackWorkspace.objects.filter(user=user, is_active=True).count()
        teams_workspaces = MicrosoftTeamsWorkspace.objects.filter(user=user, is_active=True).count()
        
        slack_channels = SlackChannel.objects.filter(workspace__user=user, is_active=True).count()
        teams_channels = TeamsChannel.objects.filter(workspace__user=user, is_active=True).count()
        
        messages_sent = IntegrationMessage.objects.filter(user=user, sent=True).count()
        
        return Response({
            'slack': {
                'workspaces': slack_workspaces,
                'channels': slack_channels,
            },
            'teams': {
                'workspaces': teams_workspaces,
                'channels': teams_channels,
            },
            'messages_sent': messages_sent,
        })
