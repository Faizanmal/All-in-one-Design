"""
Views for enhanced AI design services
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .enhanced_ai_service import EnhancedAIDesignService
from projects.models import Project
from projects.collaboration_models import DesignFeedback
from analytics.models import AIUsageLog


class EnhancedAIViewSet(viewsets.ViewSet):
    """
    ViewSet for enhanced AI design features
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_service = EnhancedAIDesignService()
    
    @action(detail=False, methods=['post'])
    def generate_variants(self, request):
        """
        Generate multiple design variants from a text prompt
        POST /api/ai/generate_variants/
        {
            "prompt": "Modern tech startup landing page",
            "design_type": "ui_ux",
            "num_variants": 3,
            "style_preferences": {"mood": "professional", "colors": "blue"}
        }
        """
        prompt = request.data.get('prompt')
        if not prompt:
            return Response(
                {'error': 'prompt is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        design_type = request.data.get('design_type', 'graphic')
        num_variants = request.data.get('num_variants', 3)
        style_preferences = request.data.get('style_preferences', {})
        
        # Generate variants
        result = self.ai_service.generate_design_variants(
            prompt=prompt,
            design_type=design_type,
            num_variants=num_variants,
            style_preferences=style_preferences
        )
        
        if result.get('success'):
            # Log AI usage
            AIUsageLog.objects.create(
                user=request.user,
                service='enhanced_ai',
                operation='generate_variants',
                tokens_used=result.get('tokens_used', 0),
                cost=result.get('tokens_used', 0) * 0.00003,  # Approximate cost
                metadata={
                    'prompt': prompt,
                    'num_variants': num_variants,
                    'design_type': design_type
                }
            )
            
            return Response({
                'variants': result['variants'],
                'comparison': result.get('comparison', ''),
                'recommendation': result.get('recommendation', ''),
                'tokens_used': result.get('tokens_used', 0)
            })
        
        return Response(
            {'error': result.get('error', 'Failed to generate variants')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=False, methods=['post'])
    def auto_layout(self, request):
        """
        Generate responsive layouts for different screen sizes
        POST /api/ai/auto_layout/
        {
            "project_id": 123,
            "target_sizes": [
                {"width": 1920, "height": 1080, "name": "desktop"},
                {"width": 768, "height": 1024, "name": "tablet"},
                {"width": 375, "height": 667, "name": "mobile"}
            ]
        }
        """
        project_id = request.data.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, id=project_id, user=request.user)
        target_sizes = request.data.get('target_sizes')
        
        # Generate responsive variants
        result = self.ai_service.generate_auto_layout(
            design_data=project.design_data,
            target_sizes=target_sizes
        )
        
        if result.get('success'):
            # Log AI usage
            AIUsageLog.objects.create(
                user=request.user,
                service='enhanced_ai',
                operation='auto_layout',
                tokens_used=result.get('tokens_used', 0),
                cost=result.get('tokens_used', 0) * 0.00003,
                metadata={'project_id': project_id}
            )
            
            return Response({
                'responsive_variants': result['responsive_variants'],
                'tokens_used': result.get('tokens_used', 0)
            })
        
        return Response(
            {'error': result.get('error', 'Failed to generate responsive layout')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=False, methods=['post'])
    def suggest_improvements(self, request):
        """
        Get AI-powered improvement suggestions for a design
        POST /api/ai/suggest_improvements/
        {
            "project_id": 123,
            "focus_areas": ["color", "typography", "layout"]
        }
        """
        project_id = request.data.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, id=project_id, user=request.user)
        focus_areas = request.data.get('focus_areas')
        
        # Get improvement suggestions
        result = self.ai_service.suggest_improvements(
            design_data=project.design_data,
            focus_areas=focus_areas
        )
        
        if result.get('success'):
            # Save feedback to database
            DesignFeedback.objects.create(
                project=project,
                feedback_type='layout_suggestion',
                feedback_data={
                    'assessment': result.get('assessment', {}),
                    'improvements': result.get('improvements', []),
                    'quick_wins': result.get('quick_wins', [])
                },
                model_used='gpt-4',
                tokens_used=result.get('tokens_used', 0),
                processing_time=0.0
            )
            
            # Log AI usage
            AIUsageLog.objects.create(
                user=request.user,
                service='enhanced_ai',
                operation='suggest_improvements',
                tokens_used=result.get('tokens_used', 0),
                cost=result.get('tokens_used', 0) * 0.00003,
                metadata={'project_id': project_id}
            )
            
            return Response({
                'assessment': result.get('assessment', {}),
                'improvements': result.get('improvements', []),
                'quick_wins': result.get('quick_wins', []),
                'advanced_tips': result.get('advanced_tips', [])
            })
        
        return Response(
            {'error': result.get('error', 'Failed to generate suggestions')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=False, methods=['post'])
    def check_accessibility(self, request):
        """
        Check design for accessibility issues
        POST /api/ai/check_accessibility/
        {
            "project_id": 123
        }
        """
        project_id = request.data.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        # Check accessibility
        result = self.ai_service.check_accessibility(project.design_data)
        
        if result.get('success'):
            # Save feedback to database
            DesignFeedback.objects.create(
                project=project,
                feedback_type='accessibility',
                feedback_data={
                    'wcag_level': result.get('wcag_level', 'A'),
                    'score': result.get('score', 0),
                    'issues': result.get('issues', []),
                    'passed_checks': result.get('passed_checks', []),
                    'summary': result.get('summary', '')
                },
                model_used='gpt-4',
                tokens_used=result.get('tokens_used', 0),
                processing_time=0.0
            )
            
            # Log AI usage
            AIUsageLog.objects.create(
                user=request.user,
                service='enhanced_ai',
                operation='check_accessibility',
                tokens_used=result.get('tokens_used', 0),
                cost=result.get('tokens_used', 0) * 0.00003,
                metadata={'project_id': project_id}
            )
            
            return Response({
                'wcag_level': result.get('wcag_level', 'A'),
                'score': result.get('score', 0),
                'issues': result.get('issues', []),
                'passed_checks': result.get('passed_checks', []),
                'summary': result.get('summary', '')
            })
        
        return Response(
            {'error': result.get('error', 'Failed to check accessibility')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=False, methods=['post'])
    def generate_brand_assets(self, request):
        """
        Generate complete brand identity system
        POST /api/ai/generate_brand_assets/
        {
            "brand_description": "Modern eco-friendly tech startup...",
            "asset_types": ["logo", "color_palette", "typography"]
        }
        """
        brand_description = request.data.get('brand_description')
        if not brand_description:
            return Response(
                {'error': 'brand_description is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        asset_types = request.data.get('asset_types')
        
        # Generate brand assets
        result = self.ai_service.generate_brand_assets(
            brand_description=brand_description,
            asset_types=asset_types
        )
        
        if result.get('success'):
            # Log AI usage
            AIUsageLog.objects.create(
                user=request.user,
                service='enhanced_ai',
                operation='generate_brand_assets',
                tokens_used=result.get('tokens_used', 0),
                cost=result.get('tokens_used', 0) * 0.00003,
                metadata={
                    'brand_description': brand_description[:100],
                    'asset_types': asset_types
                }
            )
            
            return Response({
                'brand_assets': result['brand_assets'],
                'tokens_used': result.get('tokens_used', 0)
            })
        
        return Response(
            {'error': result.get('error', 'Failed to generate brand assets')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
