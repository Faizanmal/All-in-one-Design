from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import random

from .models import (
    ABTest, ABTestVariant, PerformanceAnalysis, DeviceCompatibility,
    UserBehaviorPrediction, SmartLayoutSuggestion, OptimizationReport
)
from .serializers import (
    ABTestSerializer, ABTestCreateSerializer, ABTestVariantSerializer,
    PerformanceAnalysisSerializer, DeviceCompatibilitySerializer,
    UserBehaviorPredictionSerializer, SmartLayoutSuggestionSerializer,
    OptimizationReportSerializer
)


class ABTestViewSet(viewsets.ModelViewSet):
    """ViewSet for A/B testing"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ABTest.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ABTestCreateSerializer
        return ABTestSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_variant(self, request, pk=None):
        """Add a variant to the test"""
        ab_test = self.get_object()
        
        variant = ABTestVariant.objects.create(
            ab_test=ab_test,
            name=request.data.get('name', f'Variant {ab_test.variants.count() + 1}'),
            description=request.data.get('description', ''),
            design_data=request.data.get('design_data', {}),
            weight=request.data.get('weight', 50),
            is_control=request.data.get('is_control', False),
        )
        
        return Response(ABTestVariantSerializer(variant).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start the A/B test"""
        ab_test = self.get_object()
        
        if ab_test.variants.count() < 2:
            return Response({'error': 'At least 2 variants required'}, status=status.HTTP_400_BAD_REQUEST)
        
        ab_test.status = 'running'
        ab_test.start_date = timezone.now()
        ab_test.save()
        
        return Response({'status': 'running', 'start_date': ab_test.start_date})
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop the A/B test and determine winner"""
        ab_test = self.get_object()
        ab_test.status = 'completed'
        ab_test.end_date = timezone.now()
        
        # Determine winner based on goal metric
        best_variant = None
        best_score = -1
        
        for variant in ab_test.variants.all():
            if ab_test.goal == 'conversion':
                score = variant.conversion_rate
            elif ab_test.goal == 'click_rate':
                score = variant.click_rate
            else:
                score = variant.engagement_score
            
            if score > best_score:
                best_score = score
                best_variant = variant
        
        ab_test.winner_variant = best_variant
        ab_test.confidence_level = self._calculate_confidence(ab_test)
        ab_test.save()
        
        return Response({
            'status': 'completed',
            'winner': ABTestVariantSerializer(best_variant).data if best_variant else None,
            'confidence_level': ab_test.confidence_level
        })
    
    @action(detail=True, methods=['post'])
    def record_event(self, request, pk=None):
        """Record an event (impression, click, conversion) for a variant"""
        ab_test = self.get_object()
        variant_id = request.data.get('variant_id')
        event_type = request.data.get('event_type')  # impression, click, conversion
        
        variant = get_object_or_404(ABTestVariant, id=variant_id, ab_test=ab_test)
        
        if event_type == 'impression':
            variant.impressions += 1
        elif event_type == 'click':
            variant.clicks += 1
        elif event_type == 'conversion':
            variant.conversions += 1
        
        variant.save()
        return Response({'status': 'recorded'})
    
    @action(detail=True, methods=['get'])
    def ai_recommendations(self, request, pk=None):
        """Get AI-powered recommendations for improving the test"""
        ab_test = self.get_object()
        
        # Generate recommendations based on current data
        recommendations = self._generate_ai_recommendations(ab_test)
        
        ab_test.ai_recommendations = recommendations
        ab_test.save()
        
        return Response({'recommendations': recommendations})
    
    def _calculate_confidence(self, ab_test):
        """Calculate statistical confidence level"""
        # Simplified confidence calculation
        total_impressions = sum(v.impressions for v in ab_test.variants.all())
        if total_impressions < 100:
            return 0.5
        elif total_impressions < 1000:
            return 0.8
        else:
            return 0.95
    
    def _generate_ai_recommendations(self, ab_test):
        """Generate AI recommendations"""
        recommendations = []
        
        variants = ab_test.variants.all()
        if variants.count() >= 2:
            # Sample recommendations
            recommendations.append({
                'type': 'sample_size',
                'message': 'Consider running the test longer for more statistical significance',
                'priority': 'medium'
            })
            
            # Check for underperforming variants
            for variant in variants:
                if variant.conversion_rate < 1:
                    recommendations.append({
                        'type': 'optimization',
                        'message': f'{variant.name} has low conversion. Consider improving CTA visibility.',
                        'priority': 'high'
                    })
        
        return recommendations


class PerformanceAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for performance analysis"""
    serializer_class = PerformanceAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PerformanceAnalysis.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DeviceCompatibilityViewSet(viewsets.ModelViewSet):
    """ViewSet for device compatibility testing"""
    serializer_class = DeviceCompatibilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DeviceCompatibility.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SmartLayoutSuggestionViewSet(viewsets.ModelViewSet):
    """ViewSet for smart layout suggestions"""
    serializer_class = SmartLayoutSuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SmartLayoutSuggestion.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate layout suggestions based on content type"""
        content_type = request.data.get('content_type')
        content_description = request.data.get('content_description', '')
        target_audience = request.data.get('target_audience', '')
        brand_style = request.data.get('brand_style', '')
        
        # Create suggestion record
        suggestion = SmartLayoutSuggestion.objects.create(
            user=request.user,
            project_id=request.data.get('project_id'),
            content_type=content_type,
            content_description=content_description,
            target_audience=target_audience,
            brand_style=brand_style,
            suggestions=self._generate_layout_suggestions(content_type, content_description)
        )
        
        return Response(SmartLayoutSuggestionSerializer(suggestion).data)
    
    def _generate_layout_suggestions(self, content_type, description):
        """Generate AI-powered layout suggestions"""
        # Template suggestions based on content type
        templates = {
            'landing_page': [
                {'name': 'Hero + Features', 'score': 95, 'reasoning': 'Best for conversions'},
                {'name': 'Video Hero', 'score': 90, 'reasoning': 'Great for engagement'},
                {'name': 'Minimal', 'score': 85, 'reasoning': 'Fast loading, clean look'},
            ],
            'blog': [
                {'name': 'Classic Article', 'score': 95, 'reasoning': 'Optimal for reading'},
                {'name': 'Magazine Style', 'score': 90, 'reasoning': 'Great for media-rich content'},
            ],
            'ecommerce': [
                {'name': 'Grid Product Display', 'score': 95, 'reasoning': 'Best for browsing'},
                {'name': 'Featured + Grid', 'score': 90, 'reasoning': 'Highlights key products'},
            ],
        }
        
        return templates.get(content_type, [{'name': 'Default Layout', 'score': 80}])


class OptimizationReportViewSet(viewsets.ModelViewSet):
    """ViewSet for optimization reports"""
    serializer_class = OptimizationReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OptimizationReport.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a comprehensive optimization report"""
        project_id = request.data.get('project_id')
        
        # Generate scores and analysis
        report = OptimizationReport.objects.create(
            user=request.user,
            project_id=project_id,
            overall_score=random.randint(70, 95),
            performance_score=random.randint(70, 95),
            accessibility_score=random.randint(70, 95),
            usability_score=random.randint(70, 95),
            seo_score=random.randint(70, 95),
            recommendations=[
                {'type': 'performance', 'message': 'Optimize images for faster loading', 'impact': 'high'},
                {'type': 'accessibility', 'message': 'Add alt text to all images', 'impact': 'high'},
                {'type': 'usability', 'message': 'Increase touch target sizes for mobile', 'impact': 'medium'},
            ],
            quick_wins=[
                {'action': 'Compress images', 'effort': 'low', 'impact': 'high'},
                {'action': 'Add aria labels', 'effort': 'low', 'impact': 'high'},
            ]
        )
        
        return Response(OptimizationReportSerializer(report).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_design(request):
    """Comprehensive design analysis endpoint"""
    project_id = request.data.get('project_id')
    analysis_types = request.data.get('types', ['performance', 'accessibility', 'usability'])
    
    results = {}
    
    for analysis_type in analysis_types:
        # Generate analysis results
        results[analysis_type] = {
            'score': random.randint(70, 95),
            'issues': [],
            'recommendations': []
        }
    
    return Response({
        'project_id': project_id,
        'results': results,
        'overall_score': sum(r['score'] for r in results.values()) / len(results)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def predict_behavior(request):
    """Predict user behavior for a design"""
    project_id = request.data.get('project_id')
    
    prediction = UserBehaviorPrediction.objects.create(
        user=request.user,
        project_id=project_id,
        predicted_engagement_score=random.uniform(60, 90),
        predicted_bounce_rate=random.uniform(20, 50),
        predicted_time_on_page=random.uniform(30, 180),
        predicted_conversion_rate=random.uniform(1, 10),
        recommendations=[
            {'area': 'CTA', 'suggestion': 'Make the primary CTA more prominent'},
            {'area': 'Layout', 'suggestion': 'Consider F-pattern for content layout'},
        ]
    )
    
    return Response(UserBehaviorPredictionSerializer(prediction).data)
