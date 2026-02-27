"""
Design Tokens API Views

REST API endpoints for design token management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from .design_tokens_models import (
    DesignTokenLibrary, DesignToken, DesignTheme,
    ThemeTokenOverride, ProjectTokenBinding,
    TokenChangeLog
)
from .design_tokens_service import DesignTokensService
from projects.models import Project


class DesignTokenLibrarySerializer:
    @staticmethod
    def to_dict(library, include_tokens=False):
        data = {
            'id': library.id,
            'name': library.name,
            'description': library.description,
            'version': library.version,
            'is_public': library.is_public,
            'is_default': library.is_default,
            'sync_enabled': library.sync_enabled,
            'last_synced': library.last_synced.isoformat() if library.last_synced else None,
            'usage_count': library.usage_count,
            'token_count': library.tokens.count(),
            'theme_count': library.themes.count(),
            'created_at': library.created_at.isoformat(),
            'updated_at': library.updated_at.isoformat(),
        }
        
        if include_tokens:
            data['tokens'] = [
                DesignTokenSerializer.to_dict(t) for t in library.tokens.all()
            ]
            data['themes'] = [
                DesignThemeSerializer.to_dict(t) for t in library.themes.all()
            ]
            data['groups'] = [
                TokenGroupSerializer.to_dict(g) for g in library.groups.all()
            ]
        
        return data


class DesignTokenSerializer:
    @staticmethod
    def to_dict(token):
        return {
            'id': token.id,
            'name': token.name,
            'category': token.category,
            'token_type': token.token_type,
            'value': token.value,
            'resolved_value': token.get_resolved_value(),
            'css_variable': token.css_variable,
            'references_id': token.references_id,
            'description': token.description,
            'usage_examples': token.usage_examples,
            'deprecated': token.deprecated,
            'deprecated_message': token.deprecated_message,
            'created_at': token.created_at.isoformat(),
            'updated_at': token.updated_at.isoformat(),
        }


class DesignThemeSerializer:
    @staticmethod
    def to_dict(theme, include_overrides=False):
        data = {
            'id': theme.id,
            'name': theme.name,
            'slug': theme.slug,
            'description': theme.description,
            'theme_type': theme.theme_type,
            'extends_id': theme.extends_id,
            'is_default': theme.is_default,
            'css_selector': theme.css_selector,
            'override_count': theme.overrides.count(),
        }
        
        if include_overrides:
            data['overrides'] = [
                {
                    'token_id': o.token_id,
                    'token_name': o.token.name,
                    'value': o.value,
                }
                for o in theme.overrides.select_related('token')
            ]
        
        return data


class TokenGroupSerializer:
    @staticmethod
    def to_dict(group):
        return {
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'sort_order': group.sort_order,
            'token_ids': list(group.tokens.values_list('id', flat=True)),
        }


class DesignTokenLibraryViewSet(viewsets.ViewSet):
    """
    ViewSet for design token library management.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List user's token libraries."""
        libraries = DesignTokenLibrary.objects.filter(user=request.user)
        
        # Include public libraries
        include_public = request.query_params.get('include_public', 'false') == 'true'
        if include_public:
            libraries = libraries | DesignTokenLibrary.objects.filter(is_public=True)
        
        return Response({
            'libraries': [
                DesignTokenLibrarySerializer.to_dict(lib)
                for lib in libraries.distinct()
            ]
        })
    
    def retrieve(self, request, pk=None):
        """Get a specific library with all details."""
        library = get_object_or_404(
            DesignTokenLibrary.objects.filter(user=request.user) |
            DesignTokenLibrary.objects.filter(is_public=True),
            pk=pk
        )
        return Response(DesignTokenLibrarySerializer.to_dict(library, include_tokens=True))
    
    def create(self, request):
        """Create a new token library."""
        library = DesignTokenLibrary.objects.create(
            user=request.user,
            name=request.data.get('name', 'Untitled Library'),
            description=request.data.get('description', ''),
            is_public=request.data.get('is_public', False),
            is_default=request.data.get('is_default', False),
        )
        
        # If setting as default, unset other defaults
        if library.is_default:
            DesignTokenLibrary.objects.filter(
                user=request.user
            ).exclude(id=library.id).update(is_default=False)
        
        return Response(
            DesignTokenLibrarySerializer.to_dict(library),
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """Update a token library."""
        library = get_object_or_404(
            DesignTokenLibrary,
            pk=pk,
            user=request.user
        )
        
        library.name = request.data.get('name', library.name)
        library.description = request.data.get('description', library.description)
        library.is_public = request.data.get('is_public', library.is_public)
        library.sync_enabled = request.data.get('sync_enabled', library.sync_enabled)
        library.save()
        
        return Response(DesignTokenLibrarySerializer.to_dict(library))
    
    def destroy(self, request, pk=None):
        """Delete a token library."""
        library = get_object_or_404(
            DesignTokenLibrary,
            pk=pk,
            user=request.user
        )
        library.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def increment_version(self, request, pk=None):
        """Increment library version."""
        library = get_object_or_404(DesignTokenLibrary, pk=pk, user=request.user)
        increment_type = request.data.get('type', 'patch')
        
        new_version = library.increment_version(increment_type)
        
        return Response({
            'version': new_version,
            'message': f'Version incremented to {new_version}'
        })
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export tokens in various formats."""
        library = get_object_or_404(
            DesignTokenLibrary.objects.filter(user=request.user) |
            DesignTokenLibrary.objects.filter(is_public=True),
            pk=pk
        )
        
        format_type = request.query_params.get('format', 'css')
        theme_slug = request.query_params.get('theme')
        
        theme = None
        if theme_slug:
            theme = library.themes.filter(slug=theme_slug).first()
        
        service = DesignTokensService(library)
        
        format_handlers = {
            'css': ('text/css', service.export_to_css),
            'scss': ('text/x-scss', service.export_to_scss),
            'json': ('application/json', service.export_to_json),
            'js': ('application/javascript', lambda t: service.export_to_js(t, typescript=False)),
            'ts': ('application/typescript', lambda t: service.export_to_js(t, typescript=True)),
            'tailwind': ('application/javascript', service.export_to_tailwind),
            'figma': ('application/json', service.export_to_figma),
        }
        
        if format_type not in format_handlers:
            return Response(
                {'error': f'Unsupported format: {format_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content_type, handler = format_handlers[format_type]
        content = handler(theme)
        
        # Return as download or inline
        download = request.query_params.get('download', 'false') == 'true'
        if download:
            response = HttpResponse(content, content_type=content_type)
            filename = f"{library.name.lower().replace(' ', '-')}.{format_type}"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        return Response({
            'format': format_type,
            'content': content
        })
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a library."""
        library = get_object_or_404(
            DesignTokenLibrary.objects.filter(user=request.user) |
            DesignTokenLibrary.objects.filter(is_public=True),
            pk=pk
        )
        
        # Create copy
        new_library = DesignTokenLibrary.objects.create(
            user=request.user,
            name=f"{library.name} (Copy)",
            description=library.description,
            is_public=False,
        )
        
        # Copy tokens
        for token in library.tokens.all():
            DesignToken.objects.create(
                library=new_library,
                name=token.name,
                category=token.category,
                token_type=token.token_type,
                value=token.value,
                description=token.description,
            )
        
        # Copy themes
        for theme in library.themes.all():
            new_theme = DesignTheme.objects.create(
                library=new_library,
                name=theme.name,
                slug=theme.slug,
                description=theme.description,
                theme_type=theme.theme_type,
                is_default=theme.is_default,
                css_selector=theme.css_selector,
            )
            
            # Copy overrides
            for override in theme.overrides.all():
                # Find matching token in new library
                new_token = new_library.tokens.filter(name=override.token.name).first()
                if new_token:
                    ThemeTokenOverride.objects.create(
                        theme=new_theme,
                        token=new_token,
                        value=override.value,
                    )
        
        return Response(
            DesignTokenLibrarySerializer.to_dict(new_library, include_tokens=True),
            status=status.HTTP_201_CREATED
        )


class DesignTokenViewSet(viewsets.ViewSet):
    """
    ViewSet for individual token management.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request, library_pk=None):
        """List tokens in a library."""
        library = get_object_or_404(
            DesignTokenLibrary.objects.filter(user=request.user) |
            DesignTokenLibrary.objects.filter(is_public=True),
            pk=library_pk
        )
        
        tokens = library.tokens.all()
        
        # Filter by type
        token_type = request.query_params.get('type')
        if token_type:
            tokens = tokens.filter(token_type=token_type)
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            tokens = tokens.filter(category=category)
        
        return Response({
            'tokens': [DesignTokenSerializer.to_dict(t) for t in tokens],
            'categories': list(tokens.values_list('category', flat=True).distinct()),
            'types': list(tokens.values_list('token_type', flat=True).distinct()),
        })
    
    def create(self, request, library_pk=None):
        """Create a new token."""
        library = get_object_or_404(DesignTokenLibrary, pk=library_pk, user=request.user)
        
        # Validate
        service = DesignTokensService(library)
        token_type = request.data.get('token_type', 'custom')
        value = request.data.get('value', '')
        
        is_valid, error = service.validate_token_value(token_type, value)
        if not is_valid:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        token = DesignToken.objects.create(
            library=library,
            name=request.data.get('name'),
            category=request.data.get('category', ''),
            token_type=token_type,
            value=value,
            description=request.data.get('description', ''),
        )
        
        # Log change
        TokenChangeLog.objects.create(
            library=library,
            token=token,
            change_type='create',
            new_value=value,
            user=request.user,
            library_version=library.version,
        )
        
        return Response(
            DesignTokenSerializer.to_dict(token),
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, library_pk=None, pk=None):
        """Update a token."""
        library = get_object_or_404(DesignTokenLibrary, pk=library_pk, user=request.user)
        token = get_object_or_404(DesignToken, pk=pk, library=library)
        
        old_value = token.value
        
        token.name = request.data.get('name', token.name)
        token.category = request.data.get('category', token.category)
        token.value = request.data.get('value', token.value)
        token.description = request.data.get('description', token.description)
        token.deprecated = request.data.get('deprecated', token.deprecated)
        token.deprecated_message = request.data.get('deprecated_message', token.deprecated_message)
        token.save()
        
        # Log change
        if old_value != token.value:
            TokenChangeLog.objects.create(
                library=library,
                token=token,
                change_type='update',
                old_value=old_value,
                new_value=token.value,
                user=request.user,
                library_version=library.version,
            )
        
        return Response(DesignTokenSerializer.to_dict(token))
    
    def destroy(self, request, library_pk=None, pk=None):
        """Delete a token."""
        library = get_object_or_404(DesignTokenLibrary, pk=library_pk, user=request.user)
        token = get_object_or_404(DesignToken, pk=pk, library=library)
        
        # Log deletion
        TokenChangeLog.objects.create(
            library=library,
            token=None,
            change_type='delete',
            old_value=f"{token.name}: {token.value}",
            user=request.user,
            library_version=library.version,
        )
        
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request, library_pk=None):
        """Bulk create tokens."""
        library = get_object_or_404(DesignTokenLibrary, pk=library_pk, user=request.user)
        
        tokens_data = request.data.get('tokens', [])
        created = []
        errors = []
        
        for data in tokens_data:
            try:
                token = DesignToken.objects.create(
                    library=library,
                    name=data.get('name'),
                    category=data.get('category', ''),
                    token_type=data.get('token_type', 'custom'),
                    value=data.get('value'),
                    description=data.get('description', ''),
                )
                created.append(DesignTokenSerializer.to_dict(token))
            except Exception as e:
                errors.append({
                    'name': data.get('name'),
                    'error': str(e)
                })
        
        return Response({
            'created': created,
            'errors': errors,
            'created_count': len(created),
            'error_count': len(errors),
        })


class DesignThemeViewSet(viewsets.ViewSet):
    """
    ViewSet for theme management.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request, library_pk=None):
        """List themes in a library."""
        library = get_object_or_404(
            DesignTokenLibrary.objects.filter(user=request.user) |
            DesignTokenLibrary.objects.filter(is_public=True),
            pk=library_pk
        )
        
        themes = library.themes.all()
        return Response({
            'themes': [
                DesignThemeSerializer.to_dict(t, include_overrides=True)
                for t in themes
            ]
        })
    
    def create(self, request, library_pk=None):
        """Create a new theme."""
        library = get_object_or_404(DesignTokenLibrary, pk=library_pk, user=request.user)
        
        theme = DesignTheme.objects.create(
            library=library,
            name=request.data.get('name'),
            slug=request.data.get('slug'),
            description=request.data.get('description', ''),
            theme_type=request.data.get('theme_type', 'custom'),
            is_default=request.data.get('is_default', False),
            css_selector=request.data.get('css_selector', ''),
        )
        
        # Create overrides
        overrides = request.data.get('overrides', [])
        for override in overrides:
            token = library.tokens.filter(id=override.get('token_id')).first()
            if token:
                ThemeTokenOverride.objects.create(
                    theme=theme,
                    token=token,
                    value=override.get('value'),
                )
        
        return Response(
            DesignThemeSerializer.to_dict(theme, include_overrides=True),
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def set_override(self, request, library_pk=None, pk=None):
        """Set or update a token override for this theme."""
        library = get_object_or_404(DesignTokenLibrary, pk=library_pk, user=request.user)
        theme = get_object_or_404(DesignTheme, pk=pk, library=library)
        
        token_id = request.data.get('token_id')
        value = request.data.get('value')
        
        token = get_object_or_404(DesignToken, pk=token_id, library=library)
        
        override, created = ThemeTokenOverride.objects.update_or_create(
            theme=theme,
            token=token,
            defaults={'value': value}
        )
        
        return Response({
            'token_id': token.id,
            'token_name': token.name,
            'value': value,
            'created': created,
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bind_library_to_project(request):
    """
    Bind a token library to a project.
    
    POST /api/v1/projects/tokens/bind/
    {
        "project_id": 1,
        "library_id": 1,
        "theme_id": null
    }
    """
    project_id = request.data.get('project_id')
    library_id = request.data.get('library_id')
    theme_id = request.data.get('theme_id')
    
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    library = get_object_or_404(
        DesignTokenLibrary.objects.filter(user=request.user) |
        DesignTokenLibrary.objects.filter(is_public=True),
        pk=library_id
    )
    
    theme = None
    if theme_id:
        theme = library.themes.filter(pk=theme_id).first()
    
    binding, created = ProjectTokenBinding.objects.update_or_create(
        project=project,
        library=library,
        defaults={'theme': theme}
    )
    
    # Update library usage count
    library.usage_count = library.project_bindings.count()
    library.save()
    
    return Response({
        'binding_id': binding.id,
        'project_id': project.id,
        'library_id': library.id,
        'theme_id': theme.id if theme else None,
        'created': created,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_tokens_to_project(request):
    """
    Sync tokens to a project.
    
    POST /api/v1/projects/tokens/sync/
    {
        "project_id": 1,
        "library_id": 1
    }
    """
    project_id = request.data.get('project_id')
    library_id = request.data.get('library_id')
    
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    library = get_object_or_404(DesignTokenLibrary, pk=library_id)
    
    # Get theme from binding
    binding = ProjectTokenBinding.objects.filter(
        project=project,
        library=library
    ).first()
    
    theme = binding.theme if binding else None
    
    service = DesignTokensService(library)
    result = service.sync_to_project(project, theme)
    
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_token_usage(request, project_id):
    """
    Analyze token usage in a project.
    
    GET /api/v1/projects/{id}/tokens/analyze/
    """
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    
    # Get bound libraries
    bindings = ProjectTokenBinding.objects.filter(project=project)
    
    results = []
    for binding in bindings:
        service = DesignTokensService(binding.library)
        analysis = service.analyze_token_usage(project)
        results.append({
            'library_id': binding.library.id,
            'library_name': binding.library.name,
            'analysis': analysis,
        })
    
    return Response({'libraries': results})
