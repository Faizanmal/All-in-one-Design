"""
Smart Tools Views

REST API endpoints for smart selection and batch operations.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import json

from .models import (
    SmartSelectionPreset, BatchOperation, RenameTemplate,
    FindReplaceOperation, ResizePreset, SelectionHistory, MagicWand
)
from .serializers import (
    SmartSelectionPresetSerializer, SmartSelectionQuerySerializer,
    SelectSimilarSerializer, BatchOperationSerializer,
    BatchRenameRequestSerializer, RenameTemplateSerializer,
    FindReplaceRequestSerializer, FindReplaceOperationSerializer,
    BatchResizeRequestSerializer, ResizePresetSerializer,
    SelectionHistorySerializer, MagicWandSerializer,
    MagicWandSelectSerializer, BatchStyleChangeSerializer
)
from .services import (
    SmartSelectionService, BatchRenameService,
    FindReplaceService, BatchResizeService
)
from projects.models import Project, DesignComponent


class SmartSelectionPresetViewSet(viewsets.ModelViewSet):
    """ViewSet for smart selection presets."""
    
    serializer_class = SmartSelectionPresetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Include user presets and system presets
        return SmartSelectionPreset.objects.filter(
            user=self.request.user
        ) | SmartSelectionPreset.objects.filter(is_system=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.is_system:
            raise permissions.PermissionDenied("Cannot delete system presets")
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Mark a preset as used (updates usage stats)."""
        preset = self.get_object()
        preset.use_count += 1
        preset.last_used = timezone.now()
        preset.save()
        return Response(SmartSelectionPresetSerializer(preset).data)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status."""
        preset = self.get_object()
        preset.is_favorite = not preset.is_favorite
        preset.save()
        return Response(SmartSelectionPresetSerializer(preset).data)


class SmartSelectionView(APIView):
    """Execute smart selection queries."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = SmartSelectionQuerySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        project_id = data['project_id']
        
        # Get project
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        # Get components
        components = DesignComponent.objects.filter(project=project)
        components_data = [
            {
                'id': c.id,
                'component_type': c.component_type,
                'name': c.properties.get('name', f'{c.component_type}_{c.id}'),
                'properties': c.properties,
                'is_visible': c.properties.get('is_visible', True),
                'is_locked': c.properties.get('is_locked', False)
            }
            for c in components
        ]
        
        # Build query from preset or direct parameters
        query = data.get('query', {})
        
        if data.get('preset_id'):
            preset = get_object_or_404(SmartSelectionPreset, id=data['preset_id'])
            query = preset.query
            
            # Update preset usage
            preset.use_count += 1
            preset.last_used = timezone.now()
            preset.save()
        
        # Add quick selection parameters
        if data.get('layer_types'):
            query['layer_types'] = data['layer_types']
        if data.get('name_pattern'):
            query['name_pattern'] = data['name_pattern']
        if data.get('color'):
            query['color'] = data['color']
            query['color_tolerance'] = data.get('color_tolerance', 0)
        if data.get('font_family'):
            query['font_family'] = data['font_family']
        
        # Execute selection
        criteria = SmartSelectionService.parse_query(query)
        selected = [
            c for c in components_data
            if SmartSelectionService.matches_criteria(c, criteria)
        ]
        
        # Record selection history
        SelectionHistory.objects.create(
            user=request.user,
            project=project,
            selection_query=query,
            selected_ids=[c['id'] for c in selected],
            component_count=len(selected)
        )
        
        return Response({
            'selected_count': len(selected),
            'component_ids': [c['id'] for c in selected],
            'components': selected
        })


