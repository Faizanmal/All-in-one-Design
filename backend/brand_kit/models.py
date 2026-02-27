from django.db import models
from django.conf import settings
from design_systems.models import DesignSystem
import uuid

class BrandKitEnforcement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.OneToOneField(DesignSystem, on_delete=models.CASCADE, related_name='brand_enforcement')
    
    # Toggle Switches
    lock_color_picker = models.BooleanField(default=False, help_text="Prevent team from using off-brand hex codes")
    force_ai_variants = models.BooleanField(default=False, help_text="Force AI to strictly adhere to brand colors over general generation")
    lock_typography = models.BooleanField(default=False, help_text="Pre-define Heading/Body fonts and disable custom selections")
    require_approval = models.BooleanField(default=False, help_text="Require Admin approval before exporting/publishing if edits were made by a Junior role")
    
    # Audit log setting
    log_violations = models.BooleanField(default=True, help_text="Keep a log of when users try to break brand rules")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Enforcement Rules for {self.design_system.name}"

class BrandViolationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enforcement = models.ForeignKey(BrandKitEnforcement, on_delete=models.CASCADE, related_name='violations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='brand_violations')
    event_type = models.CharField(max_length=100, help_text="e.g., 'invalid_hex', 'unapproved_font'")
    details = models.JSONField(blank=True, null=True, help_text="Context of violation")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Violation by {self.user.username if self.user else 'Unknown'} at {self.timestamp}"
