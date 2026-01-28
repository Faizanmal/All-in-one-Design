from django.contrib import admin
from .models import (
    PluginCategory, Plugin, PluginVersion, PluginInstallation, PluginReview,
    PluginPurchase, DeveloperProfile, APIEndpoint, WebhookSubscription,
    PluginLog, PluginSandbox
)


@admin.register(PluginCategory)
class PluginCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


class PluginVersionInline(admin.TabularInline):
    model = PluginVersion
    extra = 0
    readonly_fields = ['download_count', 'created_at']


@admin.register(Plugin)
class PluginAdmin(admin.ModelAdmin):
    list_display = ['name', 'developer', 'category', 'status', 'pricing_type', 'install_count', 'rating_average']
    list_filter = ['status', 'category', 'pricing_type', 'created_at']
    search_fields = ['name', 'developer__username', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PluginVersionInline]
    readonly_fields = ['id', 'install_count', 'active_installs', 'rating_average', 'rating_count', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'developer', 'category', 'tagline', 'description')
        }),
        ('Media', {
            'fields': ('icon', 'banner', 'screenshots')
        }),
        ('Version', {
            'fields': ('current_version', 'min_platform_version', 'source_url', 'package_url')
        }),
        ('Status', {
            'fields': ('status', 'published_at')
        }),
        ('Pricing', {
            'fields': ('pricing_type', 'price', 'price_currency')
        }),
        ('Stats', {
            'fields': ('install_count', 'active_installs', 'rating_average', 'rating_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('tags', 'features', 'requirements', 'permissions'),
            'classes': ('collapse',)
        }),
        ('Support', {
            'fields': ('documentation_url', 'support_email', 'changelog_url'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PluginVersion)
class PluginVersionAdmin(admin.ModelAdmin):
    list_display = ['plugin', 'version', 'is_stable', 'is_deprecated', 'download_count', 'created_at']
    list_filter = ['is_stable', 'is_deprecated', 'created_at']
    search_fields = ['plugin__name', 'version']


@admin.register(PluginInstallation)
class PluginInstallationAdmin(admin.ModelAdmin):
    list_display = ['user', 'plugin', 'version', 'is_enabled', 'installed_at']
    list_filter = ['is_enabled', 'auto_update', 'installed_at']
    search_fields = ['user__username', 'plugin__name']


@admin.register(PluginReview)
class PluginReviewAdmin(admin.ModelAdmin):
    list_display = ['plugin', 'user', 'rating', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_featured', 'created_at']
    search_fields = ['plugin__name', 'user__username', 'content']


@admin.register(PluginPurchase)
class PluginPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'plugin', 'amount', 'currency', 'is_refunded', 'purchased_at']
    list_filter = ['is_subscription', 'is_refunded', 'purchased_at']
    search_fields = ['user__username', 'plugin__name', 'transaction_id']


@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user', 'is_verified', 'total_plugins', 'total_installs']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['display_name', 'user__username']


@admin.register(APIEndpoint)
class APIEndpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'method', 'path', 'api_version', 'is_deprecated']
    list_filter = ['method', 'api_version', 'is_deprecated']
    search_fields = ['name', 'path']


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['plugin', 'event_type', 'is_active', 'last_triggered', 'failure_count']
    list_filter = ['event_type', 'is_active']


@admin.register(PluginSandbox)
class PluginSandboxAdmin(admin.ModelAdmin):
    list_display = ['name', 'developer', 'plugin', 'is_active', 'expires_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'developer__username']
