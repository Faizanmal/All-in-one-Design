from django.db import models
from django.conf import settings
import uuid


class FontFamily(models.Model):
    """Font family with multiple weights/styles"""
    FONT_CATEGORIES = [
        ('sans-serif', 'Sans Serif'),
        ('serif', 'Serif'),
        ('display', 'Display'),
        ('handwriting', 'Handwriting'),
        ('monospace', 'Monospace'),
    ]
    
    LICENSE_TYPES = [
        ('google', 'Google Fonts'),
        ('adobe', 'Adobe Fonts'),
        ('custom', 'Custom Upload'),
        ('open_source', 'Open Source'),
        ('purchased', 'Purchased License'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fonts', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    category = models.CharField(max_length=50, choices=FONT_CATEGORIES)
    
    # Source
    source = models.CharField(max_length=50, choices=LICENSE_TYPES, default='custom')
    source_url = models.URLField(blank=True)
    google_font_id = models.CharField(max_length=255, blank=True)
    
    # Design attributes
    designer = models.CharField(max_length=255, blank=True)
    foundry = models.CharField(max_length=255, blank=True)
    
    # Classification
    tags = models.JSONField(default=list)
    languages_supported = models.JSONField(default=list)
    
    # License
    license_type = models.CharField(max_length=50, blank=True)
    license_text = models.TextField(blank=True)
    commercial_use = models.BooleanField(default=True)
    
    # Global or user-specific
    is_global = models.BooleanField(default=False)
    
    # Preview
    preview_text = models.CharField(max_length=255, default='The quick brown fox jumps')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Font Family'
        verbose_name_plural = 'Font Families'
    
    def __str__(self):
        return self.name


class FontVariant(models.Model):
    """Individual font variant (weight/style)"""
    FONT_WEIGHTS = [
        (100, 'Thin'),
        (200, 'Extra Light'),
        (300, 'Light'),
        (400, 'Regular'),
        (500, 'Medium'),
        (600, 'Semi Bold'),
        (700, 'Bold'),
        (800, 'Extra Bold'),
        (900, 'Black'),
    ]
    
    FONT_STYLES = [
        ('normal', 'Normal'),
        ('italic', 'Italic'),
        ('oblique', 'Oblique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(FontFamily, on_delete=models.CASCADE, related_name='variants')
    
    weight = models.IntegerField(choices=FONT_WEIGHTS, default=400)
    style = models.CharField(max_length=20, choices=FONT_STYLES, default='normal')
    
    # Font files
    woff2_file = models.FileField(upload_to='fonts/woff2/', null=True, blank=True)
    woff_file = models.FileField(upload_to='fonts/woff/', null=True, blank=True)
    ttf_file = models.FileField(upload_to='fonts/ttf/', null=True, blank=True)
    otf_file = models.FileField(upload_to='fonts/otf/', null=True, blank=True)
    
    # For web fonts (external)
    css_url = models.URLField(blank=True)
    
    class Meta:
        unique_together = ['family', 'weight', 'style']
        ordering = ['weight', 'style']
    
    def __str__(self):
        return f"{self.family.name} {self.get_weight_display()} {self.style}"


class FontCollection(models.Model):
    """Collections of fonts for projects"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='font_collections')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    fonts = models.ManyToManyField(FontFamily, related_name='collections')
    
    # Recommended pairings
    pairings = models.JSONField(default=list)
    # Example: [{"heading": "font_id", "body": "font_id"}]
    
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class IconSet(models.Model):
    """Icon sets/libraries"""
    ICON_STYLES = [
        ('outline', 'Outline'),
        ('filled', 'Filled'),
        ('duotone', 'Duotone'),
        ('colored', 'Colored'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='icon_sets', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    
    # Source
    source = models.CharField(max_length=255, blank=True)  # e.g., "Feather Icons", "Font Awesome"
    source_url = models.URLField(blank=True)
    version = models.CharField(max_length=50, blank=True)
    
    # Style
    style = models.CharField(max_length=20, choices=ICON_STYLES, default='outline')
    
    # Grid settings
    grid_size = models.IntegerField(default=24)  # e.g., 24x24
    stroke_width = models.FloatField(default=2.0)
    
    # License
    license_type = models.CharField(max_length=100, blank=True)
    commercial_use = models.BooleanField(default=True)
    
    # Counters
    icon_count = models.IntegerField(default=0)
    
    is_global = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Icon(models.Model):
    """Individual icons"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    icon_set = models.ForeignKey(IconSet, on_delete=models.CASCADE, related_name='icons')
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    
    # SVG data
    svg_content = models.TextField()
    
    # Alternate formats
    png_file = models.ImageField(upload_to='icons/png/', null=True, blank=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['icon_set', 'slug']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.icon_set.name} - {self.name}"


class AssetLibrary(models.Model):
    """User's asset libraries"""
    LIBRARY_TYPES = [
        ('images', 'Images'),
        ('illustrations', 'Illustrations'),
        ('photos', 'Photos'),
        ('graphics', 'Graphics'),
        ('templates', 'Templates'),
        ('mixed', 'Mixed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asset_libraries')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    library_type = models.CharField(max_length=20, choices=LIBRARY_TYPES, default='mixed')
    
    # Cover
    cover_image = models.ImageField(upload_to='library_covers/', null=True, blank=True)
    
    # Organization
    tags = models.JSONField(default=list)
    color = models.CharField(max_length=7, default='#6366f1')
    
    # Sharing
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='shared_libraries')
    
    # Stats
    asset_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Asset Library'
        verbose_name_plural = 'Asset Libraries'
    
    def __str__(self):
        return self.name


class LibraryAsset(models.Model):
    """Assets within a library"""
    ASSET_TYPES = [
        ('image', 'Image'),
        ('svg', 'SVG'),
        ('video', 'Video'),
        ('lottie', 'Lottie Animation'),
        ('template', 'Template'),
        ('component', 'Component'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    library = models.ForeignKey(AssetLibrary, on_delete=models.CASCADE, related_name='assets')
    
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    
    # File
    file = models.FileField(upload_to='library_assets/')
    thumbnail = models.ImageField(upload_to='library_thumbnails/', null=True, blank=True)
    
    # Metadata
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Colors
    dominant_colors = models.JSONField(default=list)
    
    # Organization
    tags = models.JSONField(default=list)
    folder = models.CharField(max_length=255, blank=True)
    
    # AI metadata
    ai_description = models.TextField(blank=True)
    ai_tags = models.JSONField(default=list)
    
    # Usage
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AssetVersion(models.Model):
    """Version history for assets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(LibraryAsset, on_delete=models.CASCADE, related_name='versions')
    
    version_number = models.IntegerField()
    file = models.FileField(upload_to='asset_versions/')
    
    # Changes
    change_description = models.TextField(blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='asset_versions_changed')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['asset', 'version_number']
        ordering = ['-version_number']
    
    def __str__(self):
        return f"{self.asset.name} v{self.version_number}"


class StockProvider(models.Model):
    """Stock image/video providers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    
    # API configuration
    api_base_url = models.URLField()
    api_key_required = models.BooleanField(default=True)
    
    # Capabilities
    supports_images = models.BooleanField(default=True)
    supports_videos = models.BooleanField(default=False)
    supports_vectors = models.BooleanField(default=False)
    supports_audio = models.BooleanField(default=False)
    
    # Attribution
    requires_attribution = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class StockSearch(models.Model):
    """Search history for stock assets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_searches')
    
    query = models.CharField(max_length=500)
    provider = models.ForeignKey(StockProvider, on_delete=models.CASCADE)
    
    # Filters used
    filters = models.JSONField(default=dict)
    
    # Results
    result_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class ColorPalette(models.Model):
    """Color palette collections"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='color_palettes')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Colors (list of hex values)
    colors = models.JSONField(default=list)
    # Example: ["#ff0000", "#00ff00", "#0000ff"]
    
    # Source
    source = models.CharField(max_length=100, blank=True)  # e.g., "Extracted from image", "Coolors", "Manual"
    source_image = models.ImageField(upload_to='palette_sources/', null=True, blank=True)
    
    # Tags
    tags = models.JSONField(default=list)
    
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class GradientPreset(models.Model):
    """Gradient presets"""
    GRADIENT_TYPES = [
        ('linear', 'Linear'),
        ('radial', 'Radial'),
        ('conic', 'Conic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gradients', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    gradient_type = models.CharField(max_length=20, choices=GRADIENT_TYPES, default='linear')
    
    # Gradient definition
    stops = models.JSONField(default=list)
    # Example: [{"color": "#ff0000", "position": 0}, {"color": "#0000ff", "position": 100}]
    
    angle = models.IntegerField(default=90)  # For linear gradients
    
    # CSS output
    css_value = models.TextField(blank=True)
    
    is_global = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
