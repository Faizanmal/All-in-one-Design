from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class OfflineProject(models.Model):
    """Track projects available offline"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offline_projects')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='offline_instances')
    
    # Sync metadata
    last_synced = models.DateTimeField(auto_now=True)
    sync_version = models.IntegerField(default=1)
    
    # Offline data
    cached_data = models.JSONField(default=dict)  # Cached project data
    cached_assets = models.JSONField(default=list)  # List of cached asset URLs
    
    # Size tracking
    cache_size = models.BigIntegerField(default=0)  # In bytes
    
    # Status
    is_enabled = models.BooleanField(default=True)
    needs_sync = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'project']
        ordering = ['-last_synced']
    
    def __str__(self):
        return f"Offline: {self.project.name}"


class SyncQueue(models.Model):
    """Queue of changes to sync when back online"""
    OPERATION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )
    
    ENTITY_TYPES = (
        ('project', 'Project'),
        ('component', 'Component'),
        ('asset', 'Asset'),
        ('comment', 'Comment'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('syncing', 'Syncing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('conflict', 'Conflict'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sync_queue')
    
    # Operation details
    operation = models.CharField(max_length=20, choices=OPERATION_TYPES)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_id = models.CharField(max_length=100)  # Can be temp ID for creates
    
    # Change data
    data = models.JSONField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Conflict resolution
    conflict_data = models.JSONField(null=True, blank=True)
    resolved_by = models.CharField(max_length=20, blank=True)  # 'local', 'remote', 'merged'
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    # Order for sequential operations
    sequence = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['sequence', 'created_at']
    
    def __str__(self):
        return f"{self.operation} {self.entity_type} ({self.status})"


class OfflineSettings(models.Model):
    """User offline mode settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='offline_settings')
    
    # Storage settings
    max_offline_storage = models.BigIntegerField(default=500 * 1024 * 1024)  # 500MB default
    auto_cache_recent = models.BooleanField(default=True)
    recent_project_count = models.IntegerField(default=5)
    
    # Sync settings
    auto_sync_on_connect = models.BooleanField(default=True)
    sync_interval_minutes = models.IntegerField(default=5)
    background_sync_enabled = models.BooleanField(default=True)
    
    # Cache settings
    cache_images = models.BooleanField(default=True)
    cache_fonts = models.BooleanField(default=True)
    cache_videos = models.BooleanField(default=False)  # Videos are large
    
    # Conflict resolution
    default_conflict_resolution = models.CharField(
        max_length=20,
        default='ask',
        choices=[
            ('ask', 'Ask User'),
            ('local', 'Keep Local'),
            ('remote', 'Keep Remote'),
            ('newest', 'Keep Newest'),
        ]
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Offline settings for {self.user.username}"


class SyncLog(models.Model):
    """Log of sync operations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sync_logs')
    
    # Sync details
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    items_synced = models.IntegerField(default=0)
    items_failed = models.IntegerField(default=0)
    conflicts_resolved = models.IntegerField(default=0)
    
    # Data transferred
    bytes_uploaded = models.BigIntegerField(default=0)
    bytes_downloaded = models.BigIntegerField(default=0)
    
    # Status
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        status = 'Success' if self.success else 'Failed'
        return f"Sync {self.started_at.strftime('%Y-%m-%d %H:%M')} - {status}"


class CachedAsset(models.Model):
    """Track cached assets for offline use"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cached_assets')
    
    # Asset reference
    original_url = models.URLField()
    asset_type = models.CharField(max_length=20)  # image, font, video, etc.
    
    # Cache info
    cache_key = models.CharField(max_length=255, unique=True)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    
    # Usage tracking
    last_accessed = models.DateTimeField(auto_now=True)
    access_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"Cached: {self.asset_type}"
