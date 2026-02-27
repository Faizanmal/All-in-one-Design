from rest_framework import serializers
from .models import PublishedSite

class PublishedSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishedSite
        fields = ['id', 'project_id', 'subdomain', 'custom_domain', 'status', 'published_url', 'last_published_at', 'created_at']
        read_only_fields = ['id', 'status', 'published_url', 'last_published_at', 'created_at']

    def validate_subdomain(self, value):
        # Basic subdomain validation (lowercase, alphanumeric, hyphens)
        import re
        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', value):
            raise serializers.ValidationError("Subdomain can only contain lowercase letters, numbers, and hyphens.")
        return value
