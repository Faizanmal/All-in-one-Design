from rest_framework import serializers
from django.utils import timezone
from .models import (
    TimeTracker, TimeEntry, Task, TaskComment,
    ProjectEstimate, Invoice, TimeReport, WeeklyGoal
)


class TimeTrackerSerializer(serializers.ModelSerializer):
    """Serializer for active time trackers"""
    elapsed_minutes = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = TimeTracker
        fields = [
            'id', 'user', 'project', 'project_name', 'task', 'task_title',
            'description', 'started_at', 'is_active', 'elapsed_minutes'
        ]
        read_only_fields = ['user', 'is_active', 'started_at']
    
    def get_elapsed_minutes(self, obj) -> int:
        if obj.is_active:
            delta = timezone.now() - obj.started_at
            return int(delta.total_seconds() / 60)
        return 0


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for time entries"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    billable_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = TimeEntry
        fields = [
            'id', 'user', 'user_name', 'project', 'project_name', 'task', 'task_title',
            'description', 'started_at', 'ended_at', 'duration_minutes',
            'is_billable', 'hourly_rate', 'billable_amount', 'tags',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating time entries"""
    
    class Meta:
        model = TimeEntry
        fields = [
            'project', 'task', 'description', 'started_at', 'ended_at',
            'duration_minutes', 'is_billable', 'hourly_rate', 'tags'
        ]
    
    def validate(self, data):
        if data['ended_at'] <= data['started_at']:
            raise serializers.ValidationError("End time must be after start time")
        return data


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer for task lists"""
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    logged_hours = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    subtask_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority', 'assignee', 'assignee_name',
            'estimated_hours', 'logged_hours', 'progress_percentage',
            'start_date', 'due_date', 'order', 'subtask_count'
        ]
    
    def get_subtask_count(self, obj) -> int:
        return obj.subtasks.count()


class TaskSerializer(serializers.ModelSerializer):
    """Full serializer for tasks"""
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    logged_hours = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    subtasks = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'project', 'title', 'description', 'status', 'priority',
            'assignee', 'assignee_name', 'created_by', 'created_by_name',
            'estimated_hours', 'logged_hours', 'progress_percentage',
            'start_date', 'due_date', 'completed_at', 'order', 'tags',
            'parent', 'subtasks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'completed_at', 'created_at', 'updated_at']
    
    def get_subtasks(self, obj):
        if obj.subtasks.exists():
            return TaskListSerializer(obj.subtasks.all(), many=True).data
        return []


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    
    class Meta:
        model = Task
        fields = [
            'project', 'title', 'description', 'status', 'priority',
            'assignee', 'estimated_hours', 'start_date', 'due_date',
            'order', 'tags', 'parent'
        ]


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = [
            'id', 'task', 'user', 'user_name', 'content', 'attachments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class ProjectEstimateSerializer(serializers.ModelSerializer):
    """Serializer for project estimates"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    total_budget = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = ProjectEstimate
        fields = [
            'id', 'project', 'name', 'description',
            'estimated_hours', 'hourly_rate', 'fixed_costs', 'total_budget',
            'line_items', 'is_approved', 'approved_by', 'approved_by_name',
            'approved_at', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'is_approved', 'approved_by', 'approved_at', 'created_at', 'updated_at']


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer for invoice lists"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'title', 'project', 'project_name',
            'client_name', 'total', 'status', 'issue_date', 'due_date'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    """Full serializer for invoices"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'project', 'project_name', 'invoice_number', 'title', 'notes',
            'client_name', 'client_email', 'client_address',
            'subtotal', 'tax_rate', 'tax_amount', 'discount', 'total',
            'line_items', 'issue_date', 'due_date',
            'status', 'paid_at', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'paid_at', 'created_at', 'updated_at']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invoices"""
    time_entry_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Invoice
        fields = [
            'project', 'title', 'notes', 'client_name', 'client_email', 'client_address',
            'subtotal', 'tax_rate', 'discount', 'line_items', 'issue_date', 'due_date',
            'time_entry_ids'
        ]


class TimeReportSerializer(serializers.ModelSerializer):
    """Serializer for time reports"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = TimeReport
        fields = [
            'id', 'report_type', 'name', 'project', 'project_name', 'user',
            'start_date', 'end_date', 'report_data',
            'total_hours', 'billable_hours', 'total_amount',
            'pdf_url', 'csv_url', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['report_data', 'total_hours', 'billable_hours', 'total_amount', 'pdf_url', 'csv_url', 'created_by', 'created_at']


class WeeklyGoalSerializer(serializers.ModelSerializer):
    """Serializer for weekly goals"""
    progress_percentage = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = WeeklyGoal
        fields = [
            'id', 'user', 'year', 'week', 'target_hours', 'billable_target',
            'logged_hours', 'billable_hours', 'progress_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'logged_hours', 'billable_hours', 'created_at', 'updated_at']


class DashboardSerializer(serializers.Serializer):
    """Serializer for time tracking dashboard"""
    today_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    week_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    month_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    billable_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    billable_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    active_timer = TimeTrackerSerializer(allow_null=True)
    recent_entries = TimeEntrySerializer(many=True)
    projects_breakdown = serializers.ListField()


class BulkTimeEntrySerializer(serializers.Serializer):
    """Serializer for bulk time entry operations"""
    entries = TimeEntryCreateSerializer(many=True)
