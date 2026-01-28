from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json

from .models import (
    DesignSystem, DesignToken, ComponentDefinition, ComponentVariant,
    StyleGuide, DocumentationPage, DesignSystemExport, DesignSystemSync
)
from .serializers import (
    DesignSystemListSerializer, DesignSystemDetailSerializer, DesignSystemCreateSerializer,
    DesignTokenSerializer, ComponentDefinitionSerializer, ComponentVariantSerializer,
    StyleGuideSerializer, DocumentationPageSerializer,
    DesignSystemExportSerializer, DesignSystemSyncSerializer, TokenExportSerializer
)


class DesignSystemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing design systems"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = DesignSystem.objects.filter(user=self.request.user)
        
        # Include team design systems
        team_id = self.request.query_params.get('team')
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DesignSystemDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return DesignSystemCreateSerializer
        return DesignSystemListSerializer
    
    def perform_create(self, serializer):
        design_system = serializer.save(user=self.request.user)
        # Create default style guide
        StyleGuide.objects.create(design_system=design_system)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a design system"""
        original = self.get_object()
        
        new_system = DesignSystem.objects.create(
            user=request.user,
            name=f"{original.name} (Copy)",
            description=original.description,
            tags=original.tags,
        )
        
        # Copy tokens
        for token in original.tokens.all():
            DesignToken.objects.create(
                design_system=new_system,
                name=token.name,
                category=token.category,
                token_type=token.token_type,
                value=token.value,
                description=token.description,
                usage_guidelines=token.usage_guidelines,
                group=token.group,
                order=token.order,
            )
        
        # Copy components
        for component in original.components.all():
            ComponentDefinition.objects.create(
                design_system=new_system,
                name=component.name,
                description=component.description,
                category=component.category,
                variants=component.variants,
                props=component.props,
                specs=component.specs,
            )
        
        # Copy style guide
        if hasattr(original, 'style_guide'):
            sg = original.style_guide
            StyleGuide.objects.create(
                design_system=new_system,
                brand_overview=sg.brand_overview,
                brand_values=sg.brand_values,
                tone_of_voice=sg.tone_of_voice,
                color_guidelines=sg.color_guidelines,
                typography_guidelines=sg.typography_guidelines,
            )
        
        return Response(DesignSystemDetailSerializer(new_system, context={'request': request}).data)
    
    @action(detail=True, methods=['get'])
    def export_tokens(self, request, pk=None):
        """Export tokens in various formats"""
        design_system = self.get_object()
        export_format = request.query_params.get('format', 'css')
        prefix = request.query_params.get('prefix', '')
        
        tokens = design_system.tokens.all()
        
        if export_format == 'css':
            output = self._export_css(tokens, prefix)
        elif export_format == 'scss':
            output = self._export_scss(tokens, prefix)
        elif export_format == 'json':
            output = self._export_json(tokens)
        elif export_format == 'js':
            output = self._export_js(tokens, prefix)
        else:
            output = self._export_json(tokens)
        
        return Response({
            'format': export_format,
            'content': output,
            'token_count': tokens.count()
        })
    
    def _export_css(self, tokens, prefix):
        lines = [':root {']
        for token in tokens:
            var_name = f"--{prefix}{token.name}" if prefix else f"--{token.name}"
            value = token.value.get('value', token.value) if isinstance(token.value, dict) else token.value
            lines.append(f"  {var_name}: {value};")
        lines.append('}')
        return '\n'.join(lines)
    
    def _export_scss(self, tokens, prefix):
        lines = []
        for token in tokens:
            var_name = f"${prefix}{token.name}" if prefix else f"${token.name}"
            value = token.value.get('value', token.value) if isinstance(token.value, dict) else token.value
            lines.append(f"{var_name}: {value};")
        return '\n'.join(lines)
    
    def _export_json(self, tokens):
        result = {}
        for token in tokens:
            if token.category not in result:
                result[token.category] = {}
            result[token.category][token.name] = token.value
        return json.dumps(result, indent=2)
    
    def _export_js(self, tokens, prefix):
        lines = ['export const tokens = {']
        categories = {}
        for token in tokens:
            if token.category not in categories:
                categories[token.category] = []
            categories[token.category].append(token)
        
        for category, cat_tokens in categories.items():
            lines.append(f"  {category}: {{")
            for token in cat_tokens:
                name = token.name.replace('-', '_')
                value = token.value.get('value', token.value) if isinstance(token.value, dict) else token.value
                if isinstance(value, str):
                    lines.append(f"    {name}: '{value}',")
                else:
                    lines.append(f"    {name}: {value},")
            lines.append("  },")
        lines.append('};')
        return '\n'.join(lines)
    
    @action(detail=True, methods=['post'])
    def sync_figma(self, request, pk=None):
        """Sync with Figma file"""
        design_system = self.get_object()
        
        if not design_system.figma_file_key:
            return Response({'error': 'No Figma file connected'}, status=status.HTTP_400_BAD_REQUEST)
        
        sync = DesignSystemSync.objects.create(
            design_system=design_system,
            source='figma',
            direction='pull',
            status='pending'
        )
        
        # In production, trigger async Figma sync task
        return Response({
            'status': 'Sync initiated',
            'sync_id': str(sync.id)
        })
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Create an export job"""
        design_system = self.get_object()
        
        export = DesignSystemExport.objects.create(
            design_system=design_system,
            user=request.user,
            export_format=request.data.get('format', 'pdf'),
            options=request.data.get('options', {}),
            status='pending'
        )
        
        # In production, trigger async export task
        return Response(DesignSystemExportSerializer(export).data)


