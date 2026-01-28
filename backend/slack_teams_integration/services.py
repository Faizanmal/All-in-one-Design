"""
Slack and Microsoft Teams Integration Services
"""
import json
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from django.conf import settings
from django.utils import timezone
from .models import (
    SlackWorkspace, SlackChannel, MicrosoftTeamsWorkspace, TeamsChannel,
    IntegrationMessage, BotCommand
)


class SlackService:
    """Service for Slack API interactions"""
    
    BASE_URL = 'https://slack.com/api'
    
    def __init__(self, workspace: SlackWorkspace):
        self.workspace = workspace
        self.token = workspace.bot_token or workspace.access_token
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request to Slack API"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=kwargs.get('params', {}))
        else:
            response = requests.post(url, headers=headers, json=kwargs.get('json', {}))
        
        return response.json()
    
    def post_message(self, channel_id: str, text: str = None, blocks: List[Dict] = None,
                     attachments: List[Dict] = None, thread_ts: str = None) -> Dict:
        """Post a message to a Slack channel"""
        payload = {
            'channel': channel_id,
        }
        
        if text:
            payload['text'] = text
        if blocks:
            payload['blocks'] = blocks
        if attachments:
            payload['attachments'] = attachments
        if thread_ts:
            payload['thread_ts'] = thread_ts
        
        return self._make_request('POST', 'chat.postMessage', json=payload)
    
    def post_design_preview(self, channel_id: str, project: Any, image_url: str = None,
                           message: str = None) -> Dict:
        """Post a design preview with rich formatting"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎨 {project.name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message or f"*{project.user.username}* shared a design"
                }
            },
        ]
        
        if image_url:
            blocks.append({
                "type": "image",
                "image_url": image_url,
                "alt_text": project.name
            })
        
        blocks.extend([
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Type:* {project.get_project_type_display()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Updated:* {project.updated_at.strftime('%b %d, %Y')}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Design"
                        },
                        "url": f"{settings.FRONTEND_URL}/projects/{project.id}",
                        "action_id": "view_design"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Add Comment"
                        },
                        "action_id": "add_comment"
                    }
                ]
            }
        ])
        
        return self.post_message(channel_id, blocks=blocks, text=f"Design shared: {project.name}")
    
    def post_comment_notification(self, channel_id: str, comment: Any, project: Any) -> Dict:
        """Post a comment notification"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"💬 *New comment* on <{settings.FRONTEND_URL}/projects/{project.id}|{project.name}>"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f">{comment.content}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Posted by *{comment.user.username}*"
                    }
                ]
            }
        ]
        
        return self.post_message(channel_id, blocks=blocks, text=f"New comment on {project.name}")
    
    def get_channels(self) -> List[Dict]:
        """Get list of channels in workspace"""
        result = self._make_request('GET', 'conversations.list', params={
            'types': 'public_channel,private_channel',
            'exclude_archived': True
        })
        
        if result.get('ok'):
            return result.get('channels', [])
        return []
    
    def get_users(self) -> List[Dict]:
        """Get list of users in workspace"""
        result = self._make_request('GET', 'users.list')
        
        if result.get('ok'):
            return result.get('members', [])
        return []
    
    def upload_file(self, channel_id: str, file_content: bytes, filename: str,
                   title: str = None) -> Dict:
        """Upload a file to Slack"""
        # Use files.upload API
        url = f"{self.BASE_URL}/files.upload"
        
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        
        data = {
            'channels': channel_id,
            'filename': filename,
            'title': title or filename,
        }
        
        files = {
            'file': (filename, file_content),
        }
        
        response = requests.post(url, headers=headers, data=data, files=files)
        return response.json()


