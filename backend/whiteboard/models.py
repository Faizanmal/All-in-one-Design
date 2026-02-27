"""
Whiteboard / FigJam-like Feature

Infinite canvas for brainstorming, flowcharts, sticky notes,
and collaborative ideation sessions.
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class Whiteboard(models.Model):
    """
    A collaborative whiteboard with infinite canvas.
    """
    
    BOARD_TYPE_BRAINSTORM = 'brainstorm'
    BOARD_TYPE_FLOWCHART = 'flowchart'
    BOARD_TYPE_WIREFRAME = 'wireframe'
    BOARD_TYPE_MINDMAP = 'mindmap'
    BOARD_TYPE_PLANNING = 'planning'
    BOARD_TYPE_RETROSPECTIVE = 'retrospective'
    BOARD_TYPE_CUSTOM = 'custom'
    BOARD_TYPE_CHOICES = [
        (BOARD_TYPE_BRAINSTORM, 'Brainstorm'),
        (BOARD_TYPE_FLOWCHART, 'Flowchart'),
        (BOARD_TYPE_WIREFRAME, 'Wireframe'),
        (BOARD_TYPE_MINDMAP, 'Mind Map'),
        (BOARD_TYPE_PLANNING, 'Planning'),
        (BOARD_TYPE_RETROSPECTIVE, 'Retrospective'),
        (BOARD_TYPE_CUSTOM, 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='whiteboards',
        null=True,
        blank=True
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='whiteboards'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_whiteboards'
    )
    
    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    board_type = models.CharField(
        max_length=20,
        choices=BOARD_TYPE_CHOICES,
        default=BOARD_TYPE_CUSTOM
    )
    
    # Canvas settings
    background_color = models.CharField(max_length=50, default='#f8f9fa')
    background_pattern = models.CharField(max_length=30, default='dots')  # dots, grid, lines, none
    grid_size = models.IntegerField(default=20)
    snap_to_grid = models.BooleanField(default=True)
    
    # Canvas bounds (infinite canvas but track used area)
    bounds_min_x = models.FloatField(default=-10000)
    bounds_min_y = models.FloatField(default=-10000)
    bounds_max_x = models.FloatField(default=10000)
    bounds_max_y = models.FloatField(default=10000)
    
    # Default view
    default_zoom = models.FloatField(default=1.0)
    default_center_x = models.FloatField(default=0)
    default_center_y = models.FloatField(default=0)
    
    # Thumbnail
    thumbnail = models.ImageField(upload_to='whiteboards/', null=True, blank=True)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    share_link = models.CharField(max_length=100, unique=True, null=True, blank=True)
    allow_guest_editing = models.BooleanField(default=False)
    
    # Collaborators
    collaborators = models.ManyToManyField(
        User,
        through='WhiteboardCollaborator',
        through_fields=('whiteboard', 'user'),
        related_name='collaborated_whiteboards'
    )
    
    # Status
    is_archived = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    
    # Tags
    tags = models.JSONField(default=list)
    
    # Activity
    last_activity = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = 'Whiteboard'
        verbose_name_plural = 'Whiteboards'
    
    def __str__(self):
        return self.name


class WhiteboardCollaborator(models.Model):
    """
    Collaborator permissions for whiteboard.
    """
    
    ROLE_VIEWER = 'viewer'
    ROLE_EDITOR = 'editor'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_VIEWER, 'Viewer'),
        (ROLE_EDITOR, 'Editor'),
        (ROLE_ADMIN, 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='collaborator_roles'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='whiteboard_roles'
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_EDITOR)
    
    # Cursor color for collaboration
    cursor_color = models.CharField(max_length=50, default='#6366f1')
    
    # Last seen position
    last_x = models.FloatField(null=True, blank=True)
    last_y = models.FloatField(null=True, blank=True)
    last_zoom = models.FloatField(null=True, blank=True)
    
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whiteboard_invites_sent'
    )
    
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['whiteboard', 'user']
        verbose_name = 'Whiteboard Collaborator'
        verbose_name_plural = 'Whiteboard Collaborators'


class StickyNote(models.Model):
    """
    A sticky note on the whiteboard.
    """
    
    COLOR_YELLOW = 'yellow'
    COLOR_PINK = 'pink'
    COLOR_BLUE = 'blue'
    COLOR_GREEN = 'green'
    COLOR_ORANGE = 'orange'
    COLOR_PURPLE = 'purple'
    COLOR_CHOICES = [
        (COLOR_YELLOW, 'Yellow'),
        (COLOR_PINK, 'Pink'),
        (COLOR_BLUE, 'Blue'),
        (COLOR_GREEN, 'Green'),
        (COLOR_ORANGE, 'Orange'),
        (COLOR_PURPLE, 'Purple'),
    ]
    
    SIZE_SMALL = 'small'
    SIZE_MEDIUM = 'medium'
    SIZE_LARGE = 'large'
    SIZE_CHOICES = [
        (SIZE_SMALL, 'Small'),
        (SIZE_MEDIUM, 'Medium'),
        (SIZE_LARGE, 'Large'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='sticky_notes'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sticky_notes'
    )
    
    # Content
    content = models.TextField(blank=True)
    
    # Appearance
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default=COLOR_YELLOW)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default=SIZE_MEDIUM)
    
    # Position and size
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    width = models.FloatField(default=200)
    height = models.FloatField(default=200)
    rotation = models.FloatField(default=0)
    
    # Z-order
    z_index = models.IntegerField(default=0)
    
    # Font
    font_size = models.IntegerField(default=16)
    text_align = models.CharField(max_length=20, default='left')
    
    # Grouping
    group = models.ForeignKey(
        'WhiteboardGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sticky_notes'
    )
    
    # Voting (for brainstorming sessions)
    votes = models.ManyToManyField(User, through='StickyNoteVote', related_name='voted_notes')
    
    # Locking
    locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']
        verbose_name = 'Sticky Note'
        verbose_name_plural = 'Sticky Notes'
    
    def __str__(self):
        return f"Sticky: {self.content[:30]}..."


class StickyNoteVote(models.Model):
    """
    Vote on a sticky note.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sticky_note = models.ForeignKey(
        StickyNote,
        on_delete=models.CASCADE,
        related_name='vote_records'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sticky_votes'
    )
    
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['sticky_note', 'user']
        verbose_name = 'Sticky Note Vote'
        verbose_name_plural = 'Sticky Note Votes'