class SelectSimilarView(APIView):
    """Select components similar to a target component."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = SelectSimilarSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        project = get_object_or_404(Project, id=data['project_id'], user=request.user)
        
        target = get_object_or_404(DesignComponent, id=data['component_id'], project=project)
        target_data = {
            'id': target.id,
            'component_type': target.component_type,
            'properties': target.properties
        }
        
        # Get all components
        components = DesignComponent.objects.filter(project=project)
        components_data = [
            {
                'id': c.id,
                'component_type': c.component_type,
                'properties': c.properties
            }
            for c in components
        ]
        
        # Build match options
        match_options = {
            'match_type': data['match_type'],
            'match_fill': data['match_fill'],
            'match_stroke': data['match_stroke'],
            'match_font': data['match_font'],
            'match_size': data['match_size'],
            'color_tolerance': data['color_tolerance'],
            'size_tolerance': data['size_tolerance']
        }
        
        # Find similar
        similar = SmartSelectionService.select_similar(target_data, components_data, match_options)
        
        return Response({
            'target_id': target.id,
            'similar_count': len(similar),
            'component_ids': [c['id'] for c in similar]
        })


class BatchRenameView(APIView):
    """Batch rename components."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = BatchRenameRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        project = get_object_or_404(Project, id=data['project_id'], user=request.user)
        
        # Get components in order
        components = DesignComponent.objects.filter(
            project=project,
            id__in=data['component_ids']
        ).order_by('z_index')
        
        components_data = [
            {
                'id': c.id,
                'name': c.properties.get('name', f'{c.component_type}_{c.id}'),
                'component_type': c.component_type,
                'properties': c.properties
            }
            for c in components
        ]
        
        # Generate new names
        new_names = BatchRenameService.generate_names(
            components_data,
            data['pattern'],
            data['start_number'],
            data['number_step'],
            data['case_transform']
        )
        
        # Check for duplicates
        duplicates = BatchRenameService.find_duplicates(components_data, new_names)
        
        if data['preview_only']:
            return Response({
                'preview': [
                    {'id': id, 'old_name': c['name'], 'new_name': name}
                    for (id, name), c in zip(new_names, components_data)
                ],
                'duplicates': duplicates,
                'has_duplicates': len(duplicates) > 0
            })
        
        # Store previous state for undo
        previous_state = {str(c['id']): {'name': c['name']} for c in components_data}
        
        # Apply renames
        with transaction.atomic():
            for component, (_, new_name) in zip(components, new_names):
                props = component.properties
                props['name'] = new_name
                component.properties = props
                component.save()
            
            # Record operation
            operation = BatchOperation.objects.create(
                user=request.user,
                project=project,
                operation_type='rename',
                status='completed',
                component_ids=[c['id'] for c in components_data],
                component_count=len(components_data),
                operation_data={
                    'pattern': data['pattern'],
                    'start_number': data['start_number'],
                    'case_transform': data['case_transform']
                },
                previous_state=previous_state,
                success_count=len(new_names),
                completed_at=timezone.now()
            )
        
        return Response({
            'operation': BatchOperationSerializer(operation).data,
            'renamed': [
                {'id': id, 'new_name': name}
                for id, name in new_names
            ]
        }, status=status.HTTP_200_OK)


class RenameTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for rename templates."""
    
    serializer_class = RenameTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RenameTemplate.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview template with sample names."""
        template = self.get_object()
        
        sample_components = [
            {'name': 'Button Primary', 'type': 'button', 'width': 120, 'height': 40},
            {'name': 'Icon Star', 'type': 'icon', 'width': 24, 'height': 24},
            {'name': 'Text Heading', 'type': 'text', 'width': 200, 'height': 30},
        ]
        
        previews = []
        for i, comp in enumerate(sample_components):
            new_name = template.apply_to_name(comp['name'], i, comp)
            previews.append({
                'original': comp['name'],
                'renamed': new_name
            })
        
        return Response({'previews': previews})


