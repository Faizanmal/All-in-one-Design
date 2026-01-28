from rest_framework import serializers
from .models import (
    PluginCategory, Plugin, PluginVersion, PluginInstallation, PluginReview,
    PluginPurchase, DeveloperProfile, APIEndpoint, WebhookSubscription,
    PluginLog, PluginSandbox
)


class PluginCategorySerializer(serializers.ModelSerializer):
    plugin_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PluginCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'order', 'plugin_count']
        read_only_fields = ['id']
    
    def get_plugin_count(self, obj):
        return obj.plugins.filter(status='published').count()


class PluginVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PluginVersion
        fields = [
            'id', 'version', 'release_notes', 'is_stable', 'is_deprecated',
            'package_file', 'package_size', 'checksum_sha256',
            'min_platform_version', 'max_platform_version',
            'download_count', 'created_at'
        ]
        read_only_fields = ['id', 'download_count', 'created_at']


class PluginSerializer(serializers.ModelSerializer):
    developer_name = serializers.ReadOnlyField(source='developer.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    current_version_info = PluginVersionSerializer(source='versions.first', read_only=True)
    
    class Meta:
        model = Plugin
        fields = [
            'id', 'developer', 'developer_name', 'category', 'category_name',
            'name', 'slug', 'tagline', 'description', 'icon', 'banner',
            'screenshots', 'current_version', 'min_platform_version',
            'source_url', 'status', 'published_at',
            'pricing_type', 'price', 'price_currency',
            'install_count', 'active_installs', 'rating_average', 'rating_count',
            'tags', 'features', 'requirements', 'permissions',
            'documentation_url', 'support_email', 'current_version_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'developer', 'status', 'published_at',
            'install_count', 'active_installs', 'rating_average', 'rating_count',
            'created_at', 'updated_at'
        ]


class PluginDetailSerializer(PluginSerializer):
    versions = PluginVersionSerializer(many=True, read_only=True)
    
    class Meta(PluginSerializer.Meta):
        fields = PluginSerializer.Meta.fields + ['versions']


class PluginInstallationSerializer(serializers.ModelSerializer):
    plugin_name = serializers.ReadOnlyField(source='plugin.name')
    plugin_icon = serializers.ImageField(source='plugin.icon', read_only=True)
    current_version = serializers.ReadOnlyField(source='version.version')
    
    class Meta:
        model = PluginInstallation
        fields = [
            'id', 'plugin', 'plugin_name', 'plugin_icon', 'version',
            'current_version', 'is_enabled', 'auto_update', 'settings',
            'installed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'installed_at', 'updated_at']


class PluginReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = PluginReview
        fields = [
            'id', 'plugin', 'user', 'user_name', 'rating', 'title', 'content',
            'version', 'helpful_count', 'developer_response',
            'developer_responded_at', 'is_featured', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'helpful_count', 'developer_response',
            'developer_responded_at', 'is_featured', 'created_at', 'updated_at'
        ]


class PluginPurchaseSerializer(serializers.ModelSerializer):
    plugin_name = serializers.ReadOnlyField(source='plugin.name')
    
    class Meta:
        model = PluginPurchase
        fields = [
            'id', 'plugin', 'plugin_name', 'amount', 'currency',
            'payment_method', 'transaction_id', 'is_subscription',
            'subscription_expires', 'is_refunded', 'purchased_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'purchased_at']


class DeveloperProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = DeveloperProfile
        fields = [
            'id', 'user', 'username', 'display_name', 'bio', 'avatar',
            'website', 'github_url', 'twitter_url', 'is_verified',
            'total_plugins', 'total_installs', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'is_verified', 'total_plugins', 'total_installs',
            'created_at', 'updated_at'
        ]


class APIEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIEndpoint
        fields = [
            'id', 'name', 'path', 'method', 'description',
            'parameters', 'response_schema', 'required_permissions',
            'api_version', 'is_deprecated'
        ]
        read_only_fields = ['id']


class WebhookSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookSubscription
        fields = [
            'id', 'plugin', 'installation', 'event_type', 'callback_url',
            'is_active', 'last_triggered', 'failure_count', 'created_at'
        ]
        read_only_fields = ['id', 'last_triggered', 'failure_count', 'created_at']
        extra_kwargs = {'secret': {'write_only': True}}


class PluginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PluginLog
        fields = ['id', 'level', 'message', 'details', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class PluginSandboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PluginSandbox
        fields = [
            'id', 'plugin', 'name', 'settings', 'test_project_id',
            'is_active', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']
