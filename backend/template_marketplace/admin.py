from django.contrib import admin
from .models import (
    TemplateCategory, MarketplaceTemplate, TemplateReview,
    TemplatePurchase, CreatorProfile, CreatorPayout,
    TemplateCollection
)


@admin.register(TemplateCategory)
class TemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MarketplaceTemplate)
class MarketplaceTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'category', 'pricing_type', 'price', 'status', 'downloads']
    list_filter = ['status', 'pricing_type', 'is_featured', 'category']
    search_fields = ['title', 'description', 'creator__username']
    prepopulated_fields = {'slug': ('title',)}
    actions = ['approve_templates', 'reject_templates']
    
    def approve_templates(self, request, queryset):
        queryset.update(status='approved', published_at=timezone.now())
    approve_templates.short_description = "Approve selected templates"
    
    def reject_templates(self, request, queryset):
        queryset.update(status='rejected')
    reject_templates.short_description = "Reject selected templates"


@admin.register(TemplateReview)
class TemplateReviewAdmin(admin.ModelAdmin):
    list_display = ['template', 'user', 'rating', 'is_verified_purchase', 'is_visible', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_visible']
    search_fields = ['template__title', 'user__username', 'content']


@admin.register(TemplatePurchase)
class TemplatePurchaseAdmin(admin.ModelAdmin):
    list_display = ['template', 'user', 'amount', 'status', 'purchased_at']
    list_filter = ['status', 'purchased_at']
    search_fields = ['template__title', 'user__username']


@admin.register(CreatorProfile)
class CreatorProfileAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user', 'is_verified', 'is_pro', 'total_sales', 'total_earnings']
    list_filter = ['is_verified', 'is_pro']
    search_fields = ['display_name', 'user__username']


@admin.register(CreatorPayout)
class CreatorPayoutAdmin(admin.ModelAdmin):
    list_display = ['creator', 'amount', 'status', 'period_start', 'period_end']
    list_filter = ['status', 'created_at']


@admin.register(TemplateCollection)
class TemplateCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


from django.utils import timezone
