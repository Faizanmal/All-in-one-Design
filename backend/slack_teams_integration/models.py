from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from teams.models import Team


class SlackWorkspace(models.Model):
    """Slack workspace integration"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='slack_workspaces', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='slack_workspaces')
    
    # Slack OAuth data
    workspace_id = models.CharField(max_length=50, unique=True)
    workspace_name = models.CharField(max_length=255)
    access_token = models.TextField()  # Encrypted in production
    bot_token = models.TextField(blank=True)
    bot_user_id = models.CharField(max_length=50, blank=True)
    
    # Webhook URL for incoming messages
    webhook_url = models.URLField(blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    auto_post_designs = models.BooleanField(default=False)
    notification_channel = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-connected_at']
    
    def __str__(self):
        return f"Slack: {self.workspace_name}"


class SlackChannel(models.Model):
    """Slack channels linked to projects"""
    workspace = models.ForeignKey(SlackWorkspace, on_delete=models.CASCADE, related_name='channels')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='slack_channels', null=True, blank=True)
    
    channel_id = models.CharField(max_length=50)
    channel_name = models.CharField(max_length=255)
    channel_type = models.CharField(max_length=20, default='channel')  # channel, private, dm
    
    # Notification settings
    notify_on_comment = models.BooleanField(default=True)
    notify_on_update = models.BooleanField(default=True)
    notify_on_export = models.BooleanField(default=False)
    notify_on_share = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['workspace', 'channel_id']
        ordering = ['channel_name']
    
    def __str__(self):
        return f"#{self.channel_name}"


class MicrosoftTeamsWorkspace(models.Model):
    """Microsoft Teams integration"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='teams_workspaces', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams_workspaces')
    
    # Teams OAuth data
    tenant_id = models.CharField(max_length=100)
    ms_team_id = models.CharField(max_length=100, unique=True)  # Renamed from team_id to avoid clash
    team_name = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField()
    
    # Webhook URL
    webhook_url = models.URLField(blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    auto_post_designs = models.BooleanField(default=False)
    notification_channel_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    token_expires_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-connected_at']
        verbose_name_plural = 'Microsoft Teams Workspaces'
    
    def __str__(self):
        return f"Teams: {self.team_name}"


class TeamsChannel(models.Model):
    """Teams channels linked to projects"""
    workspace = models.ForeignKey(MicrosoftTeamsWorkspace, on_delete=models.CASCADE, related_name='channels')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='teams_channels', null=True, blank=True)
    
    channel_id = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=255)
    channel_type = models.CharField(max_length=20, default='standard')  # standard, private
    
    # Notification settings
    notify_on_comment = models.BooleanField(default=True)
    notify_on_update = models.BooleanField(default=True)
    notify_on_export = models.BooleanField(default=False)
    notify_on_share = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['workspace', 'channel_id']
        ordering = ['channel_name']
    
    def __str__(self):
        return f"#{self.channel_name}"


class IntegrationMessage(models.Model):
    """Record of messages sent via integrations"""
    MESSAGE_TYPES = (
        ('design_share', 'Design Shared'),
        ('comment', 'Comment'),
        ('mention', 'Mention'),
        ('update', 'Design Updated'),
        ('export', 'Export Completed'),
        ('bot_command', 'Bot Command'),
        ('notification', 'Notification'),
    )
    
    PLATFORM_CHOICES = (
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
    )
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    message_type = models.CharField(max_length=30, choices=MESSAGE_TYPES)
    
    # Source
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='integration_messages')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Target
    workspace_id = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100)
    
    # Message content
    message_content = models.JSONField(default=dict)
    
    # Status
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # External IDs
    external_message_id = models.CharField(max_length=100, blank=True)
    thread_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.platform}: {self.message_type}"


class BotCommand(models.Model):
    """Record of bot commands received"""
    PLATFORMS = (
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
    )
    
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    
    # Command details
    command = models.CharField(max_length=100)  # e.g., /design search, /design recent
    arguments = models.TextField(blank=True)
    
    # Source
    workspace_id = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100)
    user_external_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Response
    response_sent = models.BooleanField(default=False)
    response_content = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.platform}: {self.command}"


class NotificationPreference(models.Model):
    """User notification preferences for integrations"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='integration_notification_prefs')
    
    # Slack preferences
    slack_enabled = models.BooleanField(default=True)
    slack_dm_enabled = models.BooleanField(default=True)
    slack_mention_enabled = models.BooleanField(default=True)
    
    # Teams preferences
    teams_enabled = models.BooleanField(default=True)
    teams_dm_enabled = models.BooleanField(default=True)
    teams_mention_enabled = models.BooleanField(default=True)
    
    # Notification types
    notify_on_comments = models.BooleanField(default=True)
    notify_on_mentions = models.BooleanField(default=True)
    notify_on_project_updates = models.BooleanField(default=True)
    notify_on_team_activity = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    quiet_hours_timezone = models.CharField(max_length=50, default='UTC')
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification prefs for {self.user.username}"
