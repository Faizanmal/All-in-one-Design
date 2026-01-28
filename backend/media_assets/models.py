"""
Media Assets Models - Video & GIF Support

Provides embedding videos and animated GIFs in designs,
along with export to animated formats.
"""

from django.db import models
from django.conf import settings
import uuid


class VideoAsset(models.Model):
    """Video file asset for embedding in designs."""
    
    VIDEO_SOURCES = [
        ('upload', 'Uploaded'),
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('url', 'External URL'),
        ('lottie', 'Lottie Animation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_assets')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='video_assets', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=VIDEO_SOURCES)
    
    # File or URL
    file = models.FileField(upload_to='videos/', null=True, blank=True)
    url = models.URLField(blank=True)
    embed_id = models.CharField(max_length=100, blank=True)  # YouTube/Vimeo ID
    
    # Metadata
    duration = models.FloatField(null=True, blank=True, help_text='Duration in seconds')
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    format = models.CharField(max_length=20, blank=True)  # mp4, webm, etc.
    
    # Thumbnail
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)
    
    # Playback settings
    autoplay = models.BooleanField(default=False)
    loop = models.BooleanField(default=False)
    muted = models.BooleanField(default=True)
    show_controls = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class GIFAsset(models.Model):
    """Animated GIF asset."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gif_assets')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='gif_assets', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='gifs/')
    
    # Metadata
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    frame_count = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # First frame as static preview
    static_preview = models.ImageField(upload_to='gif_previews/', null=True, blank=True)
    
    # Playback
    autoplay = models.BooleanField(default=True)
    loop = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class LottieAsset(models.Model):
    """Lottie animation asset."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lottie_assets')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='lottie_assets', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    
    # Lottie JSON data
    json_data = models.JSONField()
    file = models.FileField(upload_to='lottie/', null=True, blank=True)
    
    # Metadata
    version = models.CharField(max_length=20, blank=True)
    frame_rate = models.FloatField(null=True, blank=True)
    in_point = models.FloatField(null=True, blank=True)
    out_point = models.FloatField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    
    # Playback settings
    autoplay = models.BooleanField(default=True)
    loop = models.BooleanField(default=True)
    speed = models.FloatField(default=1.0)
    direction = models.IntegerField(default=1)  # 1 = forward, -1 = reverse
    
    # Preview
    preview_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class MediaPlacement(models.Model):
    """Placement of media in a design."""
    
    MEDIA_TYPES = [
        ('video', 'Video'),
        ('gif', 'GIF'),
        ('lottie', 'Lottie'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='media_placements')
    
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    video = models.ForeignKey(VideoAsset, on_delete=models.SET_NULL, null=True, blank=True)
    gif = models.ForeignKey(GIFAsset, on_delete=models.SET_NULL, null=True, blank=True)
    lottie = models.ForeignKey(LottieAsset, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Position and size
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    width = models.FloatField(default=320)
    height = models.FloatField(default=180)
    rotation = models.FloatField(default=0)
    
    # Clipping
    clip_path = models.TextField(blank=True)  # SVG clip path
    border_radius = models.FloatField(default=0)
    
    # Layer
    z_index = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    
    # Playback overrides
    start_time = models.FloatField(default=0)
    end_time = models.FloatField(null=True, blank=True)
    playback_rate = models.FloatField(default=1.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']


class AnimatedExport(models.Model):
    """Export job for animated content."""
    
    EXPORT_FORMATS = [
        ('gif', 'Animated GIF'),
        ('mp4', 'MP4 Video'),
        ('webm', 'WebM Video'),
        ('lottie', 'Lottie JSON'),
        ('apng', 'Animated PNG'),
        ('webp', 'Animated WebP'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animated_exports')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='animated_exports')
    
    export_format = models.CharField(max_length=20, choices=EXPORT_FORMATS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Export settings
    settings = models.JSONField(default=dict)
    # {
    #   "width": 800,
    #   "height": 600,
    #   "fps": 30,
    #   "quality": 80,
    #   "loop": true,
    #   "duration": 5.0,
    #   "start_time": 0,
    #   "end_time": 5.0,
    #   "background": "#ffffff"
    # }
    
    # Frame range
    frame_start = models.IntegerField(default=0)
    frame_end = models.IntegerField(null=True, blank=True)
    
    # Result
    output_file = models.FileField(upload_to='animated_exports/', null=True, blank=True)
    output_url = models.URLField(blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Processing info
    progress = models.FloatField(default=0)
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.export_format}"


class VideoFrame(models.Model):
    """Extracted frame from a video for use in designs."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(VideoAsset, on_delete=models.CASCADE, related_name='frames')
    
    frame_number = models.IntegerField()
    timestamp = models.FloatField()  # In seconds
    
    image = models.ImageField(upload_to='video_frames/')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['frame_number']
        unique_together = ['video', 'frame_number']
