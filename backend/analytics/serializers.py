"""
Analytics Serializers
"""
from rest_framework import serializers
from .models import UserActivity, ProjectAnalytics, AIUsageMetrics, DailyUsageStats


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'timestamp', 'ip_address',
            'user_agent', 'metadata', 'duration_ms'
        ]
        read_only_fields = fields


class ProjectAnalyticsSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ProjectAnalytics
        fields = [
            'id', 'project_name', 'view_count', 'edit_count',
            'export_count', 'share_count', 'total_edit_time_seconds',
            'last_viewed', 'last_edited', 'total_components',
            'ai_generated_components', 'total_collaborators',
            'total_comments', 'updated_at'
        ]
        read_only_fields = fields


class AIUsageMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIUsageMetrics
        fields = [
            'id', 'service_type', 'tokens_used', 'estimated_cost',
            'model_used', 'request_duration_ms', 'success',
            'error_message', 'timestamp'
        ]
        read_only_fields = fields


class DailyUsageStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyUsageStats
        fields = [
            'date', 'projects_created', 'projects_edited',
            'projects_exported', 'ai_generations_count',
            'ai_tokens_used', 'ai_cost', 'assets_uploaded',
            'storage_used_bytes', 'total_edit_time_seconds',
            'unique_sessions'
        ]
        read_only_fields = fields


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_projects = serializers.IntegerField()
    projects_this_week = serializers.IntegerField()
    ai_requests_today = serializers.IntegerField()
    ai_requests_month = serializers.IntegerField()
    total_tokens_used = serializers.IntegerField()
    estimated_cost = serializers.DecimalField(max_digits=10, decimal_places=6)
