"""
Productivity Views
REST API endpoints for A/B testing, plugins, and offline support
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import F
from django.utils import timezone
from django.utils.text import slugify

from .models import Project
from .productivity_models import (
    ABTest,
    ABTestVariant,
    ABTestResult,
    ABTestEvent,
    Plugin,
    PluginInstallation,
    PluginReview,
    OfflineSync,
    UserPreference
)
from .productivity_serializers import (
    ABTestSerializer,
    ABTestVariantSerializer,
    PluginSerializer,
    PluginInstallationSerializer,
    PluginReviewSerializer,
    OfflineSyncSerializer,
    UserPreferenceSerializer
)


class ABTestViewSet(viewsets.ModelViewSet):
    """A/B test management"""
    serializer_class = ABTestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ABTest.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start an A/B test"""
        test = self.get_object()
        
        if test.status == 'running':
            return Response(
                {'error': 'Test is already running'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if test.variants.count() < 2:
            return Response(
                {'error': 'At least 2 variants are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test.status = 'running'
        test.start_date = timezone.now()
        test.save()
        
        # Create result records for each variant
        for variant in test.variants.all():
            ABTestResult.objects.get_or_create(variant=variant)
        
        return Response({'status': 'running'})
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause an A/B test"""
        test = self.get_object()
        test.status = 'paused'
        test.save()
        return Response({'status': 'paused'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete an A/B test and determine winner"""
        test = self.get_object()
        
        winning_variant_id = request.data.get('winning_variant_id')
        if winning_variant_id:
            test.winning_variant_id = winning_variant_id
        else:
            # Auto-determine winner based on primary goal
            best_variant = None
            best_value = -1
            
            for variant in test.variants.all():
                result = getattr(variant, 'results', None)
                if result:
                    if test.primary_goal == 'clicks':
                        value = result.click_rate
                    elif test.primary_goal == 'conversions':
                        value = result.conversion_rate
                    else:
                        value = result.avg_engagement_time
                    
                    if value > best_value:
                        best_value = value
                        best_variant = variant
            
            test.winning_variant = best_variant
        
        test.status = 'completed'
        test.end_date = timezone.now()
        test.save()
        
        return Response({
            'status': 'completed',
            'winning_variant_id': test.winning_variant_id
        })
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get test results"""
        test = self.get_object()
        results = []
        
        for variant in test.variants.all():
            result = getattr(variant, 'results', None)
            if result:
                results.append({
                    'variant_id': variant.id,
                    'variant_name': variant.name,
                    'is_control': variant.is_control,
                    'impressions': result.impressions,
                    'clicks': result.clicks,
                    'conversions': result.conversions,
                    'click_rate': result.click_rate,
                    'conversion_rate': result.conversion_rate,
                    'avg_engagement_time': result.avg_engagement_time,
                    'confidence_level': result.confidence_level
                })
        
        return Response({
            'test_id': test.id,
            'status': test.status,
            'results': results,
            'winning_variant_id': test.winning_variant_id
        })


class ABTestVariantViewSet(viewsets.ModelViewSet):
    """A/B test variant management"""
    serializer_class = ABTestVariantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ABTestVariant.objects.filter(test__user=self.request.user)


@api_view(['POST'])
def track_ab_event(request):
    """
    Track an A/B test event (public endpoint)
    
    Body:
        variant_id: ID of the variant
        event_type: Type of event
        visitor_id: Unique visitor identifier
        session_id: Session identifier
        event_data: Additional event data
    """
    variant_id = request.data.get('variant_id')
    event_type = request.data.get('event_type')
    visitor_id = request.data.get('visitor_id')
    session_id = request.data.get('session_id')
    event_data = request.data.get('event_data', {})
    
    if not all([variant_id, event_type, visitor_id, session_id]):
        return Response(
            {'error': 'Missing required fields'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        variant = ABTestVariant.objects.get(id=variant_id)
    except ABTestVariant.DoesNotExist:
        return Response(
            {'error': 'Variant not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Create event
    event = ABTestEvent.objects.create(
        variant=variant,
        event_type=event_type,
        visitor_id=visitor_id,
        session_id=session_id,
        event_data=event_data,
        device_type=request.data.get('device_type', ''),
        browser=request.data.get('browser', ''),
        referrer=request.data.get('referrer', '')
    )
    
    # Update results
    result, _ = ABTestResult.objects.get_or_create(variant=variant)
    
    if event_type == 'impression':
        result.impressions = F('impressions') + 1
    elif event_type == 'click':
        result.clicks = F('clicks') + 1
    elif event_type == 'conversion':
        result.conversions = F('conversions') + 1
    
    result.save()
    
    # Recalculate rates
    result.refresh_from_db()
    if result.impressions > 0:
        result.click_rate = result.clicks / result.impressions * 100
        result.conversion_rate = result.conversions / result.impressions * 100
    result.save()
    
    return Response({'status': 'tracked'})


class PluginViewSet(viewsets.ModelViewSet):
    """Plugin management"""
    serializer_class = PluginSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['installs', 'rating_average', 'created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Plugin.objects.all()
        
        if self.action in ['list', 'retrieve']:
            queryset = queryset.filter(status='published')
        elif self.request.user.is_authenticated:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(status='published') | Q(creator=self.request.user)
            )
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    def perform_create(self, serializer):
        slug = slugify(serializer.validated_data['name'])
        base_slug = slug
        counter = 1
        while Plugin.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        serializer.save(creator=self.request.user, slug=slug)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get plugin categories"""
        categories = []
        for choice in Plugin.CATEGORY_CHOICES:
            count = Plugin.objects.filter(
                status='published',
                category=choice[0]
            ).count()
            categories.append({
                'slug': choice[0],
                'name': choice[1],
                'count': count
            })
        return Response(categories)
    
    @action(detail=True, methods=['post'])
    def install(self, request, pk=None):
        """Install a plugin"""
        plugin = self.get_object()
        
        installation, created = PluginInstallation.objects.get_or_create(
            user=request.user,
            plugin=plugin,
            defaults={
                'installed_version': plugin.version,
                'config': {}
            }
        )
        
        if created:
            Plugin.objects.filter(pk=plugin.pk).update(
                installs=F('installs') + 1
            )
        elif not installation.is_enabled:
            installation.is_enabled = True
            installation.save()
        
        return Response({
            'status': 'installed' if created else 'enabled',
            'installation_id': installation.id
        })
    
    @action(detail=True, methods=['post'])
    def uninstall(self, request, pk=None):
        """Uninstall a plugin"""
        plugin = self.get_object()
        
        try:
            installation = PluginInstallation.objects.get(
                user=request.user,
                plugin=plugin
            )
            installation.delete()
            
            Plugin.objects.filter(pk=plugin.pk).update(
                installs=F('installs') - 1
            )
            
            return Response({'status': 'uninstalled'})
        except PluginInstallation.DoesNotExist:
            return Response(
                {'error': 'Plugin not installed'},
                status=status.HTTP_404_NOT_FOUND
            )


class PluginInstallationViewSet(viewsets.ModelViewSet):
    """Manage installed plugins"""
    serializer_class = PluginInstallationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PluginInstallation.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle plugin enabled state"""
        installation = self.get_object()
        installation.is_enabled = not installation.is_enabled
        installation.save()
        return Response({'is_enabled': installation.is_enabled})
    
    @action(detail=True, methods=['post'])
    def configure(self, request, pk=None):
        """Update plugin configuration"""
        installation = self.get_object()
        installation.config = request.data.get('config', {})
        installation.save()
        return Response({'config': installation.config})


class PluginReviewViewSet(viewsets.ModelViewSet):
    """Plugin review management"""
    serializer_class = PluginReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PluginReview.objects.all()
        plugin_id = self.request.query_params.get('plugin_id')
        if plugin_id:
            queryset = queryset.filter(plugin_id=plugin_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        # Update plugin rating
        plugin = serializer.validated_data['plugin']
        from django.db.models import Avg, Count
        
        stats = PluginReview.objects.filter(plugin=plugin).aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        
        plugin.rating_average = stats['avg_rating'] or 0
        plugin.rating_count = stats['count']
        plugin.save()


class OfflineSyncViewSet(viewsets.ModelViewSet):
    """Offline sync management"""
    serializer_class = OfflineSyncSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OfflineSync.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Process offline sync"""
        sync = self.get_object()
        
        if sync.status not in ['pending', 'conflict']:
            return Response(
                {'error': 'Sync already processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sync.status = 'syncing'
        sync.save()
        
        try:
            project = sync.project
            current_data = project.design_data
            
            # Apply changes
            conflicts = []
            for change in sync.changes:
                # Simple conflict detection
                # In production, implement proper operational transformation
                try:
                    if change['type'] == 'update':
                        # Apply update
                        path = change['path']
                        value = change['value']
                        # Apply change to current_data
                        # This is simplified - real implementation needs path parsing
                    elif change['type'] == 'add':
                        path = change['path']
                        value = change['value']
                    elif change['type'] == 'delete':
                        path = change['path']
                except KeyError:
                    conflicts.append(change)
            
            if conflicts:
                sync.status = 'conflict'
                sync.conflicts = conflicts
            else:
                project.design_data = current_data
                project.save()
                sync.status = 'completed'
                sync.synced_at = timezone.now()
            
            sync.save()
            
            return Response({
                'status': sync.status,
                'conflicts': sync.conflicts
            })
            
        except Exception as e:
            sync.status = 'failed'
            sync.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def resolve_conflicts(self, request, pk=None):
        """Resolve sync conflicts"""
        sync = self.get_object()
        
        if sync.status != 'conflict':
            return Response(
                {'error': 'No conflicts to resolve'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resolved_changes = request.data.get('resolved_changes', [])
        sync.resolved_changes = resolved_changes
        sync.status = 'pending'
        sync.changes = resolved_changes
        sync.conflicts = []
        sync.save()
        
        return Response({'status': 'resolved'})


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """User preference management"""
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj, _ = UserPreference.objects.get_or_create(user=self.request.user)
        return obj
    
    def list(self, request):
        """Get current user's preferences"""
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_offline_projects(self, request):
        """Update list of projects to cache offline"""
        preferences = self.get_object()
        project_ids = request.data.get('project_ids', [])
        
        # Validate project ownership
        valid_ids = list(Project.objects.filter(
            id__in=project_ids,
            user=request.user
        ).values_list('id', flat=True))
        
        preferences.offline_projects = valid_ids
        preferences.save()
        
        return Response({'offline_projects': valid_ids})
