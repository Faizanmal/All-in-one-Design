"""
Advanced Vector Editing Models

Provides data models for:
- Vector paths with bezier curves
- Boolean operations (union, subtract, intersect, exclude)
- Corner rounding per point
- Path offset and outline stroke
"""

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
import uuid
import json


class VectorPath(models.Model):
    """
    Represents a vector path with bezier curve support.
    
    Stores path data in SVG-compatible format with additional
    metadata for advanced editing operations.
    """
    
    PATH_TYPES = [
        ('open', 'Open Path'),
        ('closed', 'Closed Path'),
        ('compound', 'Compound Path'),
    ]
    
    FILL_RULES = [
        ('nonzero', 'Non-Zero'),
        ('evenodd', 'Even-Odd'),
    ]
    
    STROKE_CAP_STYLES = [
        ('butt', 'Butt'),
        ('round', 'Round'),
        ('square', 'Square'),
    ]
    
    STROKE_JOIN_STYLES = [
        ('miter', 'Miter'),
        ('round', 'Round'),
        ('bevel', 'Bevel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='vector_paths')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vector_paths')
    
    name = models.CharField(max_length=255, default='Path')
    path_type = models.CharField(max_length=20, choices=PATH_TYPES, default='closed')
    
    # SVG path data (d attribute)
    path_data = models.TextField(help_text='SVG path data string')
    
    # Detailed path points with bezier handles
    # Format: [{"type": "M"|"L"|"C"|"Q"|"A"|"Z", "points": [...], "handles": {...}}]
    path_points = models.JSONField(default=list, help_text='Detailed path points with handles')
    
    # Fill properties
    fill_color = models.CharField(max_length=50, blank=True, default='#000000')
    fill_opacity = models.FloatField(default=1.0)
    fill_rule = models.CharField(max_length=20, choices=FILL_RULES, default='nonzero')
    
    # Gradient fill
    fill_gradient = models.JSONField(null=True, blank=True, help_text='Gradient definition')
    
    # Pattern fill
    fill_pattern = models.ForeignKey('VectorPattern', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Stroke properties
    stroke_color = models.CharField(max_length=50, blank=True, default='')
    stroke_width = models.FloatField(default=1.0)
    stroke_opacity = models.FloatField(default=1.0)
    stroke_cap = models.CharField(max_length=20, choices=STROKE_CAP_STYLES, default='round')
    stroke_join = models.CharField(max_length=20, choices=STROKE_JOIN_STYLES, default='round')
    stroke_miter_limit = models.FloatField(default=4.0)
    stroke_dash_array = models.JSONField(default=list, help_text='Dash pattern array')
    stroke_dash_offset = models.FloatField(default=0.0)
    
    # Transform
    transform_matrix = models.JSONField(default=list, help_text='2D transformation matrix [a,b,c,d,e,f]')
    
    # Position and bounds
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    width = models.FloatField(default=100)
    height = models.FloatField(default=100)
    
    # Layer info
    z_index = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    
    # Metadata
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']
        verbose_name = 'Vector Path'
        verbose_name_plural = 'Vector Paths'
    
    def __str__(self):
        return f"{self.name} ({self.path_type})"
    
    def get_svg_element(self):
        """Generate SVG path element string."""
        attrs = [
            f'd="{self.path_data}"',
            f'fill="{self.fill_color}"' if self.fill_color else 'fill="none"',
            f'fill-opacity="{self.fill_opacity}"',
            f'fill-rule="{self.fill_rule}"',
        ]
        
        if self.stroke_color:
            attrs.extend([
                f'stroke="{self.stroke_color}"',
                f'stroke-width="{self.stroke_width}"',
                f'stroke-opacity="{self.stroke_opacity}"',
                f'stroke-linecap="{self.stroke_cap}"',
                f'stroke-linejoin="{self.stroke_join}"',
            ])
            
            if self.stroke_dash_array:
                attrs.append(f'stroke-dasharray="{" ".join(map(str, self.stroke_dash_array))}"')
        
        if self.transform_matrix:
            attrs.append(f'transform="matrix({",".join(map(str, self.transform_matrix))})"')
        
        return f'<path {" ".join(attrs)} />'


class PathPoint(models.Model):
    """
    Individual point on a vector path with bezier curve handles.
    """
    
    POINT_TYPES = [
        ('corner', 'Corner Point'),
        ('smooth', 'Smooth Point'),
        ('symmetric', 'Symmetric Point'),
        ('disconnected', 'Disconnected Handles'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path = models.ForeignKey(VectorPath, on_delete=models.CASCADE, related_name='points')
    
    # Point position
    x = models.FloatField()
    y = models.FloatField()
    
    # Bezier curve handles (relative to point position)
    handle_in_x = models.FloatField(default=0, help_text='Incoming handle X offset')
    handle_in_y = models.FloatField(default=0, help_text='Incoming handle Y offset')
    handle_out_x = models.FloatField(default=0, help_text='Outgoing handle X offset')
    handle_out_y = models.FloatField(default=0, help_text='Outgoing handle Y offset')
    
    # Point type determines handle behavior
    point_type = models.CharField(max_length=20, choices=POINT_TYPES, default='corner')
    
    # Corner rounding (per-point)
    corner_radius = models.FloatField(default=0, help_text='Corner rounding radius')
    
    # Order in path
    order = models.IntegerField(default=0)
    
    # Selection state (for UI)
    is_selected = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Path Point'
        verbose_name_plural = 'Path Points'
    
    def __str__(self):
        return f"Point ({self.x}, {self.y}) - {self.point_type}"


class BooleanOperation(models.Model):
    """
    Records boolean operations performed on vector paths.
    """
    
    OPERATION_TYPES = [
        ('union', 'Union'),
        ('subtract', 'Subtract'),
        ('intersect', 'Intersect'),
        ('exclude', 'Exclude'),
        ('divide', 'Divide'),
        ('trim', 'Trim'),
        ('merge', 'Merge'),
        ('crop', 'Crop'),
        ('outline', 'Outline'),
        ('minus_back', 'Minus Back'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boolean_operations')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='boolean_operations')
    
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    
    # Source paths (JSON array of path IDs)
    source_paths = models.JSONField(help_text='Array of source path UUIDs')
    
    # Result path
    result_path = models.ForeignKey(VectorPath, on_delete=models.SET_NULL, null=True, related_name='boolean_result')
    
    # Store original state for undo
    original_state = models.JSONField(help_text='Original paths data for undo')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Boolean Operation'
        verbose_name_plural = 'Boolean Operations'
    
    def __str__(self):
        return f"{self.operation_type} operation on {len(self.source_paths)} paths"


class PathOffset(models.Model):
    """
    Path offset/outline stroke operations.
    """
    
    OFFSET_TYPES = [
        ('expand', 'Expand'),
        ('contract', 'Contract'),
        ('outline_stroke', 'Outline Stroke'),
    ]
    
    JOIN_TYPES = [
        ('miter', 'Miter'),
        ('round', 'Round'),
        ('bevel', 'Bevel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_path = models.ForeignKey(VectorPath, on_delete=models.CASCADE, related_name='offset_operations')
    
    offset_type = models.CharField(max_length=20, choices=OFFSET_TYPES)
    offset_value = models.FloatField(help_text='Offset distance in pixels')
    join_type = models.CharField(max_length=20, choices=JOIN_TYPES, default='miter')
    miter_limit = models.FloatField(default=4.0)
    
    # Result path
    result_path = models.ForeignKey(VectorPath, on_delete=models.SET_NULL, null=True, related_name='offset_result')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Path Offset'
        verbose_name_plural = 'Path Offsets'


class VectorPattern(models.Model):
    """
    Reusable vector patterns for fills.
    """
    
    PATTERN_TYPES = [
        ('user', 'User Created'),
        ('preset', 'Preset'),
        ('imported', 'Imported'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vector_patterns')
    
    name = models.CharField(max_length=255)
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES, default='user')
    
    # Pattern definition (SVG pattern element content)
    pattern_content = models.TextField()
    
    # Pattern dimensions
    width = models.FloatField(default=10)
    height = models.FloatField(default=10)
    
    # Pattern transform
    pattern_transform = models.JSONField(default=list)
    
    # Preview image
    preview_url = models.URLField(blank=True)
    
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Vector Pattern'
        verbose_name_plural = 'Vector Patterns'
    
    def __str__(self):
        return self.name


class VectorShape(models.Model):
    """
    Preset vector shapes that can be converted to editable paths.
    """
    
    SHAPE_TYPES = [
        ('rectangle', 'Rectangle'),
        ('ellipse', 'Ellipse'),
        ('polygon', 'Polygon'),
        ('star', 'Star'),
        ('line', 'Line'),
        ('arrow', 'Arrow'),
        ('arc', 'Arc'),
        ('spiral', 'Spiral'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='vector_shapes')
    
    name = models.CharField(max_length=255)
    shape_type = models.CharField(max_length=20, choices=SHAPE_TYPES)
    
    # Shape-specific parameters
    parameters = models.JSONField(default=dict)
    # Examples:
    # rectangle: {"width": 100, "height": 50, "cornerRadius": [0, 0, 0, 0]}
    # polygon: {"sides": 6, "radius": 50}
    # star: {"points": 5, "innerRadius": 25, "outerRadius": 50}
    # arc: {"startAngle": 0, "endAngle": 180, "radius": 50}
    
    # Position
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    
    # Styling (inherited by generated path)
    fill_color = models.CharField(max_length=50, default='#000000')
    stroke_color = models.CharField(max_length=50, blank=True)
    stroke_width = models.FloatField(default=1.0)
    
    # Layer info
    z_index = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']
        verbose_name = 'Vector Shape'
        verbose_name_plural = 'Vector Shapes'
    
    def __str__(self):
        return f"{self.name} ({self.shape_type})"
    
    def to_path(self):
        """Convert shape to editable vector path."""
        from .services import VectorService
        return VectorService.shape_to_path(self)


class PenToolSession(models.Model):
    """
    Tracks active pen tool drawing sessions.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pen_sessions')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='pen_sessions')
    
    # Current path being drawn
    current_path = models.ForeignKey(VectorPath, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Session state
    is_active = models.BooleanField(default=True)
    is_closed = models.BooleanField(default=False)
    
    # Tool settings
    tool_settings = models.JSONField(default=dict)
    # {"snapToGrid": true, "snapToGuides": true, "autoSmooth": false}
    
    # Temporary points (before committing to path)
    temp_points = models.JSONField(default=list)
    
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pen Tool Session'
        verbose_name_plural = 'Pen Tool Sessions'
    
    def __str__(self):
        return f"Pen session by {self.user.username}"
