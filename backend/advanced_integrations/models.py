from django.db import models
from django.conf import settings
import uuid


class IntegrationProvider(models.Model):
    """Available integration providers"""
    PROVIDER_TYPES = [
        ('design', 'Design Tools'),
        ('collaboration', 'Collaboration'),
        ('project_management', 'Project Management'),
        ('cloud_storage', 'Cloud Storage'),
        ('marketing', 'Marketing'),
        ('cms', 'CMS'),
        ('social', 'Social Media'),
        ('analytics', 'Analytics'),
        ('ai', 'AI Services'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    provider_type = models.CharField(max_length=50, choices=PROVIDER_TYPES)
    
    # Display
    icon = models.ImageField(upload_to='integration_icons/', null=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    # OAuth settings
    oauth_url = models.URLField(blank=True)
    token_url = models.URLField(blank=True)
    api_base_url = models.URLField(blank=True)
    
    # Scopes
    default_scopes = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserIntegration(models.Model):
    """User's connected integrations"""
    STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='integrations')
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE)
    
    # OAuth tokens
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='connected')
    error_message = models.TextField(blank=True)
    
    # Provider-specific data
    external_user_id = models.CharField(max_length=255, blank=True)
    external_username = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict)
    
    # Settings
    settings = models.JSONField(default=dict)
    
    connected_at = models.DateTimeField(auto_now_add=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'provider']
        ordering = ['-connected_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.name}"


class SlackIntegration(models.Model):
    """Slack workspace integration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_integration = models.OneToOneField(UserIntegration, on_delete=models.CASCADE)
    
    # Workspace info
    workspace_id = models.CharField(max_length=255)
    workspace_name = models.CharField(max_length=255)
    
    # Bot
    bot_user_id = models.CharField(max_length=255, blank=True)
    bot_access_token = models.TextField(blank=True)
    
    # Notification settings
    notification_channel = models.CharField(max_length=255, blank=True)
    notify_on_comment = models.BooleanField(default=True)
    notify_on_approval = models.BooleanField(default=True)
    notify_on_export = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.workspace_name


class JiraIntegration(models.Model):
    """Jira project integration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_integration = models.OneToOneField(UserIntegration, on_delete=models.CASCADE)
    
    # Site info
    cloud_id = models.CharField(max_length=255)
    site_url = models.URLField()
    
    # Project mapping
    default_project_key = models.CharField(max_length=50, blank=True)
    project_mappings = models.JSONField(default=dict)
    # Example: {"project_uuid": "JIRA-PROJECT-KEY"}
    
    # Issue settings
    default_issue_type = models.CharField(max_length=50, default='Task')
    auto_create_issues = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Jira: {self.site_url}"


class AdobeIntegration(models.Model):
    """Adobe Creative Cloud integration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_integration = models.OneToOneField(UserIntegration, on_delete=models.CASCADE)
    
    # Adobe user info
    adobe_user_id = models.CharField(max_length=255)
    
    # Connected apps
    photoshop_connected = models.BooleanField(default=False)
    illustrator_connected = models.BooleanField(default=False)
    xd_connected = models.BooleanField(default=False)
    indesign_connected = models.BooleanField(default=False)
    
    # CC Libraries
    library_ids = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Adobe CC: {self.adobe_user_id}"


class GoogleDriveIntegration(models.Model):
    """Google Drive integration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_integration = models.OneToOneField(UserIntegration, on_delete=models.CASCADE)
    
    # Drive settings
    default_folder_id = models.CharField(max_length=255, blank=True)
    auto_backup = models.BooleanField(default=False)
    backup_folder_id = models.CharField(max_length=255, blank=True)
    
    # Sync settings
    sync_direction = models.CharField(max_length=20, default='both')  # upload, download, both
    
    created_at = models.DateTimeField(auto_now_add=True)


class DropboxIntegration(models.Model):
    """Dropbox integration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_integration = models.OneToOneField(UserIntegration, on_delete=models.CASCADE)
    
    # Account info
    account_id = models.CharField(max_length=255)
    
    # Sync settings
    default_path = models.CharField(max_length=500, default='/DesignPlatform')
    auto_backup = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)


class NotionIntegration(models.Model):
    """Notion integration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_integration = models.OneToOneField(UserIntegration, on_delete=models.CASCADE)
    
    # Workspace info
    workspace_id = models.CharField(max_length=255)
    workspace_name = models.CharField(max_length=255)
    workspace_icon = models.URLField(blank=True)
    
    # Database mappings
    database_mappings = models.JSONField(default=dict)
    # Example: {"projects": "notion_db_id", "assets": "notion_db_id"}
    
    # Export settings
    auto_export_to_notion = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notion: {self.workspace_name}"


class WordPressIntegration(models.Model):
    """WordPress site integration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_integration = models.OneToOneField(UserIntegration, on_delete=models.CASCADE)
    
    # Site info
    site_url = models.URLField()
    site_name = models.CharField(max_length=255, blank=True)
    
    # REST API settings
    api_base = models.URLField()
    
    # Publish settings
    default_status = models.CharField(max_length=20, default='draft')  # draft, publish
    default_category = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"WordPress: {self.site_url}"


class WebhookEndpoint(models.Model):
    """Custom webhook endpoints"""
    EVENT_TYPES = [
        ('project.created', 'Project Created'),
        ('project.updated', 'Project Updated'),
        ('project.deleted', 'Project Deleted'),
        ('design.exported', 'Design Exported'),
        ('comment.added', 'Comment Added'),
        ('asset.uploaded', 'Asset Uploaded'),
        ('team.member_added', 'Team Member Added'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='webhooks')
    
    name = models.CharField(max_length=255)
    url = models.URLField()
    
    # Events to trigger
    events = models.JSONField(default=list)
    
    # Security
    secret = models.CharField(max_length=255, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    failure_count = models.IntegerField(default=0)
    
    # Headers
    custom_headers = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class WebhookLog(models.Model):
    """Webhook delivery logs"""
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='logs')
    
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    
    # Response
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    
    # Timing
    triggered_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-triggered_at']


class ZapierIntegration(models.Model):
    """Zapier integration hooks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='zapier_hooks')
    
    # Hook info
    hook_url = models.URLField()
    trigger_type = models.CharField(max_length=50)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Zapier: {self.trigger_type}"


class IntegrationSync(models.Model):
    """Track sync operations with integrations"""
    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    SYNC_TYPES = [
        ('import', 'Import'),
        ('export', 'Export'),
        ('two_way', 'Two-Way Sync'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_integration = models.ForeignKey(UserIntegration, on_delete=models.CASCADE, related_name='syncs')
    
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    
    # Details
    items_synced = models.IntegerField(default=0)
    items_failed = models.IntegerField(default=0)
    error_details = models.JSONField(default=list)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Integration Sync'
        verbose_name_plural = 'Integration Syncs'
    
    def __str__(self):
        return f"{self.user_integration.provider.name} - {self.sync_type}"