class FindReplaceView(APIView):
    """Find and replace operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = FindReplaceRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        project = get_object_or_404(Project, id=data['project_id'], user=request.user)
        
        # Get components based on scope
        if data['scope'] == 'selection':
            components = DesignComponent.objects.filter(
                project=project,
                id__in=data.get('component_ids', [])
            )
        else:
            components = DesignComponent.objects.filter(project=project)
        
        components_data = [
            {
                'id': c.id,
                'name': c.properties.get('name', ''),
                'properties': c.properties
            }
            for c in components
        ]
        
        target_type = data['target_type']
        find_value = data['find_value']
        replace_value = data['replace_value']
        
        if target_type == 'text':
            matches = FindReplaceService.find_text(
                components_data, find_value,
                data['case_sensitive'], data['whole_word'], data['use_regex']
            )
        elif target_type == 'layer_name':
            # Search in names
            for c in components_data:
                c['properties']['text'] = c['name']  # Temporarily for matching
            matches = FindReplaceService.find_text(
                components_data, find_value,
                data['case_sensitive'], data['whole_word'], data['use_regex']
            )
        elif target_type == 'color':
            matches = FindReplaceService.find_colors(
                components_data, find_value, data['color_tolerance']
            )
        else:
            matches = []
        
        if data['preview_only']:
            return Response({
                'matches': [
                    {
                        'component_id': m['component'].get('id'),
                        'match_count': m.get('match_count', len(m.get('matches', [])))
                    }
                    for m in matches
                ],
                'total_matches': sum(m.get('match_count', len(m.get('matches', []))) for m in matches)
            })
        
        # Perform replacements
        previous_state = {}
        replacements_made = 0
        
        with transaction.atomic():
            for match_info in matches:
                comp_id = match_info['component']['id']
                component = DesignComponent.objects.get(id=comp_id)
                
                # Store previous state
                previous_state[str(comp_id)] = {
                    'properties': component.properties.copy()
                }
                
                props = component.properties
                
                if target_type == 'text':
                    text = props.get('text', '')
                    new_text, count = FindReplaceService.replace_text(
                        text, find_value, replace_value,
                        data['case_sensitive'], data['whole_word'], data['use_regex']
                    )
                    props['text'] = new_text
                    replacements_made += count
                
                elif target_type == 'layer_name':
                    name = props.get('name', '')
                    new_name, count = FindReplaceService.replace_text(
                        name, find_value, replace_value,
                        data['case_sensitive'], data['whole_word'], data['use_regex']
                    )
                    props['name'] = new_name
                    replacements_made += count
                
                elif target_type == 'color':
                    # Replace colors
                    for match in match_info.get('matches', []):
                        prop = match['property']
                        props[prop] = replace_value
                        replacements_made += 1
                
                component.properties = props
                component.save()
            
            # Record operation
            operation = FindReplaceOperation.objects.create(
                user=request.user,
                project=project,
                target_type=target_type,
                scope=data['scope'],
                find_value=find_value,
                replace_value=replace_value,
                use_regex=data['use_regex'],
                case_sensitive=data['case_sensitive'],
                whole_word=data['whole_word'],
                color_tolerance=data.get('color_tolerance', 0),
                matches_found=len(matches),
                replacements_made=replacements_made,
                affected_components=[m['component']['id'] for m in matches],
                previous_state=previous_state
            )
        
        return Response({
            'operation': FindReplaceOperationSerializer(operation).data,
            'replacements_made': replacements_made
        })


class BatchResizeView(APIView):
    """Batch resize operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = BatchResizeRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        project = get_object_or_404(Project, id=data['project_id'], user=request.user)
        
        components = DesignComponent.objects.filter(
            project=project,
            id__in=data['component_ids']
        )
        
        components_data = [
            {
                'id': c.id,
                'properties': c.properties
            }
            for c in components
        ]
        
        # Build constraints
        constraints = {}
        if data.get('min_width'):
            constraints['min_width'] = data['min_width']
        if data.get('max_width'):
            constraints['max_width'] = data['max_width']
        if data.get('min_height'):
            constraints['min_height'] = data['min_height']
        if data.get('max_height'):
            constraints['max_height'] = data['max_height']
        
        # Calculate new sizes
        resize_results = BatchResizeService.batch_resize(
            components_data,
            data['resize_mode'],
            data.get('width'),
            data.get('height'),
            data.get('scale_x', 1.0),
            data.get('scale_y', 1.0),
            data['maintain_aspect_ratio'],
            data['anchor'],
            data['round_to_pixels'],
            constraints if constraints else None
        )
        
        if data['preview_only']:
            return Response({
                'preview': resize_results
            })
        
        # Store previous state and apply resizes
        previous_state = {}
        
        with transaction.atomic():
            for result in resize_results:
                component = DesignComponent.objects.get(id=result['id'])
                
                previous_state[str(result['id'])] = {
                    'size': result['old_size'],
                    'position': result['old_position']
                }
                
                props = component.properties
                props['size'] = result['new_size']
                props['position'] = result['new_position']
                component.properties = props
                component.save()
            
            # Record operation
            operation = BatchOperation.objects.create(
                user=request.user,
                project=project,
                operation_type='resize',
                status='completed',
                component_ids=data['component_ids'],
                component_count=len(data['component_ids']),
                operation_data={
                    'resize_mode': data['resize_mode'],
                    'width': data.get('width'),
                    'height': data.get('height'),
                    'scale_x': data.get('scale_x'),
                    'scale_y': data.get('scale_y'),
                    'maintain_aspect_ratio': data['maintain_aspect_ratio'],
                    'anchor': data['anchor']
                },
                previous_state=previous_state,
                success_count=len(resize_results),
                completed_at=timezone.now()
            )
        
        return Response({
            'operation': BatchOperationSerializer(operation).data,
            'resized': resize_results
        })


