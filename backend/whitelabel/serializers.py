from rest_framework import serializers
from .models import (
    Agency, AgencyMember, Client, ClientPortal, ClientFeedback,
    APIKey, AgencyBilling, AgencyInvoice, BrandLibrary
)


class AgencyMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    
    class Meta:
        model = AgencyMember
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'role', 'permissions', 'invited_by', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']


class AgencySerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.username')
    member_count = serializers.SerializerMethodField()
    client_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Agency
        fields = [
            'id', 'owner', 'owner_name', 'name', 'slug', 'description',
            'logo', 'logo_dark', 'favicon',
            'primary_color', 'secondary_color', 'accent_color',
            'custom_domain', 'domain_verified',
            'email', 'website', 'phone', 'address',
            'white_label_enabled', 'remove_branding', 'custom_email_templates',
            'client_limit', 'project_limit', 'storage_limit_gb',
            'member_count', 'client_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'domain_verified', 'created_at', 'updated_at']
    
    def get_member_count(self, obj) -> int:
        return obj.members.count()
    
    def get_client_count(self, obj) -> int:
        return obj.clients.count()


class AgencyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['name', 'slug', 'description', 'email', 'website']


class ClientPortalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPortal
        fields = [
            'id', 'is_active', 'access_token', 'token_expires',
            'welcome_message', 'custom_css', 'visible_projects',
            'allow_comments', 'allow_approvals',
            'last_accessed', 'access_count', 'created_at'
        ]
        read_only_fields = ['id', 'access_token', 'last_accessed', 'access_count', 'created_at']


class ClientSerializer(serializers.ModelSerializer):
    portal = ClientPortalSerializer(read_only=True)
    feedback_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'agency', 'name', 'email', 'company',
            'portal_enabled', 'phone', 'address', 'notes',
            'logo', 'brand_colors', 'tags', 'portal',
            'feedback_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_feedback_count(self, obj) -> int:
        return obj.feedback.count()


class ClientFeedbackSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.name')
    
    class Meta:
        model = ClientFeedback
        fields = [
            'id', 'client', 'client_name', 'project', 'feedback_type',
            'content', 'position_x', 'position_y', 'page_number',
            'is_resolved', 'resolved_by', 'resolved_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = [
            'id', 'agency', 'name', 'key', 'permissions',
            'rate_limit', 'last_used', 'usage_count',
            'is_active', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'key', 'last_used', 'usage_count', 'created_at']
        extra_kwargs = {'secret': {'write_only': True}}


class AgencyBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyBilling
        fields = [
            'id', 'agency', 'plan', 'status',
            'billing_email', 'billing_address',
            'current_period_start', 'current_period_end',
            'current_usage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_usage', 'created_at', 'updated_at']


class AgencyInvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.name')
    
    class Meta:
        model = AgencyInvoice
        fields = [
            'id', 'agency', 'client', 'client_name', 'invoice_number',
            'subtotal', 'tax', 'total', 'currency', 'status',
            'issue_date', 'due_date', 'paid_date',
            'line_items', 'notes', 'pdf_file', 'created_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'pdf_file', 'created_at']


class BrandLibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandLibrary
        fields = [
            'id', 'agency', 'client', 'name', 'description',
            'logos', 'colors', 'fonts', 'guidelines', 'assets',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
