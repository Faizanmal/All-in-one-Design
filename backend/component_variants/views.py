"""
Views for Component Variants app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import (
    ComponentSet, ComponentProperty, PropertyOption,
    ComponentVariant, VariantOverride, ComponentInstance,
    InteractiveState, ComponentSlot
)
from .serializers import (
    ComponentSetSerializer, ComponentSetListSerializer,
    ComponentPropertySerializer, PropertyOptionSerializer,
    ComponentVariantSerializer, VariantOverrideSerializer,
    ComponentInstanceSerializer, InteractiveStateSerializer,
    ComponentSlotSerializer, VariantMatchSerializer, SwapVariantSerializer
)


class ComponentSetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing component sets."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'design_system', 'category', 'is_published']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ComponentSetListSerializer
        return ComponentSetSerializer
    
    def get_queryset(self):
        user = self.request.user
        return ComponentSet.objects.filter(
            Q(project__owner=user) | 
            Q(project__team__members=user) |
            Q(is_published=True)
        ).distinct().prefetch_related('properties', 'variants')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_property(self, request, pk=None):
        """Add a property to the component set."""
        component_set = self.get_object()
        serializer = ComponentPropertySerializer(data={
            **request.data,
            'component_set': component_set.id
        })
        if serializer.is_valid():
            serializer.save(component_set=component_set)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_variant(self, request, pk=None):
        """Add a variant to the component set."""
        component_set = self.get_object()
        serializer = ComponentVariantSerializer(data={
            **request.data,
            'component_set': component_set.id
        })
        if serializer.is_valid():
            serializer.save(component_set=component_set)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def find_variant(self, request, pk=None):
        """Find variant matching property values."""
        component_set = self.get_object()
        serializer = VariantMatchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        properties = serializer.validated_data['properties']
        variants = component_set.variants.all()
        
        # Find best matching variant
        best_match = None
        best_score = -1
        
        for variant in variants:
            variant_props = variant.property_values or {}
            score = sum(
                1 for k, v in properties.items()
                if variant_props.get(k) == v
            )
            if score > best_score:
                best_score = score
                best_match = variant
        
        if best_match:
            return Response(ComponentVariantSerializer(best_match).data)
        return Response({'detail': 'No matching variant found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish the component set."""
        component_set = self.get_object()
        component_set.is_published = True
        component_set.save()
        return Response({'status': 'published'})
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish the component set."""
        component_set = self.get_object()
        component_set.is_published = False
        component_set.save()
        return Response({'status': 'unpublished'})
    
    @action(detail=True, methods=['get'])
    def instances(self, request, pk=None):
        """Get all instances of this component set."""
        component_set = self.get_object()
        instances = ComponentInstance.objects.filter(
            variant__component_set=component_set
        )
        serializer = ComponentInstanceSerializer(instances, many=True)
        return Response(serializer.data)


class ComponentPropertyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing component properties."""
    serializer_class = ComponentPropertySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['component_set', 'property_type', 'is_required']
    ordering_fields = ['order', 'name']
    ordering = ['order']
    
    def get_queryset(self):
        user = self.request.user
        return ComponentProperty.objects.filter(
            Q(component_set__project__owner=user) |
            Q(component_set__project__team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def add_option(self, request, pk=None):
        """Add an option to this property."""
        property_obj = self.get_object()
        if property_obj.property_type != 'variant':
            return Response(
                {'error': 'Options can only be added to variant properties'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PropertyOptionSerializer(data={
            **request.data,
            'property': property_obj.id
        })
        if serializer.is_valid():
            serializer.save(property=property_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyOptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing property options."""
    serializer_class = PropertyOptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property', 'is_default']
    ordering = ['order']
    
    def get_queryset(self):
        user = self.request.user
        return PropertyOption.objects.filter(
            Q(property__component_set__project__owner=user) |
            Q(property__component_set__project__team__members=user)
        ).distinct()


class ComponentVariantViewSet(viewsets.ModelViewSet):
    """ViewSet for managing component variants."""
    serializer_class = ComponentVariantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['component_set', 'is_default']
    search_fields = ['name', 'description']
    ordering = ['order']
    
    def get_queryset(self):
        user = self.request.user
        return ComponentVariant.objects.filter(
            Q(component_set__project__owner=user) |
            Q(component_set__project__team__members=user)
        ).distinct().prefetch_related('overrides', 'interactive_states', 'slots')
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this variant as the default."""
        variant = self.get_object()
        # Unset current default
        ComponentVariant.objects.filter(
            component_set=variant.component_set,
            is_default=True
        ).update(is_default=False)
        variant.is_default = True
        variant.save()
        return Response({'status': 'set as default'})
    
    @action(detail=True, methods=['post'])
    def add_state(self, request, pk=None):
        """Add an interactive state to this variant."""
        variant = self.get_object()
        serializer = InteractiveStateSerializer(data={
            **request.data,
            'variant': variant.id
        })
        if serializer.is_valid():
            serializer.save(variant=variant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate this variant."""
        variant = self.get_object()
        new_variant = ComponentVariant.objects.create(
            component_set=variant.component_set,
            name=f"{variant.name} (copy)",
            description=variant.description,
            property_values=variant.property_values,
            base_node_data=variant.base_node_data,
            style_overrides=variant.style_overrides,
            order=variant.order + 1,
        )
        return Response(ComponentVariantSerializer(new_variant).data, status=status.HTTP_201_CREATED)


class VariantOverrideViewSet(viewsets.ModelViewSet):
    """ViewSet for managing variant overrides."""
    serializer_class = VariantOverrideSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['variant', 'override_type']
    
    def get_queryset(self):
        user = self.request.user
        return VariantOverride.objects.filter(
            Q(variant__component_set__project__owner=user) |
            Q(variant__component_set__project__team__members=user)
        ).distinct()


class ComponentInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing component instances."""
    serializer_class = ComponentInstanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['variant', 'is_detached']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return ComponentInstance.objects.filter(
            Q(variant__component_set__project__owner=user) |
            Q(variant__component_set__project__team__members=user)
        ).distinct().select_related('variant', 'variant__component_set')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def swap_variant(self, request, pk=None):
        """Swap the variant for this instance."""
        instance = self.get_object()
        serializer = SwapVariantSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_variant_id = serializer.validated_data['new_variant_id']
        preserve_overrides = serializer.validated_data['preserve_overrides']
        
        try:
            new_variant = ComponentVariant.objects.get(id=new_variant_id)
        except ComponentVariant.DoesNotExist:
            return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not preserve_overrides:
            instance.property_overrides = {}
        
        instance.variant = new_variant
        instance.save()
        
        return Response(ComponentInstanceSerializer(instance).data)
    
    @action(detail=True, methods=['post'])
    def detach(self, request, pk=None):
        """Detach instance from its component."""
        instance = self.get_object()
        instance.is_detached = True
        instance.save()
        return Response({'status': 'detached'})
    
    @action(detail=True, methods=['post'])
    def reset_overrides(self, request, pk=None):
        """Reset all property overrides."""
        instance = self.get_object()
        instance.property_overrides = {}
        instance.save()
        return Response(ComponentInstanceSerializer(instance).data)


class InteractiveStateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing interactive states."""
    serializer_class = InteractiveStateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['variant', 'state_type', 'is_enabled']
    
    def get_queryset(self):
        user = self.request.user
        return InteractiveState.objects.filter(
            Q(variant__component_set__project__owner=user) |
            Q(variant__component_set__project__team__members=user)
        ).distinct()


class ComponentSlotViewSet(viewsets.ModelViewSet):
    """ViewSet for managing component slots."""
    serializer_class = ComponentSlotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['variant']
    ordering = ['order']
    
    def get_queryset(self):
        user = self.request.user
        return ComponentSlot.objects.filter(
            Q(variant__component_set__project__owner=user) |
            Q(variant__component_set__project__team__members=user)
        ).distinct()
