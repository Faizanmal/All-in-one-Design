"""
Design QA & Linting System

Automated design consistency checks, accessibility validation,
and design system compliance verification.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class LintRuleSet(models.Model):
    """
    A collection of lint rules that can be applied to designs.
    """
    
    RULESET_TYPE_SYSTEM = 'system'
    RULESET_TYPE_CUSTOM = 'custom'
    RULESET_TYPE_TEAM = 'team'
    TYPE_CHOICES = [
        (RULESET_TYPE_SYSTEM, 'System Default'),
        (RULESET_TYPE_CUSTOM, 'Custom'),
        (RULESET_TYPE_TEAM, 'Team'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lint_rule_sets'
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lint_rule_sets'
    )
    design_system = models.ForeignKey(
        'design_systems.DesignSystem',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lint_rule_sets'
    )
    
    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ruleset_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=RULESET_TYPE_CUSTOM
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    
    # Configuration
    strict_mode = models.BooleanField(default=False)  # Treat warnings as errors
    auto_fix_enabled = models.BooleanField(default=True)
    
    # Severity thresholds
    error_threshold = models.IntegerField(default=0)  # Max errors before failing
    warning_threshold = models.IntegerField(default=10)  # Max warnings before failing
    
    # Version
    version = models.CharField(max_length=50, default='1.0.0')
    
    # Icon and color for UI
    icon = models.CharField(max_length=50, default='check-circle')
    color = models.CharField(max_length=50, default='#6366f1')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Lint Rule Set'
        verbose_name_plural = 'Lint Rule Sets'
    
    def __str__(self):
        return f"{self.name} ({self.ruleset_type})"


class LintRule(models.Model):
    """
    Individual lint rule for checking design consistency.
    """
    
    SEVERITY_ERROR = 'error'
    SEVERITY_WARNING = 'warning'
    SEVERITY_INFO = 'info'
    SEVERITY_HINT = 'hint'
    SEVERITY_CHOICES = [
        (SEVERITY_ERROR, 'Error'),
        (SEVERITY_WARNING, 'Warning'),
        (SEVERITY_INFO, 'Info'),
        (SEVERITY_HINT, 'Hint'),
    ]
    
    CATEGORY_SPACING = 'spacing'
    CATEGORY_ALIGNMENT = 'alignment'
    CATEGORY_COLOR = 'color'
    CATEGORY_TYPOGRAPHY = 'typography'
    CATEGORY_ACCESSIBILITY = 'accessibility'
    CATEGORY_NAMING = 'naming'
    CATEGORY_STRUCTURE = 'structure'
    CATEGORY_COMPONENTS = 'components'
    CATEGORY_ASSETS = 'assets'
    CATEGORY_PERFORMANCE = 'performance'
    CATEGORY_CHOICES = [
        (CATEGORY_SPACING, 'Spacing'),
        (CATEGORY_ALIGNMENT, 'Alignment'),
        (CATEGORY_COLOR, 'Color'),
        (CATEGORY_TYPOGRAPHY, 'Typography'),
        (CATEGORY_ACCESSIBILITY, 'Accessibility'),
        (CATEGORY_NAMING, 'Naming'),
        (CATEGORY_STRUCTURE, 'Structure'),
        (CATEGORY_COMPONENTS, 'Components'),
        (CATEGORY_ASSETS, 'Assets'),
        (CATEGORY_PERFORMANCE, 'Performance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_set = models.ForeignKey(
        LintRuleSet,
        on_delete=models.CASCADE,
        related_name='rules'
    )
    
    # Rule identification
    code = models.CharField(max_length=50)  # e.g., "spacing-001"
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Categorization
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default=SEVERITY_WARNING
    )
    
    # Rule configuration
    enabled = models.BooleanField(default=True)
    auto_fixable = models.BooleanField(default=False)
    
    # Rule logic (stored as JSON)
    rule_config = models.JSONField(default=dict)
    # Examples:
    # spacing: {"allowed_values": [4, 8, 12, 16, 24, 32], "tolerance": 1}
    # color: {"require_from_palette": true, "palette_id": "..."}
    # alignment: {"snap_threshold": 2}
    
    # Fix configuration
    fix_config = models.JSONField(default=dict)
    # {"action": "snap_to_grid", "grid_size": 8}
    
    # Documentation
    documentation_url = models.URLField(blank=True)
    examples = models.JSONField(default=list)  # Example violations and fixes
    
    # Tags
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'code']
        verbose_name = 'Lint Rule'
        verbose_name_plural = 'Lint Rules'
        unique_together = ['rule_set', 'code']
    
    def __str__(self):
        return f"[{self.code}] {self.name}"


class DesignLintReport(models.Model):
    """
    Results of a lint run on a design project.
    """
    
    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='lint_reports'
    )
    rule_set = models.ForeignKey(
        LintRuleSet,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports'
    )
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='triggered_lint_reports'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    
    # Summary stats
    total_issues = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    warning_count = models.IntegerField(default=0)
    info_count = models.IntegerField(default=0)
    
    # Fixed stats
    auto_fixed_count = models.IntegerField(default=0)
    manually_fixed_count = models.IntegerField(default=0)
    ignored_count = models.IntegerField(default=0)
    
    # Elements checked
    elements_checked = models.IntegerField(default=0)
    layers_checked = models.IntegerField(default=0)
    components_checked = models.IntegerField(default=0)
    
    # Pass/fail
    passed = models.BooleanField(default=False)
    
    # Execution time
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    
    # Score (0-100)
    health_score = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Diff from last report
    improvement = models.IntegerField(default=0)  # Positive = fewer issues
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Design Lint Report'
        verbose_name_plural = 'Design Lint Reports'
    
    def __str__(self):
        return f"Lint Report for {self.project.name} ({self.created_at})"


class LintIssue(models.Model):
    """
    Individual issue found during linting.
    """
    
    STATUS_OPEN = 'open'
    STATUS_FIXED = 'fixed'
    STATUS_IGNORED = 'ignored'
    STATUS_WONT_FIX = 'wont_fix'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_FIXED, 'Fixed'),
        (STATUS_IGNORED, 'Ignored'),
        (STATUS_WONT_FIX, "Won't Fix"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        DesignLintReport,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    rule = models.ForeignKey(
        LintRule,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issues'
    )
    
    # Issue details
    message = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=LintRule.SEVERITY_CHOICES
    )
    
    # Affected element
    element_id = models.CharField(max_length=100)
    element_type = models.CharField(max_length=50)
    element_name = models.CharField(max_length=255, blank=True)
    element_path = models.CharField(max_length=500, blank=True)  # Hierarchy path
    
    # Location on canvas
    position_x = models.FloatField(null=True, blank=True)
    position_y = models.FloatField(null=True, blank=True)
    
    # Property with issue
    property_name = models.CharField(max_length=100, blank=True)
    current_value = models.JSONField(null=True, blank=True)
    expected_value = models.JSONField(null=True, blank=True)
    suggested_fix = models.JSONField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN
    )
    
    # Auto-fix available
    auto_fixable = models.BooleanField(default=False)
    fix_applied = models.BooleanField(default=False)
    
    # Resolution
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_lint_issues'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['severity', 'element_type', 'element_name']
        verbose_name = 'Lint Issue'
        verbose_name_plural = 'Lint Issues'
    
    def __str__(self):
        return f"[{self.severity}] {self.message[:50]}"


class AccessibilityCheck(models.Model):
    """
    Accessibility-specific checks based on WCAG guidelines.
    """
    
    WCAG_LEVELS = [
        ('A', 'Level A'),
        ('AA', 'Level AA'),
        ('AAA', 'Level AAA'),
    ]
    
    WCAG_PRINCIPLES = [
        ('perceivable', 'Perceivable'),
        ('operable', 'Operable'),
        ('understandable', 'Understandable'),
        ('robust', 'Robust'),
    ]
    
    CHECK_TYPES = [
        ('color_contrast', 'Color Contrast'),
        ('text_size', 'Text Size'),
        ('alt_text', 'Alt Text'),
        ('focus_indicator', 'Focus Indicator'),
        ('touch_target', 'Touch Target Size'),
        ('heading_hierarchy', 'Heading Hierarchy'),
        ('link_purpose', 'Link Purpose'),
        ('form_labels', 'Form Labels'),
        ('error_identification', 'Error Identification'),
        ('language', 'Language'),
        ('consistent_navigation', 'Consistent Navigation'),
        ('timing', 'Timing Adjustable'),
        ('motion', 'Motion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_set = models.ForeignKey(
        LintRuleSet,
        on_delete=models.CASCADE,
        related_name='accessibility_checks'
    )
    
    # Check identification
    code = models.CharField(max_length=50)  # e.g., "wcag-1.4.3"
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # WCAG mapping
    wcag_criterion = models.CharField(max_length=50)  # e.g., "1.4.3"
    wcag_level = models.CharField(max_length=5, choices=WCAG_LEVELS)
    wcag_principle = models.CharField(max_length=20, choices=WCAG_PRINCIPLES)
    
    # Check type
    check_type = models.CharField(max_length=30, choices=CHECK_TYPES)
    
    # Configuration
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    # color_contrast: {"min_ratio_normal": 4.5, "min_ratio_large": 3.0}
    # text_size: {"min_size": 12}
    # touch_target: {"min_width": 44, "min_height": 44}
    
    # Impact
    impact = models.CharField(max_length=20, default='serious')  # minor, moderate, serious, critical
    
    # Documentation
    how_to_fix = models.TextField(blank=True)
    documentation_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['wcag_criterion']
        verbose_name = 'Accessibility Check'
        verbose_name_plural = 'Accessibility Checks'
    
    def __str__(self):
        return f"[{self.wcag_criterion}] {self.name}"


class AccessibilityReport(models.Model):
    """
    Accessibility audit report for a design.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='accessibility_reports'
    )
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='accessibility_reports'
    )
    
    # WCAG compliance level checked
    wcag_level = models.CharField(max_length=5, choices=AccessibilityCheck.WCAG_LEVELS, default='AA')
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=DesignLintReport.STATUS_CHOICES,
        default=DesignLintReport.STATUS_PENDING
    )
    
    # Results summary
    total_elements = models.IntegerField(default=0)
    passed_checks = models.IntegerField(default=0)
    failed_checks = models.IntegerField(default=0)
    
    # By severity
    critical_issues = models.IntegerField(default=0)
    serious_issues = models.IntegerField(default=0)
    moderate_issues = models.IntegerField(default=0)
    minor_issues = models.IntegerField(default=0)
    
    # By principle
    perceivable_issues = models.IntegerField(default=0)
    operable_issues = models.IntegerField(default=0)
    understandable_issues = models.IntegerField(default=0)
    robust_issues = models.IntegerField(default=0)
    
    # Compliance score
    compliance_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Is compliant at the checked level
    is_compliant = models.BooleanField(default=False)
    
    # Execution
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Accessibility Report'
        verbose_name_plural = 'Accessibility Reports'
    
    def __str__(self):
        return f"A11y Report for {self.project.name} (WCAG {self.wcag_level})"


