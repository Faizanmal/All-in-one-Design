from rest_framework import serializers
from .models import Asset, ColorPalette, FontFamily


class AssetSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ('user', 'file_url', 'file_size', 'created_at')


class AssetUploadSerializer(serializers.Serializer):
    """Serializer for file uploads"""
    file = serializers.FileField(required=True)
    name = serializers.CharField(max_length=255, required=False)
    asset_type = serializers.ChoiceField(
        choices=['image', 'icon', 'font', 'video', 'audio', 'svg'],
        required=True
    )
    project_id = serializers.IntegerField(required=False, allow_null=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )


class ColorPaletteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ColorPalette
        fields = '__all__'
        read_only_fields = ('created_by', 'use_count', 'created_at')


class FontFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = FontFamily
        fields = '__all__'
        read_only_fields = ('created_at',)
