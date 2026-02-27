from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from .models import AIGenerationRequest, AIPromptTemplate
from .serializers import (
    AIGenerationRequestSerializer,
    LayoutGenerationSerializer,
    LogoGenerationSerializer,
    ColorPaletteGenerationSerializer,
    DesignRefinementSerializer,
    ImageGenerationSerializer,
    AIPromptTemplateSerializer
)
from .services import AIDesignService, AIImageService
from .ai_assistant import AIDesignAssistant
from .prompt_templates import get_enhanced_prompt, get_ai_error_response, INDUSTRY_PROMPTS
from .enhanced_generation_engine import (
    get_generation_engine,
    GenerationConfig,
    DesignCategory,
    PlacementStrategy
)
from subscriptions.quota_service import check_ai_quota, QuotaService
import logging

logger = logging.getLogger('ai_services')


class AIGenerationThrottle(UserRateThrottle):
    """Rate limiting for AI generation endpoints"""
    rate = '50/hour'
    scope = 'ai_generation'


class AIBurstThrottle(UserRateThrottle):
    """Burst rate limiting for AI endpoints"""
    rate = '10/minute'
    scope = 'burst'


class AIGenerationRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing AI generation request history.
    """
    serializer_class = AIGenerationRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIGenerationRequest.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AIGenerationThrottle, AIBurstThrottle])
@check_ai_quota('layout_generation')
def generate_layout(request):
    """
    Generate a complete design layout from text prompt using enhanced generation engine.
    
    POST /api/ai/generate-layout/
    Body: {
        "prompt": "Create a modern travel app UI with map and booking button",
        "design_type": "ui_ux|graphic|logo",
        "industry": "travel" (optional - for industry-specific templates),
        "style": "modern" (optional),
        "canvas_width": 1920 (optional),
        "canvas_height": 1080 (optional),
        "color_scheme": ["#HEX", ...] (optional),
        "placement_strategy": "grid|centered|layered|flow|symmetrical" (optional)
    }
    """
    serializer = LayoutGenerationSerializer(data=request.data)
    if not serializer.is_valid():
        error_response = get_ai_error_response('invalid_prompt', str(serializer.errors))
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Map design_type to category
        design_type_map = {
            'ui_ux': DesignCategory.UI_UX,
            'graphic': DesignCategory.GRAPHIC,
            'logo': DesignCategory.LOGO,
        }
        
        design_type = serializer.validated_data.get('design_type', 'ui_ux')
        category = design_type_map.get(design_type, DesignCategory.UI_UX)
        
        # Map placement strategy
        placement_map = {
            'grid': PlacementStrategy.GRID,
            'centered': PlacementStrategy.CENTERED,
            'layered': PlacementStrategy.LAYERED,
            'flow': PlacementStrategy.FLOW,
            'symmetrical': PlacementStrategy.SYMMETRICAL,
        }
        
        placement_str = request.data.get('placement_strategy', 'grid')
        placement = placement_map.get(placement_str, PlacementStrategy.GRID)
        
        # Enhance prompt with industry context
        industry = request.data.get('industry', '')
        enhanced_prompt = get_enhanced_prompt(
            prompt=serializer.validated_data['prompt'],
            design_type=design_type,
            industry=industry,
            style=request.data.get('style', 'modern'),
            canvas_width=request.data.get('canvas_width', 1920),
            canvas_height=request.data.get('canvas_height', 1080),
        )
        
        # Get industry color scheme if not provided
        color_scheme = request.data.get('color_scheme')
        if not color_scheme and industry:
            industry_key = industry.lower().replace(' ', '_')
            if industry_key in INDUSTRY_PROMPTS:
                color_scheme = INDUSTRY_PROMPTS[industry_key]['color_schema']
        
        # Create configuration
        config = GenerationConfig(
            category=category,
            prompt=enhanced_prompt,
            canvas_width=request.data.get('canvas_width', 1920),
            canvas_height=request.data.get('canvas_height', 1080),
            style=request.data.get('style', 'modern'),
            color_scheme=color_scheme,
            placement_strategy=placement,
            include_guidelines=request.data.get('include_guidelines', True),
            include_variations=request.data.get('include_variations', False)
        )
        
        # Generate using enhanced engine
        engine = get_generation_engine()
        result = engine.generate_design(config)
        
        # Track request
        AIGenerationRequest.objects.create(
            user=request.user,
            request_type='layout',
            prompt=config.prompt,
            parameters={
                'design_type': design_type,
                'style': config.style,
                'canvas_size': f"{config.canvas_width}x{config.canvas_height}",
                'placement_strategy': placement_str
            },
            status='completed',
            result=result,
            model_used='enhanced_generation_engine_v1',
            tokens_used=2500  # 500 input + 2000 output tokens
        )
        
        # Record quota usage
        try:
            quota_service = QuotaService(request.user)
            quota_service.record_usage('layout_generation', input_tokens=500, output_tokens=2000)
        except Exception:
            pass  # Don't fail the request if quota recording fails
        
        return Response(result)
    
    except Exception as e:
        import traceback
        logger.exception("Error in generate_layout")
        
        # Determine error type for user-friendly messaging
        error_str = str(e).lower()
        if 'rate' in error_str or 'throttl' in error_str:
            error_type = 'rate_limit'
        elif 'quota' in error_str:
            error_type = 'quota_exceeded'
        elif 'content' in error_str and 'policy' in error_str:
            error_type = 'content_blocked'
        elif 'timeout' in error_str or 'connect' in error_str:
            error_type = 'service_unavailable'
        else:
            error_type = 'generation_failed'
        
        # Track failed request
        AIGenerationRequest.objects.create(
            user=request.user,
            request_type='layout',
            prompt=serializer.validated_data.get('prompt', ''),
            status='failed',
            error_message=str(e),
            model_used='enhanced_generation_engine_v1'
        )
        
        error_response = get_ai_error_response(error_type, str(e) if logger.isEnabledFor(logging.DEBUG) else '')
        return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('logo_generation')
def generate_logo(request):
    """
    Generate logo variations using AI.
    
    POST /api/ai/generate-logo/
    Body: {
        "company_name": "SkyTrip",
        "industry": "Travel",
        "style": "modern",
        "colors": ["#00AEEF", "#FFFFFF"]
    }
    """
    serializer = LogoGenerationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        ai_service = AIDesignService()
        result = ai_service.generate_logo(
            company_name=serializer.validated_data['company_name'],
            industry=serializer.validated_data.get('industry', ''),
            style=serializer.validated_data['style'],
            colors=serializer.validated_data.get('colors', []),
            user=request.user
        )
        
        return Response(result)
    
    except Exception:
        logger.exception("Error generating logo")
        return Response(
            {'error': 'Failed to generate logo. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('color_palette')
def generate_color_palette(request):
    """
    Generate color palette based on theme.
    
    POST /api/ai/generate-color-palette/
    Body: {
        "theme": "tropical beach sunset"
    }
    """
    serializer = ColorPaletteGenerationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        ai_service = AIDesignService()
        colors = ai_service.generate_color_palette(
            theme=serializer.validated_data['theme'],
            user=request.user
        )
        
        return Response({'colors': colors})
    
    except Exception:
        logger.exception("Error generating color palette")
        return Response(
            {'error': 'Failed to generate color palette. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('font_suggestion')
def suggest_fonts(request):
    """
    Suggest fonts based on design style.
    
    POST /api/ai/suggest-fonts/
    Body: {
        "design_style": "modern minimalist",
        "purpose": "heading"
    }
    """
    design_style = request.data.get('design_style', 'modern')
    purpose = request.data.get('purpose', 'general')
    
    try:
        ai_service = AIDesignService()
        fonts = ai_service.suggest_fonts(design_style, purpose)
        
        return Response({'fonts': fonts})
    
    except Exception:
        logger.exception("Error suggesting fonts")
        return Response(
            {'error': 'Failed to suggest fonts. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('design_refinement')
def refine_design(request):
    """
    Refine existing design based on instructions.
    
    POST /api/ai/refine-design/
    Body: {
        "current_design": {...},
        "refinement_instruction": "Make the header bigger and change colors to blue"
    }
    """
    serializer = DesignRefinementSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        ai_service = AIDesignService()
        result = ai_service.refine_design(
            current_design=serializer.validated_data['current_design'],
            refinement_instruction=serializer.validated_data['refinement_instruction'],
            user=request.user
        )
        
        return Response(result)
    
    except Exception:
        logger.exception("Error refining design")
        return Response(
            {'error': 'Failed to refine design. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('image_generation')
def generate_image(request):
    """
    Generate image using DALL-E.
    
    POST /api/ai/generate-image/
    Body: {
        "prompt": "A modern office workspace illustration",
        "size": "1024x1024",
        "style": "vivid"
    }
    """
    serializer = ImageGenerationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        ai_service = AIImageService()
        image_url = ai_service.generate_image(
            prompt=serializer.validated_data['prompt'],
            size=serializer.validated_data['size'],
            style=serializer.validated_data['style'],
            user=request.user
        )
        
        return Response({'image_url': image_url})
    
    except Exception:
        logger.exception("Error generating image")
        return Response(
            {'error': 'Failed to generate image. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AIPromptTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing AI prompt templates.
    """
    queryset = AIPromptTemplate.objects.filter(is_active=True)
    serializer_class = AIPromptTemplateSerializer
    permission_classes = [IsAuthenticated]