class WhiteboardShape(models.Model):
    """
    Shapes drawn on the whiteboard.
    """
    
    SHAPE_TYPES = [
        ('rectangle', 'Rectangle'),
        ('ellipse', 'Ellipse'),
        ('triangle', 'Triangle'),
        ('diamond', 'Diamond'),
        ('star', 'Star'),
        ('arrow', 'Arrow'),
        ('line', 'Line'),
        ('polygon', 'Polygon'),
        ('cloud', 'Cloud'),
        ('cylinder', 'Cylinder'),
        ('parallelogram', 'Parallelogram'),
        ('hexagon', 'Hexagon'),
        ('trapezoid', 'Trapezoid'),
        ('callout', 'Callout'),
        ('freeform', 'Freeform'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='shapes'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whiteboard_shapes'
    )
    
    # Shape type
    shape_type = models.CharField(max_length=30, choices=SHAPE_TYPES)
    
    # Position and dimensions
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    width = models.FloatField(default=100)
    height = models.FloatField(default=100)
    rotation = models.FloatField(default=0)
    
    # For lines and arrows
    start_x = models.FloatField(null=True, blank=True)
    start_y = models.FloatField(null=True, blank=True)
    end_x = models.FloatField(null=True, blank=True)
    end_y = models.FloatField(null=True, blank=True)
    
    # For polygons and freeform
    points = models.JSONField(null=True, blank=True)  # Array of {x, y} points
    
    # Styling
    fill_color = models.CharField(max_length=50, default='#ffffff')
    fill_opacity = models.FloatField(default=1.0)
    stroke_color = models.CharField(max_length=50, default='#000000')
    stroke_width = models.FloatField(default=2)
    stroke_style = models.CharField(max_length=20, default='solid')  # solid, dashed, dotted
    
    # Corner radius
    corner_radius = models.FloatField(default=0)
    
    # Text inside shape
    text_content = models.TextField(blank=True)
    text_color = models.CharField(max_length=50, default='#000000')
    font_size = models.IntegerField(default=14)
    text_align = models.CharField(max_length=20, default='center')
    
    # Arrow settings
    start_arrow = models.CharField(max_length=20, default='none')  # none, arrow, circle, diamond
    end_arrow = models.CharField(max_length=20, default='none')
    
    # Z-order
    z_index = models.IntegerField(default=0)
    
    # Grouping
    group = models.ForeignKey(
        'WhiteboardGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shapes'
    )
    
    # Locking
    locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']
        verbose_name = 'Whiteboard Shape'
        verbose_name_plural = 'Whiteboard Shapes'


class Connector(models.Model):
    """
    Connectors between shapes (for flowcharts, diagrams).
    """
    
    CONNECTOR_TYPE_LINE = 'line'
    CONNECTOR_TYPE_ELBOW = 'elbow'
    CONNECTOR_TYPE_CURVE = 'curve'
    CONNECTOR_TYPE_CHOICES = [
        (CONNECTOR_TYPE_LINE, 'Straight Line'),
        (CONNECTOR_TYPE_ELBOW, 'Elbow'),
        (CONNECTOR_TYPE_CURVE, 'Curve'),
    ]
    
    ANCHOR_TOP = 'top'
    ANCHOR_RIGHT = 'right'
    ANCHOR_BOTTOM = 'bottom'
    ANCHOR_LEFT = 'left'
    ANCHOR_CENTER = 'center'
    ANCHOR_AUTO = 'auto'
    ANCHOR_CHOICES = [
        (ANCHOR_TOP, 'Top'),
        (ANCHOR_RIGHT, 'Right'),
        (ANCHOR_BOTTOM, 'Bottom'),
        (ANCHOR_LEFT, 'Left'),
        (ANCHOR_CENTER, 'Center'),
        (ANCHOR_AUTO, 'Auto'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='connectors'
    )
    
    # Source and target
    source_shape = models.ForeignKey(
        WhiteboardShape,
        on_delete=models.CASCADE,
        related_name='outgoing_connectors',
        null=True,
        blank=True
    )
    source_sticky = models.ForeignKey(
        StickyNote,
        on_delete=models.CASCADE,
        related_name='outgoing_connectors',
        null=True,
        blank=True
    )
    source_anchor = models.CharField(max_length=20, choices=ANCHOR_CHOICES, default=ANCHOR_AUTO)
    
    target_shape = models.ForeignKey(
        WhiteboardShape,
        on_delete=models.CASCADE,
        related_name='incoming_connectors',
        null=True,
        blank=True
    )
    target_sticky = models.ForeignKey(
        StickyNote,
        on_delete=models.CASCADE,
        related_name='incoming_connectors',
        null=True,
        blank=True
    )
    target_anchor = models.CharField(max_length=20, choices=ANCHOR_CHOICES, default=ANCHOR_AUTO)
    
    # Connector type
    connector_type = models.CharField(
        max_length=20,
        choices=CONNECTOR_TYPE_CHOICES,
        default=CONNECTOR_TYPE_ELBOW
    )
    
    # Styling
    stroke_color = models.CharField(max_length=50, default='#000000')
    stroke_width = models.FloatField(default=2)
    stroke_style = models.CharField(max_length=20, default='solid')
    
    # Arrows
    start_arrow = models.CharField(max_length=20, default='none')
    end_arrow = models.CharField(max_length=20, default='arrow')
    
    # Label
    label = models.CharField(max_length=255, blank=True)
    label_position = models.FloatField(default=0.5)  # 0-1, position along connector
    
    # Control points for curves
    control_points = models.JSONField(null=True, blank=True)
    
    # Z-order
    z_index = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']
        verbose_name = 'Connector'
        verbose_name_plural = 'Connectors'


class WhiteboardText(models.Model):
    """
    Standalone text elements on the whiteboard.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='text_elements'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whiteboard_texts'
    )
    
    # Content
    content = models.TextField()
    
    # Position
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    rotation = models.FloatField(default=0)
    
    # Styling
    font_family = models.CharField(max_length=100, default='Inter')
    font_size = models.IntegerField(default=24)
    font_weight = models.CharField(max_length=20, default='normal')
    font_style = models.CharField(max_length=20, default='normal')
    text_color = models.CharField(max_length=50, default='#000000')
    text_align = models.CharField(max_length=20, default='left')
    
    # Text decoration
    underline = models.BooleanField(default=False)
    strikethrough = models.BooleanField(default=False)
    
    # Width (for text wrapping)
    max_width = models.FloatField(null=True, blank=True)
    
    # Z-order
    z_index = models.IntegerField(default=0)
    
    # Grouping
    group = models.ForeignKey(
        'WhiteboardGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='text_elements'
    )
    
    # Locking
    locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']
        verbose_name = 'Whiteboard Text'
        verbose_name_plural = 'Whiteboard Texts'


class WhiteboardImage(models.Model):
    """
    Images placed on the whiteboard.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='images'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whiteboard_images'
    )
    
    # Image source
    image = models.ImageField(upload_to='whiteboard_images/')
    image_url = models.URLField(blank=True)  # For external images
    
    # Position and size
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    rotation = models.FloatField(default=0)
    
    # Original dimensions
    original_width = models.IntegerField(null=True, blank=True)
    original_height = models.IntegerField(null=True, blank=True)
    
    # Styling
    opacity = models.FloatField(default=1.0)
    corner_radius = models.FloatField(default=0)
    border_color = models.CharField(max_length=50, blank=True)
    border_width = models.FloatField(default=0)
    
    # Z-order
    z_index = models.IntegerField(default=0)
    
    # Grouping
    group = models.ForeignKey(
        'WhiteboardGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='images'
    )
    
    # Locking
    locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']
        verbose_name = 'Whiteboard Image'
        verbose_name_plural = 'Whiteboard Images'


class WhiteboardGroup(models.Model):
    """
    Groups of elements on the whiteboard.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='groups'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whiteboard_groups'
    )
    
    # Group name
    name = models.CharField(max_length=255, blank=True)
    
    # Parent group (for nested groups)
    parent_group = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_groups'
    )
    
    # Locking
    locked = models.BooleanField(default=False)
    
    # Z-order
    z_index = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['z_index']
        verbose_name = 'Whiteboard Group'
        verbose_name_plural = 'Whiteboard Groups'


class WhiteboardSection(models.Model):
    """
    Labeled sections/frames on the whiteboard for organization.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whiteboard_sections'
    )
    
    # Section info
    name = models.CharField(max_length=255)
    
    # Bounds
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    width = models.FloatField(default=500)
    height = models.FloatField(default=400)
    
    # Styling
    background_color = models.CharField(max_length=50, default='#f3f4f6')
    border_color = models.CharField(max_length=50, default='#d1d5db')
    title_background = models.CharField(max_length=50, default='#6366f1')
    title_color = models.CharField(max_length=50, default='#ffffff')
    
    # Order
    order = models.IntegerField(default=0)
    
    # Locking
    locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Whiteboard Section'
        verbose_name_plural = 'Whiteboard Sections'


