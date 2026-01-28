"""
Productivity Serializers
Serializers for A/B testing, plugins, and offline support
"""
from typing import Dict, Optional
from rest_framework import serializers
from .productivity_models import (
    ABTest,
    ABTestVariant,
    ABTestResult,
    ABTestEvent,
    Plugin,
    PluginInstallation,
    PluginReview,
    OfflineSync,
    UserPreference
)
from typing import Optional, Dict, List


class ABTestVariantSerializer(serializers.ModelSerializer):
    """Serializer for A/B test variants"""
    results = serializers.SerializerMethodField()
    
    class Meta:
        model = ABTestVariant
        fields = [
            'id', 'test', 'name', 'description', 'design_data',
            'traffic_percentage', 'is_control', 'created_at', 'results'
        ]
        read_only_fields = ['id', 'created_at', 'results']
    
    def get_results(self, obj) -> Optional[Dict]:
        result = getattr(obj, 'results', None)
        if result:
            return {
                'impressions': result.impressions,
                'clicks': result.clicks,
                'conversions': result.conversions,
                'click_rate': result.click_rate,
                'conversion_rate': result.conversion_rate,
                'avg_engagement_time': result.avg_engagement_time,
                'confidence_level': result.confidence_level
            }
        return None


class ABTestSerializer(serializers.ModelSerializer):
    """Serializer for A/B tests"""
    variants = ABTestVariantSerializer(many=True, read_only=True)
    winning_variant_name = serializers.CharField(
        source='winning_variant.name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = ABTest
        fields = [
            'id', 'project', 'name', 'description', 'status',
            'primary_goal', 'target_audience', 'start_date', 'end_date',
            'min_sample_size', 'confidence_threshold', 'winning_variant',
            'winning_variant_name', 'variants', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'start_date', 'end_date', 
                          'winning_variant', 'created_at', 'updated_at']


class ABTestResultSerializer(serializers.ModelSerializer):
    """Serializer for A/B test results"""
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    
    class Meta:
        model = ABTestResult
        fields = [
            'id', 'variant', 'variant_name', 'impressions', 'clicks',
            'conversions', 'click_rate', 'conversion_rate', 
            'avg_engagement_time', 'confidence_level', 'updated_at'
        ]
        read_only_fields = fields


class ABTestEventSerializer(serializers.ModelSerializer):
    """Serializer for A/B test events"""
    
    class Meta:
        model = ABTestEvent
        fields = [
            'id', 'variant', 'event_type', 'visitor_id', 'session_id',
            'event_data', 'device_type', 'browser', 'referrer', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PluginSerializer(serializers.ModelSerializer):
    """Serializer for plugins"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    is_installed = serializers.SerializerMethodField()
    
    class Meta:
        model = Plugin
        fields = [
            'id', 'slug', 'name', 'description', 'version', 'category',
            'icon', 'banner', 'screenshots', 'creator', 'creator_name',
            'entry_point', 'permissions', 'hooks', 'api_version',
            'price', 'currency', 'is_free', 'status', 'installs',
            'rating_average', 'rating_count', 'is_installed',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'creator', 'status', 'installs', 
            'rating_average', 'rating_count', 'created_at', 'updated_at'
        ]
    
    def get_is_installed(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PluginInstallation.objects.filter(
                user=request.user,
                plugin=obj
            ).exists()
        return False


class PluginInstallationSerializer(serializers.ModelSerializer):
    """Serializer for plugin installations"""
    plugin_name = serializers.CharField(source='plugin.name', read_only=True)
    plugin_version = serializers.CharField(source='plugin.version', read_only=True)
    
    class Meta:
        model = PluginInstallation
        fields = [
            'id', 'plugin', 'plugin_name', 'plugin_version',
            'installed_version', 'is_enabled', 'config',
            'installed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'installed_at', 'updated_at']


class PluginReviewSerializer(serializers.ModelSerializer):
    """Serializer for plugin reviews"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PluginReview
        fields = [
            'id', 'plugin', 'user', 'user_name', 'rating', 'title',
            'review', 'is_verified_install', 'helpful_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified_install', 
                          'helpful_count', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate(self, data):
        user = self.context['request'].user
        plugin = data.get('plugin')
        
        # Check if user has already reviewed this plugin
        if self.instance is None:
            if PluginReview.objects.filter(user=user, plugin=plugin).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this plugin"
                )
        
        # Check if user has installed the plugin
        data['is_verified_install'] = PluginInstallation.objects.filter(
            user=user,
            plugin=plugin
        ).exists()
        
        return data


class OfflineSyncSerializer(serializers.ModelSerializer):
    """Serializer for offline sync"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = OfflineSync
        fields = [
            'id', 'project', 'project_name', 'device_id', 'device_name',
            'client_version', 'changes', 'last_known_version', 'status',
            'conflicts', 'resolved_changes', 'synced_at', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'conflicts', 
                          'resolved_changes', 'synced_at', 'created_at']
    
    def validate_project(self, value):
        request = self.context.get('request')
        if value.user != request.user:
            raise serializers.ValidationError(
                "You don't have access to this project"
            )
        return value


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user preferences"""
    
    class Meta:
        model = UserPreference
        fields = [
            'id', 'theme', 'language', 'timezone', 'keyboard_shortcuts',
            'auto_save', 'auto_save_interval', 'canvas_grid', 'snap_to_grid',
            'grid_size', 'default_export_format', 'notification_email',
            'notification_push', 'notification_sound', 'offline_mode',
            'offline_projects', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'updated_at']


class ABTestCreateWithVariantsSerializer(serializers.Serializer):
    """Serializer for creating A/B test with variants in one request"""
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    project = serializers.IntegerField()
    primary_goal = serializers.ChoiceField(
        choices=['clicks', 'conversions', 'engagement_time']
    )
    target_audience = serializers.JSONField(required=False)
    min_sample_size = serializers.IntegerField(default=100)
    confidence_threshold = serializers.FloatField(default=95.0)
    variants = serializers.ListField(
        child=serializers.JSONField(),
        min_length=2
    )
    
    def validate_variants(self, value):
        total_traffic = sum(v.get('traffic_percentage', 0) for v in value)
        if total_traffic != 100:
            raise serializers.ValidationError(
                "Total traffic percentage must equal 100"
            )
        
        control_count = sum(1 for v in value if v.get('is_control', False))
        if control_count != 1:
            raise serializers.ValidationError(
                "Exactly one variant must be marked as control"
            )
        
        return value


class PluginDeveloperSerializer(serializers.Serializer):
    """Serializer for plugin developer analytics"""
    plugin_id = serializers.IntegerField()
    total_installs = serializers.IntegerField()
    active_installs = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    rating_average = serializers.FloatField()
    rating_count = serializers.IntegerField()
    reviews_this_month = serializers.IntegerField()
    installs_by_date = serializers.ListField(child=serializers.DictField())
    revenue_by_date = serializers.ListField(child=serializers.DictField())
