from django.db import models
from django.conf import settings
import uuid

class PublishedSite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='published_sites')
    project_id = models.IntegerField(help_text="Reference to the design project UI/UX layout")
    subdomain = models.CharField(max_length=63, unique=True, help_text="e.g., 'my-portfolio' for my-portfolio.designco.site")
    custom_domain = models.CharField(max_length=255, blank=True, null=True, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Deploying'),
        ('active', 'Active'),
        ('failed', 'Failed'),
        ('suspended', 'Suspended')
    ], default='pending')
    
    # Deployment/Hosting details
    deployment_id = models.CharField(max_length=255, blank=True, null=True, help_text="Vercel/Netlify deployment ID")
    published_url = models.URLField(max_length=1000, blank=True, null=True)
    last_published_at = models.DateTimeField(null=True, blank=True)
    error_logs = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.subdomain}.designco.site"
