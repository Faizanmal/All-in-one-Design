"""
Workflow Automation Engine Models

A visual workflow builder for automating design operations:
- Trigger-based workflows (on approval, on brand change, on schedule)
- Action chains (export, resize, publish, notify)
- Conditional logic and branching
- Integration with existing services
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid


class Workflow(models.Model):
    """A user-defined automation workflow."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('disabled', 'Disabled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflows')
    team = models.ForeignKey(
        'teams.Team', on_delete=models.CASCADE,
        related_name='workflows', null=True, blank=True
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Visual workflow graph (nodes + edges as JSON)
    graph_data = models.JSONField(default=dict, help_text='Visual graph: nodes, edges, positions')

    # Execution settings
    max_retries = models.IntegerField(default=3, validators=[MinValueValidator(0)])
    retry_delay_seconds = models.IntegerField(default=60)
    timeout_seconds = models.IntegerField(default=300)
    run_as_async = models.BooleanField(default=True)

    # Stats
    total_runs = models.IntegerField(default=0)
    successful_runs = models.IntegerField(default=0)
    failed_runs = models.IntegerField(default=0)
    last_run_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class WorkflowTrigger(models.Model):
    """A trigger that initiates a workflow."""

    TRIGGER_TYPES = [
        ('design_approved', 'Design Approved'),
        ('design_updated', 'Design Updated'),
        ('comment_added', 'Comment Added'),
        ('brand_colors_changed', 'Brand Colors Changed'),
        ('schedule', 'Scheduled'),
        ('webhook', 'Webhook'),
        ('manual', 'Manual'),
        ('project_created', 'Project Created'),
        ('export_completed', 'Export Completed'),
        ('team_member_joined', 'Team Member Joined'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='triggers')

    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    config = models.JSONField(default=dict, help_text='Trigger-specific configuration')

    # Schedule config (for cron-style triggers)
    cron_expression = models.CharField(max_length=100, blank=True)

    # Webhook config
    webhook_secret = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_trigger_type_display()} → {self.workflow.name}"


class WorkflowAction(models.Model):
    """An action node in the workflow."""

    ACTION_TYPES = [
        # Export actions
        ('export_png', 'Export as PNG'),
        ('export_pdf', 'Export as PDF'),
        ('export_svg', 'Export as SVG'),
        ('export_all_formats', 'Export All Formats'),
        ('magic_resize', 'Magic Resize'),
        # Publish actions
        ('publish_web', 'Publish to Web'),
        ('schedule_social', 'Schedule Social Post'),
        # Notification actions
        ('send_email', 'Send Email'),
        ('send_slack', 'Send Slack Message'),
        ('send_webhook', 'Send Webhook'),
        ('notify_team', 'Notify Team'),
        # Design actions
        ('update_brand_colors', 'Update Brand Colors'),
        ('apply_template', 'Apply Template'),
        ('run_accessibility_check', 'Run Accessibility Check'),
        ('run_qa_check', 'Run QA Check'),
        # Condition actions
        ('condition', 'Conditional Branch'),
        ('delay', 'Wait/Delay'),
        ('loop', 'Loop/Repeat'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='actions')

    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    name = models.CharField(max_length=255)
    config = models.JSONField(default=dict, help_text='Action-specific parameters')

    # Position in workflow graph
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    # Condition (for conditional branches)
    condition_expression = models.TextField(blank=True)

    # Connected to (next actions)
    next_action_on_success = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='prev_success'
    )
    next_action_on_failure = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='prev_failure'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.get_action_type_display()})"


class WorkflowRun(models.Model):
    """A single execution of a workflow."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('timed_out', 'Timed Out'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='runs')
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    trigger_type = models.CharField(max_length=30, blank=True)
    trigger_data = models.JSONField(default=dict)

    # Execution tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    # Results
    output = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Run {self.id} - {self.status}"


class WorkflowActionLog(models.Model):
    """Log entry for each action executed in a workflow run."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_run = models.ForeignKey(WorkflowRun, on_delete=models.CASCADE, related_name='action_logs')
    action = models.ForeignKey(WorkflowAction, on_delete=models.CASCADE, related_name='logs')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.action.name}: {self.status}"
