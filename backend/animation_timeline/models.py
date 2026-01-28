"""
Advanced Animation Timeline System

Production-ready keyframe animation system with After Effects-like timeline,
easing curves, and Lottie export capabilities.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json


class AnimationProject(models.Model):
    """
    An animation project containing multiple compositions and assets.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='animation_projects'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='animation_projects'
    )
    
    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Global settings
    frame_rate = models.FloatField(default=60.0, validators=[MinValueValidator(1), MaxValueValidator(120)])
    default_duration = models.FloatField(default=3.0)  # seconds
    
    # Canvas settings
    width = models.IntegerField(default=1920)
    height = models.IntegerField(default=1080)
    background_color = models.CharField(max_length=50, default='#ffffff')
    
    # Preview settings
    thumbnail = models.ImageField(upload_to='animation_projects/', null=True, blank=True)
    preview_url = models.URLField(blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    
    # Tags
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Animation Project'
        verbose_name_plural = 'Animation Projects'
    
    def __str__(self):
        return self.name


class AnimationComposition(models.Model):
    """
    A composition is a container for animated layers, similar to After Effects comps.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animation_project = models.ForeignKey(
        AnimationProject,
        on_delete=models.CASCADE,
        related_name='compositions'
    )
    
    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Composition settings
    width = models.IntegerField(default=1920)
    height = models.IntegerField(default=1080)
    frame_rate = models.FloatField(null=True, blank=True)  # null = use project default
    duration = models.FloatField(default=3.0)  # seconds
    
    # Work area (in/out points for rendering)
    work_area_start = models.FloatField(default=0)
    work_area_end = models.FloatField(null=True, blank=True)
    
    # Background
    background_color = models.CharField(max_length=50, default='transparent')
    background_opacity = models.FloatField(default=1.0)
    
    # Is this the main composition
    is_main = models.BooleanField(default=False)
    
    # Order in project
    order = models.IntegerField(default=0)
    
    # Thumbnail
    thumbnail = models.ImageField(upload_to='compositions/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Animation Composition'
        verbose_name_plural = 'Animation Compositions'
    
    def __str__(self):
        return f"{self.animation_project.name}/{self.name}"
    
    def get_frame_rate(self):
        return self.frame_rate or self.animation_project.frame_rate
    
    def get_total_frames(self):
        return int(self.duration * self.get_frame_rate())


class AnimationLayer(models.Model):
    """
    A layer within a composition that can be animated.
    """
    
    LAYER_TYPE_SHAPE = 'shape'
    LAYER_TYPE_TEXT = 'text'
    LAYER_TYPE_IMAGE = 'image'
    LAYER_TYPE_VIDEO = 'video'
    LAYER_TYPE_AUDIO = 'audio'
    LAYER_TYPE_NULL = 'null'  # For parenting
    LAYER_TYPE_CAMERA = 'camera'
    LAYER_TYPE_COMPOSITION = 'composition'  # Nested composition
    LAYER_TYPE_SOLID = 'solid'
    LAYER_TYPE_CHOICES = [
        (LAYER_TYPE_SHAPE, 'Shape'),
        (LAYER_TYPE_TEXT, 'Text'),
        (LAYER_TYPE_IMAGE, 'Image'),
        (LAYER_TYPE_VIDEO, 'Video'),
        (LAYER_TYPE_AUDIO, 'Audio'),
        (LAYER_TYPE_NULL, 'Null Object'),
        (LAYER_TYPE_CAMERA, 'Camera'),
        (LAYER_TYPE_COMPOSITION, 'Composition'),
        (LAYER_TYPE_SOLID, 'Solid'),
    ]
    
    BLEND_MODES = [
        ('normal', 'Normal'),
        ('multiply', 'Multiply'),
        ('screen', 'Screen'),
        ('overlay', 'Overlay'),
        ('darken', 'Darken'),
        ('lighten', 'Lighten'),
        ('color-dodge', 'Color Dodge'),
        ('color-burn', 'Color Burn'),
        ('hard-light', 'Hard Light'),
        ('soft-light', 'Soft Light'),
        ('difference', 'Difference'),
        ('exclusion', 'Exclusion'),
        ('hue', 'Hue'),
        ('saturation', 'Saturation'),
        ('color', 'Color'),
        ('luminosity', 'Luminosity'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    composition = models.ForeignKey(
        AnimationComposition,
        on_delete=models.CASCADE,
        related_name='layers'
    )
    
    # Basic info
    name = models.CharField(max_length=255)
    layer_type = models.CharField(max_length=20, choices=LAYER_TYPE_CHOICES)
    
    # Layer content (varies by type)
    content_data = models.JSONField(default=dict)
    # Shape: {"type": "rect", "width": 100, "height": 100, "fill": "#000"}
    # Text: {"text": "Hello", "font": "Arial", "size": 24}
    # Image: {"asset_id": "...", "src": "..."}
    
    # Nested composition reference
    nested_composition = models.ForeignKey(
        AnimationComposition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_in_layers'
    )
    
    # Design component reference
    design_component = models.ForeignKey(
        'projects.DesignComponent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='animation_layers'
    )
    
    # Layer timing
    in_point = models.FloatField(default=0)  # Start time in seconds
    out_point = models.FloatField(null=True, blank=True)  # End time in seconds
    start_offset = models.FloatField(default=0)  # Time remap offset
    
    # Initial transform values (can be animated via tracks)
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    position_z = models.FloatField(default=0)  # For 3D layers
    anchor_x = models.FloatField(default=0)
    anchor_y = models.FloatField(default=0)
    scale_x = models.FloatField(default=100)  # percentage
    scale_y = models.FloatField(default=100)
    scale_z = models.FloatField(default=100)
    rotation = models.FloatField(default=0)  # degrees
    rotation_x = models.FloatField(default=0)  # 3D
    rotation_y = models.FloatField(default=0)  # 3D
    opacity = models.FloatField(default=100)  # percentage
    
    # Layer hierarchy
    parent_layer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_layers'
    )
    
    # Layer order (higher = on top)
    order = models.IntegerField(default=0)
    
    # Visibility and locking
    visible = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)
    solo = models.BooleanField(default=False)
    shy = models.BooleanField(default=False)  # Hide in timeline
    
    # 3D layer
    is_3d = models.BooleanField(default=False)
    
    # Collapse transformations (for compositions)
    collapse_transform = models.BooleanField(default=False)
    
    # Motion blur
    motion_blur = models.BooleanField(default=False)
    motion_blur_samples = models.IntegerField(default=16)
    
    # Blend mode
    blend_mode = models.CharField(max_length=20, choices=BLEND_MODES, default='normal')
    
    # Track matte settings
    TRACK_MATTE_NONE = 'none'
    TRACK_MATTE_ALPHA = 'alpha'
    TRACK_MATTE_ALPHA_INVERTED = 'alpha_inverted'
    TRACK_MATTE_LUMA = 'luma'
    TRACK_MATTE_LUMA_INVERTED = 'luma_inverted'
    TRACK_MATTE_CHOICES = [
        (TRACK_MATTE_NONE, 'None'),
        (TRACK_MATTE_ALPHA, 'Alpha Matte'),
        (TRACK_MATTE_ALPHA_INVERTED, 'Alpha Inverted'),
        (TRACK_MATTE_LUMA, 'Luma Matte'),
        (TRACK_MATTE_LUMA_INVERTED, 'Luma Inverted'),
    ]
    track_matte_type = models.CharField(
        max_length=20,
        choices=TRACK_MATTE_CHOICES,
        default=TRACK_MATTE_NONE
    )
    track_matte_layer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matte_for_layers'
    )
    
    # Color label for organization
    color_label = models.CharField(max_length=50, default='#808080')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order']
        verbose_name = 'Animation Layer'
        verbose_name_plural = 'Animation Layers'
    
    def __str__(self):
        return f"{self.name} ({self.layer_type})"


class AnimationTrack(models.Model):
    """
    An animation track controls a specific property over time.
    Contains keyframes for the property.
    """
    
    PROPERTY_TYPES = [
        # Transform
        ('position_x', 'Position X'),
        ('position_y', 'Position Y'),
        ('position_z', 'Position Z'),
        ('anchor_x', 'Anchor X'),
        ('anchor_y', 'Anchor Y'),
        ('scale_x', 'Scale X'),
        ('scale_y', 'Scale Y'),
        ('scale_z', 'Scale Z'),
        ('scale_uniform', 'Scale Uniform'),
        ('rotation', 'Rotation'),
        ('rotation_x', 'Rotation X'),
        ('rotation_y', 'Rotation Y'),
        ('rotation_z', 'Rotation Z'),
        ('opacity', 'Opacity'),
        # Shape
        ('fill_color', 'Fill Color'),
        ('stroke_color', 'Stroke Color'),
        ('stroke_width', 'Stroke Width'),
        ('path', 'Path'),
        ('corner_radius', 'Corner Radius'),
        # Text
        ('text_content', 'Text Content'),
        ('font_size', 'Font Size'),
        ('letter_spacing', 'Letter Spacing'),
        ('line_height', 'Line Height'),
        # Effects
        ('blur', 'Blur'),
        ('brightness', 'Brightness'),
        ('contrast', 'Contrast'),
        ('saturate', 'Saturate'),
        # Custom
        ('custom', 'Custom Property'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    layer = models.ForeignKey(
        AnimationLayer,
        on_delete=models.CASCADE,
        related_name='tracks'
    )
    
    # Property being animated
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPES)
    property_path = models.CharField(max_length=255, blank=True)  # For nested properties
    
    # Display name
    display_name = models.CharField(max_length=100, blank=True)
    
    # Is track enabled
    enabled = models.BooleanField(default=True)
    
    # Expanded in timeline UI
    expanded = models.BooleanField(default=True)
    
    # Expression (for advanced animations)
    expression = models.TextField(blank=True)
    expression_enabled = models.BooleanField(default=False)
    
    # Color for track in timeline
    color = models.CharField(max_length=50, default='#6366f1')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['property_type']
        verbose_name = 'Animation Track'
        verbose_name_plural = 'Animation Tracks'
    
    def __str__(self):
        return f"{self.layer.name} - {self.get_property_type_display()}"


class AnimationKeyframe(models.Model):
    """
    A keyframe defines a value at a specific point in time.
    """
    
    INTERPOLATION_LINEAR = 'linear'
    INTERPOLATION_BEZIER = 'bezier'
    INTERPOLATION_HOLD = 'hold'
    INTERPOLATION_EASE = 'ease'
    INTERPOLATION_EASE_IN = 'ease_in'
    INTERPOLATION_EASE_OUT = 'ease_out'
    INTERPOLATION_EASE_IN_OUT = 'ease_in_out'
    INTERPOLATION_SPRING = 'spring'
    INTERPOLATION_BOUNCE = 'bounce'
    INTERPOLATION_ELASTIC = 'elastic'
    INTERPOLATION_CHOICES = [
        (INTERPOLATION_LINEAR, 'Linear'),
        (INTERPOLATION_BEZIER, 'Bezier'),
        (INTERPOLATION_HOLD, 'Hold'),
        (INTERPOLATION_EASE, 'Ease'),
        (INTERPOLATION_EASE_IN, 'Ease In'),
        (INTERPOLATION_EASE_OUT, 'Ease Out'),
        (INTERPOLATION_EASE_IN_OUT, 'Ease In Out'),
        (INTERPOLATION_SPRING, 'Spring'),
        (INTERPOLATION_BOUNCE, 'Bounce'),
        (INTERPOLATION_ELASTIC, 'Elastic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    track = models.ForeignKey(
        AnimationTrack,
        on_delete=models.CASCADE,
        related_name='keyframes'
    )
    
    # Time position in seconds
    time = models.FloatField(validators=[MinValueValidator(0)])
    
    # Value at this keyframe (stored as JSON for flexibility)
    value = models.JSONField()
    # For numbers: {"value": 100}
    # For colors: {"r": 255, "g": 100, "b": 50, "a": 1}
    # For paths: {"points": [...], "closed": true}
    
    # Interpolation type
    interpolation = models.CharField(
        max_length=20,
        choices=INTERPOLATION_CHOICES,
        default=INTERPOLATION_EASE_IN_OUT
    )
    
    # Bezier curve handles (for bezier interpolation)
    # Values are relative to keyframe position
    handle_in_x = models.FloatField(default=0)
    handle_in_y = models.FloatField(default=0)
    handle_out_x = models.FloatField(default=0)
    handle_out_y = models.FloatField(default=0)
    
    # Temporal easing (how fast animation moves through time)
    temporal_ease_in = models.FloatField(default=0.33)
    temporal_ease_out = models.FloatField(default=0.33)
    
    # Spatial easing (for position - curved motion paths)
    spatial_tangent_in = models.JSONField(null=True, blank=True)
    spatial_tangent_out = models.JSONField(null=True, blank=True)
    roving = models.BooleanField(default=False)  # Auto-time based on distance
    
    # Spring physics (for spring interpolation)
    spring_stiffness = models.FloatField(default=100)
    spring_damping = models.FloatField(default=10)
    spring_mass = models.FloatField(default=1)
    
    # Is this a selected keyframe (UI state, not persisted typically)
    is_selected = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['time']
        verbose_name = 'Animation Keyframe'
        verbose_name_plural = 'Animation Keyframes'
    
    def __str__(self):
        return f"Keyframe at {self.time}s"


class EasingPreset(models.Model):
    """
    Saved easing curve presets for reuse.
    """
    
    CATEGORY_CHOICES = [
        ('ease', 'Ease'),
        ('bounce', 'Bounce'),
        ('elastic', 'Elastic'),
        ('spring', 'Spring'),
        ('steps', 'Steps'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='easing_presets'
    )
    
    # Basic info
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='custom')
    
    # Bezier curve control points
    x1 = models.FloatField(default=0.42)
    y1 = models.FloatField(default=0)
    x2 = models.FloatField(default=0.58)
    y2 = models.FloatField(default=1)
    
    # For spring/physics based easing
    spring_config = models.JSONField(null=True, blank=True)
    # {"stiffness": 100, "damping": 10, "mass": 1}
    
    # Is system preset
    is_system = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    
    # Usage count
    use_count = models.IntegerField(default=0)
    
    # Preview image
    preview = models.ImageField(upload_to='easing_presets/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-use_count', 'name']
        verbose_name = 'Easing Preset'
        verbose_name_plural = 'Easing Presets'
    
    def __str__(self):
        return self.name
    
    def to_css_timing_function(self):
        """Convert to CSS cubic-bezier format."""
        return f"cubic-bezier({self.x1}, {self.y1}, {self.x2}, {self.y2})"


class AnimationEffect(models.Model):
    """
    Effects applied to layers (blur, glow, color correction, etc.)
    """
    
    EFFECT_TYPES = [
        ('blur', 'Blur'),
        ('gaussian_blur', 'Gaussian Blur'),
        ('motion_blur', 'Motion Blur'),
        ('drop_shadow', 'Drop Shadow'),
        ('inner_shadow', 'Inner Shadow'),
        ('glow', 'Glow'),
        ('color_correction', 'Color Correction'),
        ('hue_saturation', 'Hue/Saturation'),
        ('brightness_contrast', 'Brightness/Contrast'),
        ('levels', 'Levels'),
        ('curves', 'Curves'),
        ('gradient_overlay', 'Gradient Overlay'),
        ('pattern_overlay', 'Pattern Overlay'),
        ('stroke', 'Stroke'),
        ('displacement', 'Displacement'),
        ('turbulent_displace', 'Turbulent Displace'),
        ('wave_warp', 'Wave Warp'),
        ('spherize', 'Spherize'),
        ('twirl', 'Twirl'),
        ('vignette', 'Vignette'),
        ('noise', 'Noise'),
        ('grain', 'Grain'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    layer = models.ForeignKey(
        AnimationLayer,
        on_delete=models.CASCADE,
        related_name='effects'
    )
    
    # Effect type
    effect_type = models.CharField(max_length=30, choices=EFFECT_TYPES)
    name = models.CharField(max_length=100, blank=True)
    
    # Effect parameters (varies by type)
    parameters = models.JSONField(default=dict)
    # blur: {"radius": 10}
    # drop_shadow: {"color": "#000", "opacity": 0.5, "angle": 135, "distance": 10, "blur": 20}
    
    # Is effect enabled
    enabled = models.BooleanField(default=True)
    
    # Order (effects are applied in order)
    order = models.IntegerField(default=0)
    
    # Expanded in UI
    expanded = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Animation Effect'
        verbose_name_plural = 'Animation Effects'
    
    def __str__(self):
        return f"{self.layer.name} - {self.get_effect_type_display()}"


class LottieExport(models.Model):
    """
    Exported Lottie animation files.
    """
    
    QUALITY_CHOICES = [
        ('low', 'Low (smaller file)'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('lossless', 'Lossless (largest file)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    composition = models.ForeignKey(
        AnimationComposition,
        on_delete=models.CASCADE,
        related_name='lottie_exports'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lottie_exports'
    )
    
    # Export settings
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='high')
    include_hidden_layers = models.BooleanField(default=False)
    
    # Output files
    lottie_file = models.FileField(upload_to='lottie_exports/')
    file_size = models.BigIntegerField(default=0)
    
    # Lottie metadata
    lottie_version = models.CharField(max_length=50, default='5.9.0')
    lottie_data = models.JSONField(null=True, blank=True)  # Cached JSON
    
    # Preview
    preview_gif = models.FileField(upload_to='lottie_previews/', null=True, blank=True)
    preview_mp4 = models.FileField(upload_to='lottie_previews/', null=True, blank=True)
    
    # Export stats
    duration = models.FloatField(null=True, blank=True)
    frame_count = models.IntegerField(null=True, blank=True)
    layer_count = models.IntegerField(null=True, blank=True)
    
    # Compatibility
    supported_features = models.JSONField(default=list)
    unsupported_features = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lottie Export'
        verbose_name_plural = 'Lottie Exports'
    
    def __str__(self):
        return f"{self.composition.name} - Lottie Export"


class AnimationSequence(models.Model):
    """
    A sequence of animations for prototyping interactions.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animation_project = models.ForeignKey(
        AnimationProject,
        on_delete=models.CASCADE,
        related_name='sequences'
    )
    
    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Trigger for this sequence
    TRIGGER_TYPES = [
        ('click', 'On Click'),
        ('hover', 'On Hover'),
        ('hover_end', 'On Hover End'),
        ('load', 'On Load'),
        ('scroll', 'On Scroll'),
        ('drag', 'On Drag'),
        ('key_press', 'On Key Press'),
        ('timer', 'After Timer'),
        ('custom', 'Custom Trigger'),
    ]
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES, default='click')
    trigger_config = models.JSONField(default=dict)
    # click: {"target": "button_id"}
    # scroll: {"threshold": 0.5}
    # timer: {"delay": 2000}
    
    # Animation settings
    duration = models.FloatField(default=0.3)
    delay = models.FloatField(default=0)
    
    # Sequence of animations
    animations = models.JSONField(default=list)
    # [
    #   {"layer_id": "...", "property": "opacity", "to": 0, "duration": 0.3},
    #   {"layer_id": "...", "property": "scale", "to": 1.2, "delay": 0.1}
    # ]
    
    # Loop settings
    loop = models.BooleanField(default=False)
    loop_count = models.IntegerField(default=0)  # 0 = infinite
    
    # Order
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Animation Sequence'
        verbose_name_plural = 'Animation Sequences'
    
    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"