class Timer(models.Model):
    """
    Timer for whiteboard sessions (for timed brainstorming, etc.)
    """
    
    STATUS_STOPPED = 'stopped'
    STATUS_RUNNING = 'running'
    STATUS_PAUSED = 'paused'
    STATUS_CHOICES = [
        (STATUS_STOPPED, 'Stopped'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_PAUSED, 'Paused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='timers'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whiteboard_timers'
    )
    
    # Timer name
    name = models.CharField(max_length=100, default='Timer')
    
    # Duration in seconds
    duration = models.IntegerField(default=300)  # 5 minutes default
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_STOPPED)
    
    # Elapsed time (for pause/resume)
    elapsed = models.IntegerField(default=0)
    
    # Last started
    started_at = models.DateTimeField(null=True, blank=True)
    
    # Sound on complete
    play_sound = models.BooleanField(default=True)
    
    # Visibility
    visible_to_all = models.BooleanField(default=True)
    
    # Position on canvas
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Timer'
        verbose_name_plural = 'Timers'


class WhiteboardComment(models.Model):
    """
    Comments on whiteboard or specific elements.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='whiteboard_comments'
    )
    
    # Comment content
    content = models.TextField()
    
    # Position on canvas
    position_x = models.FloatField()
    position_y = models.FloatField()
    
    # Associated element (optional)
    sticky_note = models.ForeignKey(
        StickyNote,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments'
    )
    shape = models.ForeignKey(
        WhiteboardShape,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments'
    )
    
    # Thread support
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_whiteboard_comments'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Whiteboard Comment'
        verbose_name_plural = 'Whiteboard Comments'


class WhiteboardEmoji(models.Model):
    """
    Emoji reactions placed on the whiteboard (for quick feedback).
    """
    
    EMOJI_THUMBS_UP = '👍'
    EMOJI_THUMBS_DOWN = '👎'
    EMOJI_HEART = '❤️'
    EMOJI_STAR = '⭐'
    EMOJI_FIRE = '🔥'
    EMOJI_CHECK = '✅'
    EMOJI_QUESTION = '❓'
    EMOJI_LIGHTBULB = '💡'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whiteboard = models.ForeignKey(
        Whiteboard,
        on_delete=models.CASCADE,
        related_name='emojis'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='whiteboard_emojis'
    )
    
    # Emoji
    emoji = models.CharField(max_length=10)
    
    # Position
    position_x = models.FloatField()
    position_y = models.FloatField()
    
    # Size
    size = models.IntegerField(default=32)
    
    # Animation (temporary emoji that fades)
    is_temporary = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Whiteboard Emoji'
        verbose_name_plural = 'Whiteboard Emojis'


class WhiteboardTemplate(models.Model):
    """
    Reusable whiteboard templates.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whiteboard_templates'
    )
    
    # Template info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    
    # Template data (full whiteboard state)
    template_data = models.JSONField(default=dict)
    
    # Preview
    thumbnail = models.ImageField(upload_to='whiteboard_templates/', null=True, blank=True)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    
    # Usage
    use_count = models.IntegerField(default=0)
    
    # Tags
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-use_count', 'name']
        verbose_name = 'Whiteboard Template'
        verbose_name_plural = 'Whiteboard Templates'
    
    def __str__(self):
        return self.name