class AccessibilityIssue(models.Model):
    """
    Individual accessibility issue.
    """
    
    IMPACT_CHOICES = [
        ('critical', 'Critical'),
        ('serious', 'Serious'),
        ('moderate', 'Moderate'),
        ('minor', 'Minor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        AccessibilityReport,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    accessibility_check = models.ForeignKey(
        AccessibilityCheck,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issues'
    )
    
    # Issue details
    message = models.TextField()
    impact = models.CharField(max_length=20, choices=IMPACT_CHOICES)
    
    # Affected element
    element_id = models.CharField(max_length=100)
    element_type = models.CharField(max_length=50)
    element_name = models.CharField(max_length=255, blank=True)
    
    # Specific failure data
    failure_summary = models.TextField(blank=True)
    failure_data = models.JSONField(default=dict)
    # color_contrast: {"foreground": "#666", "background": "#fff", "ratio": 4.2, "required": 4.5}
    
    # Fix suggestion
    fix_suggestion = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=LintIssue.STATUS_CHOICES,
        default=LintIssue.STATUS_OPEN
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['impact', 'element_type']
        verbose_name = 'Accessibility Issue'
        verbose_name_plural = 'Accessibility Issues'
    
    def __str__(self):
        return f"[{self.impact}] {self.message[:50]}"


class StyleUsageReport(models.Model):
    """
    Report on style usage and potential cleanup opportunities.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='style_usage_reports'
    )
    
    # Analysis results
    total_styles = models.IntegerField(default=0)
    used_styles = models.IntegerField(default=0)
    unused_styles = models.IntegerField(default=0)
    
    # By type
    unused_colors = models.JSONField(default=list)
    unused_text_styles = models.JSONField(default=list)
    unused_effects = models.JSONField(default=list)
    unused_components = models.JSONField(default=list)
    
    # Duplicate detection
    duplicate_colors = models.JSONField(default=list)
    similar_colors = models.JSONField(default=list)  # Colors that are nearly identical
    duplicate_text_styles = models.JSONField(default=list)
    
    # Inconsistencies
    off_palette_colors = models.JSONField(default=list)  # Colors not from design system
    non_standard_spacing = models.JSONField(default=list)  # Spacing not on the grid
    orphaned_layers = models.JSONField(default=list)  # Layers outside frames
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    potential_savings = models.JSONField(default=dict)  # Estimated cleanup impact
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Style Usage Report'
        verbose_name_plural = 'Style Usage Reports'
    
    def __str__(self):
        return f"Style Usage Report for {self.project.name}"


class LintIgnoreRule(models.Model):
    """
    Rules for ignoring specific lint issues.
    """
    
    IGNORE_SCOPE_FILE = 'file'
    IGNORE_SCOPE_ELEMENT = 'element'
    IGNORE_SCOPE_RULE = 'rule'
    IGNORE_SCOPE_PROJECT = 'project'
    SCOPE_CHOICES = [
        (IGNORE_SCOPE_FILE, 'File'),
        (IGNORE_SCOPE_ELEMENT, 'Element'),
        (IGNORE_SCOPE_RULE, 'Rule'),
        (IGNORE_SCOPE_PROJECT, 'Project'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='lint_ignore_rules'
    )
    
    # What to ignore
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    rule_code = models.CharField(max_length=50, blank=True)  # Specific rule to ignore
    element_id = models.CharField(max_length=100, blank=True)  # Specific element
    
    # Reason for ignoring
    reason = models.TextField()
    
    # Who created this ignore rule
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_ignore_rules'
    )
    
    # Expiration (optional)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Is active
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lint Ignore Rule'
        verbose_name_plural = 'Lint Ignore Rules'
    
    def __str__(self):
        return f"Ignore {self.rule_code or 'all'} on {self.scope}"
