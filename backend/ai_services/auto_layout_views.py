"""
Auto-Layout API Views

REST API endpoints for the smart auto-layout engine.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from projects.models import Project, DesignComponent
from .auto_layout_service import AutoLayoutEngine, LayoutConstraint, AlignmentType


class AutoLayoutViewSet(viewsets.ViewSet):
    """
    ViewSet for auto-layout operations.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='analyze')
    def analyze_layout(self, request):
        """
        Analyze components and return layout suggestions.
        
        POST /api/v1/ai/layout/analyze/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],  // optional, defaults to all
            "constraints": {
                "min_width": 0,
                "max_width": 1920,
                "padding": 16,
                "gap": 16
            },
            "preferences": {
                "style": "modern",
                "density": "comfortable"
            }
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids')
        constraints_data = request.data.get('constraints', {})
        preferences = request.data.get('preferences', {})
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        # Get components
        queryset = DesignComponent.objects.filter(project=project)
        if component_ids:
            queryset = queryset.filter(id__in=component_ids)
        
        components = [
            {
                'id': str(comp.id),
                'component_type': comp.component_type,
                'properties': comp.properties,
                'z_index': comp.z_index,
            }
            for comp in queryset
        ]
        
        if not components:
            return Response(
                {'error': 'No components found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create layout engine
        engine = AutoLayoutEngine(
            canvas_width=project.canvas_width,
            canvas_height=project.canvas_height
        )
        
        # Create constraints
        constraints = LayoutConstraint(
            min_width=constraints_data.get('min_width', 0),
            max_width=constraints_data.get('max_width', 9999),
            min_height=constraints_data.get('min_height', 0),
            max_height=constraints_data.get('max_height', 9999),
            padding=constraints_data.get('padding', 16),
            gap=constraints_data.get('gap', 16),
        )
        
        # Get analysis
        analysis = engine.analyze_components(components)
        
        # Get suggestions
        suggestions = engine.suggest_layouts(components, constraints, preferences)
        
        return Response({
            'project_id': project_id,
            'analysis': analysis,
            'suggestions': [
                {
                    'layout_type': s.layout_type.value,
                    'confidence': s.confidence,
                    'properties': s.properties,
                    'reasoning': s.reasoning,
                    'preview': s.preview_data,
                }
                for s in suggestions
            ]
        })
    
    @action(detail=False, methods=['post'], url_path='apply')
    def apply_layout(self, request):
        """
        Apply a layout suggestion to components.
        
        POST /api/v1/ai/layout/apply/
        {
            "project_id": 1,
            "layout_type": "grid",
            "layout_properties": {...},
            "positions": [...]
        }
        """
        project_id = request.data.get('project_id')
        positions = request.data.get('positions', [])
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        # Update component positions
        updated_count = 0
        for pos in positions:
            try:
                component = DesignComponent.objects.get(
                    id=int(pos['id']),
                    project=project
                )
                component.properties['position'] = {
                    'x': pos['x'],
                    'y': pos['y']
                }
                component.properties['size'] = {
                    'width': pos['width'],
                    'height': pos['height']
                }
                component.save()
                updated_count += 1
            except (DesignComponent.DoesNotExist, ValueError, KeyError):
                continue
        
        return Response({
            'success': True,
            'updated_count': updated_count,
            'message': f'Applied layout to {updated_count} components'
        })
    
    @action(detail=False, methods=['post'], url_path='align')
    def align_components(self, request):
        """
        Align selected components.
        
        POST /api/v1/ai/layout/align/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "alignment": "center",  // left, center, right
            "distribute": true
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        alignment = request.data.get('alignment', 'left')
        distribute = request.data.get('distribute', False)
        
        if not project_id or not component_ids:
            return Response(
                {'error': 'project_id and component_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        components = DesignComponent.objects.filter(
            project=project,
            id__in=component_ids
        )
        
        if not components.exists():
            return Response(
                {'error': 'No components found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        comp_list = [
            {
                'id': str(c.id),
                'properties': c.properties,
            }
            for c in components
        ]
        
        engine = AutoLayoutEngine(project.canvas_width, project.canvas_height)
        
        # Map alignment string to enum
        alignment_map = {
            'left': AlignmentType.LEFT,
            'center': AlignmentType.CENTER,
            'right': AlignmentType.RIGHT,
        }
        align_type = alignment_map.get(alignment, AlignmentType.LEFT)
        
        # Align components
        aligned = engine.auto_align(comp_list, align_type, distribute)
        
        # Update in database
        for item in aligned:
            try:
                comp = components.get(id=int(item['id']))
                comp.properties = item['properties']
                comp.save()
            except (DesignComponent.DoesNotExist, ValueError):
                continue
        
        return Response({
            'success': True,
            'aligned_components': aligned
        })
    
    @action(detail=False, methods=['post'], url_path='snap-to-grid')
    def snap_to_grid(self, request):
        """
        Snap components to a grid.
        
        POST /api/v1/ai/layout/snap-to-grid/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "grid_size": 8
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        grid_size = request.data.get('grid_size', 8)
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        queryset = DesignComponent.objects.filter(project=project)
        if component_ids:
            queryset = queryset.filter(id__in=component_ids)
        
        comp_list = [
            {
                'id': str(c.id),
                'properties': c.properties,
            }
            for c in queryset
        ]
        
        engine = AutoLayoutEngine(project.canvas_width, project.canvas_height)
        snapped = engine.snap_to_grid(comp_list, grid_size)
        
        # Update in database
        for item in snapped:
            try:
                comp = queryset.get(id=int(item['id']))
                comp.properties = item['properties']
                comp.save()
            except (DesignComponent.DoesNotExist, ValueError):
                continue
        
        return Response({
            'success': True,
            'grid_size': grid_size,
            'snapped_components': snapped
        })
    
    @action(detail=False, methods=['post'], url_path='auto-spacing')
    def auto_spacing(self, request):
        """
        Automatically apply consistent spacing between components.
        
        POST /api/v1/ai/layout/auto-spacing/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "spacing": 16,
            "direction": "vertical"  // vertical, horizontal
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        spacing = request.data.get('spacing', 16)
        direction = request.data.get('direction', 'vertical')
        
        if not project_id or not component_ids:
            return Response(
                {'error': 'project_id and component_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        components = list(DesignComponent.objects.filter(
            project=project,
            id__in=component_ids
        ))
        
        if len(components) < 2:
            return Response(
                {'error': 'At least 2 components required for spacing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sort by position
        if direction == 'vertical':
            components.sort(key=lambda c: c.properties.get('position', {}).get('y', 0))
        else:
            components.sort(key=lambda c: c.properties.get('position', {}).get('x', 0))
        
        # Apply spacing
        results = []
        for i, comp in enumerate(components):
            if i == 0:
                results.append({
                    'id': comp.id,
                    'position': comp.properties.get('position', {'x': 0, 'y': 0})
                })
                continue
            
            prev_comp = components[i - 1]
            prev_pos = prev_comp.properties.get('position', {'x': 0, 'y': 0})
            prev_size = prev_comp.properties.get('size', {'width': 100, 'height': 100})
            curr_pos = comp.properties.get('position', {'x': 0, 'y': 0}).copy()
            
            if direction == 'vertical':
                curr_pos['y'] = prev_pos['y'] + prev_size['height'] + spacing
            else:
                curr_pos['x'] = prev_pos['x'] + prev_size['width'] + spacing
            
            comp.properties['position'] = curr_pos
            comp.save()
            
            results.append({
                'id': comp.id,
                'position': curr_pos
            })
        
        return Response({
            'success': True,
            'spacing': spacing,
            'direction': direction,
            'components': results
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_layout_presets(request):
    """
    Get available layout presets.
    
    GET /api/v1/ai/layout/presets/
    """
    presets = [
        {
            'id': 'landing-hero',
            'name': 'Landing Page Hero',
            'description': 'Full-width hero section with centered content',
            'thumbnail': '/static/presets/landing-hero.png',
            'category': 'landing',
        },
        {
            'id': 'feature-grid',
            'name': 'Feature Grid',
            'description': '3-column grid for features or benefits',
            'thumbnail': '/static/presets/feature-grid.png',
            'category': 'sections',
        },
        {
            'id': 'pricing-table',
            'name': 'Pricing Table',
            'description': 'Side-by-side pricing comparison',
            'thumbnail': '/static/presets/pricing-table.png',
            'category': 'sections',
        },
        {
            'id': 'testimonial-carousel',
            'name': 'Testimonial Carousel',
            'description': 'Customer testimonials with avatars',
            'thumbnail': '/static/presets/testimonial.png',
            'category': 'sections',
        },
        {
            'id': 'blog-grid',
            'name': 'Blog Grid',
            'description': 'Masonry-style blog post grid',
            'thumbnail': '/static/presets/blog-grid.png',
            'category': 'content',
        },
        {
            'id': 'contact-split',
            'name': 'Contact Split',
            'description': 'Form on one side, info on the other',
            'thumbnail': '/static/presets/contact-split.png',
            'category': 'forms',
        },
        {
            'id': 'dashboard-cards',
            'name': 'Dashboard Cards',
            'description': 'Stats cards with consistent sizing',
            'thumbnail': '/static/presets/dashboard-cards.png',
            'category': 'dashboard',
        },
        {
            'id': 'mobile-app-screen',
            'name': 'Mobile App Screen',
            'description': 'Standard mobile app layout',
            'thumbnail': '/static/presets/mobile-app.png',
            'category': 'mobile',
        },
    ]
    
    # Filter by category if provided
    category = request.query_params.get('category')
    if category:
        presets = [p for p in presets if p['category'] == category]
    
    return Response({
        'presets': presets,
        'categories': ['landing', 'sections', 'content', 'forms', 'dashboard', 'mobile']
    })
