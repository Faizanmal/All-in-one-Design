from django.db import models
from django.contrib.auth.models import User
from teams.models import Team
from projects.models import Project


class AssetFolder(models.Model):
    """Smart folders for organizing assets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asset_folders')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_folders')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Hierarchy
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    path = models.CharField(max_length=1000, blank=True)  # Full path: /root/subfolder/current
    
    # Visual
    color = models.CharField(max_length=20, default='#3B82F6')
    icon = models.CharField(max_length=50, default='folder')
    
    # Smart folder settings
    is_smart = models.BooleanField(default=False)
    smart_rules = models.JSONField(default=dict)  # Auto-include rules
    
    # Metadata
    asset_count = models.IntegerField(default=0)
    total_size = models.BigIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.path or self.name
    
    def save(self, *args, **kwargs):
        # Update path
        if self.parent:
            self.path = f"{self.parent.path}/{self.name}"
        else:
            self.path = f"/{self.name}"
        super().save(*args, **kwargs)


class AssetTag(models.Model):
    """Tags for organizing assets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asset_tags')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_tags')
    
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='#6B7280')
    
    # AI-generated
    ai_generated = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class EnhancedAsset(models.Model):
    """Enhanced asset with advanced management features"""
    ASSET_TYPES = (
        ('image', 'Image'),
        ('icon', 'Icon'),
        ('illustration', 'Illustration'),
        ('photo', 'Photo'),
        ('logo', 'Logo'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('font', 'Font'),
        ('svg', 'SVG'),
        ('lottie', 'Lottie Animation'),
        ('3d', '3D Model'),
        ('document', 'Document'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enhanced_assets')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='enhanced_assets')
    
    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    
    # File storage
    file_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # in bytes
    mime_type = models.CharField(max_length=100)
    
    # Dimensions (for images/videos)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # for video/audio
    
    # Organization
    folder = models.ForeignKey(AssetFolder, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    tags = models.ManyToManyField(AssetTag, blank=True, related_name='assets')
    
    # AI Analysis
    ai_tags = models.JSONField(default=list)  # AI-generated tags
    ai_description = models.TextField(blank=True)  # AI-generated description
    ai_colors = models.JSONField(default=list)  # Extracted dominant colors
    ai_objects = models.JSONField(default=list)  # Detected objects
    ai_text = models.TextField(blank=True)  # Extracted text (OCR)
    embedding = models.JSONField(null=True, blank=True)  # Vector embedding for search
    
    # CDN Integration
    cdn_url = models.URLField(blank=True)  # Cloudinary/Imgix URL
    cdn_public_id = models.CharField(max_length=255, blank=True)
    cdn_transformations = models.JSONField(default=dict)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    used_in_projects = models.ManyToManyField(Project, blank=True, related_name='used_assets')
    
    # Versioning
    version = models.IntegerField(default=1)
    previous_versions = models.JSONField(default=list)
    
    # Status
    is_favorite = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['asset_type']),
            models.Index(fields=['user', 'is_archived']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.asset_type})"


class AssetCollection(models.Model):
    """Collections of assets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enhanced_asset_collections')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='enhanced_asset_collections')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    assets = models.ManyToManyField(EnhancedAsset, related_name='collections')
    
    # Visual
    cover_image = models.URLField(blank=True)
    color = models.CharField(max_length=20, default='#3B82F6')
    
    # Sharing
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_collections')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class AssetUsageLog(models.Model):
    """Track asset usage across projects"""
    asset = models.ForeignKey(EnhancedAsset, on_delete=models.CASCADE, related_name='usage_logs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='asset_usage_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Usage context
    component_id = models.CharField(max_length=100, blank=True)
    usage_type = models.CharField(max_length=50)  # background, fill, pattern, etc.
    
    added_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.asset.name} in {self.project.name}"


class CDNIntegration(models.Model):
    """CDN provider integrations"""
    PROVIDER_CHOICES = (
        ('cloudinary', 'Cloudinary'),
        ('imgix', 'Imgix'),
        ('cloudflare', 'Cloudflare Images'),
        ('aws_cloudfront', 'AWS CloudFront'),
        ('bunny', 'Bunny CDN'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cdn_integrations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    
    provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES)
    name = models.CharField(max_length=255)
    
    # Credentials
    api_key = models.TextField()
    api_secret = models.TextField(blank=True)
    cloud_name = models.CharField(max_length=100, blank=True)  # For Cloudinary
    
    # Settings
    default_transformations = models.JSONField(default=dict)
    auto_optimize = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.provider})"


class BulkOperation(models.Model):
    """Track bulk operations on assets"""
    OPERATION_TYPES = (
        ('delete', 'Delete'),
        ('move', 'Move'),
        ('tag', 'Add Tags'),
        ('untag', 'Remove Tags'),
        ('archive', 'Archive'),
        ('unarchive', 'Unarchive'),
        ('resize', 'Resize'),
        ('convert', 'Convert Format'),
        ('optimize', 'Optimize'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bulk_operations')
    
    operation = models.CharField(max_length=20, choices=OPERATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Target assets
    asset_ids = models.JSONField(default=list)
    total_assets = models.IntegerField(default=0)
    processed_assets = models.IntegerField(default=0)
    
    # Operation parameters
    parameters = models.JSONField(default=dict)
    
    # Results
    results = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.operation} ({self.status})"


class UnusedAssetReport(models.Model):
    """Report of unused assets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unused_reports')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    
    # Report data
    unused_assets = models.JSONField(default=list)  # List of asset IDs
    total_unused = models.IntegerField(default=0)
    total_size = models.BigIntegerField(default=0)
    
    # Thresholds
    unused_days_threshold = models.IntegerField(default=90)
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Unused Report ({self.generated_at.date()})"
