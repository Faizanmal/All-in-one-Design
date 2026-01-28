from django.contrib import admin
from .models import (
    FontFamily, FontVariant, FontCollection, IconSet, Icon,
    AssetLibrary, LibraryAsset, AssetVersion, StockProvider,
    StockSearch, ColorPalette, GradientPreset
)


class FontVariantInline(admin.TabularInline):
    model = FontVariant
    extra = 1


@admin.register(FontFamily)
class FontFamilyAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'source', 'is_global', 'created_at']
    list_filter = ['category', 'source', 'is_global']
    search_fields = ['name', 'designer', 'foundry']
    inlines = [FontVariantInline]
    prepopulated_fields = {'slug': ('name',)}


@admin.register(FontCollection)
class FontCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'user__username']
    filter_horizontal = ['fonts']


class IconInline(admin.TabularInline):
    model = Icon
    extra = 0
    readonly_fields = ['svg_content']


@admin.register(IconSet)
class IconSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'style', 'icon_count', 'is_global', 'created_at']
    list_filter = ['style', 'is_global']
    search_fields = ['name', 'source']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Icon)
class IconAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_set', 'category', 'usage_count']
    list_filter = ['icon_set', 'category']
    search_fields = ['name', 'tags']


class LibraryAssetInline(admin.TabularInline):
    model = LibraryAsset
    extra = 0


@admin.register(AssetLibrary)
class AssetLibraryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'library_type', 'asset_count', 'is_public', 'created_at']
    list_filter = ['library_type', 'is_public', 'created_at']
    search_fields = ['name', 'user__username']
    filter_horizontal = ['shared_with']


class AssetVersionInline(admin.TabularInline):
    model = AssetVersion
    extra = 0
    readonly_fields = ['version_number', 'created_at']


@admin.register(LibraryAsset)
class LibraryAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'library', 'asset_type', 'file_size', 'usage_count', 'created_at']
    list_filter = ['asset_type', 'library', 'created_at']
    search_fields = ['name', 'tags']
    inlines = [AssetVersionInline]


@admin.register(StockProvider)
class StockProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'supports_images', 'supports_videos', 'is_active']
    list_filter = ['is_active', 'supports_images', 'supports_videos']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(StockSearch)
class StockSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'query', 'result_count', 'created_at']
    list_filter = ['provider', 'created_at']
    search_fields = ['query', 'user__username']


@admin.register(ColorPalette)
class ColorPaletteAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'source', 'is_public', 'created_at']
    list_filter = ['is_public', 'source', 'created_at']
    search_fields = ['name', 'user__username']


@admin.register(GradientPreset)
class GradientPresetAdmin(admin.ModelAdmin):
    list_display = ['name', 'gradient_type', 'is_global', 'created_at']
    list_filter = ['gradient_type', 'is_global']
    search_fields = ['name']
