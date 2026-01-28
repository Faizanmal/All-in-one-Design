from django.db import models
from django.conf import settings
import uuid


class Animation(models.Model):
    """Base animation model"""
    ANIMATION_TYPES = [
        ('keyframe', 'Keyframe Animation'),
        ('lottie', 'Lottie Animation'),
        ('css', 'CSS Animation'),
        ('svg', 'SVG Animation'),
        ('sprite', 'Sprite Animation'),
    ]
    
    EASING_TYPES = [
        ('linear', 'Linear'),
        ('ease', 'Ease'),
        ('ease-in', 'Ease In'),
        ('ease-out', 'Ease Out'),
        ('ease-in-out', 'Ease In Out'),
        ('cubic-bezier', 'Cubic Bezier'),
        ('spring', 'Spring'),
        ('bounce', 'Bounce'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animations')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='animations', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    animation_type = models.CharField(max_length=20, choices=ANIMATION_TYPES, default='keyframe')
    
    # Animation properties
    duration = models.FloatField(default=1.0)  # seconds
    delay = models.FloatField(default=0)  # seconds
    easing = models.CharField(max_length=50, choices=EASING_TYPES, default='ease')
    easing_params = models.JSONField(default=dict)  # For cubic-bezier params
    iterations = models.IntegerField(default=1)  # -1 for infinite
    direction = models.CharField(max_length=20, default='normal')  # normal, reverse, alternate
    fill_mode = models.CharField(max_length=20, default='forwards')  # none, forwards, backwards, both
    
    # Animation data
    keyframes = models.JSONField(default=list)  # List of keyframe objects
    
    # Metadata
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True)
    is_preset = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    
    # Preview
    thumbnail = models.ImageField(upload_to='animation_thumbnails/', null=True, blank=True)
    preview_gif = models.FileField(upload_to='animation_previews/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.animation_type})"


class Keyframe(models.Model):
    """Individual keyframe within an animation"""
    animation = models.ForeignKey(Animation, on_delete=models.CASCADE, related_name='keyframe_set')
    
    # Keyframe position (0-100 percent)
    position = models.FloatField()
    
    # Properties at this keyframe
    properties = models.JSONField(default=dict)
    # Example: {"opacity": 1, "transform": {"x": 0, "y": 0, "scale": 1, "rotate": 0}}
    
    # Per-keyframe easing (optional, overrides animation easing)
    easing = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['position']


class LottieAnimation(models.Model):
    """Lottie animation file storage and metadata"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lottie_animations')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='lottie_animations', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # File
    lottie_file = models.FileField(upload_to='lottie/')
    file_size = models.BigIntegerField(default=0)
    
    # Parsed metadata
    version = models.CharField(max_length=50, blank=True)
    frame_rate = models.FloatField(default=30)
    in_point = models.FloatField(default=0)
    out_point = models.FloatField(default=0)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    
    # Assets within lottie
    asset_count = models.IntegerField(default=0)
    layer_count = models.IntegerField(default=0)
    
    # Thumbnail
    thumbnail = models.ImageField(upload_to='lottie_thumbnails/', null=True, blank=True)
    
    # Tags
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lottie Animation'
        verbose_name_plural = 'Lottie Animations'
    
    def __str__(self):
        return self.name


class MicroInteraction(models.Model):
    """Pre-built micro-interaction library"""
    INTERACTION_TYPES = [
        ('button', 'Button'),
        ('hover', 'Hover Effect'),
        ('loading', 'Loading'),
        ('transition', 'Page Transition'),
        ('notification', 'Notification'),
        ('toggle', 'Toggle'),
        ('scroll', 'Scroll'),
        ('drag', 'Drag'),
        ('input', 'Input'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('menu', 'Menu'),
        ('modal', 'Modal'),
        ('tooltip', 'Tooltip'),
        ('carousel', 'Carousel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_TYPES)
    
    # Animation definition
    animation_data = models.JSONField(default=dict)
    
    # Code exports
    css_code = models.TextField(blank=True)
    js_code = models.TextField(blank=True)
    react_code = models.TextField(blank=True)
    vue_code = models.TextField(blank=True)
    lottie_data = models.JSONField(default=dict, blank=True)
    
    # Preview
    thumbnail = models.ImageField(upload_to='interaction_thumbnails/', null=True, blank=True)
    preview_url = models.URLField(blank=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    is_premium = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
        verbose_name = 'Micro Interaction'
        verbose_name_plural = 'Micro Interactions'
    
    def __str__(self):
        return f"{self.name} ({self.interaction_type})"


class AnimationPreset(models.Model):
    """Animation presets and templates"""
    PRESET_CATEGORIES = [
        ('entrance', 'Entrance'),
        ('exit', 'Exit'),
        ('emphasis', 'Emphasis'),
        ('motion-path', 'Motion Path'),
        ('background', 'Background'),
        ('text', 'Text'),
        ('character', 'Character'),
        ('ui', 'UI Elements'),
        ('3d', '3D'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=PRESET_CATEGORIES)
    
    # Animation definition
    animation_data = models.JSONField(default=dict)
    
    # Configurable parameters
    parameters = models.JSONField(default=list)
    # Example: [{"name": "duration", "type": "number", "default": 1, "min": 0.1, "max": 10}]
    
    # Preview
    thumbnail = models.ImageField(upload_to='preset_thumbnails/', null=True, blank=True)
    preview_gif = models.FileField(upload_to='preset_previews/', null=True, blank=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    is_premium = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Animation Preset'
        verbose_name_plural = 'Animation Presets'
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class AnimationTimeline(models.Model):
    """Timeline for compositing multiple animations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animation_timelines')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='animation_timelines', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Timeline settings
    duration = models.FloatField(default=5.0)  # Total duration in seconds
    frame_rate = models.IntegerField(default=60)
    
    # Timeline layers/tracks
    tracks = models.JSONField(default=list)
    # Example: [{"id": "1", "name": "Track 1", "items": [...], "muted": false}]
    
    # Export settings
    export_settings = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class TimelineItem(models.Model):
    """Individual item on an animation timeline"""
    timeline = models.ForeignKey(AnimationTimeline, on_delete=models.CASCADE, related_name='items')
    animation = models.ForeignKey(Animation, on_delete=models.CASCADE, null=True, blank=True)
    lottie = models.ForeignKey(LottieAnimation, on_delete=models.CASCADE, null=True, blank=True)
    
    # Position on timeline
    track_index = models.IntegerField(default=0)
    start_time = models.FloatField(default=0)
    end_time = models.FloatField(default=1)
    
    # Target element
    target_element_id = models.CharField(max_length=255)
    
    # Item properties
    properties = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['track_index', 'start_time']