class TeamsService:
    """Service for Microsoft Teams API interactions"""
    
    GRAPH_URL = 'https://graph.microsoft.com/v1.0'
    
    def __init__(self, workspace: MicrosoftTeamsWorkspace):
        self.workspace = workspace
        self.token = workspace.access_token
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request to Microsoft Graph API"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        
        url = f"{self.GRAPH_URL}/{endpoint}"
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=kwargs.get('params', {}))
        else:
            response = requests.post(url, headers=headers, json=kwargs.get('json', {}))
        
        if response.status_code == 200:
            return response.json()
        return {'error': response.status_code, 'message': response.text}
    
    def refresh_token(self) -> bool:
        """Refresh the access token"""
        token_url = f"https://login.microsoftonline.com/{self.workspace.tenant_id}/oauth2/v2.0/token"
        
        data = {
            'client_id': settings.MICROSOFT_CLIENT_ID,
            'client_secret': settings.MICROSOFT_CLIENT_SECRET,
            'refresh_token': self.workspace.refresh_token,
            'grant_type': 'refresh_token',
            'scope': 'https://graph.microsoft.com/.default',
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            tokens = response.json()
            self.workspace.access_token = tokens['access_token']
            self.workspace.refresh_token = tokens.get('refresh_token', self.workspace.refresh_token)
            self.workspace.token_expires_at = timezone.now() + timezone.timedelta(
                seconds=tokens.get('expires_in', 3600)
            )
            self.workspace.save()
            self.token = self.workspace.access_token
            return True
        return False
    
    def post_message(self, channel_id: str, content: str, content_type: str = 'html') -> Dict:
        """Post a message to a Teams channel"""
        endpoint = f"teams/{self.workspace.team_id}/channels/{channel_id}/messages"
        
        payload = {
            'body': {
                'contentType': content_type,
                'content': content
            }
        }
        
        return self._make_request('POST', endpoint, json=payload)
    
    def post_design_preview(self, channel_id: str, project: Any, image_url: str = None,
                           message: str = None) -> Dict:
        """Post a design preview with Adaptive Card"""
        # Create Adaptive Card for rich content
        adaptive_card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"🎨 {project.name}",
                    "weight": "Bolder",
                    "size": "Large"
                },
                {
                    "type": "TextBlock",
                    "text": message or f"{project.user.username} shared a design",
                    "wrap": True
                }
            ]
        }
        
        if image_url:
            adaptive_card["body"].append({
                "type": "Image",
                "url": image_url,
                "size": "Large"
            })
        
        adaptive_card["body"].extend([
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Type:", "value": project.get_project_type_display()},
                    {"title": "Updated:", "value": project.updated_at.strftime('%b %d, %Y')}
                ]
            }
        ])
        
        adaptive_card["actions"] = [
            {
                "type": "Action.OpenUrl",
                "title": "View Design",
                "url": f"{settings.FRONTEND_URL}/projects/{project.id}"
            }
        ]
        
        endpoint = f"teams/{self.workspace.team_id}/channels/{channel_id}/messages"
        
        payload = {
            'body': {
                'contentType': 'html',
                'content': f"<attachment id=\"card\"></attachment>"
            },
            'attachments': [
                {
                    'id': 'card',
                    'contentType': 'application/vnd.microsoft.card.adaptive',
                    'content': json.dumps(adaptive_card)
                }
            ]
        }
        
        return self._make_request('POST', endpoint, json=payload)
    
    def post_comment_notification(self, channel_id: str, comment: Any, project: Any) -> Dict:
        """Post a comment notification"""
        content = f"""
        <div>
            <strong>💬 New comment</strong> on 
            <a href="{settings.FRONTEND_URL}/projects/{project.id}">{project.name}</a>
            <blockquote>{comment.content}</blockquote>
            <p style="color: gray;">Posted by {comment.user.username}</p>
        </div>
        """
        
        return self.post_message(channel_id, content)
    
    def get_channels(self) -> List[Dict]:
        """Get list of channels in team"""
        endpoint = f"teams/{self.workspace.team_id}/channels"
        result = self._make_request('GET', endpoint)
        
        return result.get('value', [])
    
    def get_members(self) -> List[Dict]:
        """Get list of team members"""
        endpoint = f"teams/{self.workspace.team_id}/members"
        result = self._make_request('GET', endpoint)
        
        return result.get('value', [])


