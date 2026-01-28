"""
Enhanced Accessibility Testing Models

Color blindness simulation, screen reader preview, focus order testing.
"""

from django.db import models
from django.conf import settings
import uuid


class AccessibilityTest(models.Model):
    """Comprehensive accessibility test for a design."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    WCAG_LEVELS = [
        ('A', 'Level A'),
        ('AA', 'Level AA'),
        ('AAA', 'Level AAA'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accessibility_tests')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='accessibility_tests')
    
    # Test configuration
    target_level = models.CharField(max_length=3, choices=WCAG_LEVELS, default='AA')
    test_categories = models.JSONField(default=list)  # ["contrast", "focus", "screen_reader", "color_blindness"]
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.FloatField(default=0)
    
    # Results summary
    passed = models.BooleanField(null=True, blank=True)
    total_issues = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)
    warnings = models.IntegerField(default=0)
    notices = models.IntegerField(default=0)
    
    # Detailed results
    results = models.JSONField(default=dict)
    
    # Score (0-100)
    accessibility_score = models.FloatField(null=True, blank=True)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class AccessibilityIssue(models.Model):
    """Individual accessibility issue found."""
    
    SEVERITY_CHOICES = [
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('notice', 'Notice'),
    ]
    
    CATEGORY_CHOICES = [
        ('contrast', 'Color Contrast'),
        ('focus', 'Focus Order'),
        ('keyboard', 'Keyboard Navigation'),
        ('screen_reader', 'Screen Reader'),
        ('alt_text', 'Alternative Text'),
        ('semantics', 'Semantic Structure'),
        ('motion', 'Motion & Animation'),
        ('color_alone', 'Color as Only Indicator'),
        ('text_size', 'Text Size'),
        ('touch_target', 'Touch Target Size'),
        ('timing', 'Timing'),
        ('language', 'Language'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(AccessibilityTest, on_delete=models.CASCADE, related_name='issues')
    
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # WCAG reference
    wcag_criterion = models.CharField(max_length=20)  # e.g., "1.4.3"
    wcag_level = models.CharField(max_length=3)
    
    # Issue details
    title = models.CharField(max_length=255)
    description = models.TextField()
    how_to_fix = models.TextField(blank=True)
    
    # Element reference
    element_id = models.CharField(max_length=100, blank=True)
    element_type = models.CharField(max_length=50, blank=True)
    element_name = models.CharField(max_length=255, blank=True)
    
    # Current values
    current_value = models.JSONField(default=dict)
    
    # Suggested fix
    suggested_fix = models.JSONField(default=dict)
    auto_fixable = models.BooleanField(default=False)
    
    # Fix status
    is_fixed = models.BooleanField(default=False)
    ignored = models.BooleanField(default=False)
    ignore_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['severity', 'category']


class ColorBlindnessSimulation(models.Model):
    """Color blindness simulation results."""
    
    SIMULATION_TYPES = [
        ('protanopia', 'Protanopia (No Red)'),
        ('deuteranopia', 'Deuteranopia (No Green)'),
        ('tritanopia', 'Tritanopia (No Blue)'),
        ('protanomaly', 'Protanomaly (Weak Red)'),
        ('deuteranomaly', 'Deuteranomaly (Weak Green)'),
        ('tritanomaly', 'Tritanomaly (Weak Blue)'),
        ('achromatopsia', 'Achromatopsia (Monochrome)'),
        ('achromatomaly', 'Achromatomaly (Weak Color)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='color_blindness_simulations')
    
    simulation_type = models.CharField(max_length=20, choices=SIMULATION_TYPES)
    
    # Frame/element scope
    frame_id = models.CharField(max_length=100, blank=True)
    
    # Original and simulated images
    original_image = models.ImageField(upload_to='accessibility/original/', null=True, blank=True)
    simulated_image = models.ImageField(upload_to='accessibility/simulated/', null=True, blank=True)
    
    # Color mapping (original -> simulated)
    color_mapping = models.JSONField(default=dict)
    
    # Issues found (e.g., colors that become indistinguishable)
    issues = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class ScreenReaderPreview(models.Model):
    """Screen reader content preview."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='screen_reader_previews')
    
    frame_id = models.CharField(max_length=100, blank=True)
    
    # Reading order content
    content = models.JSONField(default=list)
    # [
    #   {"type": "heading", "level": 1, "text": "Welcome", "element_id": "h1_1"},
    #   {"type": "text", "text": "This is a paragraph", "element_id": "p_1"},
    #   {"type": "link", "text": "Click here", "href": "#", "element_id": "a_1"},
    #   {"type": "image", "alt": "Logo", "element_id": "img_1"},
    #   {"type": "button", "text": "Submit", "element_id": "btn_1"},
    # ]
    
    # Generated speech text
    speech_text = models.TextField(blank=True)
    
    # Issues with reading order
    reading_order_issues = models.JSONField(default=list)
    
    # Missing alternative text
    missing_alt_text = models.JSONField(default=list)
    
    # ARIA labels
    aria_analysis = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class FocusOrderTest(models.Model):
    """Focus order testing results."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='focus_order_tests')
    
    frame_id = models.CharField(max_length=100, blank=True)
    
    # Focus order sequence
    focus_order = models.JSONField(default=list)
    # [
    #   {"order": 1, "element_id": "nav_1", "type": "nav", "name": "Navigation"},
    #   {"order": 2, "element_id": "btn_1", "type": "button", "name": "Menu"},
    # ]
    
    # Detected issues
    issues = models.JSONField(default=list)
    # [
    #   {"type": "skip_nav_missing", "description": "No skip navigation link"},
    #   {"type": "trap", "element_id": "modal_1", "description": "Focus trap detected"},
    # ]
    
    # Focus indicators
    focus_indicator_issues = models.JSONField(default=list)
    
    # Tab order visualization
    visualization_data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class ContrastCheck(models.Model):
    """Individual contrast check result."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(AccessibilityTest, on_delete=models.CASCADE, related_name='contrast_checks', null=True, blank=True)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='contrast_checks')
    
    # Element info
    element_id = models.CharField(max_length=100)
    element_type = models.CharField(max_length=50)
    element_name = models.CharField(max_length=255, blank=True)
    
    # Colors
    foreground_color = models.CharField(max_length=20)
    background_color = models.CharField(max_length=20)
    
    # Contrast ratio
    contrast_ratio = models.FloatField()
    
    # Text size
    font_size = models.FloatField(null=True, blank=True)
    is_large_text = models.BooleanField(default=False)
    is_bold = models.BooleanField(default=False)
    
    # WCAG compliance
    passes_aa = models.BooleanField(default=False)
    passes_aaa = models.BooleanField(default=False)
    
    # Suggested colors
    suggested_foreground = models.CharField(max_length=20, blank=True)
    suggested_background = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['contrast_ratio']


