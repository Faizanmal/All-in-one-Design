from django.contrib import admin
from .models import (
    Agency, AgencyMember, Client, ClientPortal, ClientFeedback,
    APIKey, AgencyBilling, AgencyInvoice, BrandLibrary
)


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'custom_domain', 'white_label_enabled', 'created_at']
    list_filter = ['white_label_enabled', 'domain_verified', 'created_at']
    search_fields = ['name', 'owner__username', 'custom_domain']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AgencyMember)
class AgencyMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'agency', 'role', 'joined_at']
    list_filter = ['role', 'agency']
    search_fields = ['user__username', 'agency__name']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'agency', 'email', 'company', 'portal_enabled', 'created_at']
    list_filter = ['portal_enabled', 'agency', 'created_at']
    search_fields = ['name', 'email', 'company']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ClientPortal)
class ClientPortalAdmin(admin.ModelAdmin):
    list_display = ['client', 'is_active', 'last_accessed', 'access_count']
    list_filter = ['is_active']
    readonly_fields = ['id', 'access_token', 'created_at']


@admin.register(ClientFeedback)
class ClientFeedbackAdmin(admin.ModelAdmin):
    list_display = ['client', 'project', 'feedback_type', 'is_resolved', 'created_at']
    list_filter = ['feedback_type', 'is_resolved', 'created_at']
    search_fields = ['client__name', 'content']
    readonly_fields = ['id', 'created_at']


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'agency', 'is_active', 'last_used', 'usage_count', 'created_at']
    list_filter = ['is_active', 'agency', 'created_at']
    search_fields = ['name', 'agency__name']
    readonly_fields = ['id', 'key', 'created_at']


@admin.register(AgencyBilling)
class AgencyBillingAdmin(admin.ModelAdmin):
    list_display = ['agency', 'plan', 'status', 'current_period_end']
    list_filter = ['plan', 'status']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AgencyInvoice)
class AgencyInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'agency', 'client', 'total', 'status', 'due_date']
    list_filter = ['status', 'agency', 'created_at']
    search_fields = ['invoice_number', 'agency__name', 'client__name']
    readonly_fields = ['id', 'created_at']


@admin.register(BrandLibrary)
class BrandLibraryAdmin(admin.ModelAdmin):
    list_display = ['name', 'agency', 'client', 'created_at']
    list_filter = ['agency', 'created_at']
    search_fields = ['name', 'agency__name', 'client__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
