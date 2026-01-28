from rest_framework import serializers
from .models import (
    FontFamily, FontVariant, FontCollection, IconSet, Icon,
    AssetLibrary, LibraryAsset, AssetVersion, StockProvider,
    StockSearch, ColorPalette, GradientPreset
)


class FontVariantSerializer(serializers.ModelSerializer):
    weight_display = serializers.CharField(source='get_weight_display', read_only=True)
    
    class Meta:
        model = FontVariant
        fields = [
            'id', 'weight', 'weight_display', 'style',
            'woff2_file', 'woff_file', 'ttf_file', 'otf_file', 'css_url'
        ]
        read_only_fields = ['id']


class FontFamilySerializer(serializers.ModelSerializer):
    variants = FontVariantSerializer(many=True, read_only=True)
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FontFamily
        fields = [
            'id', 'name', 'slug', 'category', 'source', 'source_url',
            'google_font_id', 'designer', 'foundry', 'tags',
            'languages_supported', 'license_type', 'commercial_use',
            'is_global', 'preview_text', 'variants', 'variant_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_variant_count(self, obj):
        return obj.variants.count()


class FontCollectionSerializer(serializers.ModelSerializer):
    font_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FontCollection
        fields = [
            'id', 'name', 'description', 'fonts', 'pairings',
            'is_public', 'font_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_font_count(self, obj):
        return obj.fonts.count()


class IconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Icon
        fields = [
            'id', 'name', 'slug', 'svg_content', 'png_file',
            'tags', 'category', 'usage_count'
        ]
        read_only_fields = ['id', 'usage_count']


class IconSetSerializer(serializers.ModelSerializer):
    icon_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = IconSet
        fields = [
            'id', 'name', 'slug', 'description', 'source', 'source_url',
            'version', 'style', 'grid_size', 'stroke_width',
            'license_type', 'commercial_use', 'icon_count', 'is_global',
            'created_at'
        ]
        read_only_fields = ['id', 'icon_count', 'created_at']


class IconSetDetailSerializer(IconSetSerializer):
    icons = IconSerializer(many=True, read_only=True)
    
    class Meta(IconSetSerializer.Meta):
        fields = IconSetSerializer.Meta.fields + ['icons']


class AssetVersionSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.ReadOnlyField(source='changed_by.username')
    
    class Meta:
        model = AssetVersion
        fields = [
            'id', 'version_number', 'file', 'change_description',
            'changed_by', 'changed_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LibraryAssetSerializer(serializers.ModelSerializer):
    versions = AssetVersionSerializer(many=True, read_only=True)
    version_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LibraryAsset
        fields = [
            'id', 'library', 'name', 'asset_type', 'file', 'thumbnail',
            'width', 'height', 'file_size', 'mime_type', 'dominant_colors',
            'tags', 'folder', 'ai_description', 'ai_tags',
            'usage_count', 'last_used', 'versions', 'version_count',
            'created_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'mime_type', 'dominant_colors',
            'ai_description', 'ai_tags', 'usage_count', 'last_used', 'created_at'
        ]
    
    def get_version_count(self, obj):
        return obj.versions.count()


class AssetLibrarySerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = AssetLibrary
        fields = [
            'id', 'name', 'description', 'library_type', 'cover_image',
            'tags', 'color', 'is_public', 'shared_with', 'asset_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'asset_count', 'created_at', 'updated_at']


class StockProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProvider
        fields = [
            'id', 'name', 'slug', 'api_base_url',
            'supports_images', 'supports_videos', 'supports_vectors',
            'supports_audio', 'requires_attribution', 'is_active'
        ]
        read_only_fields = ['id']


class StockSearchSerializer(serializers.ModelSerializer):
    provider_name = serializers.ReadOnlyField(source='provider.name')
    
    class Meta:
        model = StockSearch
        fields = [
            'id', 'query', 'provider', 'provider_name',
            'filters', 'result_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ColorPaletteSerializer(serializers.ModelSerializer):
    color_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ColorPalette
        fields = [
            'id', 'name', 'description', 'colors', 'source',
            'source_image', 'tags', 'is_public', 'color_count',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_color_count(self, obj):
        return len(obj.colors)


class GradientPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradientPreset
        fields = [
            'id', 'name', 'gradient_type', 'stops', 'angle',
            'css_value', 'is_global', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
