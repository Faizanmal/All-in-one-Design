from django.db import models
from django.conf import settings
import uuid


class Model3D(models.Model):
    """3D Model storage and metadata"""
    FORMAT_CHOICES = [
        ('gltf', 'GLTF'),
        ('glb', 'GLB'),
        ('obj', 'OBJ'),
        ('fbx', 'FBX'),
        ('stl', 'STL'),
        ('usdz', 'USDZ'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='models_3d')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='models_3d', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # File storage
    file = models.FileField(upload_to='3d_models/')
    file_format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file_size = models.BigIntegerField(default=0)
    
    # Thumbnail preview
    thumbnail = models.ImageField(upload_to='3d_thumbnails/', null=True, blank=True)
    
    # 3D Model metadata
    vertex_count = models.IntegerField(default=0)
    face_count = models.IntegerField(default=0)
    material_count = models.IntegerField(default=0)
    texture_count = models.IntegerField(default=0)
    animation_count = models.IntegerField(default=0)
    
    # Bounding box
    bbox_min_x = models.FloatField(default=0)
    bbox_min_y = models.FloatField(default=0)
    bbox_min_z = models.FloatField(default=0)
    bbox_max_x = models.FloatField(default=0)
    bbox_max_y = models.FloatField(default=0)
    bbox_max_z = models.FloatField(default=0)
    
    # AR/VR settings
    ar_enabled = models.BooleanField(default=True)
    ar_scale = models.FloatField(default=1.0)
    ar_anchor_type = models.CharField(max_length=50, default='plane')
    
    # Tags and categorization
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '3D Model'
        verbose_name_plural = '3D Models'
    
    def __str__(self):
        return f"{self.name} ({self.file_format})"


class Scene3D(models.Model):
    """3D Scene composition with multiple models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scenes_3d')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='scenes_3d', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Scene configuration
    scene_data = models.JSONField(default=dict)  # Three.js scene serialization
    camera_settings = models.JSONField(default=dict)
    lighting_settings = models.JSONField(default=dict)
    environment_settings = models.JSONField(default=dict)
    
    # Thumbnail
    thumbnail = models.ImageField(upload_to='scene_thumbnails/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '3D Scene'
        verbose_name_plural = '3D Scenes'
    
    def __str__(self):
        return self.name


class SceneModel(models.Model):
    """Model instance within a scene with transforms"""
    scene = models.ForeignKey(Scene3D, on_delete=models.CASCADE, related_name='scene_models')
    model = models.ForeignKey(Model3D, on_delete=models.CASCADE, related_name='scene_instances')
    
    # Transform
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    position_z = models.FloatField(default=0)
    rotation_x = models.FloatField(default=0)
    rotation_y = models.FloatField(default=0)
    rotation_z = models.FloatField(default=0)
    scale_x = models.FloatField(default=1)
    scale_y = models.FloatField(default=1)
    scale_z = models.FloatField(default=1)
    
    # Visibility and rendering
    visible = models.BooleanField(default=True)
    cast_shadow = models.BooleanField(default=True)
    receive_shadow = models.BooleanField(default=True)
    
    # Material overrides
    material_overrides = models.JSONField(default=dict)
    
    # Layer ordering
    layer = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['layer', 'created_at']


class Prototype3D(models.Model):
    """Interactive 3D prototype with animations and interactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prototypes_3d')
    scene = models.ForeignKey(Scene3D, on_delete=models.CASCADE, related_name='prototypes')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Prototype configuration
    interactions = models.JSONField(default=list)  # List of interaction definitions
    animations = models.JSONField(default=list)  # Animation sequences
    states = models.JSONField(default=dict)  # State machine configuration
    triggers = models.JSONField(default=list)  # Event triggers
    
    # Preview settings
    preview_mode = models.CharField(max_length=50, default='desktop')  # desktop, mobile, vr, ar
    auto_play = models.BooleanField(default=False)
    loop = models.BooleanField(default=False)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    share_link = models.CharField(max_length=100, unique=True, null=True, blank=True)
    password = models.CharField(max_length=100, blank=True)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '3D Prototype'
        verbose_name_plural = '3D Prototypes'
    
    def __str__(self):
        return self.name


class ARPreview(models.Model):
    """AR preview configuration for mobile designs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ar_previews')
    
    # Source can be 3D model, scene, or 2D design
    model_3d = models.ForeignKey(Model3D, on_delete=models.CASCADE, null=True, blank=True, related_name='ar_previews')
    scene_3d = models.ForeignKey(Scene3D, on_delete=models.CASCADE, null=True, blank=True, related_name='ar_previews')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='ar_previews')
    
    name = models.CharField(max_length=255)
    
    # AR Configuration
    ar_type = models.CharField(max_length=50, default='plane')  # plane, face, image, world
    tracking_image = models.ImageField(upload_to='ar_tracking/', null=True, blank=True)
    
    # Placement settings
    scale = models.FloatField(default=1.0)
    offset_x = models.FloatField(default=0)
    offset_y = models.FloatField(default=0)
    offset_z = models.FloatField(default=0)
    
    # Interaction settings
    allow_scale = models.BooleanField(default=True)
    allow_rotate = models.BooleanField(default=True)
    allow_move = models.BooleanField(default=True)
    
    # USDZ file for iOS Quick Look
    usdz_file = models.FileField(upload_to='ar_usdz/', null=True, blank=True)
    
    # QR code for easy mobile access
    qr_code = models.ImageField(upload_to='ar_qr_codes/', null=True, blank=True)
    
    # Share settings
    is_public = models.BooleanField(default=False)
    share_link = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AR Preview'
        verbose_name_plural = 'AR Previews'
    
    def __str__(self):
        return self.name


class Conversion3DTo2D(models.Model):
    """3D to 2D conversion job"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    VIEW_CHOICES = [
        ('front', 'Front'),
        ('back', 'Back'),
        ('left', 'Left'),
        ('right', 'Right'),
        ('top', 'Top'),
        ('bottom', 'Bottom'),
        ('isometric', 'Isometric'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversions_3d_to_2d')
    
    # Source
    model_3d = models.ForeignKey(Model3D, on_delete=models.CASCADE, null=True, blank=True)
    scene_3d = models.ForeignKey(Scene3D, on_delete=models.CASCADE, null=True, blank=True)
    
    # Conversion settings
    view = models.CharField(max_length=20, choices=VIEW_CHOICES, default='isometric')
    width = models.IntegerField(default=1920)
    height = models.IntegerField(default=1080)
    transparent_background = models.BooleanField(default=True)
    
    # Custom camera for custom view
    camera_position = models.JSONField(default=dict)
    camera_target = models.JSONField(default=dict)
    
    # Output format
    output_format = models.CharField(max_length=10, default='png')  # png, svg, pdf
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Result
    output_file = models.FileField(upload_to='3d_to_2d_output/', null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '3D to 2D Conversion'
        verbose_name_plural = '3D to 2D Conversions'
