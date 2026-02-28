"""
Serializers for Workflow Automation Engine.
"""

from rest_framework import serializers
from .workflow_models import (
    Workflow,
    WorkflowTrigger,
    WorkflowAction,
    WorkflowRun,
    WorkflowActionLog,
)


class WorkflowActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowAction
        fields = [
            'id', 'workflow', 'action_type', 'name', 'config',
            'position_x', 'position_y', 'order',
            'condition_expression',
            'next_action_on_success', 'next_action_on_failure',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'workflow': {'required': False}}


class WorkflowTriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTrigger
        fields = [
            'id', 'workflow', 'trigger_type', 'config',
            'cron_expression', 'webhook_secret',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'webhook_secret']
        extra_kwargs = {'workflow': {'required': False}}


class WorkflowActionLogSerializer(serializers.ModelSerializer):
    action_name = serializers.CharField(source='action.name', read_only=True)
    action_type = serializers.CharField(source='action.action_type', read_only=True)

    class Meta:
        model = WorkflowActionLog
        fields = [
            'id', 'action', 'action_name', 'action_type',
            'status', 'started_at', 'completed_at', 'duration_ms',
            'input_data', 'output_data', 'error_message',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class WorkflowRunSerializer(serializers.ModelSerializer):
    action_logs = WorkflowActionLogSerializer(many=True, read_only=True)
    triggered_by_username = serializers.CharField(
        source='triggered_by.username', read_only=True, default=None
    )

    class Meta:
        model = WorkflowRun
        fields = [
            'id', 'workflow', 'triggered_by', 'triggered_by_username',
            'status', 'trigger_type', 'trigger_data',
            'started_at', 'completed_at', 'duration_ms',
            'output', 'error_message', 'retry_count',
            'action_logs', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class WorkflowListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing workflows."""
    trigger_count = serializers.SerializerMethodField()
    action_count = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'status',
            'total_runs', 'successful_runs', 'failed_runs',
            'last_run_at', 'trigger_count', 'action_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_trigger_count(self, obj):
        return obj.triggers.count()

    def get_action_count(self, obj):
        return obj.actions.count()


class WorkflowDetailSerializer(serializers.ModelSerializer):
    """Full serializer with nested triggers and actions."""
    triggers = WorkflowTriggerSerializer(many=True, read_only=True)
    actions = WorkflowActionSerializer(many=True, read_only=True)
    recent_runs = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'status',
            'graph_data',
            'max_retries', 'retry_delay_seconds', 'timeout_seconds',
            'run_as_async',
            'total_runs', 'successful_runs', 'failed_runs',
            'last_run_at',
            'triggers', 'actions', 'recent_runs',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_runs', 'successful_runs', 'failed_runs',
                           'last_run_at', 'created_at', 'updated_at']

    def get_recent_runs(self, obj):
        runs = obj.runs.all()[:5]
        return WorkflowRunSerializer(runs, many=True).data


class WorkflowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = [
            'name', 'description', 'status',
            'graph_data',
            'max_retries', 'retry_delay_seconds', 'timeout_seconds',
            'run_as_async',
        ]
