from rest_framework import serializers
from .models import BrandKitEnforcement, BrandViolationLog

class BrandKitEnforcementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandKitEnforcement
        fields = ['id', 'design_system', 'lock_color_picker', 'force_ai_variants', 'lock_typography', 'require_approval', 'log_violations', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class BrandViolationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandViolationLog
        fields = ['id', 'enforcement', 'user', 'event_type', 'details', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']
