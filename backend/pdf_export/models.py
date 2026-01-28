from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class PDFExportPreset(models.Model):
    """Saved PDF export presets"""
    PAPER_SIZES = (
        ('letter', 'Letter (8.5 x 11 in)'),
        ('legal', 'Legal (8.5 x 14 in)'),
        ('tabloid', 'Tabloid (11 x 17 in)'),
        ('a3', 'A3 (297 x 420 mm)'),
        ('a4', 'A4 (210 x 297 mm)'),
        ('a5', 'A5 (148 x 210 mm)'),
        ('custom', 'Custom Size'),
    )
    
    COLOR_MODES = (
        ('rgb', 'RGB (Screen)'),
        ('cmyk', 'CMYK (Print)'),
        ('grayscale', 'Grayscale'),
    )
    
    PDF_STANDARDS = (
        ('pdf_1_7', 'PDF 1.7'),
        ('pdf_2_0', 'PDF 2.0'),
        ('pdf_a_1b', 'PDF/A-1b (Archival)'),
        ('pdf_a_2b', 'PDF/A-2b (Archival)'),
        ('pdf_x_1a', 'PDF/X-1a (Print)'),
        ('pdf_x_3', 'PDF/X-3 (Print)'),
        ('pdf_x_4', 'PDF/X-4 (Print)'),
    )
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_presets')
    
    # Basic info
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    
    # Paper settings
    paper_size = models.CharField(max_length=20, choices=PAPER_SIZES, default='letter')
    custom_width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # in mm
    custom_height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # in mm
    orientation = models.CharField(max_length=20, default='portrait')  # portrait/landscape
    
    # Color settings
    color_mode = models.CharField(max_length=20, choices=COLOR_MODES, default='rgb')
    icc_profile = models.CharField(max_length=100, blank=True)  # Color profile
    
    # Bleed settings
    bleed_enabled = models.BooleanField(default=False)
    bleed_top = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('3.00'))  # in mm
    bleed_bottom = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('3.00'))
    bleed_left = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('3.00'))
    bleed_right = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('3.00'))
    
    # Marks
    crop_marks = models.BooleanField(default=False)
    bleed_marks = models.BooleanField(default=False)
    registration_marks = models.BooleanField(default=False)
    color_bars = models.BooleanField(default=False)
    page_info = models.BooleanField(default=False)
    
    mark_offset = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('5.00'))  # in mm
    mark_weight = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.25'))  # in pt
    
    # Output settings
    pdf_standard = models.CharField(max_length=20, choices=PDF_STANDARDS, default='pdf_1_7')
    quality = models.IntegerField(default=300, validators=[MinValueValidator(72), MaxValueValidator(600)])  # DPI
    compress_images = models.BooleanField(default=True)
    image_quality = models.IntegerField(default=85, validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    # Font settings
    embed_fonts = models.BooleanField(default=True)
    subset_fonts = models.BooleanField(default=True)
    
    # Security
    password_protect = models.BooleanField(default=False)
    allow_printing = models.BooleanField(default=True)
    allow_copying = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PDFExport(models.Model):
    """PDF export jobs"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_export_jobs')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='pdf_export_jobs')
    preset = models.ForeignKey(PDFExportPreset, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Pages
    pages = models.JSONField(default=list)  # List of page IDs or 'all'
    page_range = models.CharField(max_length=100, blank=True)  # e.g., "1-5, 8, 10-12"
    
    # Export settings (overrides preset if provided)
    export_settings = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    error_message = models.TextField(blank=True)
    
    # Output
    file_url = models.URLField(blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    page_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PDF Export'
        verbose_name_plural = 'PDF Exports'
    
    def __str__(self):
        return f"PDF Export for {self.project.name}"


class PrintProfile(models.Model):
    """Pre-defined print profiles for common use cases"""
    PROFILE_TYPES = (
        ('digital', 'Digital Printing'),
        ('offset', 'Offset Printing'),
        ('large_format', 'Large Format'),
        ('newspaper', 'Newspaper'),
        ('magazine', 'Magazine'),
        ('packaging', 'Packaging'),
    )
    
    name = models.CharField(max_length=100)
    profile_type = models.CharField(max_length=20, choices=PROFILE_TYPES)
    description = models.TextField(blank=True)
    
    # Recommended settings
    recommended_dpi = models.IntegerField(default=300)
    recommended_color_mode = models.CharField(max_length=20, default='cmyk')
    recommended_bleed = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('3.00'))
    
    # PDF standard
    pdf_standard = models.CharField(max_length=20, default='pdf_x_4')
    
    # ICC profile
    icc_profile = models.CharField(max_length=100, blank=True)
    icc_profile_url = models.URLField(blank=True)
    
    # Additional settings
    settings = models.JSONField(default=dict)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SpreadView(models.Model):
    """Multi-page spread configurations"""
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='spreads')
    
    name = models.CharField(max_length=100)
    
    # Spread type
    spread_type = models.CharField(max_length=20, default='2up')  # 2up, 3up, 4up, custom
    
    # Pages in spread (ordered)
    pages = models.JSONField(default=list)  # [{'page_id': 1, 'position': 'left'}, ...]
    
    # Layout settings
    gutter = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))  # mm between pages
    spine_width = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))  # for booklets
    
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name


class ImpositionLayout(models.Model):
    """Imposition layouts for professional printing"""
    IMPOSITION_TYPES = (
        ('saddle_stitch', 'Saddle Stitch'),
        ('perfect_bind', 'Perfect Binding'),
        ('gang_up', 'Gang-Up / N-Up'),
        ('step_repeat', 'Step & Repeat'),
        ('booklet', 'Booklet'),
        ('folding', 'Folding'),
    )
    
    name = models.CharField(max_length=100)
    imposition_type = models.CharField(max_length=20, choices=IMPOSITION_TYPES)
    description = models.TextField(blank=True)
    
    # Sheet settings
    sheet_width = models.DecimalField(max_digits=8, decimal_places=2)  # mm
    sheet_height = models.DecimalField(max_digits=8, decimal_places=2)  # mm
    
    # Layout
    columns = models.IntegerField(default=2)
    rows = models.IntegerField(default=2)
    
    # Margins
    margin_top = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('10.00'))
    margin_bottom = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('10.00'))
    margin_left = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('10.00'))
    margin_right = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('10.00'))
    
    # Gaps
    horizontal_gap = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    vertical_gap = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    
    # Page ordering
    page_ordering = models.JSONField(default=list)  # Custom page order for imposition
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PDFTemplate(models.Model):
    """Templates for PDF generation (headers, footers, etc.)"""
    name = models.CharField(max_length=100)
    
    # Header
    header_enabled = models.BooleanField(default=False)
    header_content = models.JSONField(default=dict)  # {left: '', center: '', right: ''}
    header_height = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('15.00'))  # mm
    
    # Footer
    footer_enabled = models.BooleanField(default=False)
    footer_content = models.JSONField(default=dict)
    footer_height = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('15.00'))  # mm
    
    # Page numbers
    page_numbers = models.BooleanField(default=True)
    page_number_position = models.CharField(max_length=20, default='bottom_center')
    page_number_format = models.CharField(max_length=50, default='{page} of {total}')
    start_page_number = models.IntegerField(default=1)
    
    # Watermark
    watermark_enabled = models.BooleanField(default=False)
    watermark_text = models.CharField(max_length=255, blank=True)
    watermark_image = models.URLField(blank=True)
    watermark_opacity = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.30'))
    
    # Background
    background_color = models.CharField(max_length=20, blank=True)
    background_image = models.URLField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_templates')
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
