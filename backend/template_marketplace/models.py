from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class TemplateCategory(models.Model):
    """Categories for templates"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='folder')
    color = models.CharField(max_length=20, default='#3B82F6')
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    # Display
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Template categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class MarketplaceTemplate(models.Model):
    """Community-created templates for marketplace"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
    
    PRICING_TYPES = (
        ('free', 'Free'),
        ('paid', 'Paid'),
        ('subscription', 'Subscription Only'),
    )
    
    # Creator
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_templates')
    
    # Basic info
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    
    # Categories and tags
    category = models.ForeignKey(TemplateCategory, on_delete=models.SET_NULL, null=True, related_name='templates')
    tags = models.JSONField(default=list)
    
    # Template data
    template_data = models.JSONField()  # Design data
    canvas_width = models.IntegerField(default=1920)
    canvas_height = models.IntegerField(default=1080)
    
    # Media
    thumbnail = models.URLField()
    preview_images = models.JSONField(default=list)  # List of image URLs
    preview_video = models.URLField(blank=True)
    
    # Pricing
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES, default='free')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    rejection_reason = models.TextField(blank=True)
    
    # Statistics
    downloads = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    favorites = models.IntegerField(default=0)
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    rating_count = models.IntegerField(default=0)
    
    # Features
    is_featured = models.BooleanField(default=False)
    is_editors_choice = models.BooleanField(default=False)
    
    # Licensing
    license_type = models.CharField(max_length=50, default='standard')
    commercial_use = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'pricing_type']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['-downloads']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def effective_price(self):
        if self.sale_price:
            return self.sale_price
        return self.price


class TemplateVersion(models.Model):
    """Version history for templates"""
    template = models.ForeignKey(MarketplaceTemplate, on_delete=models.CASCADE, related_name='versions')
    
    version = models.CharField(max_length=20)
    template_data = models.JSONField()
    changelog = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['template', 'version']
    
    def __str__(self):
        return f"{self.template.title} v{self.version}"


class TemplateReview(models.Model):
    """User reviews for templates"""
    template = models.ForeignKey(MarketplaceTemplate, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_reviews')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    # Helpful votes
    helpful_votes = models.IntegerField(default=0)
    
    # Status
    is_verified_purchase = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['template', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.template.title}"


class TemplatePurchase(models.Model):
    """Record of template purchases"""
    template = models.ForeignKey(MarketplaceTemplate, on_delete=models.CASCADE, related_name='purchases')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_purchases')
    
    # Payment
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_id = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Status
    status = models.CharField(max_length=20, default='completed')
    
    # Refund
    refunded = models.BooleanField(default=False)
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.user.username} purchased {self.template.title}"


class TemplateFavorite(models.Model):
    """User favorites for templates"""
    template = models.ForeignKey(MarketplaceTemplate, on_delete=models.CASCADE, related_name='user_favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_templates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['template', 'user']
    
    def __str__(self):
        return f"{self.user.username} favorited {self.template.title}"


class CreatorProfile(models.Model):
    """Profile for template creators"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='creator_profile')
    
    # Profile info
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    cover_image = models.URLField(blank=True)
    website = models.URLField(blank=True)
    
    # Social links
    twitter = models.CharField(max_length=100, blank=True)
    dribbble = models.CharField(max_length=100, blank=True)
    behance = models.CharField(max_length=100, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    is_pro = models.BooleanField(default=False)
    
    # Payout
    payout_email = models.EmailField(blank=True)
    payout_method = models.CharField(max_length=50, default='paypal')  # paypal, stripe, bank
    payout_details = models.JSONField(default=dict)
    
    # Statistics
    total_sales = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_downloads = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_name


class CreatorPayout(models.Model):
    """Payout records for creators"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    creator = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='payouts')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Payment details
    payout_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout {self.amount} to {self.creator.display_name}"


class TemplateCollection(models.Model):
    """Curated collections of templates"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    templates = models.ManyToManyField(MarketplaceTemplate, related_name='in_collections')
    
    # Display
    cover_image = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Curator
    curator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