class BotCommandHandler:
    """Handle bot commands from Slack/Teams"""
    
    def __init__(self, platform: str, user=None):
        self.platform = platform
        self.user = user
    
    def handle_command(self, command: str, args: str) -> Dict:
        """Route command to appropriate handler"""
        command = command.lower().strip()
        
        handlers = {
            'search': self._handle_search,
            'recent': self._handle_recent,
            'help': self._handle_help,
            'share': self._handle_share,
            'export': self._handle_export,
            'status': self._handle_status,
        }
        
        handler = handlers.get(command, self._handle_unknown)
        return handler(args)
    
    def _handle_search(self, query: str) -> Dict:
        """Search for designs"""
        from projects.models import Project
        
        if not self.user:
            return {'text': 'Please link your account first to search designs.'}
        
        projects = Project.objects.filter(
            user=self.user,
            name__icontains=query
        )[:5]
        
        if not projects:
            return {'text': f'No designs found matching "{query}"'}
        
        results = []
        for p in projects:
            results.append(f"• *{p.name}* - {p.get_project_type_display()}")
        
        return {
            'text': f'Found {projects.count()} designs:',
            'blocks': [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '\n'.join(results)
                    }
                }
            ]
        }
    
    def _handle_recent(self, args: str) -> Dict:
        """Get recent designs"""
        from projects.models import Project
        
        if not self.user:
            return {'text': 'Please link your account first to view recent designs.'}
        
        limit = 5
        try:
            if args:
                limit = min(int(args), 10)
        except ValueError:
            pass
        
        projects = Project.objects.filter(user=self.user).order_by('-updated_at')[:limit]
        
        if not projects:
            return {'text': 'No recent designs found.'}
        
        results = []
        for p in projects:
            results.append(f"• *{p.name}* - Updated {p.updated_at.strftime('%b %d')}")
        
        return {
            'text': f'Your {len(projects)} most recent designs:',
            'blocks': [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '\n'.join(results)
                    }
                }
            ]
        }
    
    def _handle_help(self, args: str) -> Dict:
        """Show help message"""
        return {
            'text': '''*Available Commands:*
• `/design search <query>` - Search your designs
• `/design recent [count]` - Show recent designs
• `/design share <project_id>` - Share a design
• `/design export <project_id>` - Export a design
• `/design status` - Check connection status
• `/design help` - Show this help message'''
        }
    
    def _handle_share(self, project_id: str) -> Dict:
        """Share a design"""
        if not project_id:
            return {'text': 'Please provide a project ID: `/design share <project_id>`'}
        
        return {
            'text': f'Share feature triggered for project {project_id}',
            'response_type': 'ephemeral'
        }
    
    def _handle_export(self, project_id: str) -> Dict:
        """Export a design"""
        if not project_id:
            return {'text': 'Please provide a project ID: `/design export <project_id>`'}
        
        return {
            'text': f'Export initiated for project {project_id}. You will receive a notification when complete.',
            'response_type': 'ephemeral'
        }
    
    def _handle_status(self, args: str) -> Dict:
        """Show connection status"""
        status = 'connected' if self.user else 'not connected'
        return {
            'text': f'*Status:* {status}\n*Platform:* {self.platform}'
        }
    
    def _handle_unknown(self, args: str) -> Dict:
        """Handle unknown command"""
        return {
            'text': 'Unknown command. Type `/design help` for available commands.'
        }


