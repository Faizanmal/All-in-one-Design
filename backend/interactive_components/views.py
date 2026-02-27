"""
Interactive Components Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import (
    InteractiveComponent, ComponentState, ComponentInteraction,
    ComponentVariable, InteractiveTemplate
)
from .serializers import (
    InteractiveComponentSerializer, InteractiveComponentCreateSerializer,
    ComponentStateSerializer, ComponentInteractionSerializer,
    ComponentVariableSerializer, InteractiveTemplateSerializer,
    CreateFromTemplateSerializer, InteractionTestSerializer
)


class InteractiveComponentViewSet(viewsets.ModelViewSet):
    """ViewSet for interactive components."""
    
    serializer_class = InteractiveComponentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = InteractiveComponent.objects.filter(user=self.request.user)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        component_type = self.request.query_params.get('type')
        if component_type:
            queryset = queryset.filter(component_type=component_type)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InteractiveComponentCreateSerializer
        return InteractiveComponentSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_state(self, request, pk=None):
        """Add a new state to the component."""
        component = self.get_object()
        serializer = ComponentStateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(component=component)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_interaction(self, request, pk=None):
        """Add an interaction to the component."""
        component = self.get_object()
        serializer = ComponentInteractionSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(component=component)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_variable(self, request, pk=None):
        """Add a variable to the component."""
        component = self.get_object()
        serializer = ComponentVariableSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(component=component)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate the component with all states and interactions."""
        original = self.get_object()
        
        with transaction.atomic():
            # Duplicate component
            new_component = InteractiveComponent.objects.create(
                project=original.project,
                user=request.user,
                name=f"{original.name} (Copy)",
                component_type=original.component_type,
                description=original.description,
                default_state=original.default_state,
                config=original.config,
                styles=original.styles,
                x=original.x + 20,
                y=original.y + 20,
                width=original.width,
                height=original.height
            )
            
            # Duplicate states
            for state in original.states.all():
                ComponentState.objects.create(
                    component=new_component,
                    name=state.name,
                    description=state.description,
                    properties=state.properties,
                    elements=state.elements,
                    enter_transition=state.enter_transition,
                    exit_transition=state.exit_transition,
                    is_default=state.is_default,
                    order=state.order
                )
            
            # Duplicate interactions
            for interaction in original.interactions.all():
                ComponentInteraction.objects.create(
                    component=new_component,
                    name=interaction.name,
                    trigger_type=interaction.trigger_type,
                    trigger_target=interaction.trigger_target,
                    trigger_config=interaction.trigger_config,
                    condition=interaction.condition,
                    action_type=interaction.action_type,
                    action_config=interaction.action_config,
                    order=interaction.order,
                    is_enabled=interaction.is_enabled
                )
            
            # Duplicate variables
            for variable in original.variables.all():
                ComponentVariable.objects.create(
                    component=new_component,
                    name=variable.name,
                    variable_type=variable.variable_type,
                    default_value=variable.default_value,
                    description=variable.description,
                    min_value=variable.min_value,
                    max_value=variable.max_value,
                    options=variable.options
                )
        
        return Response(
            InteractiveComponentSerializer(new_component).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export component as JSON for sharing."""
        component = self.get_object()
        
        export_data = {
            'name': component.name,
            'component_type': component.component_type,
            'description': component.description,
            'config': component.config,
            'styles': component.styles,
            'width': component.width,
            'height': component.height,
            'states': [
                {
                    'name': s.name,
                    'properties': s.properties,
                    'elements': s.elements,
                    'enter_transition': s.enter_transition,
                    'exit_transition': s.exit_transition,
                    'is_default': s.is_default
                }
                for s in component.states.all()
            ],
            'interactions': [
                {
                    'trigger_type': i.trigger_type,
                    'trigger_config': i.trigger_config,
                    'condition': i.condition,
                    'action_type': i.action_type,
                    'action_config': i.action_config
                }
                for i in component.interactions.all()
            ],
            'variables': [
                {
                    'name': v.name,
                    'variable_type': v.variable_type,
                    'default_value': v.default_value
                }
                for v in component.variables.all()
            ]
        }
        
        return Response(export_data)
    
    @action(detail=False, methods=['post'])
    def import_component(self, request):
        """Import a component from JSON."""
        data = request.data
        project_id = data.get('project_id')
        component_data = data.get('component_data', {})
        
        if not project_id or not component_data:
            return Response(
                {'error': 'project_id and component_data required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            component = InteractiveComponent.objects.create(
                project_id=project_id,
                user=request.user,
                name=component_data.get('name', 'Imported Component'),
                component_type=component_data.get('component_type', 'custom'),
                description=component_data.get('description', ''),
                config=component_data.get('config', {}),
                styles=component_data.get('styles', {}),
                width=component_data.get('width', 200),
                height=component_data.get('height', 100)
            )
            
            # Create states
            for state_data in component_data.get('states', []):
                ComponentState.objects.create(
                    component=component,
                    name=state_data.get('name', 'default'),
                    properties=state_data.get('properties', {}),
                    elements=state_data.get('elements', []),
                    enter_transition=state_data.get('enter_transition', {}),
                    exit_transition=state_data.get('exit_transition', {}),
                    is_default=state_data.get('is_default', False)
                )
            
            # Create interactions
            for int_data in component_data.get('interactions', []):
                ComponentInteraction.objects.create(
                    component=component,
                    trigger_type=int_data.get('trigger_type', 'click'),
                    trigger_config=int_data.get('trigger_config', {}),
                    condition=int_data.get('condition'),
                    action_type=int_data.get('action_type', 'change_state'),
                    action_config=int_data.get('action_config', {})
                )
            
            # Create variables
            for var_data in component_data.get('variables', []):
                ComponentVariable.objects.create(
                    component=component,
                    name=var_data.get('name', 'var'),
                    variable_type=var_data.get('variable_type', 'string'),
                    default_value=var_data.get('default_value')
                )
        
        return Response(
            InteractiveComponentSerializer(component).data,
            status=status.HTTP_201_CREATED
        )


class ComponentStateViewSet(viewsets.ModelViewSet):
    """ViewSet for component states."""
    
    serializer_class = ComponentStateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ComponentState.objects.filter(component__user=self.request.user)


class ComponentInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for component interactions."""
    
    serializer_class = ComponentInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ComponentInteraction.objects.filter(component__user=self.request.user)


class InteractiveTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for interactive templates."""
    
    serializer_class = InteractiveTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = InteractiveTemplate.objects.all()
    
    def get_queryset(self):
        queryset = InteractiveTemplate.objects.all()
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        component_type = self.request.query_params.get('type')
        if component_type:
            queryset = queryset.filter(component_type=component_type)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Create a component from template."""
        template = self.get_object()
        serializer = CreateFromTemplateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        template_data = template.template_data
        
        with transaction.atomic():
            component = InteractiveComponent.objects.create(
                project_id=data['project_id'],
                user=request.user,
                name=data.get('name', template.name),
                component_type=template.component_type,
                description=template.description,
                config=template_data.get('config', {}),
                styles=template_data.get('styles', {}),
                x=data.get('x', 0),
                y=data.get('y', 0),
                width=template_data.get('width', 200),
                height=template_data.get('height', 100)
            )
            
            # Create states from template
            for state_data in template_data.get('states', []):
                ComponentState.objects.create(
                    component=component,
                    **state_data
                )
            
            # Create interactions from template
            for int_data in template_data.get('interactions', []):
                ComponentInteraction.objects.create(
                    component=component,
                    **int_data
                )
        
        return Response(
            InteractiveComponentSerializer(component).data,
            status=status.HTTP_201_CREATED
        )


class InteractionPreviewView(APIView):
    """Preview and test interactions."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = InteractionTestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        component = get_object_or_404(
            InteractiveComponent,
            id=data['component_id'],
            user=request.user
        )
        
        # Find matching interactions
        interactions = component.interactions.filter(
            trigger_type=data['trigger_type'],
            is_enabled=True
        )
        
        results = []
        current_state = data.get('current_state', component.default_state)
        variables = data.get('variables', {})
        
        for interaction in interactions:
            # Check condition
            if interaction.condition:
                # Simple condition evaluation
                var_name = interaction.condition.get('variable')
                operator = interaction.condition.get('operator')
                expected = interaction.condition.get('value')
                actual = variables.get(var_name)
                
                if operator == 'equals' and actual != expected:
                    continue
                elif operator == 'not_equals' and actual == expected:
                    continue
            
            # Simulate action
            action_result = {
                'interaction_id': str(interaction.id),
                'action_type': interaction.action_type,
                'action_config': interaction.action_config
            }
            
            if interaction.action_type == 'change_state':
                action_result['new_state'] = interaction.action_config.get('targetState')
            elif interaction.action_type == 'set_variable':
                action_result['variable_change'] = {
                    'name': interaction.action_config.get('variable'),
                    'value': interaction.action_config.get('value')
                }
            
            results.append(action_result)
        
        return Response({
            'component_id': str(component.id),
            'trigger_type': data['trigger_type'],
            'current_state': current_state,
            'actions': results
        })
