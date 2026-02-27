"""
AI Usage Quota Models

Models for tracking AI usage quotas, records, and budget management.
"""
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta


class AIUsageQuota(models.Model):
    """
    Monthly AI usage quota tracking.
    Tracks requests, tokens, image generations, and costs.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_quotas'
    )
    
    # Period tracking
    period_start = models.DateField(
        help_text="First day of the billing period"
    )
    period_end = models.DateField(
        help_text="Last day of the billing period"
    )
    
    # Usage counters
    ai_requests_used = models.IntegerField(default=0)
    ai_tokens_used = models.BigIntegerField(default=0)
    image_generations_used = models.IntegerField(default=0)
    
    # Limits
    ai_requests_limit = models.IntegerField(
        default=10,
        help_text="Max AI requests per period, -1 for unlimited"
    )
    ai_tokens_limit = models.BigIntegerField(
        default=10000,
        help_text="Max tokens per period, -1 for unlimited"
    )
    image_generations_limit = models.IntegerField(
        default=3,
        help_text="Max image generations per period, -1 for unlimited"
    )
    
    # Budget tracking
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0')
    )
    budget_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('10.00'),
        help_text="Budget limit in USD, 0 for no limit"
    )
    
    # Success tracking
    successful_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_start']
        unique_together = ['user', 'period_start']
        indexes = [
            models.Index(fields=['user', 'period_start']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.period_start.strftime('%Y-%m')}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate period_end if not set
        if not self.period_end:
            # Get last day of the month
            next_month = self.period_start.replace(day=28) + timedelta(days=4)
            self.period_end = next_month - timedelta(days=next_month.day)
        super().save(*args, **kwargs)
    
    @property
    def requests_remaining(self) -> int:
        """Get remaining AI requests."""
        if self.ai_requests_limit == -1:
            return -1  # Unlimited
        return max(0, self.ai_requests_limit - self.ai_requests_used)
    
    @property
    def tokens_remaining(self) -> int:
        """Get remaining tokens."""
        if self.ai_tokens_limit == -1:
            return -1  # Unlimited
        return max(0, self.ai_tokens_limit - self.ai_tokens_used)
    
    @property
    def budget_remaining(self) -> Decimal:
        """Get remaining budget."""
        if self.budget_limit == 0:
            return Decimal('-1')  # No limit
        return max(Decimal('0'), self.budget_limit - self.total_cost)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.successful_requests + self.failed_requests
        if total == 0:
            return 100.0
        return (self.successful_requests / total) * 100
    
    @property
    def is_request_limit_reached(self) -> bool:
        """Check if request limit is reached."""
        return self.ai_requests_limit > 0 and self.ai_requests_used >= self.ai_requests_limit
    
    @property
    def is_budget_exceeded(self) -> bool:
        """Check if budget is exceeded."""
        return self.budget_limit > 0 and self.total_cost >= self.budget_limit


class AIUsageRecord(models.Model):
    """
    Individual AI usage record for detailed tracking and analytics.
    """
    REQUEST_TYPES = [
        ('layout_generation', 'Layout Generation'),
        ('logo_generation', 'Logo Generation'),
        ('color_palette', 'Color Palette'),
        ('font_suggestion', 'Font Suggestion'),
        ('design_refinement', 'Design Refinement'),
        ('image_generation', 'Image Generation'),
        ('design_critique', 'Design Critique'),
        ('typography_suggestion', 'Typography Suggestion'),
        ('layout_optimization', 'Layout Optimization'),
        ('trend_analysis', 'Trend Analysis'),
        ('improvement_suggestions', 'Improvement Suggestions'),
        ('image_to_design', 'Image to Design'),
        ('style_transfer', 'Style Transfer'),
        ('voice_to_design', 'Voice to Design'),
        ('accessibility_check', 'Accessibility Check'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_usage_records'
    )
    quota = models.ForeignKey(
        AIUsageQuota,
        on_delete=models.CASCADE,
        related_name='records',
        null=True,
        blank=True
    )
    
    # Request details
    request_type = models.CharField(
        max_length=50,
        choices=REQUEST_TYPES
    )
    model = models.CharField(
        max_length=50,
        help_text="AI model used (e.g., gpt-4-turbo, dall-e-3)"
    )
    
    # Token usage
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    images_generated = models.IntegerField(default=0)
    
    # Cost
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0')
    )
    
    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Performance metrics
    latency_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Request latency in milliseconds"
    )
    
    # Context
    project_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Related project ID if applicable"
    )
    prompt_preview = models.CharField(
        max_length=200,
        blank=True,
        help_text="First 200 chars of prompt for reference"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the request"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['request_type', '-created_at']),
            models.Index(fields=['model', '-created_at']),
            models.Index(fields=['success', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.request_type} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return self.input_tokens + self.output_tokens


class BudgetAlert(models.Model):
    """
    User-configured budget alerts.
    """
    ALERT_TYPES = [
        ('threshold', 'Usage Threshold'),
        ('daily_limit', 'Daily Spending Limit'),
        ('weekly_limit', 'Weekly Spending Limit'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='budget_alerts'
    )
    
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES
    )
    
    # Threshold settings
    threshold_percent = models.IntegerField(
        null=True,
        blank=True,
        help_text="Alert when usage reaches this percentage (1-100)"
    )
    spending_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Spending limit in USD"
    )
    
    # Notification settings
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['threshold_percent', 'spending_limit']
    
    def __str__(self):
        if self.alert_type == 'threshold':
            return f"{self.user.username} - Alert at {self.threshold_percent}%"
        return f"{self.user.username} - {self.get_alert_type_display()}: ${self.spending_limit}"


class AIModelPricing(models.Model):
    """
    Configurable AI model pricing for cost calculations.
    """
    model_name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    
    # Token pricing per 1000 tokens
    input_cost_per_1k = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=Decimal('0')
    )
    output_cost_per_1k = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=Decimal('0')
    )
    
    # Image pricing (for DALL-E etc)
    cost_per_image = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True
    )
    
    # Model characteristics
    max_tokens = models.IntegerField(
        default=4096,
        help_text="Maximum context length"
    )
    supports_images = models.BooleanField(default=False)
    supports_vision = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_name']
        verbose_name = 'AI Model Pricing'
        verbose_name_plural = 'AI Model Pricing'
    
    def __str__(self):
        return self.display_name
    
    def calculate_cost(self, input_tokens: int = 0, output_tokens: int = 0, images: int = 0) -> Decimal:
        """Calculate total cost for usage."""
        cost = Decimal('0')
        
        if self.input_cost_per_1k:
            cost += (Decimal(input_tokens) / 1000) * self.input_cost_per_1k
        
        if self.output_cost_per_1k:
            cost += (Decimal(output_tokens) / 1000) * self.output_cost_per_1k
        
        if self.cost_per_image and images > 0:
            cost += self.cost_per_image * images
        
        return cost.quantize(Decimal('0.0001'))
