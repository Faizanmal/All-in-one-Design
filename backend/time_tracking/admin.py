from django.contrib import admin
from .models import (
    TimeTracker, TimeEntry, Task, TaskComment,
    ProjectEstimate, Invoice, TimeReport, WeeklyGoal
)


@admin.register(TimeTracker)
class TimeTrackerAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'task', 'started_at', 'is_active']
    list_filter = ['is_active', 'started_at']
    search_fields = ['user__username', 'project__name', 'description']


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'task', 'duration_minutes', 'is_billable', 'started_at']
    list_filter = ['is_billable', 'started_at', 'project']
    search_fields = ['user__username', 'project__name', 'description']
    date_hierarchy = 'started_at'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assignee', 'due_date']
    list_filter = ['status', 'priority', 'due_date']
    search_fields = ['title', 'description', 'project__name']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'task__title']


@admin.register(ProjectEstimate)
class ProjectEstimateAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'estimated_hours', 'hourly_rate', 'is_approved']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['name', 'project__name']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'project', 'client_name', 'total', 'status', 'due_date']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'client_name', 'project__name']


@admin.register(TimeReport)
class TimeReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'project', 'total_hours', 'created_at']
    list_filter = ['report_type', 'created_at']
    search_fields = ['name']


@admin.register(WeeklyGoal)
class WeeklyGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'week', 'target_hours', 'logged_hours']
    list_filter = ['year', 'week']
    search_fields = ['user__username']