class AccessibilityReport(models.Model):
    """Generated accessibility report."""
    
    REPORT_FORMATS = [
        ('html', 'HTML Report'),
        ('pdf', 'PDF Report'),
        ('json', 'JSON Data'),
        ('csv', 'CSV Export'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(AccessibilityTest, on_delete=models.CASCADE, related_name='reports')
    
    format = models.CharField(max_length=10, choices=REPORT_FORMATS)
    
    # Report file
    file = models.FileField(upload_to='accessibility_reports/', null=True, blank=True)
    
    # Include options
    include_summary = models.BooleanField(default=True)
    include_issues = models.BooleanField(default=True)
    include_screenshots = models.BooleanField(default=True)
    include_recommendations = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class AccessibilityGuideline(models.Model):
    """WCAG guideline reference."""
    
    id = models.CharField(max_length=20, primary_key=True)  # e.g., "1.4.3"
    
    principle = models.CharField(max_length=100)  # Perceivable, Operable, etc.
    guideline = models.CharField(max_length=255)
    criterion = models.CharField(max_length=255)
    level = models.CharField(max_length=3)  # A, AA, AAA
    
    description = models.TextField()
    understanding_url = models.URLField(blank=True)
    how_to_meet_url = models.URLField(blank=True)
    
    # Techniques
    sufficient_techniques = models.JSONField(default=list)
    advisory_techniques = models.JSONField(default=list)
    failures = models.JSONField(default=list)
    
    class Meta:
        ordering = ['id']
