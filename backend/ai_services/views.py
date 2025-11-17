from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
def generate_layout(request):
    """
    Generate a complete design layout from text prompt.
    
    POST /api/ai/generate-layout/
    Body: {
        "prompt": "Create a modern travel app UI with map and booking button",
        "design_type": "ui_ux"
    }
    """
    serializer = LayoutGenerationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        ai_service = AIDesignService()
        result = ai_service.generate_layout_from_prompt(
            prompt=serializer.validated_data['prompt'],
            design_type=serializer.validated_data['design_type'],
            user=request.user
        )
        
        return Response(result)
    
    except Exception as e:
        import traceback
        print("Error in generate_layout:")
        print(traceback.format_exc())
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