class IntegrationNotificationService:
    """Service for sending notifications to Slack/Teams"""
    
    @staticmethod
    def notify_comment(project, comment):
        """Send comment notification to linked channels"""
        # Slack channels
        for channel in project.slack_channels.filter(notify_on_comment=True, is_active=True):
            service = SlackService(channel.workspace)
            result = service.post_comment_notification(channel.channel_id, comment, project)
            
            IntegrationMessage.objects.create(
                platform='slack',
                message_type='comment',
                user=comment.user,
                project=project,
                workspace_id=channel.workspace.workspace_id,
                channel_id=channel.channel_id,
                message_content={'comment_id': comment.id},
                sent=result.get('ok', False),
                sent_at=timezone.now() if result.get('ok') else None,
                external_message_id=result.get('ts', ''),
                error_message='' if result.get('ok') else str(result.get('error', ''))
            )
        
        # Teams channels
        for channel in project.teams_channels.filter(notify_on_comment=True, is_active=True):
            service = TeamsService(channel.workspace)
            result = service.post_comment_notification(channel.channel_id, comment, project)
            
            IntegrationMessage.objects.create(
                platform='teams',
                message_type='comment',
                user=comment.user,
                project=project,
                workspace_id=channel.workspace.team_id,
                channel_id=channel.channel_id,
                message_content={'comment_id': comment.id},
                sent='error' not in result,
                sent_at=timezone.now() if 'error' not in result else None,
                external_message_id=result.get('id', ''),
                error_message=result.get('message', '') if 'error' in result else ''
            )
    
    @staticmethod
    def notify_design_update(project, user):
        """Send design update notification"""
        # Slack channels
        for channel in project.slack_channels.filter(notify_on_update=True, is_active=True):
            service = SlackService(channel.workspace)
            message = f"*{user.username}* updated the design *{project.name}*"
            result = service.post_message(channel.channel_id, text=message)
            
            IntegrationMessage.objects.create(
                platform='slack',
                message_type='update',
                user=user,
                project=project,
                workspace_id=channel.workspace.workspace_id,
                channel_id=channel.channel_id,
                sent=result.get('ok', False),
                sent_at=timezone.now() if result.get('ok') else None,
            )
        
        # Teams channels
        for channel in project.teams_channels.filter(notify_on_update=True, is_active=True):
            service = TeamsService(channel.workspace)
            content = f"<strong>{user.username}</strong> updated the design <strong>{project.name}</strong>"
            result = service.post_message(channel.channel_id, content)
            
            IntegrationMessage.objects.create(
                platform='teams',
                message_type='update',
                user=user,
                project=project,
                workspace_id=channel.workspace.team_id,
                channel_id=channel.channel_id,
                sent='error' not in result,
                sent_at=timezone.now() if 'error' not in result else None,
            )
    
    @staticmethod
    def share_design(project, channel, message: str = None, image_url: str = None):
        """Share design to a channel"""
        if hasattr(channel, 'workspace') and hasattr(channel.workspace, 'workspace_id'):
            # Slack
            service = SlackService(channel.workspace)
            result = service.post_design_preview(channel.channel_id, project, image_url, message)
            
            return IntegrationMessage.objects.create(
                platform='slack',
                message_type='design_share',
                user=project.user,
                project=project,
                workspace_id=channel.workspace.workspace_id,
                channel_id=channel.channel_id,
                message_content={'message': message, 'image_url': image_url},
                sent=result.get('ok', False),
                sent_at=timezone.now() if result.get('ok') else None,
                external_message_id=result.get('ts', ''),
            )
        else:
            # Teams
            service = TeamsService(channel.workspace)
            result = service.post_design_preview(channel.channel_id, project, image_url, message)
            
            return IntegrationMessage.objects.create(
                platform='teams',
                message_type='design_share',
                user=project.user,
                project=project,
                workspace_id=channel.workspace.team_id,
                channel_id=channel.channel_id,
                message_content={'message': message, 'image_url': image_url},
                sent='error' not in result,
                sent_at=timezone.now() if 'error' not in result else None,
                external_message_id=result.get('id', ''),
            )


def verify_slack_signature(request) -> bool:
    """Verify Slack request signature"""
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    signature = request.headers.get('X-Slack-Signature', '')
    
    if not timestamp or not signature:
        return False
    
    # Check if request is older than 5 minutes
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False
    
    sig_basestring = f"v0:{timestamp}:{request.body.decode('utf-8')}"
    my_signature = 'v0=' + hmac.new(
        settings.SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature, signature)
