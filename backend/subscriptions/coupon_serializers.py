"""
Serializers for Subscription enhancements
"""
from rest_framework import serializers
from .models import Coupon, CouponUsage


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for coupons"""
    is_valid = serializers.BooleanField(read_only=True)
    uses_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'name', 'description',
            'discount_type', 'discount_value',
            'valid_from', 'valid_until',
            'max_uses', 'max_uses_per_user', 'current_uses',
            'applicable_tiers', 'is_active', 'is_valid',
            'uses_remaining', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_uses', 'created_at', 'updated_at']
    
    def get_uses_remaining(self, obj):
        if obj.max_uses is None:
            return None
        return max(0, obj.max_uses - obj.current_uses)


class CouponValidationSerializer(serializers.Serializer):
    """Serializer for validating coupon codes"""
    code = serializers.CharField(max_length=50)
    
    def validate_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value)
            if not coupon.is_valid():
                raise serializers.ValidationError("This coupon is no longer valid.")
            return value
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")


class CouponUsageSerializer(serializers.ModelSerializer):
    """Serializer for coupon usage tracking"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = [
            'id', 'coupon', 'coupon_code', 'user', 'user_name',
            'subscription', 'discount_amount', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
