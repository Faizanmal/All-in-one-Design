from rest_framework import serializers
from .models import (
    SlackWorkspace, SlackChannel, MicrosoftTeamsWorkspace, TeamsChannel,
    IntegrationMessage, BotCommand, NotificationPreference
)


class SlackWorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for Slack workspaces"""
    channel_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SlackWorkspace
        fields = [
            'id', 'workspace_id', 'workspace_name', 'is_active',
            'auto_post_designs', 'notification_channel', 'channel_count',
            'connected_at', 'updated_at'
        ]
        read_only_fields = ['workspace_id', 'workspace_name', 'connected_at', 'updated_at']
    
    def get_channel_count(self, obj) -> int:
        return obj.channels.count()


class SlackChannelSerializer(serializers.ModelSerializer):
    """Serializer for Slack channels"""
    workspace_name = serializers.CharField(source='workspace.workspace_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = SlackChannel
        fields = [
            'id', 'workspace', 'workspace_name', 'project', 'project_name',
            'channel_id', 'channel_name', 'channel_type',
            'notify_on_comment', 'notify_on_update', 'notify_on_export',
            'notify_on_share', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['channel_id', 'channel_name', 'created_at', 'updated_at']


class MicrosoftTeamsWorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for Microsoft Teams workspaces"""
    channel_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MicrosoftTeamsWorkspace
        fields = [
            'id', 'team_id', 'team_name', 'is_active',
            'auto_post_designs', 'notification_channel_id', 'channel_count',
            'connected_at', 'updated_at'
        ]
        read_only_fields = ['team_id', 'team_name', 'connected_at', 'updated_at']
    
    def get_channel_count(self, obj) -> int:
        return obj.channels.count()


class TeamsChannelSerializer(serializers.ModelSerializer):
    """Serializer for Teams channels"""
    workspace_name = serializers.CharField(source='workspace.team_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = TeamsChannel
        fields = [
            'id', 'workspace', 'workspace_name', 'project', 'project_name',
            'channel_id', 'channel_name', 'channel_type',
            'notify_on_comment', 'notify_on_update', 'notify_on_export',
            'notify_on_share', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['channel_id', 'channel_name', 'created_at', 'updated_at']


class IntegrationMessageSerializer(serializers.ModelSerializer):
    """Serializer for integration messages"""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = IntegrationMessage
        fields = [
            'id', 'platform', 'platform_display', 'message_type', 'message_type_display',
            'project', 'project_name', 'workspace_id', 'channel_id',
            'message_content', 'sent', 'sent_at', 'error_message',
            'external_message_id', 'thread_id', 'created_at'
        ]
        read_only_fields = ['created_at']


class BotCommandSerializer(serializers.ModelSerializer):
    """Serializer for bot commands"""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    
    class Meta:
        model = BotCommand
        fields = [
            'id', 'platform', 'platform_display', 'command', 'arguments',
            'workspace_id', 'channel_id', 'user_external_id', 'user',
            'response_sent', 'response_content', 'created_at', 'processed_at'
        ]
        read_only_fields = ['created_at', 'processed_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'slack_enabled', 'slack_dm_enabled', 'slack_mention_enabled',
            'teams_enabled', 'teams_dm_enabled', 'teams_mention_enabled',
            'notify_on_comments', 'notify_on_mentions', 'notify_on_project_updates',
            'notify_on_team_activity', 'quiet_hours_enabled', 'quiet_hours_start',
            'quiet_hours_end', 'quiet_hours_timezone', 'updated_at'
        ]
        read_only_fields = ['updated_at']


class ShareDesignSerializer(serializers.Serializer):
    """Serializer for sharing designs"""
    project_id = serializers.IntegerField()
    channel_type = serializers.ChoiceField(choices=['slack', 'teams'])
    channel_id = serializers.IntegerField()
    message = serializers.CharField(required=False, allow_blank=True)
    include_preview = serializers.BooleanField(default=True)


class SlackOAuthSerializer(serializers.Serializer):
    """Serializer for Slack OAuth callback"""
    code = serializers.CharField()
    state = serializers.CharField(required=False)


class TeamsOAuthSerializer(serializers.Serializer):
    """Serializer for Teams OAuth callback"""
    code = serializers.CharField()
    state = serializers.CharField(required=False)
    tenant = serializers.CharField(required=False)


class SlackCommandSerializer(serializers.Serializer):
    """Serializer for incoming Slack commands"""
    token = serializers.CharField()
    team_id = serializers.CharField()
    channel_id = serializers.CharField()
    user_id = serializers.CharField()
    command = serializers.CharField()
    text = serializers.CharField(required=False, allow_blank=True)
    response_url = serializers.URLField()


class ChannelListSerializer(serializers.Serializer):
    """Serializer for channel list response"""
    id = serializers.CharField()
    name = serializers.CharField()
    type = serializers.CharField(default='channel')
    is_private = serializers.BooleanField(default=False)


class LinkChannelSerializer(serializers.Serializer):
    """Serializer for linking a channel to a project"""
    project_id = serializers.IntegerField()
    channel_id = serializers.CharField()
    channel_name = serializers.CharField()
    notify_on_comment = serializers.BooleanField(default=True)
    notify_on_update = serializers.BooleanField(default=True)
    notify_on_export = serializers.BooleanField(default=False)
    notify_on_share = serializers.BooleanField(default=True)
