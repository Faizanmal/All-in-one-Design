from rest_framework import serializers
from .models import (
    PDFExportPreset, PDFExport, PrintProfile,
    SpreadView, ImpositionLayout, PDFTemplate
)


class PDFExportPresetSerializer(serializers.ModelSerializer):
    """Serializer for PDF export presets"""
    
    class Meta:
        model = PDFExportPreset
        fields = [
            'id', 'name', 'description', 'is_default',
            'paper_size', 'custom_width', 'custom_height', 'orientation',
            'color_mode', 'icc_profile',
            'bleed_enabled', 'bleed_top', 'bleed_bottom', 'bleed_left', 'bleed_right',
            'crop_marks', 'bleed_marks', 'registration_marks', 'color_bars', 'page_info',
            'mark_offset', 'mark_weight',
            'pdf_standard', 'quality', 'compress_images', 'image_quality',
            'embed_fonts', 'subset_fonts',
            'password_protect', 'allow_printing', 'allow_copying',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PDFExportSerializer(serializers.ModelSerializer):
    """Serializer for PDF exports"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    preset_name = serializers.CharField(source='preset.name', read_only=True)
    
    class Meta:
        model = PDFExport
        fields = [
            'id', 'user', 'project', 'project_name', 'preset', 'preset_name',
            'pages', 'page_range', 'export_settings',
            'status', 'progress', 'error_message',
            'file_url', 'file_size', 'page_count',
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'user', 'status', 'progress', 'error_message',
            'file_url', 'file_size', 'page_count',
            'created_at', 'started_at', 'completed_at'
        ]


class PDFExportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PDF exports"""
    
    class Meta:
        model = PDFExport
        fields = ['project', 'preset', 'pages', 'page_range', 'export_settings']
    
    def validate(self, data):
        # Validate page range format if provided
        page_range = data.get('page_range')
        if page_range:
            try:
                self._parse_page_range(page_range)
            except ValueError as e:
                raise serializers.ValidationError({'page_range': str(e)})
        return data
    
    def _parse_page_range(self, range_str):
        """Parse page range string like '1-5, 8, 10-12'"""
        pages = []
        parts = range_str.replace(' ', '').split(',')
        
        for part in parts:
            if '-' in part:
                start, end = part.split('-', 1)
                start = int(start)
                end = int(end)
                if start > end:
                    raise ValueError(f"Invalid range: {part}")
                pages.extend(range(start, end + 1))
            else:
                pages.append(int(part))
        
        return sorted(set(pages))


class PrintProfileSerializer(serializers.ModelSerializer):
    """Serializer for print profiles"""
    
    class Meta:
        model = PrintProfile
        fields = [
            'id', 'name', 'profile_type', 'description',
            'recommended_dpi', 'recommended_color_mode', 'recommended_bleed',
            'pdf_standard', 'icc_profile', 'icc_profile_url',
            'settings', 'is_active', 'created_at'
        ]


class SpreadViewSerializer(serializers.ModelSerializer):
    """Serializer for spread views"""
    
    class Meta:
        model = SpreadView
        fields = [
            'id', 'project', 'name', 'spread_type', 'pages',
            'gutter', 'spine_width', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ImpositionLayoutSerializer(serializers.ModelSerializer):
    """Serializer for imposition layouts"""
    
    class Meta:
        model = ImpositionLayout
        fields = [
            'id', 'name', 'imposition_type', 'description',
            'sheet_width', 'sheet_height',
            'columns', 'rows',
            'margin_top', 'margin_bottom', 'margin_left', 'margin_right',
            'horizontal_gap', 'vertical_gap',
            'page_ordering', 'is_active', 'created_at'
        ]


class PDFTemplateSerializer(serializers.ModelSerializer):
    """Serializer for PDF templates"""
    
    class Meta:
        model = PDFTemplate
        fields = [
            'id', 'name',
            'header_enabled', 'header_content', 'header_height',
            'footer_enabled', 'footer_content', 'footer_height',
            'page_numbers', 'page_number_position', 'page_number_format', 'start_page_number',
            'watermark_enabled', 'watermark_text', 'watermark_image', 'watermark_opacity',
            'background_color', 'background_image',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class QuickExportSerializer(serializers.Serializer):
    """Serializer for quick PDF export"""
    project_id = serializers.IntegerField()
    pages = serializers.ListField(child=serializers.IntegerField(), required=False)
    paper_size = serializers.ChoiceField(
        choices=['letter', 'legal', 'tabloid', 'a3', 'a4', 'a5'],
        default='letter'
    )
    orientation = serializers.ChoiceField(
        choices=['portrait', 'landscape'],
        default='portrait'
    )
    color_mode = serializers.ChoiceField(
        choices=['rgb', 'cmyk', 'grayscale'],
        default='rgb'
    )
    quality = serializers.IntegerField(min_value=72, max_value=600, default=300)
    with_bleed = serializers.BooleanField(default=False)
    bleed_amount = serializers.DecimalField(max_digits=6, decimal_places=2, default=3.0)
    with_crop_marks = serializers.BooleanField(default=False)


class PreflightCheckSerializer(serializers.Serializer):
    """Serializer for preflight check results"""
    passed = serializers.BooleanField()
    warnings = serializers.ListField(child=serializers.DictField())
    errors = serializers.ListField(child=serializers.DictField())
    info = serializers.DictField()
