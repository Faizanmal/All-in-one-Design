"""
Subscription and Billing Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SubscriptionTier(models.Model):
    """Define subscription tiers/plans"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Limits
    max_projects = models.IntegerField(help_text="Max projects, -1 for unlimited")
    max_ai_requests_per_month = models.IntegerField(help_text="Max AI requests per month, -1 for unlimited")
    max_storage_mb = models.IntegerField(help_text="Max storage in MB, -1 for unlimited")
    max_collaborators_per_project = models.IntegerField(default=0)
    max_exports_per_month = models.IntegerField(default=100)
    
    # Features
    features = models.JSONField(default=dict, help_text="JSON of feature flags")
    # {
    #   "advanced_ai": true,
    #   "priority_support": true,
    #   "custom_branding": false,
    #   "api_access": true,
    #   "white_label": false
    # }
    
    # Stripe integration
    stripe_product_id = models.CharField(max_length=255, blank=True)
    stripe_price_id_monthly = models.CharField(max_length=255, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=255, blank=True)
    
    # Display
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'price_monthly']
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """User subscriptions"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('trial', 'Trial'),
        ('paused', 'Paused'),
    )
    
    BILLING_PERIOD_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIOD_CHOICES, default='monthly')
    
    # Dates
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe integration
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    
    # Auto-renewal
    auto_renew = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'next_billing_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.tier.name} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status == 'active':
            return True
        if self.status == 'trial' and self.trial_end_date:
            return timezone.now() < self.trial_end_date
        return False
    
    def days_until_renewal(self):
        """Calculate days until next billing"""
        if self.next_billing_date:
            delta = self.next_billing_date - timezone.now()
            return max(0, delta.days)
        return None
    
    def check_limit(self, resource_type):
        """Check if user is within limits for a resource"""
        if resource_type == 'projects':
            from projects.models import Project
            count = Project.objects.filter(user=self.user).count()
            limit = self.tier.max_projects
            return (limit == -1) or (count < limit)
        
        elif resource_type == 'ai_requests':
            from analytics.models import AIUsageMetrics
            first_day = timezone.now().replace(day=1, hour=0, minute=0, second=0)
            count = AIUsageMetrics.objects.filter(
                user=self.user,
                timestamp__gte=first_day
            ).count()
            limit = self.tier.max_ai_requests_per_month
            return (limit == -1) or (count < limit)
        
        elif resource_type == 'storage':
            from assets.models import Asset
            from django.db.models import Sum
            storage_used = Asset.objects.filter(user=self.user).aggregate(
                total=Sum('file_size')
            )['total'] or 0
            storage_mb = storage_used / (1024 * 1024)
            limit = self.tier.max_storage_mb
            return (limit == -1) or (storage_mb < limit)
        
        return True


class UsageQuota(models.Model):
    """Track monthly usage quotas"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotas')
    month = models.DateField(help_text="First day of the month")
    
    # Usage tracking
    ai_requests_used = models.IntegerField(default=0)
    exports_used = models.IntegerField(default=0)
    storage_bytes_used = models.BigIntegerField(default=0)
    
    # Limits (cached from subscription tier)
    ai_requests_limit = models.IntegerField()
    exports_limit = models.IntegerField()
    storage_bytes_limit = models.BigIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'month']
        indexes = [
            models.Index(fields=['user', 'month']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%Y-%m')}"
    
    def is_ai_limit_reached(self):
        return self.ai_requests_limit > 0 and self.ai_requests_used >= self.ai_requests_limit
    
    def is_export_limit_reached(self):
        return self.exports_limit > 0 and self.exports_used >= self.exports_limit
    
    def is_storage_limit_reached(self):
        return self.storage_bytes_limit > 0 and self.storage_bytes_used >= self.storage_bytes_limit


class Payment(models.Model):
    """Payment transactions"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment details
    description = models.TextField(blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Stripe integration
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_invoice_id = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status})"


class Invoice(models.Model):
    """Billing invoices"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    
    invoice_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Dates
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    # Status
    is_paid = models.BooleanField(default=False)
    
    # Stripe
    stripe_invoice_id = models.CharField(max_length=255, blank=True)
    invoice_pdf_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.username}"


class Coupon(models.Model):
    """Discount coupons for subscriptions"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Discount
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Limits
    max_uses = models.IntegerField(null=True, blank=True, help_text="Max total uses, null for unlimited")
    max_uses_per_user = models.IntegerField(default=1)
    current_uses = models.IntegerField(default=0)
    
    # Applicable tiers
    applicable_tiers = models.ManyToManyField(SubscriptionTier, blank=True, related_name='coupons')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Stripe
    stripe_coupon_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        return True


class CouponUsage(models.Model):
    """Track coupon usage"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['coupon', 'user']
    
    def __str__(self):
        return f"{self.user.username} used {self.coupon.code}"
