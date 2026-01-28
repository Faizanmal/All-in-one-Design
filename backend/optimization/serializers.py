from rest_framework import serializers
from .models import (
    ABTest, ABTestVariant, PerformanceAnalysis, DeviceCompatibility,
    UserBehaviorPrediction, SmartLayoutSuggestion, OptimizationReport
)


class ABTestVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ABTestVariant
        fields = [
            'id', 'name', 'description', 'design_data', 'screenshot',
            'weight', 'impressions', 'conversions', 'clicks',
            'engagement_score', 'conversion_rate', 'click_rate',
            'is_control', 'created_at'
        ]
        read_only_fields = ['id', 'impressions', 'conversions', 'clicks',
                          'engagement_score', 'conversion_rate', 'click_rate', 'created_at']


class ABTestSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    variants = ABTestVariantSerializer(many=True, read_only=True)
    winner_variant_name = serializers.ReadOnlyField(source='winner_variant.name')
    
    class Meta:
        model = ABTest
        fields = [
            'id', 'user', 'project', 'name', 'description',
            'status', 'goal', 'goal_description',
            'traffic_percentage', 'start_date', 'end_date',
            'winner_variant', 'winner_variant_name', 'confidence_level',
            'ai_recommendations', 'variants',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'winner_variant', 'confidence_level',
                          'ai_recommendations', 'created_at', 'updated_at']


class ABTestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ABTest
        fields = ['project', 'name', 'description', 'goal', 'goal_description', 'traffic_percentage']


class PerformanceAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceAnalysis
        fields = [
            'id', 'project', 'analysis_type', 'overall_score',
            'results', 'ai_suggestions', 'created_at'
        ]
        read_only_fields = ['id', 'overall_score', 'results', 'ai_suggestions', 'created_at']


class DeviceCompatibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceCompatibility
        fields = [
            'id', 'project', 'devices_tested', 'device_results',
            'screenshots', 'overall_score', 'issues', 'created_at'
        ]
        read_only_fields = ['id', 'device_results', 'screenshots', 'overall_score', 'issues', 'created_at']


class UserBehaviorPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehaviorPrediction
        fields = [
            'id', 'project', 'attention_heatmap', 'click_predictions',
            'scroll_depth_prediction', 'predicted_engagement_score',
            'predicted_bounce_rate', 'predicted_time_on_page',
            'predicted_conversion_rate', 'conversion_barriers',
            'recommendations', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SmartLayoutSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartLayoutSuggestion
        fields = [
            'id', 'project', 'content_type', 'content_description',
            'target_audience', 'brand_style', 'suggestions',
            'selected_suggestion_index', 'created_at'
        ]
        read_only_fields = ['id', 'suggestions', 'created_at']


class OptimizationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizationReport
        fields = [
            'id', 'project', 'overall_score', 'performance_score',
            'accessibility_score', 'usability_score', 'seo_score',
            'performance_analysis', 'accessibility_analysis',
            'usability_analysis', 'seo_analysis',
            'critical_issues', 'major_issues', 'minor_issues',
            'recommendations', 'quick_wins', 'industry_benchmark',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
