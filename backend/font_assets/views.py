from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .models import (
    FontFamily, FontCollection, IconSet, Icon,
    AssetLibrary, LibraryAsset, AssetVersion, StockProvider,
    StockSearch, ColorPalette, GradientPreset
)
from .serializers import (
    FontFamilySerializer, FontVariantSerializer, FontCollectionSerializer,
    IconSetSerializer, IconSetDetailSerializer, IconSerializer,
    AssetLibrarySerializer, LibraryAssetSerializer, AssetVersionSerializer,
    StockProviderSerializer, StockSearchSerializer,
    ColorPaletteSerializer, GradientPresetSerializer
)


class FontFamilyViewSet(viewsets.ModelViewSet):
    """ViewSet for font management"""
    serializer_class = FontFamilySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FontFamily.objects.filter(
            Q(user=self.request.user) | Q(is_global=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get fonts grouped by category"""
        fonts = {}
        for category, _ in FontFamily.FONT_CATEGORIES:
            fonts[category] = FontFamilySerializer(
                self.get_queryset().filter(category=category),
                many=True
            ).data
        return Response(fonts)
    
    @action(detail=False, methods=['get'])
    def google_fonts(self, request):
        """Get Google Fonts"""
        fonts = self.get_queryset().filter(source='google')
        return Response(FontFamilySerializer(fonts, many=True).data)
    
    @action(detail=True, methods=['post'])
    def add_variant(self, request, pk=None):
        """Add a font variant"""
        font = self.get_object()
        
        serializer = FontVariantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(family=font)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def import_google_font(self, request):
        """Import a font from Google Fonts"""
        font_name = request.data.get('font_name')
        
        # In production, fetch from Google Fonts API
        font = FontFamily.objects.create(
            user=request.user,
            name=font_name,
            slug=font_name.lower().replace(' ', '-'),
            source='google',
            category='sans-serif'
        )
        
        return Response(FontFamilySerializer(font).data, status=status.HTTP_201_CREATED)


class FontCollectionViewSet(viewsets.ModelViewSet):
    """ViewSet for font collections"""
    serializer_class = FontCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FontCollection.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_font(self, request, pk=None):
        """Add font to collection"""
        collection = self.get_object()
        font_id = request.data.get('font_id')
        
        font = get_object_or_404(FontFamily, id=font_id)
        collection.fonts.add(font)
        
        return Response({'status': 'added'})
    
    @action(detail=True, methods=['post'])
    def remove_font(self, request, pk=None):
        """Remove font from collection"""
        collection = self.get_object()
        font_id = request.data.get('font_id')
        
        collection.fonts.remove(font_id)
        return Response({'status': 'removed'})


class IconSetViewSet(viewsets.ModelViewSet):
    """ViewSet for icon sets"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return IconSet.objects.filter(
            Q(user=self.request.user) | Q(is_global=True)
        )
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IconSetDetailSerializer
        return IconSetSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def icons(self, request, pk=None):
        """Get all icons in set"""
        icon_set = self.get_object()
        icons = icon_set.icons.all()
        
        # Filter by search
        search = request.query_params.get('search')
        if search:
            icons = icons.filter(
                Q(name__icontains=search) | Q(tags__contains=[search])
            )
        
        return Response(IconSerializer(icons, many=True).data)
    
    @action(detail=True, methods=['post'])
    def add_icon(self, request, pk=None):
        """Add icon to set"""
        icon_set = self.get_object()
        
        icon = Icon.objects.create(
            icon_set=icon_set,
            name=request.data.get('name'),
            slug=request.data.get('name', '').lower().replace(' ', '-'),
            svg_content=request.data.get('svg_content'),
            tags=request.data.get('tags', [])
        )
        
        icon_set.icon_count = icon_set.icons.count()
        icon_set.save()
        
        return Response(IconSerializer(icon).data, status=status.HTTP_201_CREATED)


class IconViewSet(viewsets.ModelViewSet):
    """ViewSet for individual icons"""
    serializer_class = IconSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Icon.objects.filter(
            Q(icon_set__user=self.request.user) | Q(icon_set__is_global=True)
        )
    
    @action(detail=True, methods=['post'])
    def track_usage(self, request, pk=None):
        """Track icon usage"""
        icon = self.get_object()
        icon.usage_count += 1
        icon.save()
        return Response({'usage_count': icon.usage_count})


class AssetLibraryViewSet(viewsets.ModelViewSet):
    """ViewSet for asset libraries"""
    serializer_class = AssetLibrarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AssetLibrary.objects.filter(
            Q(user=self.request.user) | 
            Q(is_public=True) |
            Q(shared_with=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        """Get library assets"""
        library = self.get_object()
        assets = library.assets.all()
        
        # Filter by type
        asset_type = request.query_params.get('type')
        if asset_type:
            assets = assets.filter(asset_type=asset_type)
        
        # Filter by folder
        folder = request.query_params.get('folder')
        if folder:
            assets = assets.filter(folder=folder)
        
        return Response(LibraryAssetSerializer(assets, many=True).data)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share library with users"""
        library = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        library.shared_with.add(*user_ids)
        return Response({'status': 'shared', 'shared_with': user_ids})


class LibraryAssetViewSet(viewsets.ModelViewSet):
    """ViewSet for library assets"""
    serializer_class = LibraryAssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LibraryAsset.objects.filter(
            Q(library__user=self.request.user) |
            Q(library__is_public=True) |
            Q(library__shared_with=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        asset = serializer.save()
        
        # Update library count
        asset.library.asset_count = asset.library.assets.count()
        asset.library.save()
        
        # Extract metadata (in production, do this async)
        # - Get dimensions, file size
        # - Extract dominant colors
        # - Generate AI description
    
    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create new version of asset"""
        asset = self.get_object()
        
        last_version = asset.versions.first()
        new_version_num = (last_version.version_number + 1) if last_version else 1
        
        version = AssetVersion.objects.create(
            asset=asset,
            version_number=new_version_num,
            file=request.FILES.get('file'),
            change_description=request.data.get('description', ''),
            changed_by=request.user
        )
        
        return Response(AssetVersionSerializer(version).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def restore_version(self, request, pk=None):
        """Restore to a previous version"""
        asset = self.get_object()
        version_id = request.data.get('version_id')
        
        version = get_object_or_404(AssetVersion, id=version_id, asset=asset)
        asset.file = version.file
        asset.save()
        
        return Response({'status': 'restored', 'version': version.version_number})
    
    @action(detail=True, methods=['post'])
    def track_usage(self, request, pk=None):
        """Track asset usage"""
        asset = self.get_object()
        asset.usage_count += 1
        asset.last_used = timezone.now()
        asset.save()
        return Response({'usage_count': asset.usage_count})


class StockProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for stock providers"""
    queryset = StockProvider.objects.filter(is_active=True)
    serializer_class = StockProviderSerializer
    permission_classes = [permissions.IsAuthenticated]


class StockSearchViewSet(viewsets.ModelViewSet):
    """ViewSet for stock searches"""
    serializer_class = StockSearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return StockSearch.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search stock assets"""
        provider_id = request.data.get('provider_id')
        query = request.data.get('query')
        filters = request.data.get('filters', {})
        
        provider = get_object_or_404(StockProvider, id=provider_id)
        
        # In production, make API call to provider
        # Mock results for now
        results = {
            'images': [
                {'id': '1', 'url': 'https://example.com/image1.jpg', 'thumbnail': '...'},
                {'id': '2', 'url': 'https://example.com/image2.jpg', 'thumbnail': '...'},
            ],
            'total': 100
        }
        
        # Save search history
        search = StockSearch.objects.create(
            user=request.user,
            provider=provider,
            query=query,
            filters=filters,
            result_count=results['total']
        )
        
        return Response({
            'search_id': str(search.id),
            'results': results
        })


class ColorPaletteViewSet(viewsets.ModelViewSet):
    """ViewSet for color palettes"""
    serializer_class = ColorPaletteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ColorPalette.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def extract_from_image(self, request):
        """Extract colors from an image"""
        image = request.FILES.get('image')
        
        # In production, use color extraction algorithm
        # Mock colors for now
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        palette = ColorPalette.objects.create(
            user=request.user,
            name='Extracted Palette',
            colors=colors,
            source='Extracted from image',
            source_image=image
        )
        
        return Response(ColorPaletteSerializer(palette).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a color palette"""
        base_color = request.data.get('base_color')
        harmony = request.data.get('harmony', 'complementary')  # complementary, analogous, triadic, etc.
        
        # In production, calculate harmonious colors
        colors = [base_color, '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        palette = ColorPalette.objects.create(
            user=request.user,
            name=f'{harmony.title()} Palette',
            colors=colors,
            source=f'Generated ({harmony})'
        )
        
        return Response(ColorPaletteSerializer(palette).data, status=status.HTTP_201_CREATED)


class GradientPresetViewSet(viewsets.ModelViewSet):
    """ViewSet for gradient presets"""
    serializer_class = GradientPresetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return GradientPreset.objects.filter(
            Q(user=self.request.user) | Q(is_global=True)
        )
    
    def perform_create(self, serializer):
        # Generate CSS value
        gradient = serializer.validated_data
        stops = gradient.get('stops', [])
        angle = gradient.get('angle', 90)
        gradient_type = gradient.get('gradient_type', 'linear')
        
        stop_strings = [f"{s['color']} {s['position']}%" for s in stops]
        
        if gradient_type == 'linear':
            css_value = f"linear-gradient({angle}deg, {', '.join(stop_strings)})"
        elif gradient_type == 'radial':
            css_value = f"radial-gradient(circle, {', '.join(stop_strings)})"
        else:
            css_value = f"conic-gradient(from {angle}deg, {', '.join(stop_strings)})"
        
        serializer.save(user=self.request.user, css_value=css_value)
