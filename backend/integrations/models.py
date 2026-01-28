"""
Third-party Integration Models
Handles external service connections and imported assets
"""
from django.db import models
from django.contrib.auth.models import User


class ExternalServiceConnection(models.Model):
    """User connections to external services like Figma, Adobe, etc."""
    SERVICE_CHOICES = (
        ('figma', 'Figma'),
        ('adobe_xd', 'Adobe XD'),
        ('sketch', 'Sketch'),
        ('google_drive', 'Google Drive'),
        ('dropbox', 'Dropbox'),
        ('unsplash', 'Unsplash'),
        ('pexels', 'Pexels'),
        ('shutterstock', 'Shutterstock'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='external_connections')
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    
    # OAuth tokens
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Service-specific data
    service_user_id = models.CharField(max_length=255, blank=True)
    service_username = models.CharField(max_length=255, blank=True)
    service_metadata = models.JSONField(default=dict)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'service']
        ordering = ['service']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_service_display()}"


class ImportedAsset(models.Model):
    """Track assets imported from external services"""
    SOURCE_CHOICES = (
        ('figma', 'Figma'),
        ('adobe_xd', 'Adobe XD'),
        ('sketch', 'Sketch'),
        ('unsplash', 'Unsplash'),
        ('pexels', 'Pexels'),
        ('shutterstock', 'Shutterstock'),
        ('upload', 'Direct Upload'),
    )
    
    ASSET_TYPES = (
        ('image', 'Image'),
        ('vector', 'Vector'),
        ('icon', 'Icon'),
        ('component', 'Component'),
        ('design_file', 'Design File'),
        ('font', 'Font'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='imported_assets')
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPES)
    
    # External reference
    external_id = models.CharField(max_length=255, blank=True)
    external_url = models.URLField(blank=True)
    
    # Local storage
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='imported_assets/%Y/%m/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='imported_assets/thumbnails/%Y/%m/', null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    # {
    #   "width": 1920,
    #   "height": 1080,
    #   "format": "png",
    #   "size_bytes": 123456,
    #   "photographer": "John Doe",
    #   "license": "Unsplash License"
    # }
    
    # Attribution
    attribution_required = models.BooleanField(default=False)
    attribution_text = models.TextField(blank=True)
    
    # Tags and search
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_source_display()})"


class FigmaImport(models.Model):
    """Track Figma file imports"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='figma_imports')
    
    # Figma file info
    figma_file_key = models.CharField(max_length=255)
    figma_file_name = models.CharField(max_length=255)
    figma_node_ids = models.JSONField(default=list, help_text="Specific nodes to import, empty for all")
    
    # Import settings
    import_images = models.BooleanField(default=True)
    import_vectors = models.BooleanField(default=True)
    import_styles = models.BooleanField(default=True)
    import_components = models.BooleanField(default=True)
    
    # Result
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Stats
    total_nodes = models.IntegerField(default=0)
    imported_nodes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Figma import: {self.figma_file_name}"


class StockAssetSearch(models.Model):
    """Track stock asset searches for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integration_stock_searches')
    
    provider = models.CharField(max_length=50)  # unsplash, pexels, shutterstock
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict)
    
    results_count = models.IntegerField(default=0)
    selected_asset_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
