"""
Smart Tools Serializers
"""

from rest_framework import serializers
from .models import (
    SmartSelectionPreset, BatchOperation, RenameTemplate,
    FindReplaceOperation, ResizePreset, SelectionHistory, MagicWand
)


class SmartSelectionPresetSerializer(serializers.ModelSerializer):
    """Serializer for smart selection presets."""
    
    class Meta:
        model = SmartSelectionPreset
        fields = [
            'id', 'name', 'description', 'preset_type', 'query',
            'icon', 'color', 'keyboard_shortcut',
            'use_count', 'last_used', 'is_system', 'is_favorite',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'use_count', 'last_used', 'is_system', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SmartSelectionQuerySerializer(serializers.Serializer):
    """Serializer for smart selection queries."""
    
    project_id = serializers.IntegerField()
    query = serializers.DictField(required=False)
    preset_id = serializers.UUIDField(required=False)
    
    # Quick selection options
    layer_types = serializers.ListField(child=serializers.CharField(), required=False)
    name_pattern = serializers.CharField(required=False)
    color = serializers.CharField(required=False)
    color_tolerance = serializers.IntegerField(default=0, min_value=0, max_value=255)
    font_family = serializers.CharField(required=False)
    
    def validate(self, data):
        if not data.get('query') and not data.get('preset_id') and not any([
            data.get('layer_types'),
            data.get('name_pattern'),
            data.get('color'),
            data.get('font_family')
        ]):
            raise serializers.ValidationError(
                "Either 'query', 'preset_id', or a quick selection option is required"
            )
        return data


class SelectSimilarSerializer(serializers.Serializer):
    """Serializer for select similar operation."""
    
    project_id = serializers.IntegerField()
    component_id = serializers.IntegerField()
    match_type = serializers.BooleanField(default=True)
    match_fill = serializers.BooleanField(default=True)
    match_stroke = serializers.BooleanField(default=False)
    match_font = serializers.BooleanField(default=False)
    match_size = serializers.BooleanField(default=False)
    color_tolerance = serializers.IntegerField(default=0, min_value=0, max_value=255)
    size_tolerance = serializers.FloatField(default=5.0)


class BatchOperationSerializer(serializers.ModelSerializer):
    """Serializer for batch operations."""
    
    class Meta:
        model = BatchOperation
        fields = [
            'id', 'operation_type', 'status',
            'component_ids', 'component_count',
            'operation_data',
            'success_count', 'failure_count', 'error_messages',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'success_count', 'failure_count',
            'error_messages', 'started_at', 'completed_at', 'created_at'
        ]


class BatchRenameRequestSerializer(serializers.Serializer):
    """Serializer for batch rename requests."""
    
    project_id = serializers.IntegerField()
    component_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    pattern = serializers.CharField(max_length=500)
    start_number = serializers.IntegerField(default=1, min_value=0)
    number_step = serializers.IntegerField(default=1, min_value=1)
    case_transform = serializers.ChoiceField(
        choices=[
            ('none', 'No Change'),
            ('lower', 'lowercase'),
            ('upper', 'UPPERCASE'),
            ('title', 'Title Case'),
            ('sentence', 'Sentence case'),
            ('camel', 'camelCase'),
            ('pascal', 'PascalCase'),
            ('snake', 'snake_case'),
            ('kebab', 'kebab-case'),
        ],
        default='none'
    )
    preview_only = serializers.BooleanField(default=False)


class RenameTemplateSerializer(serializers.ModelSerializer):
    """Serializer for rename templates."""
    
    class Meta:
        model = RenameTemplate
        fields = [
            'id', 'name', 'description', 'pattern',
            'start_number', 'number_step', 'preserve_extension',
            'case_transform', 'is_favorite', 'use_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'use_count', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FindReplaceRequestSerializer(serializers.Serializer):
    """Serializer for find and replace requests."""
    
    project_id = serializers.IntegerField()
    target_type = serializers.ChoiceField(choices=[
        ('text', 'Text Content'),
        ('layer_name', 'Layer Names'),
        ('color', 'Colors'),
        ('font', 'Fonts'),
    ])
    scope = serializers.ChoiceField(
        choices=[('selection', 'Selection'), ('page', 'Page'), ('project', 'Project')],
        default='project'
    )
    find_value = serializers.CharField()
    replace_value = serializers.CharField(allow_blank=True)
    
    # Options
    use_regex = serializers.BooleanField(default=False)
    case_sensitive = serializers.BooleanField(default=False)
    whole_word = serializers.BooleanField(default=False)
    color_tolerance = serializers.IntegerField(default=0, min_value=0, max_value=100)
    
    # Selected component IDs for scope='selection'
    component_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    preview_only = serializers.BooleanField(default=False)


class FindReplaceOperationSerializer(serializers.ModelSerializer):
    """Serializer for find/replace operation records."""
    
    class Meta:
        model = FindReplaceOperation
        fields = [
            'id', 'target_type', 'scope',
            'find_value', 'replace_value',
            'use_regex', 'case_sensitive', 'whole_word',
            'color_tolerance',
            'matches_found', 'replacements_made',
            'affected_components', 'created_at'
        ]
        read_only_fields = ['id', 'matches_found', 'replacements_made', 'affected_components', 'created_at']


class BatchResizeRequestSerializer(serializers.Serializer):
    """Serializer for batch resize requests."""
    
    project_id = serializers.IntegerField()
    component_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    
    resize_mode = serializers.ChoiceField(choices=[
        ('absolute', 'Absolute Size'),
        ('scale', 'Scale Factor'),
        ('fit', 'Fit to Size'),
        ('fill', 'Fill to Size'),
        ('width', 'Set Width'),
        ('height', 'Set Height'),
    ])
    
    # Size values
    width = serializers.FloatField(required=False, min_value=1)
    height = serializers.FloatField(required=False, min_value=1)
    scale_x = serializers.FloatField(default=1.0, min_value=0.01, max_value=100)
    scale_y = serializers.FloatField(default=1.0, min_value=0.01, max_value=100)
    
    # Options
    maintain_aspect_ratio = serializers.BooleanField(default=True)
    anchor = serializers.ChoiceField(
        choices=[
            ('top-left', 'Top Left'),
            ('top-center', 'Top Center'),
            ('top-right', 'Top Right'),
            ('center-left', 'Center Left'),
            ('center', 'Center'),
            ('center-right', 'Center Right'),
            ('bottom-left', 'Bottom Left'),
            ('bottom-center', 'Bottom Center'),
            ('bottom-right', 'Bottom Right'),
        ],
        default='center'
    )
    round_to_pixels = serializers.BooleanField(default=True)
    
    # Constraints
    min_width = serializers.FloatField(required=False, min_value=1)
    min_height = serializers.FloatField(required=False, min_value=1)
    max_width = serializers.FloatField(required=False)
    max_height = serializers.FloatField(required=False)
    
    preview_only = serializers.BooleanField(default=False)


class ResizePresetSerializer(serializers.ModelSerializer):
    """Serializer for resize presets."""
    
    class Meta:
        model = ResizePreset
        fields = [
            'id', 'name', 'description', 'resize_mode',
            'width', 'height', 'scale_x', 'scale_y',
            'maintain_aspect_ratio', 'anchor', 'round_to_pixels',
            'min_width', 'min_height', 'max_width', 'max_height',
            'is_favorite', 'use_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'use_count', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SelectionHistorySerializer(serializers.ModelSerializer):
    """Serializer for selection history."""
    
    class Meta:
        model = SelectionHistory
        fields = [
            'id', 'project', 'selection_query',
            'selected_ids', 'component_count',
            'action_taken', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MagicWandSerializer(serializers.ModelSerializer):
    """Serializer for magic wand settings."""
    
    class Meta:
        model = MagicWand
        fields = [
            'id', 'project', 'color_tolerance',
            'include_similar_fonts', 'include_similar_sizes',
            'size_tolerance', 'search_scope',
            'match_fill', 'match_stroke', 'match_font', 'match_effects',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MagicWandSelectSerializer(serializers.Serializer):
    """Serializer for magic wand selection."""
    
    project_id = serializers.IntegerField()
    source_component_id = serializers.IntegerField()
    
    # Override settings (optional)
    color_tolerance = serializers.IntegerField(required=False, min_value=0, max_value=255)
    match_fill = serializers.BooleanField(required=False)
    match_stroke = serializers.BooleanField(required=False)
    match_font = serializers.BooleanField(required=False)
    search_scope = serializers.ChoiceField(
        choices=[('page', 'Page'), ('project', 'Project'), ('selection', 'Selection')],
        required=False
    )


class BatchStyleChangeSerializer(serializers.Serializer):
    """Serializer for batch style changes."""
    
    project_id = serializers.IntegerField()
    component_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    
    # Style changes (only provided fields will be changed)
    fill_color = serializers.CharField(required=False)
    stroke_color = serializers.CharField(required=False)
    stroke_width = serializers.FloatField(required=False, min_value=0)
    opacity = serializers.FloatField(required=False, min_value=0, max_value=1)
    
    # Text styles
    font_family = serializers.CharField(required=False)
    font_size = serializers.FloatField(required=False, min_value=1)
    font_weight = serializers.IntegerField(required=False)
    text_color = serializers.CharField(required=False)
    
    # Effects
    add_shadow = serializers.DictField(required=False)
    remove_shadow = serializers.BooleanField(required=False)
    
    preview_only = serializers.BooleanField(default=False)


class AlignDistributeSerializer(serializers.Serializer):
    """Serializer for align/distribute operations."""
    
    project_id = serializers.IntegerField()
    component_ids = serializers.ListField(child=serializers.IntegerField(), min_length=2)
    
    operation = serializers.ChoiceField(choices=[
        ('align-left', 'Align Left'),
        ('align-center-h', 'Align Center Horizontal'),
        ('align-right', 'Align Right'),
        ('align-top', 'Align Top'),
        ('align-center-v', 'Align Center Vertical'),
        ('align-bottom', 'Align Bottom'),
        ('distribute-h', 'Distribute Horizontal'),
        ('distribute-v', 'Distribute Vertical'),
        ('space-h', 'Space Horizontal'),
        ('space-v', 'Space Vertical'),
    ])
    
    # Optional spacing for space operations
    spacing = serializers.FloatField(required=False, min_value=0)


class BatchOperationUndoSerializer(serializers.Serializer):
    """Serializer for undoing batch operations."""
    
    operation_id = serializers.UUIDField()
