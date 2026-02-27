from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Avg
import secrets

from .models import (
    PluginCategory, Plugin, PluginVersion, PluginInstallation, PluginReview,
    DeveloperProfile, APIEndpoint, WebhookSubscription,
    PluginLog, PluginSandbox
)
from .serializers import (
    PluginCategorySerializer, PluginSerializer, PluginDetailSerializer,
    PluginVersionSerializer, PluginInstallationSerializer, PluginReviewSerializer,
    DeveloperProfileSerializer, APIEndpointSerializer,
    WebhookSubscriptionSerializer, PluginLogSerializer, PluginSandboxSerializer
)


class PluginCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for plugin categories"""
    queryset = PluginCategory.objects.all()
    serializer_class = PluginCategorySerializer
    permission_classes = [permissions.AllowAny]


class PluginViewSet(viewsets.ModelViewSet):
    """ViewSet for plugins"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Plugin.objects.all()
        
        if self.action in ['list', 'retrieve']:
            # Public can see published plugins
            if not self.request.user.is_authenticated:
                return queryset.filter(status='published')
            # Authenticated users can see their own + published
            return queryset.filter(
                Q(status='published') | Q(developer=self.request.user)
            )
        
        # For edit actions, only own plugins
        return queryset.filter(developer=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PluginDetailSerializer
        return PluginSerializer
    
    def perform_create(self, serializer):
        serializer.save(developer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured plugins"""
        plugins = Plugin.objects.filter(
            status='published'
        ).order_by('-rating_average', '-install_count')[:10]
        return Response(PluginSerializer(plugins, many=True).data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular plugins"""
        plugins = Plugin.objects.filter(
            status='published'
        ).order_by('-install_count')[:20]
        return Response(PluginSerializer(plugins, many=True).data)
    
    @action(detail=False, methods=['get'])
    def new(self, request):
        """Get new plugins"""
        plugins = Plugin.objects.filter(
            status='published'
        ).order_by('-published_at')[:20]
        return Response(PluginSerializer(plugins, many=True).data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search plugins"""
        query = request.query_params.get('q', '')
        category = request.query_params.get('category')
        pricing = request.query_params.get('pricing')
        
        plugins = Plugin.objects.filter(status='published')
        
        if query:
            plugins = plugins.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(tags__contains=[query])
            )
        
        if category:
            plugins = plugins.filter(category__slug=category)
        
        if pricing:
            plugins = plugins.filter(pricing_type=pricing)
        
        return Response(PluginSerializer(plugins, many=True).data)
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """Submit plugin for review"""
        plugin = self.get_object()
        
        if plugin.status != 'draft':
            return Response({'error': 'Plugin is not in draft status'}, status=400)
        
        plugin.status = 'review'
        plugin.save()
        
        return Response({'status': 'submitted'})
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a plugin (admin only)"""
        plugin = self.get_object()
        
        if plugin.status != 'approved':
            return Response({'error': 'Plugin not approved'}, status=400)
        
        plugin.status = 'published'
        plugin.published_at = timezone.now()
        plugin.save()
        
        return Response({'status': 'published'})
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get plugin reviews"""
        plugin = self.get_object()
        reviews = plugin.reviews.filter(is_approved=True)
        return Response(PluginReviewSerializer(reviews, many=True).data)
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get plugin versions"""
        plugin = self.get_object()
        versions = plugin.versions.all()
        return Response(PluginVersionSerializer(versions, many=True).data)


class PluginVersionViewSet(viewsets.ModelViewSet):
    """ViewSet for plugin versions"""
    serializer_class = PluginVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        plugin_id = self.kwargs.get('plugin_pk')
        return PluginVersion.objects.filter(plugin_id=plugin_id)
    
    def perform_create(self, serializer):
        plugin_id = self.kwargs.get('plugin_pk')
        plugin = get_object_or_404(Plugin, id=plugin_id, developer=self.request.user)
        
        version = serializer.save(plugin=plugin)
        
        # Update plugin current version
        plugin.current_version = version.version
        plugin.save()


class PluginInstallationViewSet(viewsets.ModelViewSet):
    """ViewSet for plugin installations"""
    serializer_class = PluginInstallationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PluginInstallation.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def install(self, request):
        """Install a plugin"""
        plugin_id = request.data.get('plugin_id')
        plugin = get_object_or_404(Plugin, id=plugin_id, status='published')
        
        # Check if already installed
        if PluginInstallation.objects.filter(user=request.user, plugin=plugin).exists():
            return Response({'error': 'Plugin already installed'}, status=400)
        
        # Get latest version
        version = plugin.versions.filter(is_stable=True).first()
        
        installation = PluginInstallation.objects.create(
            user=request.user,
            plugin=plugin,
            version=version
        )
        
        # Update stats
        plugin.install_count += 1
        plugin.active_installs += 1
        plugin.save()
        
        return Response(PluginInstallationSerializer(installation).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def uninstall(self, request, pk=None):
        """Uninstall a plugin"""
        installation = self.get_object()
        plugin = installation.plugin
        
        installation.delete()
        
        # Update stats
        plugin.active_installs = max(0, plugin.active_installs - 1)
        plugin.save()
        
        return Response({'status': 'uninstalled'})
    
    @action(detail=True, methods=['post'])
    def toggle_enabled(self, request, pk=None):
        """Enable/disable a plugin"""
        installation = self.get_object()
        installation.is_enabled = not installation.is_enabled
        installation.save()
        return Response({'is_enabled': installation.is_enabled})
    
    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        """Update plugin to latest version"""
        installation = self.get_object()
        plugin = installation.plugin
        
        latest_version = plugin.versions.filter(is_stable=True).first()
        if latest_version and latest_version != installation.version:
            installation.version = latest_version
            installation.save()
            return Response({'version': latest_version.version})
        
        return Response({'message': 'Already up to date'})


class PluginReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for plugin reviews"""
    serializer_class = PluginReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        plugin_id = self.kwargs.get('plugin_pk')
        return PluginReview.objects.filter(plugin_id=plugin_id, is_approved=True)
    
    def perform_create(self, serializer):
        plugin_id = self.kwargs.get('plugin_pk')
        plugin = get_object_or_404(Plugin, id=plugin_id)
        
        review = serializer.save(user=self.request.user, plugin=plugin)
        
        # Update plugin rating
        avg_rating = plugin.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        plugin.rating_average = avg_rating
        plugin.rating_count = plugin.reviews.count()
        plugin.save()
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, plugin_pk=None, pk=None):
        """Mark review as helpful"""
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        return Response({'helpful_count': review.helpful_count})
    
    @action(detail=True, methods=['post'])
    def respond(self, request, plugin_pk=None, pk=None):
        """Developer response to review"""
        review = self.get_object()
        
        # Verify requester is developer
        if review.plugin.developer != request.user:
            return Response({'error': 'Not authorized'}, status=403)
        
        review.developer_response = request.data.get('response')
        review.developer_responded_at = timezone.now()
        review.save()
        
        return Response(PluginReviewSerializer(review).data)


class DeveloperProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for developer profiles"""
    serializer_class = DeveloperProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DeveloperProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's developer profile"""
        profile, created = DeveloperProfile.objects.get_or_create(
            user=request.user,
            defaults={'display_name': request.user.username}
        )
        return Response(DeveloperProfileSerializer(profile).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get developer stats"""
        plugins = Plugin.objects.filter(developer=request.user)
        
        return Response({
            'total_plugins': plugins.count(),
            'published_plugins': plugins.filter(status='published').count(),
            'total_installs': sum(p.install_count for p in plugins),
            'total_reviews': sum(p.reviews.count() for p in plugins),
            'avg_rating': plugins.aggregate(Avg('rating_average'))['rating_average__avg'] or 0
        })


class APIEndpointViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for API documentation"""
    queryset = APIEndpoint.objects.filter(is_deprecated=False)
    serializer_class = APIEndpointSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def by_version(self, request):
        """Get endpoints by API version"""
        version = request.query_params.get('version', 'v1')
        endpoints = self.queryset.filter(api_version=version)
        return Response(APIEndpointSerializer(endpoints, many=True).data)


class WebhookSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for webhook subscriptions"""
    serializer_class = WebhookSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WebhookSubscription.objects.filter(installation__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(secret=secrets.token_hex(32))


class PluginSandboxViewSet(viewsets.ModelViewSet):
    """ViewSet for plugin sandboxes"""
    serializer_class = PluginSandboxSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PluginSandbox.objects.filter(developer=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(
            developer=self.request.user,
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
    
    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        """Extend sandbox expiration"""
        sandbox = self.get_object()
        sandbox.expires_at = timezone.now() + timezone.timedelta(hours=24)
        sandbox.save()
        return Response({'expires_at': sandbox.expires_at})


class PluginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for plugin logs"""
    serializer_class = PluginLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        installation_id = self.kwargs.get('installation_pk')
        return PluginLog.objects.filter(
            installation_id=installation_id,
            installation__user=self.request.user
        )


# Import plugin runtime for execution
from rest_framework.decorators import api_view, permission_classes as perm_classes
from .runtime import plugin_runtime


@api_view(['POST'])
@perm_classes([permissions.IsAuthenticated])
def execute_plugin(request, installation_id):
    """
    Execute a plugin's main function in a sandboxed environment.
    
    Request body:
    {
        "function": "main",  // Function to execute
        "args": {...},       // Arguments to pass
        "project_id": 123,   // Optional project context
        "element_ids": [...]  // Optional element context
    }
    """
    try:
        installation = get_object_or_404(
            PluginInstallation,
            id=installation_id,
            user=request.user,
            is_active=True
        )
        
        function_name = request.data.get('function', 'main')
        args = request.data.get('args', {})
        project_id = request.data.get('project_id')
        element_ids = request.data.get('element_ids', [])
        
        # Check if plugin is enabled
        if not installation.is_enabled:
            return Response(
                {'error': 'Plugin is disabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get latest version
        plugin = installation.plugin
        version = plugin.versions.filter(status='approved').order_by('-version').first()
        
        if not version:
            return Response(
                {'error': 'No approved version available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build context
        context = {
            'user_id': request.user.id,
            'project_id': project_id,
            'element_ids': element_ids,
            'settings': installation.custom_settings or {},
        }
        
        # Execute in runtime
        result = plugin_runtime.execute_plugin(
            plugin_id=str(plugin.id),
            code=version.code if hasattr(version, 'code') else '',
            function_name=function_name,
            args=args,
            context=context,
            permissions=plugin.permissions or [],
        )
        
        # Log execution
        PluginLog.objects.create(
            installation=installation,
            level='info',
            message=f'Executed function: {function_name}',
            data={'args': args, 'result_type': type(result).__name__}
        )
        
        return Response({
            'status': 'success',
            'result': result,
            'plugin': plugin.name,
            'function': function_name,
        })
        
    except Exception as e:
        # Log error
        if 'installation' in locals():
            PluginLog.objects.create(
                installation=installation,
                level='error',
                message=f'Execution failed: {str(e)}',
                data={'function': function_name, 'error': str(e)}
            )
        
        return Response(
            {'error': 'Plugin execution failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@perm_classes([permissions.IsAuthenticated])
def trigger_plugin_event(request, installation_id):
    """
    Trigger a plugin event handler.
    
    Request body:
    {
        "event": "element:created",
        "data": {...}
    }
    """
    try:
        installation = get_object_or_404(
            PluginInstallation,
            id=installation_id,
            user=request.user,
            is_active=True
        )
        
        event_name = request.data.get('event')
        event_data = request.data.get('data', {})
        
        if not event_name:
            return Response(
                {'error': 'Event name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plugin = installation.plugin
        version = plugin.versions.filter(status='approved').order_by('-version').first()
        
        if not version:
            return Response(
                {'error': 'No approved version available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger event in runtime
        result = plugin_runtime.trigger_event(
            plugin_id=str(plugin.id),
            event_name=event_name,
            event_data=event_data,
        )
        
        return Response({
            'status': 'success',
            'event': event_name,
            'handlers_triggered': result.get('handlers_count', 0),
        })
        
    except Exception as e:
        return Response(
            {'error': 'Event trigger failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@perm_classes([permissions.IsAuthenticated])
def get_plugin_capabilities(request, installation_id):
    """
    Get a plugin's capabilities and permissions.
    """
    installation = get_object_or_404(
        PluginInstallation,
        id=installation_id,
        user=request.user
    )
    
    plugin = installation.plugin
    
    return Response({
        'plugin': {
            'id': plugin.id,
            'name': plugin.name,
            'version': plugin.latest_version,
        },
        'permissions': plugin.permissions or [],
        'events': [
            'project:opened',
            'project:saved',
            'element:created',
            'element:updated',
            'element:deleted',
            'selection:changed',
            'canvas:clicked',
        ],
        'api_access': {
            'elements': 'read' in (plugin.permissions or []) or 'write' in (plugin.permissions or []),
            'project': 'project:read' in (plugin.permissions or []),
            'ai': 'ai:generate' in (plugin.permissions or []),
            'network': 'network' in (plugin.permissions or []),
            'storage': 'storage' in (plugin.permissions or []),
        },
        'settings': installation.custom_settings or {},
    })