class ResizePresetViewSet(viewsets.ModelViewSet):
    """ViewSet for resize presets."""
    
    serializer_class = ResizePresetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ResizePreset.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MagicWandViewSet(viewsets.ModelViewSet):
    """ViewSet for magic wand settings."""
    
    serializer_class = MagicWandSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MagicWand.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MagicWandSelectView(APIView):
    """Execute magic wand selection."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = MagicWandSelectSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        project = get_object_or_404(Project, id=data['project_id'], user=request.user)
        
        # Get source component
        source = get_object_or_404(
            DesignComponent,
            id=data['source_component_id'],
            project=project
        )
        
        # Get magic wand settings
        settings, _ = MagicWand.objects.get_or_create(
            user=request.user,
            project=project
        )
        
        # Override with request data if provided
        color_tolerance = data.get('color_tolerance', settings.color_tolerance)
        match_fill = data.get('match_fill', settings.match_fill)
        match_stroke = data.get('match_stroke', settings.match_stroke)
        match_font = data.get('match_font', settings.match_font)
        
        # Get all components
        components = DesignComponent.objects.filter(project=project)
        components_data = [
            {
                'id': c.id,
                'component_type': c.component_type,
                'properties': c.properties
            }
            for c in components
        ]
        
        source_data = {
            'id': source.id,
            'component_type': source.component_type,
            'properties': source.properties
        }
        
        # Find similar using magic wand
        similar = SmartSelectionService.select_similar(
            source_data,
            components_data,
            {
                'match_type': True,
                'match_fill': match_fill,
                'match_stroke': match_stroke,
                'match_font': match_font,
                'color_tolerance': color_tolerance
            }
        )
        
        return Response({
            'source_id': source.id,
            'selected_count': len(similar) + 1,  # Include source
            'component_ids': [source.id] + [c['id'] for c in similar]
        })


class BatchStyleChangeView(APIView):
    """Batch style change operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = BatchStyleChangeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        project = get_object_or_404(Project, id=data['project_id'], user=request.user)
        
        components = DesignComponent.objects.filter(
            project=project,
            id__in=data['component_ids']
        )
        
        # Build style changes
        style_changes = {}
        if 'fill_color' in data:
            style_changes['fill_color'] = data['fill_color']
        if 'stroke_color' in data:
            style_changes['stroke_color'] = data['stroke_color']
        if 'stroke_width' in data:
            style_changes['stroke_width'] = data['stroke_width']
        if 'opacity' in data:
            style_changes['opacity'] = data['opacity']
        if 'font_family' in data:
            style_changes['font_family'] = data['font_family']
        if 'font_size' in data:
            style_changes['font_size'] = data['font_size']
        if 'font_weight' in data:
            style_changes['font_weight'] = data['font_weight']
        if 'text_color' in data:
            style_changes['color'] = data['text_color']
        
        if data['preview_only']:
            return Response({
                'preview': {
                    'component_count': components.count(),
                    'style_changes': style_changes
                }
            })
        
        # Store previous state and apply changes
        previous_state = {}
        
        with transaction.atomic():
            for component in components:
                previous_state[str(component.id)] = {
                    'properties': component.properties.copy()
                }
                
                props = component.properties
                for key, value in style_changes.items():
                    props[key] = value
                component.properties = props
                component.save()
            
            # Record operation
            operation = BatchOperation.objects.create(
                user=request.user,
                project=project,
                operation_type='style',
                status='completed',
                component_ids=data['component_ids'],
                component_count=len(data['component_ids']),
                operation_data={'style_changes': style_changes},
                previous_state=previous_state,
                success_count=components.count(),
                completed_at=timezone.now()
            )
        
        return Response({
            'operation': BatchOperationSerializer(operation).data,
            'changed_count': components.count()
        })


class BatchOperationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for batch operation history."""
    
    serializer_class = BatchOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = BatchOperation.objects.filter(user=self.request.user)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        operation_type = self.request.query_params.get('type')
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)
        
        return queryset[:100]
    
    @action(detail=True, methods=['post'])
    def undo(self, request, pk=None):
        """Undo a batch operation."""
        operation = self.get_object()
        
        if operation.status == 'undone':
            return Response(
                {'error': 'Operation already undone'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Restore previous state
            for comp_id, prev_state in operation.previous_state.items():
                try:
                    component = DesignComponent.objects.get(id=int(comp_id))
                    
                    if 'properties' in prev_state:
                        component.properties = prev_state['properties']
                    else:
                        # Handle specific property restorations
                        props = component.properties
                        if 'name' in prev_state:
                            props['name'] = prev_state['name']
                        if 'size' in prev_state:
                            props['size'] = prev_state['size']
                        if 'position' in prev_state:
                            props['position'] = prev_state['position']
                        component.properties = props
                    
                    component.save()
                except DesignComponent.DoesNotExist:
                    pass
            
            operation.status = 'undone'
            operation.save()
        
        return Response({'message': 'Operation undone successfully'})


class SelectionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for selection history."""
    
    serializer_class = SelectionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SelectionHistory.objects.filter(user=self.request.user)[:50]
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get selection suggestions based on history."""
        project_id = request.query_params.get('project')
        
        # Get recent selections
        history = SelectionHistory.objects.filter(
            user=request.user
        )
        if project_id:
            history = history.filter(project_id=project_id)
        history = history[:20]
        
        # Analyze common patterns
        query_counts = {}
        for h in history:
            query_str = json.dumps(h.selection_query, sort_keys=True)
            query_counts[query_str] = query_counts.get(query_str, 0) + 1
        
        # Sort by frequency
        sorted_queries = sorted(
            query_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        suggestions = [
            {
                'query': json.loads(q),
                'frequency': count
            }
            for q, count in sorted_queries
        ]
        
        return Response({'suggestions': suggestions})
