"""
Template Marketplace Models
Models for the template marketplace and white-labeling
"""
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class MarketplaceTemplate(models.Model):
    """Templates available in the marketplace"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    )
    
    CATEGORY_CHOICES = (
        ('social_media', 'Social Media'),
        ('presentation', 'Presentation'),
        ('marketing', 'Marketing'),
        ('ui_kit', 'UI Kit'),
        ('website', 'Website'),
        ('mobile_app', 'Mobile App'),
        ('logo', 'Logo'),
        ('print', 'Print'),
        ('other', 'Other'),
    )
    
    # Creator
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_templates')
    
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Design data
    design_data = models.JSONField(default=dict)
    thumbnail = models.ImageField(upload_to='marketplace/thumbnails/%Y/%m/')
    preview_images = models.JSONField(default=list)  # List of image URLs
    
    # Pricing
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Revenue sharing
    creator_revenue_share = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('70.00'),
        help_text="Percentage of revenue going to creator"
    )
    
    # Metadata
    tags = models.JSONField(default=list)
    features = models.JSONField(default=list)  # List of feature highlights
    
    # Dimensions and compatibility
    dimensions = models.JSONField(default=dict)  # {"width": 1920, "height": 1080}
    compatible_with = models.JSONField(default=list)  # ["figma", "sketch", "xd"]
    
    # Stats
    downloads = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    rating_count = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    rejection_reason = models.TextField(blank=True)
    
    # Featured
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class TemplateReview(models.Model):
    """User reviews for marketplace templates"""
    template = models.ForeignKey(MarketplaceTemplate, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_reviews')
    
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    
    # Verification
    is_verified_purchase = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['template', 'user']
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.template.name}"


class TemplatePurchase(models.Model):
    """Track template purchases"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    )
    
    template = models.ForeignKey(MarketplaceTemplate, on_delete=models.CASCADE, related_name='purchases')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_purchases')
    
    # Pricing at time of purchase
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    creator_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    platform_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_id = models.CharField(max_length=255, blank=True)
    
    # Download tracking
    download_count = models.IntegerField(default=0)
    last_downloaded = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['template', 'user']
    
    def __str__(self):
        return f"{self.user.username} purchased {self.template.name}"


class CreatorProfile(models.Model):
    """Extended profile for marketplace creators"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='creator_profile')
    
    # Profile
    display_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='creators/avatars/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='creators/covers/', null=True, blank=True)
    
    # Social links
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=255, blank=True)
    dribbble = models.CharField(max_length=255, blank=True)
    behance = models.CharField(max_length=255, blank=True)
    
    # Stats
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    follower_count = models.IntegerField(default=0)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Payout
    payout_email = models.EmailField(blank=True)
    stripe_account_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_name


class CreatorFollower(models.Model):
    """Track creator followers"""
    creator = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_creators')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['creator', 'follower']


class WhiteLabelConfig(models.Model):
    """White-label configuration for agencies"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='whitelabel_config')
    
    # Branding
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='whitelabel/logos/', null=True, blank=True)
    favicon = models.ImageField(upload_to='whitelabel/favicons/', null=True, blank=True)
    
    # Colors
    primary_color = models.CharField(max_length=20, default='#2196F3')
    secondary_color = models.CharField(max_length=20, default='#9C27B0')
    accent_color = models.CharField(max_length=20, default='#FF5722')
    
    # Custom domain
    custom_domain = models.CharField(max_length=255, blank=True)
    domain_verified = models.BooleanField(default=False)
    
    # Features
    hide_platform_branding = models.BooleanField(default=False)
    custom_email_domain = models.CharField(max_length=255, blank=True)
    custom_support_email = models.EmailField(blank=True)
    
    # Client limits
    max_clients = models.IntegerField(default=10)
    max_projects_per_client = models.IntegerField(default=50)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"White-label: {self.company_name}"


class WhiteLabelClient(models.Model):
    """Clients managed under white-label"""
    whitelabel = models.ForeignKey(WhiteLabelConfig, on_delete=models.CASCADE, related_name='clients')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='whitelabel_membership')
    
    # Client-specific limits
    max_projects = models.IntegerField(default=50)
    max_storage_mb = models.IntegerField(default=5000)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['whitelabel', 'user']
    
    def __str__(self):
        return f"{self.user.username} @ {self.whitelabel.company_name}"