# AI Design Assistant Endpoints

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('design_critique')
def critique_design(request):
    """
    Get AI critique and feedback on a design.
    
    POST /api/ai/critique-design/
    Body: {
        "project_type": "social_media",
        "colors": ["#FF6B6B", "#4ECDC4"],
        "fonts": ["Roboto", "Open Sans"],
        "element_count": 12,
        "layout_type": "grid"
    }
    """
    design_data = request.data
    
    try:
        assistant = AIDesignAssistant()
        result = assistant.critique_design(design_data)
        
        if result['success']:
            # Log AI usage
            AIGenerationRequest.objects.create(
                user=request.user,
                request_type='design_critique',
                prompt=str(design_data),
                tokens_used=result.get('tokens_used', 0),
                status='completed'
            )
        
        return Response(result)
    
    except Exception:
        logger.exception("Error critiquing design")
        return Response(
            {'error': 'Failed to critique design. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('color_palette')
def generate_color_harmony(request):
    """
    Generate harmonious color palettes with AI.
    
    POST /api/ai/generate-color-harmony/
    Body: {
        "base_color": "#FF6B6B",
        "mood": "professional",
        "industry": "tech",
        "count": 5
    }
    """
    base_color = request.data.get('base_color')
    mood = request.data.get('mood')
    industry = request.data.get('industry')
    count = request.data.get('count', 5)
    
    try:
        assistant = AIDesignAssistant()
        result = assistant.generate_color_palette(
            base_color=base_color,
            mood=mood,
            industry=industry,
            count=count
        )
        
        if result['success']:
            # Log AI usage
            AIGenerationRequest.objects.create(
                user=request.user,
                request_type='color_harmony',
                prompt=f"Base: {base_color}, Mood: {mood}, Industry: {industry}",
                tokens_used=result.get('tokens_used', 0),
                status='completed'
            )
        
        return Response(result)
    
    except Exception:
        logger.exception("Error generating color harmony")
        return Response(
            {'error': 'Failed to generate color harmony. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('typography_suggestion')
def suggest_typography(request):
    """
    Get AI-powered typography pairing suggestions.
    
    POST /api/ai/suggest-typography/
    Body: {
        "design_type": "website",
        "mood": "professional",
        "brand_attributes": ["modern", "trustworthy", "innovative"]
    }
    """
    design_type = request.data.get('design_type', 'website')
    mood = request.data.get('mood', 'professional')
    brand_attributes = request.data.get('brand_attributes', [])
    
    try:
        assistant = AIDesignAssistant()
        result = assistant.suggest_typography(
            design_type=design_type,
            mood=mood,
            brand_attributes=brand_attributes
        )
        
        if result['success']:
            # Log AI usage
            AIGenerationRequest.objects.create(
                user=request.user,
                request_type='typography_suggestion',
                prompt=f"Type: {design_type}, Mood: {mood}",
                tokens_used=result.get('tokens_used', 0),
                status='completed'
            )
        
        return Response(result)
    
    except Exception:
        logger.exception("Error suggesting typography")
        return Response(
            {'error': 'Failed to suggest typography. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('layout_optimization')
def optimize_layout(request):
    """
    Get AI suggestions for layout optimization.
    
    POST /api/ai/optimize-layout/
    Body: {
        "element_count": 15,
        "layout_type": "grid",
        "width": 1920,
        "height": 1080,
        "element_distribution": "uneven"
    }
    """
    design_data = request.data
    
    try:
        assistant = AIDesignAssistant()
        result = assistant.optimize_layout(design_data)
        
        if result['success']:
            # Log AI usage
            AIGenerationRequest.objects.create(
                user=request.user,
                request_type='layout_optimization',
                prompt=str(design_data),
                tokens_used=result.get('tokens_used', 0),
                status='completed'
            )
        
        return Response(result)
    
    except Exception:
        logger.exception("Error optimizing layout")
        return Response(
            {'error': 'Failed to optimize layout. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('trend_analysis')
def analyze_design_trends(request):
    """
    Get insights on current design trends.
    
    POST /api/ai/analyze-design-trends/
    Body: {
        "industry": "tech",
        "design_type": "website"
    }
    """
    industry = request.data.get('industry', 'general')
    design_type = request.data.get('design_type', 'general')
    
    try:
        assistant = AIDesignAssistant()
        result = assistant.analyze_design_trends(
            industry=industry,
            design_type=design_type
        )
        
        if result['success']:
            # Log AI usage
            AIGenerationRequest.objects.create(
                user=request.user,
                request_type='trend_analysis',
                prompt=f"Industry: {industry}, Type: {design_type}",
                tokens_used=result.get('tokens_used', 0),
                status='completed'
            )
        
        return Response(result)
    
    except Exception:
        logger.exception("Error analyzing design trends")
        return Response(
            {'error': 'Failed to analyze design trends. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('improvement_suggestions')
def suggest_improvements(request):
    """
    Get comprehensive design improvement suggestions.
    
    POST /api/ai/suggest-improvements/
    Body: {
        "project_type": "website",
        "colors": [...],
        "fonts": [...],
        "focus_areas": ["accessibility", "visual_hierarchy"]
    }
    """
    design_data = request.data.get('design_data', {})
    focus_areas = request.data.get('focus_areas', [])
    
    try:
        assistant = AIDesignAssistant()
        result = assistant.suggest_improvements(
            design_data=design_data,
            focus_areas=focus_areas
        )
        
        if result['success']:
            # Log AI usage
            AIGenerationRequest.objects.create(
                user=request.user,
                request_type='improvement_suggestions',
                prompt=str(design_data),
                tokens_used=result.get('tokens_used', 0),
                status='completed'
            )
        
        return Response(result)
    
    except Exception:
        logger.exception("Error suggesting improvements")
        return Response(
            get_ai_error_response('generation_failed'),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_industries(request):
    """
    List available industry templates for AI generation.
    Returns industry names and their design characteristics.
    """
    industries = []
    for key, data in INDUSTRY_PROMPTS.items():
        industries.append({
            'id': key,
            'name': key.replace('_', ' ').title(),
            'color_schema': data['color_schema'],
            'components': data['components'][:5],
            'style_guide': data['style_guide'][:100] + '...',
        })
    return Response({'industries': industries})
