"""
Serializers for Component Variants app.
"""
from rest_framework import serializers
from .models import (
    ComponentSet, ComponentProperty, PropertyOption,
    ComponentVariant, VariantOverride, ComponentInstance,
    InteractiveState, ComponentSlot
)


class PropertyOptionSerializer(serializers.ModelSerializer):
    """Serializer for property options."""
    
    class Meta:
        model = PropertyOption
        fields = [
            'id', 'property', 'value', 'label', 'description',
            'icon', 'is_default', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ComponentPropertySerializer(serializers.ModelSerializer):
    """Serializer for component properties."""
    options = PropertyOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = ComponentProperty
        fields = [
            'id', 'component_set', 'name', 'property_type', 'description',
            'default_value', 'default_boolean', 'min_value', 'max_value',
            'step', 'preferred_values', 'is_required', 'order',
            'created_at', 'updated_at', 'options'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InteractiveStateSerializer(serializers.ModelSerializer):
    """Serializer for interactive states."""
    
    class Meta:
        model = InteractiveState
        fields = [
            'id', 'variant', 'state_type', 'style_overrides',
            'transition_duration', 'transition_easing', 'cursor',
            'is_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VariantOverrideSerializer(serializers.ModelSerializer):
    """Serializer for variant overrides."""
    
    class Meta:
        model = VariantOverride
        fields = [
            'id', 'variant', 'property_path', 'override_type',
            'value', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ComponentSlotSerializer(serializers.ModelSerializer):
    """Serializer for component slots."""
    
    class Meta:
        model = ComponentSlot
        fields = [
            'id', 'variant', 'name', 'description', 'default_content',
            'allowed_types', 'min_items', 'max_items', 'order',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ComponentVariantSerializer(serializers.ModelSerializer):
    """Serializer for component variants."""
    overrides = VariantOverrideSerializer(many=True, read_only=True)
    interactive_states = InteractiveStateSerializer(many=True, read_only=True)
    slots = ComponentSlotSerializer(many=True, read_only=True)
    property_values = serializers.JSONField(read_only=True)
    
    class Meta:
        model = ComponentVariant
        fields = [
            'id', 'component_set', 'name', 'description', 'property_values',
            'is_default', 'thumbnail', 'base_node_data', 'style_overrides',
            'order', 'created_at', 'updated_at', 'overrides',
            'interactive_states', 'slots'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ComponentSetSerializer(serializers.ModelSerializer):
    """Serializer for component sets."""
    properties = ComponentPropertySerializer(many=True, read_only=True)
    variants = ComponentVariantSerializer(many=True, read_only=True)
    variant_count = serializers.SerializerMethodField()
    property_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ComponentSet
        fields = [
            'id', 'project', 'design_system', 'name', 'description',
            'base_component', 'category', 'tags', 'documentation_url',
            'is_published', 'version', 'created_by', 'created_at',
            'updated_at', 'properties', 'variants', 'variant_count',
            'property_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_variant_count(self, obj):
        return obj.variants.count()
    
    def get_property_count(self, obj):
        return obj.properties.count()


class ComponentSetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for component set lists."""
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ComponentSet
        fields = [
            'id', 'name', 'description', 'category', 'tags',
            'is_published', 'version', 'variant_count', 'updated_at'
        ]
    
    def get_variant_count(self, obj):
        return obj.variants.count()


class ComponentInstanceSerializer(serializers.ModelSerializer):
    """Serializer for component instances."""
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    component_set_name = serializers.CharField(source='variant.component_set.name', read_only=True)
    computed_properties = serializers.SerializerMethodField()
    
    class Meta:
        model = ComponentInstance
        fields = [
            'id', 'variant', 'variant_name', 'component_set_name',
            'parent_node_id', 'position_x', 'position_y', 'width',
            'height', 'rotation', 'property_overrides', 'slot_content',
            'is_detached', 'created_by', 'created_at', 'updated_at',
            'computed_properties'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_computed_properties(self, obj):
        """Merge variant properties with instance overrides."""
        base_props = obj.variant.property_values or {}
        overrides = obj.property_overrides or {}
        return {**base_props, **overrides}


class VariantMatchSerializer(serializers.Serializer):
    """Serializer for variant matching request."""
    properties = serializers.JSONField()


class SwapVariantSerializer(serializers.Serializer):
    """Serializer for variant swap request."""
    new_variant_id = serializers.UUIDField()
    preserve_overrides = serializers.BooleanField(default=True)
