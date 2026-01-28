"""
Interactive Components Serializers
"""

from rest_framework import serializers
from .models import (
    InteractiveComponent, ComponentState, ComponentInteraction,
    ComponentVariable, CarouselItem, DropdownOption,
    AccordionSection, TabItem, InteractiveTemplate
)


class ComponentStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentState
        fields = [
            'id', 'name', 'description', 'properties', 'elements',
            'enter_transition', 'exit_transition', 'is_default', 'order'
        ]


class ComponentInteractionSerializer(serializers.ModelSerializer):
    trigger_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    action_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = ComponentInteraction
        fields = [
            'id', 'name', 'trigger_type', 'trigger_display', 'trigger_target',
            'trigger_config', 'condition', 'action_type', 'action_display',
            'action_config', 'order', 'is_enabled'
        ]


class ComponentVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentVariable
        fields = [
            'id', 'name', 'variable_type', 'default_value',
            'description', 'min_value', 'max_value', 'options'
        ]


class CarouselItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselItem
        fields = ['id', 'content_type', 'content', 'title', 'description', 'link', 'order']


class DropdownOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropdownOption
        fields = ['id', 'label', 'value', 'icon', 'is_disabled', 'is_selected', 'group', 'order']


class AccordionSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccordionSection
        fields = ['id', 'title', 'content', 'icon', 'is_expanded', 'is_disabled', 'order']


class TabItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TabItem
        fields = ['id', 'label', 'content', 'icon', 'badge', 'is_active', 'is_disabled', 'order']


class InteractiveComponentSerializer(serializers.ModelSerializer):
    states = ComponentStateSerializer(many=True, read_only=True)
    interactions = ComponentInteractionSerializer(many=True, read_only=True)
    variables = ComponentVariableSerializer(many=True, read_only=True)
    carousel_items = CarouselItemSerializer(many=True, read_only=True)
    dropdown_options = DropdownOptionSerializer(many=True, read_only=True)
    accordion_sections = AccordionSectionSerializer(many=True, read_only=True)
    tab_items = TabItemSerializer(many=True, read_only=True)
    component_type_display = serializers.CharField(source='get_component_type_display', read_only=True)
    
    class Meta:
        model = InteractiveComponent
        fields = [
            'id', 'project', 'name', 'component_type', 'component_type_display',
            'description', 'default_state', 'config', 'styles',
            'x', 'y', 'width', 'height', 'z_index', 'is_visible', 'is_locked',
            'states', 'interactions', 'variables',
            'carousel_items', 'dropdown_items', 'accordion_sections', 'tab_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class InteractiveComponentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating components."""
    
    class Meta:
        model = InteractiveComponent
        fields = [
            'project', 'name', 'component_type', 'description',
            'config', 'styles', 'x', 'y', 'width', 'height'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        component = super().create(validated_data)
        
        # Create default state
        ComponentState.objects.create(
            component=component,
            name='default',
            is_default=True
        )
        
        return component


class InteractiveTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveTemplate
        fields = [
            'id', 'name', 'description', 'category', 'component_type',
            'template_data', 'preview_image', 'preview_animation',
            'tags', 'is_premium', 'created_at', 'updated_at'
        ]


class CreateFromTemplateSerializer(serializers.Serializer):
    template_id = serializers.UUIDField()
    project_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255, required=False)
    x = serializers.FloatField(default=0)
    y = serializers.FloatField(default=0)


class ComponentPreviewSerializer(serializers.Serializer):
    """For generating component previews."""
    component_id = serializers.UUIDField()
    state = serializers.CharField(required=False)
    width = serializers.IntegerField(default=400)
    height = serializers.IntegerField(default=300)
    format = serializers.ChoiceField(
        choices=['png', 'svg', 'html'],
        default='html'
    )


class InteractionTestSerializer(serializers.Serializer):
    """For testing interactions in preview mode."""
    component_id = serializers.UUIDField()
    trigger_type = serializers.CharField()
    trigger_data = serializers.DictField(required=False)
    current_state = serializers.CharField(required=False)
    variables = serializers.DictField(required=False)
