from django.db import models
from django.conf import settings
import uuid

class SocialAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=50, choices=[
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram')
    ])
    access_token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500, blank=True, null=True)
    account_id = models.CharField(max_length=200, help_text="Platform-specific user ID")
    account_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'platform', 'account_id')

    def __str__(self):
        return f"{self.user.username} - {self.platform}"

class ScheduledPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('publishing', 'Publishing'),
        ('published', 'Published'),
        ('failed', 'Failed')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_posts')
    project_id = models.IntegerField(null=True, blank=True, help_text="Reference to the design project")
    content = models.TextField()
    media_url = models.URLField(max_length=1000, blank=True, null=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    accounts = models.ManyToManyField(SocialAccount, related_name='posts')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user.username} at {self.scheduled_time}"