class DesignTokenViewSet(viewsets.ModelViewSet):
    """ViewSet for managing design tokens"""
    serializer_class = DesignTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        design_system_id = self.kwargs.get('design_system_pk')
        return DesignToken.objects.filter(
            design_system_id=design_system_id,
            design_system__user=self.request.user
        )
    
    def perform_create(self, serializer):
        design_system_id = self.kwargs.get('design_system_pk')
        design_system = get_object_or_404(DesignSystem, id=design_system_id, user=self.request.user)
        serializer.save(design_system=design_system)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request, design_system_pk=None):
        """Bulk create tokens"""
        design_system = get_object_or_404(DesignSystem, id=design_system_pk, user=request.user)
        tokens_data = request.data.get('tokens', [])
        
        created_tokens = []
        for token_data in tokens_data:
            token = DesignToken.objects.create(
                design_system=design_system,
                **token_data
            )
            created_tokens.append(token)
        
        return Response({
            'created': len(created_tokens),
            'tokens': DesignTokenSerializer(created_tokens, many=True).data
        })
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request, design_system_pk=None):
        """Bulk delete tokens"""
        token_ids = request.data.get('token_ids', [])
        
        deleted_count = DesignToken.objects.filter(
            id__in=token_ids,
            design_system_id=design_system_pk,
            design_system__user=request.user
        ).delete()[0]
        
        return Response({'deleted': deleted_count})


class ComponentDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing component definitions"""
    serializer_class = ComponentDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        design_system_id = self.kwargs.get('design_system_pk')
        queryset = ComponentDefinition.objects.filter(
            design_system_id=design_system_id,
            design_system__user=self.request.user
        )
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        design_system_id = self.kwargs.get('design_system_pk')
        design_system = get_object_or_404(DesignSystem, id=design_system_id, user=self.request.user)
        serializer.save(design_system=design_system)
    
    @action(detail=True, methods=['post'])
    def add_variant(self, request, design_system_pk=None, pk=None):
        """Add a variant to a component"""
        component = self.get_object()
        
        variant = ComponentVariant.objects.create(
            component=component,
            name=request.data.get('name', 'New Variant'),
            description=request.data.get('description', ''),
            props=request.data.get('props', {}),
            tokens=request.data.get('tokens', {}),
            code_example=request.data.get('code_example', ''),
        )
        
        return Response(ComponentVariantSerializer(variant).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, design_system_pk=None, pk=None):
        """Approve a component"""
        component = self.get_object()
        component.status = 'approved'
        component.save()
        return Response({'status': 'approved'})
    
    @action(detail=True, methods=['post'])
    def deprecate(self, request, design_system_pk=None, pk=None):
        """Deprecate a component"""
        component = self.get_object()
        component.status = 'deprecated'
        component.save()
        return Response({'status': 'deprecated'})


class StyleGuideViewSet(viewsets.ModelViewSet):
    """ViewSet for managing style guides"""
    serializer_class = StyleGuideSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        design_system_id = self.kwargs.get('design_system_pk')
        return StyleGuide.objects.filter(
            design_system_id=design_system_id,
            design_system__user=self.request.user
        )


class DocumentationPageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing documentation pages"""
    serializer_class = DocumentationPageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        design_system_id = self.kwargs.get('design_system_pk')
        return DocumentationPage.objects.filter(
            design_system_id=design_system_id,
            design_system__user=self.request.user
        )
    
    def perform_create(self, serializer):
        design_system_id = self.kwargs.get('design_system_pk')
        design_system = get_object_or_404(DesignSystem, id=design_system_id, user=self.request.user)
        serializer.save(design_system=design_system)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_design_system(request, pk):
    """Get a public design system"""
    design_system = get_object_or_404(DesignSystem, id=pk, is_public=True)
    return Response(DesignSystemDetailSerializer(design_system, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_token_categories(request):
    """Get available token categories"""
    return Response({
        'categories': [
            {'id': 'color', 'name': 'Colors', 'icon': 'palette'},
            {'id': 'typography', 'name': 'Typography', 'icon': 'type'},
            {'id': 'spacing', 'name': 'Spacing', 'icon': 'move'},
            {'id': 'sizing', 'name': 'Sizing', 'icon': 'maximize'},
            {'id': 'border-radius', 'name': 'Border Radius', 'icon': 'square'},
            {'id': 'shadow', 'name': 'Shadows', 'icon': 'layers'},
            {'id': 'opacity', 'name': 'Opacity', 'icon': 'eye'},
            {'id': 'z-index', 'name': 'Z-Index', 'icon': 'layers'},
            {'id': 'duration', 'name': 'Duration', 'icon': 'clock'},
            {'id': 'easing', 'name': 'Easing', 'icon': 'activity'},
            {'id': 'breakpoint', 'name': 'Breakpoints', 'icon': 'monitor'},
        ]
    })
