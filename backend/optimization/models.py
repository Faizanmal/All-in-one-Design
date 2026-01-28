from django.db import models
from django.conf import settings
import uuid


class ABTest(models.Model):
    """A/B Testing for designs"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ab_tests')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='ab_tests')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Test configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    goal = models.CharField(max_length=100)  # e.g., "click_rate", "conversion", "engagement"
    goal_description = models.TextField(blank=True)
    
    # Traffic allocation
    traffic_percentage = models.IntegerField(default=100)  # % of users in test
    
    # Duration
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Results
    winner_variant = models.ForeignKey('ABTestVariant', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_tests')
    confidence_level = models.FloatField(default=0)  # Statistical confidence
    
    # AI recommendations
    ai_recommendations = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'A/B Test'
        verbose_name_plural = 'A/B Tests'
    
    def __str__(self):
        return f"{self.name} ({self.status})"


class ABTestVariant(models.Model):
    """Variants within an A/B test"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ab_test = models.ForeignKey(ABTest, on_delete=models.CASCADE, related_name='variants')
    
    name = models.CharField(max_length=255)  # e.g., "Control", "Variant A"
    description = models.TextField(blank=True)
    
    # Design data
    design_data = models.JSONField(default=dict)
    screenshot = models.ImageField(upload_to='ab_test_variants/', null=True, blank=True)
    
    # Traffic weight
    weight = models.IntegerField(default=50)  # % of test traffic
    
    # Results
    impressions = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    engagement_score = models.FloatField(default=0)
    
    # Calculated metrics
    conversion_rate = models.FloatField(default=0)
    click_rate = models.FloatField(default=0)
    
    is_control = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['is_control', 'created_at']
    
    def __str__(self):
        return f"{self.ab_test.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if self.impressions > 0:
            self.conversion_rate = (self.conversions / self.impressions) * 100
            self.click_rate = (self.clicks / self.impressions) * 100
        super().save(*args, **kwargs)


class PerformanceAnalysis(models.Model):
    """Performance analysis results for designs"""
    ANALYSIS_TYPES = [
        ('load_time', 'Load Time'),
        ('accessibility', 'Accessibility'),
        ('seo', 'SEO'),
        ('mobile', 'Mobile Responsiveness'),
        ('cross_browser', 'Cross-Browser'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_analyses')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='performance_analyses')
    
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES)
    
    # Scores
    overall_score = models.FloatField(default=0)  # 0-100
    
    # Detailed results
    results = models.JSONField(default=dict)
    # Example: {"metrics": {...}, "issues": [...], "recommendations": [...]}
    
    # AI suggestions
    ai_suggestions = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Performance Analysis'
        verbose_name_plural = 'Performance Analyses'
    
    def __str__(self):
        return f"{self.project.name} - {self.analysis_type}"


class DeviceCompatibility(models.Model):
    """Cross-device compatibility analysis"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_compatibilities')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='device_compatibilities')
    
    # Device categories tested
    devices_tested = models.JSONField(default=list)
    # Example: ["iPhone 14", "iPad Pro", "Samsung Galaxy S23", "Desktop 1920x1080"]
    
    # Results per device
    device_results = models.JSONField(default=dict)
    # Example: {"iPhone 14": {"score": 95, "issues": [...]}, ...}
    
    # Screenshots
    screenshots = models.JSONField(default=dict)  # Device -> screenshot URL
    
    # Overall compatibility score
    overall_score = models.FloatField(default=0)
    
    # Issues found
    issues = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Device Compatibility'
        verbose_name_plural = 'Device Compatibilities'


class UserBehaviorPrediction(models.Model):
    """AI predictions for user behavior based on design"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='behavior_predictions')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='behavior_predictions')
    
    # Predictions
    attention_heatmap = models.JSONField(default=dict)  # Predicted eye-tracking
    click_predictions = models.JSONField(default=list)  # Likely click areas
    scroll_depth_prediction = models.FloatField(default=0)  # % expected to scroll
    
    # Engagement predictions
    predicted_engagement_score = models.FloatField(default=0)
    predicted_bounce_rate = models.FloatField(default=0)
    predicted_time_on_page = models.FloatField(default=0)  # seconds
    
    # Conversion predictions
    predicted_conversion_rate = models.FloatField(default=0)
    conversion_barriers = models.JSONField(default=list)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class SmartLayoutSuggestion(models.Model):
    """AI-powered layout suggestions based on content type"""
    CONTENT_TYPES = [
        ('landing_page', 'Landing Page'),
        ('blog', 'Blog/Article'),
        ('portfolio', 'Portfolio'),
        ('ecommerce', 'E-commerce'),
        ('dashboard', 'Dashboard'),
        ('form', 'Form/Survey'),
        ('presentation', 'Presentation'),
        ('social', 'Social Media'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='layout_suggestions')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='layout_suggestions', null=True, blank=True)
    
    # Input
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES)
    content_description = models.TextField(blank=True)
    target_audience = models.CharField(max_length=255, blank=True)
    brand_style = models.CharField(max_length=100, blank=True)
    
    # Generated suggestions
    suggestions = models.JSONField(default=list)
    # Example: [{"layout": {...}, "preview": "url", "score": 95, "reasoning": "..."}]
    
    # Selected suggestion
    selected_suggestion_index = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class OptimizationReport(models.Model):
    """Comprehensive optimization report"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='optimization_reports')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='optimization_reports')
    
    # Overall scores
    overall_score = models.FloatField(default=0)
    performance_score = models.FloatField(default=0)
    accessibility_score = models.FloatField(default=0)
    usability_score = models.FloatField(default=0)
    seo_score = models.FloatField(default=0)
    
    # Detailed analysis
    performance_analysis = models.JSONField(default=dict)
    accessibility_analysis = models.JSONField(default=dict)
    usability_analysis = models.JSONField(default=dict)
    seo_analysis = models.JSONField(default=dict)
    
    # Issues by severity
    critical_issues = models.JSONField(default=list)
    major_issues = models.JSONField(default=list)
    minor_issues = models.JSONField(default=list)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    quick_wins = models.JSONField(default=list)  # Easy fixes with high impact
    
    # Comparison with best practices
    industry_benchmark = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report for {self.project.name} - {self.created_at.date()}"
