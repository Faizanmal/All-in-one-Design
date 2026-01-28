from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class TimeTracker(models.Model):
    """Active time tracking session"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_trackers')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='time_trackers', null=True, blank=True)
    task = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True, blank=True, related_name='trackers')
    
    description = models.CharField(max_length=500, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Timer for {self.user.username} - {self.project or 'No project'}"


class TimeEntry(models.Model):
    """Completed time entries"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='time_entries', null=True, blank=True)
    task = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True, blank=True, related_name='time_entries')
    
    # Time data
    description = models.CharField(max_length=500, blank=True)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Billing
    is_billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Tags
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name_plural = 'Time entries'
        indexes = [
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['project', 'started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.duration_minutes}min"
    
    @property
    def billable_amount(self):
        if not self.is_billable:
            return Decimal('0.00')
        hours = Decimal(self.duration_minutes) / Decimal('60')
        return hours * self.hourly_rate


class Task(models.Model):
    """Project tasks for assignment and tracking"""
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    )
    
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='time_tracking_tasks')
    
    # Basic info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Assignment
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='time_tracking_assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_tracking_created_tasks')
    
    # Time estimation
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Organization
    order = models.IntegerField(default=0)
    tags = models.JSONField(default=list)
    
    # Parent task for subtasks
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def logged_hours(self):
        total_minutes = self.time_entries.aggregate(
            total=models.Sum('duration_minutes')
        )['total'] or 0
        return Decimal(total_minutes) / Decimal('60')
    
    @property
    def progress_percentage(self):
        if not self.estimated_hours or self.estimated_hours == 0:
            return 0
        return min(100, int((self.logged_hours / self.estimated_hours) * 100))


class TaskComment(models.Model):
    """Comments on tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    content = models.TextField()
    attachments = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"


class ProjectEstimate(models.Model):
    """Project time/budget estimates"""
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='estimates')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Estimate details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Time estimate
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Budget
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    fixed_costs = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Status
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_estimates')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Line items
    line_items = models.JSONField(default=list)  # [{'name': '', 'hours': 0, 'rate': 0}]
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Estimate: {self.name}"
    
    @property
    def total_budget(self):
        return (self.estimated_hours * self.hourly_rate) + self.fixed_costs


class Invoice(models.Model):
    """Client invoices"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('viewed', 'Viewed'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='invoices')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    
    # Client
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField()
    client_address = models.TextField(blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Line items from time entries
    line_items = models.JSONField(default=list)
    time_entries = models.ManyToManyField(TimeEntry, blank=True, related_name='invoices')
    
    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number}"


class TimeReport(models.Model):
    """Generated time reports"""
    REPORT_TYPES = (
        ('project', 'Project Report'),
        ('user', 'User Report'),
        ('team', 'Team Report'),
        ('client', 'Client Report'),
    )
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_reports')
    
    # Report config
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    name = models.CharField(max_length=255)
    
    # Filters
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reports_about')
    
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Results
    report_data = models.JSONField(default=dict)
    total_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    billable_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Export
    pdf_url = models.URLField(blank=True)
    csv_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class WeeklyGoal(models.Model):
    """Weekly time tracking goals"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_goals')
    
    # Week
    year = models.IntegerField()
    week = models.IntegerField()
    
    # Goals
    target_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('40.00'))
    billable_target = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Progress
    logged_hours = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    billable_hours = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'year', 'week']
        ordering = ['-year', '-week']
    
    def __str__(self):
        return f"Week {self.week}/{self.year} - {self.user.username}"
    
    @property
    def progress_percentage(self):
        if self.target_hours == 0:
            return 0
        return min(100, int((self.logged_hours / self.target_hours) * 100))
