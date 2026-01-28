from django.db import models
from django.conf import settings
import uuid
import secrets


class Agency(models.Model):
    """Agency account with white-label capabilities"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_agencies')
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    # Branding
    logo = models.ImageField(upload_to='agency_logos/', null=True, blank=True)
    logo_dark = models.ImageField(upload_to='agency_logos/', null=True, blank=True)
    favicon = models.ImageField(upload_to='agency_favicons/', null=True, blank=True)
    
    # Colors
    primary_color = models.CharField(max_length=7, default='#6366f1')
    secondary_color = models.CharField(max_length=7, default='#8b5cf6')
    accent_color = models.CharField(max_length=7, default='#f59e0b')
    
    # Custom domain
    custom_domain = models.CharField(max_length=255, blank=True)
    domain_verified = models.BooleanField(default=False)
    
    # Contact info
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    
    # Settings
    white_label_enabled = models.BooleanField(default=False)
    remove_branding = models.BooleanField(default=False)
    custom_email_templates = models.BooleanField(default=False)
    
    # Limits
    client_limit = models.IntegerField(default=10)
    project_limit = models.IntegerField(default=100)
    storage_limit_gb = models.IntegerField(default=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Agency'
        verbose_name_plural = 'Agencies'
    
    def __str__(self):
        return self.name


class AgencyMember(models.Model):
    """Agency team members"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('designer', 'Designer'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agency_memberships')
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='designer')
    permissions = models.JSONField(default=dict)
    
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_agency_invitations')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['agency', 'user']
    
    def __str__(self):
        return f"{self.user.username} @ {self.agency.name}"


class Client(models.Model):
    """Client accounts for agencies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='clients')
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company = models.CharField(max_length=255, blank=True)
    
    # Client portal access
    portal_enabled = models.BooleanField(default=True)
    portal_password = models.CharField(max_length=255, blank=True)  # Hashed
    
    # Contact info
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Custom branding for client
    logo = models.ImageField(upload_to='client_logos/', null=True, blank=True)
    brand_colors = models.JSONField(default=dict)
    
    # Tags and organization
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.agency.name})"


class ClientPortal(models.Model):
    """Client portal settings and content"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='portal')
    
    # Portal settings
    is_active = models.BooleanField(default=True)
    
    # Access token
    access_token = models.CharField(max_length=255, unique=True)
    token_expires = models.DateTimeField(null=True, blank=True)
    
    # Portal customization
    welcome_message = models.TextField(blank=True)
    custom_css = models.TextField(blank=True)
    
    # Visible projects
    visible_projects = models.ManyToManyField('projects.Project', blank=True)
    
    # Feedback settings
    allow_comments = models.BooleanField(default=True)
    allow_approvals = models.BooleanField(default=True)
    
    # Activity log
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Client Portal'
        verbose_name_plural = 'Client Portals'
    
    def __str__(self):
        return f"Portal for {self.client.name}"
    
    def save(self, *args, **kwargs):
        if not self.access_token:
            self.access_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class ClientFeedback(models.Model):
    """Feedback from clients on designs"""
    FEEDBACK_TYPES = [
        ('comment', 'Comment'),
        ('approval', 'Approval'),
        ('revision_request', 'Revision Request'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='feedback')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='client_feedback')
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    content = models.TextField()
    
    # Position on design (for comments)
    position_x = models.FloatField(null=True, blank=True)
    position_y = models.FloatField(null=True, blank=True)
    page_number = models.IntegerField(default=1)
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.feedback_type} from {self.client.name}"


class APIKey(models.Model):
    """API keys for agency integrations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='api_keys')
    
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255, unique=True)
    secret = models.CharField(max_length=255)  # Hashed
    
    # Permissions
    permissions = models.JSONField(default=list)
    # Example: ["read:projects", "write:projects", "read:assets"]
    
    # Rate limiting
    rate_limit = models.IntegerField(default=1000)  # requests per hour
    
    # Usage tracking
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
    
    def __str__(self):
        return f"{self.name} ({self.agency.name})"
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = f"ak_{secrets.token_hex(16)}"
        super().save(*args, **kwargs)


class AgencyBilling(models.Model):
    """Billing management for agencies"""
    BILLING_STATUS = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('trial', 'Trial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.OneToOneField(Agency, on_delete=models.CASCADE, related_name='billing')
    
    # Subscription
    plan = models.CharField(max_length=50, default='free')
    status = models.CharField(max_length=20, choices=BILLING_STATUS, default='trial')
    
    # Payment info
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    
    # Billing details
    billing_email = models.EmailField(blank=True)
    billing_address = models.JSONField(default=dict)
    
    # Current period
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    
    # Usage
    current_usage = models.JSONField(default=dict)
    # Example: {"clients": 5, "projects": 50, "storage_gb": 10}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Agency Billing'
        verbose_name_plural = 'Agency Billings'
    
    def __str__(self):
        return f"Billing for {self.agency.name}"


class AgencyInvoice(models.Model):
    """Invoices for agency billing"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    
    invoice_number = models.CharField(max_length=50, unique=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    # Line items
    line_items = models.JSONField(default=list)
    # Example: [{"description": "Web Design", "quantity": 1, "rate": 1000, "amount": 1000}]
    
    # Notes
    notes = models.TextField(blank=True)
    
    # PDF
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number}"


class BrandLibrary(models.Model):
    """Shared brand assets library for agencies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='brand_libraries')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='brand_library', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Brand assets
    logos = models.JSONField(default=list)  # Logo variations
    colors = models.JSONField(default=dict)  # Color palette
    fonts = models.JSONField(default=list)  # Font specifications
    guidelines = models.TextField(blank=True)  # Brand guidelines
    
    # Asset files
    assets = models.ManyToManyField('assets.Asset', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Brand Library'
        verbose_name_plural = 'Brand Libraries'
    
    def __str__(self):
        return self.name
