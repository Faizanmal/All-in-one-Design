"""
Advanced AI Views
REST API endpoints for advanced AI capabilities
"""
import base64
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from subscriptions.quota_service import check_ai_quota
from subscriptions.feature_gating import require_feature

logger = logging.getLogger('ai_services')

from .advanced_ai_models import (
    ImageToDesignRequest,
    StyleTransferRequest,
    VoiceToDesignRequest,
    DesignTrend,
    TrendAnalysisRequest,
    AIDesignSuggestion
)
from .advanced_ai_serializers import (
    DesignTrendSerializer,
    AIDesignSuggestionSerializer
)
from .advanced_ai_service import get_advanced_ai_service
from projects.models import Project


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_feature('advanced_ai')
@check_ai_quota('image_to_design')
def image_to_design(request):
    """
    Convert an image to a design structure
    
    Body:
        image: Base64 encoded image or file upload
        prompt: Additional instructions (optional)
        design_type: Target design type (default: ui_ux)
        options: Extraction options
    """
    # Get image
    image_file = request.FILES.get('image')
    image_base64 = request.data.get('image_base64')
    
    if image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    elif not image_base64:
        return Response(
            {'error': 'Image is required (file upload or base64)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    prompt = request.data.get('prompt', '')
    design_type = request.data.get('design_type', 'ui_ux')
    options = request.data.get('options', {})
    
    # Create request record
    img_request = ImageToDesignRequest.objects.create(
        user=request.user,
        prompt=prompt,
        target_design_type=design_type,
        extract_colors=options.get('extract_colors', True),
        extract_typography=options.get('extract_typography', True),
        extract_layout=options.get('extract_layout', True),
        preserve_style=options.get('preserve_style', True),
        status='processing'
    )
    
    try:
        service = get_advanced_ai_service()
        result = service.image_to_design(
            image_base64=image_base64,
            prompt=prompt,
            design_type=design_type,
            options=options,
            user=request.user
        )
        
        # Create project if requested
        if request.data.get('create_project', False):
            project = Project.objects.create(
                user=request.user,
                name=request.data.get('project_name', 'Image Import'),
                description=f'Generated from image: {prompt}',
                project_type=design_type,
                design_data=result,
                ai_prompt=prompt
            )
            img_request.result_project = project
        
        img_request.status = 'completed'
        img_request.result_data = result
        img_request.completed_at = timezone.now()
        img_request.save()
        
        return Response({
            'request_id': img_request.id,
            'design_data': result,
            'project_id': img_request.result_project_id
        })
        
    except Exception as e:
        img_request.status = 'failed'
        img_request.error_message = str(e)
        img_request.save()
        
        logger.exception("Error in image_to_design")
        return Response(
            {'error': 'Failed to convert image to design. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_feature('advanced_ai')
@check_ai_quota('style_transfer')
def apply_style_transfer(request):
    """
    Apply style transfer to a design
    
    Body:
        project_id: Source project ID
        style_preset: Style preset name
        style_description: Custom style description (optional)
        options: Transfer options
        create_new_project: Whether to create a new project
    """
    project_id = request.data.get('project_id')
    style_preset = request.data.get('style_preset', 'minimalist')
    style_description = request.data.get('style_description', '')
    options = request.data.get('options', {})
    
    if not project_id:
        return Response(
            {'error': 'project_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response(
            {'error': 'Project not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Create request record
    style_request = StyleTransferRequest.objects.create(
        user=request.user,
        source_project=project,
        style_preset=style_preset,
        style_description=style_description,
        transfer_colors=options.get('transfer_colors', True),
        transfer_typography=options.get('transfer_typography', True),
        transfer_spacing=options.get('transfer_spacing', True),
        transfer_shapes=options.get('transfer_shapes', True),
        intensity=options.get('intensity', 0.8),
        status='processing'
    )
    
    try:
        service = get_advanced_ai_service()
        result = service.apply_style_transfer(
            design_data=project.design_data,
            style_preset=style_preset,
            style_description=style_description,
            options=options,
            user=request.user
        )
        
        # Create new project or update existing
        if request.data.get('create_new_project', True):
            new_project = Project.objects.create(
                user=request.user,
                name=f"{project.name} ({style_preset} style)",
                description=f'Style transfer from {project.name}',
                project_type=project.project_type,
                design_data=result,
                ai_prompt=f'Style transfer: {style_preset}'
            )
            style_request.result_project = new_project
        else:
            project.design_data = result
            project.save()
            style_request.result_project = project
        
        style_request.status = 'completed'
        style_request.result_data = result
        style_request.completed_at = timezone.now()
        style_request.save()
        
        return Response({
            'request_id': style_request.id,
            'design_data': result,
            'project_id': style_request.result_project_id
        })
        
    except Exception as e:
        style_request.status = 'failed'
        style_request.error_message = str(e)
        style_request.save()
        
        logger.exception("Error in apply_style_transfer")
        return Response(
            {'error': 'Failed to apply style transfer. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_feature('advanced_ai')
@check_ai_quota('voice_to_design')
def voice_to_design(request):
    """
    Convert voice recording to design
    
    Body:
        audio: Audio file upload
        design_type: Target design type
        additional_context: Extra context
    """
    audio_file = request.FILES.get('audio')
    
    if not audio_file:
        return Response(
            {'error': 'Audio file is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    design_type = request.data.get('design_type', 'ui_ux')
    additional_context = request.data.get('additional_context', '')
    
    # Create request record
    voice_request = VoiceToDesignRequest.objects.create(
        user=request.user,
        audio_file=audio_file,
        design_type=design_type,
        additional_context=additional_context,
        status='transcribing'
    )
    
    # Note: Full implementation requires Whisper API integration
    # For now, return a placeholder response
    
    return Response({
        'request_id': voice_request.id,
        'status': 'transcribing',
        'message': 'Voice transcription in progress. Use /voice-to-design/{id}/generate/ after transcription.'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_feature('advanced_ai')
@check_ai_quota('voice_to_design')
def generate_from_voice_transcription(request, request_id):
    """
    Generate design from transcribed voice text
    
    Body:
        transcribed_text: The transcribed text (if manual)
    """
    try:
        voice_request = VoiceToDesignRequest.objects.get(
            id=request_id,
            user=request.user
        )
    except VoiceToDesignRequest.DoesNotExist:
        return Response(
            {'error': 'Voice request not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Use provided text or stored transcription
    transcribed_text = request.data.get('transcribed_text') or voice_request.transcribed_text
    
    if not transcribed_text:
        return Response(
            {'error': 'No transcribed text available'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    voice_request.transcribed_text = transcribed_text
    voice_request.status = 'generating'
    voice_request.save()
    
    try:
        service = get_advanced_ai_service()
        result = service.generate_from_transcription(
            transcribed_text=transcribed_text,
            design_type=voice_request.design_type,
            user=request.user
        )
        
        # Create project
        project = Project.objects.create(
            user=request.user,
            name=f"Voice Design - {transcribed_text[:50]}...",
            description=f'Generated from voice: {transcribed_text}',
            project_type=voice_request.design_type,
            design_data=result,
            ai_prompt=transcribed_text
        )
        
        voice_request.result_project = project
        voice_request.status = 'completed'
        voice_request.result_data = result
        voice_request.completed_at = timezone.now()
        voice_request.save()
        
        return Response({
            'request_id': voice_request.id,
            'transcribed_text': transcribed_text,
            'design_data': result,
            'project_id': project.id
        })
        
    except Exception as e:
        voice_request.status = 'failed'
        voice_request.error_message = str(e)
        voice_request.save()
        
        logger.exception("Error in generate_from_voice_transcription")
        return Response(
            {'error': 'Failed to generate design from voice. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('trend_analysis')
def analyze_design_trends(request, project_id):
    """
    Analyze a project against current design trends
    """
    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response(
            {'error': 'Project not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    industry = request.data.get('industry', 'general')
    
    try:
        service = get_advanced_ai_service()
        result = service.analyze_design_trends(
            design_data=project.design_data,
            industry=industry,
            user=request.user
        )
        
        # Create analysis record
        analysis = TrendAnalysisRequest.objects.create(
            user=request.user,
            project=project,
            overall_score=result.get('overall_score'),
            color_score=result.get('scores', {}).get('colors'),
            typography_score=result.get('scores', {}).get('typography'),
            layout_score=result.get('scores', {}).get('layout'),
            recommendations=result.get('recommendations', []),
            analysis_data=result
        )
        
        return Response({
            'analysis_id': analysis.id,
            'project_id': project.id,
            **result
        })
        
    except Exception:
        logger.exception("Error analyzing design trends")
        return Response(
            {'error': 'Failed to analyze design trends. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_trends(request):
    """
    Get current design trends
    
    Query params:
        category: Filter by category
        industry: Filter by industry
        limit: Number of trends to return
    """
    queryset = DesignTrend.objects.filter(is_active=True)
    
    category = request.query_params.get('category')
    if category:
        queryset = queryset.filter(category=category)
    
    industry = request.query_params.get('industry')
    if industry:
        queryset = queryset.filter(industries__contains=[industry])
    
    limit = int(request.query_params.get('limit', 20))
    queryset = queryset[:limit]
    
    serializer = DesignTrendSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@check_ai_quota('improvement_suggestions')
def get_design_suggestions(request, project_id):
    """
    Get AI-powered improvement suggestions for a project
    
    Body:
        focus_areas: List of areas to focus on
    """
    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response(
            {'error': 'Project not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    focus_areas = request.data.get('focus_areas', ['colors', 'typography', 'layout', 'accessibility'])
    
    try:
        service = get_advanced_ai_service()
        suggestions = service.get_design_suggestions(
            design_data=project.design_data,
            focus_areas=focus_areas,
            user=request.user
        )
        
        # Store suggestions
        created_suggestions = []
        for suggestion in suggestions:
            db_suggestion = AIDesignSuggestion.objects.create(
                project=project,
                suggestion_type=suggestion.get('type', 'layout'),
                priority=suggestion.get('priority', 'medium'),
                title=suggestion.get('title', 'Improvement suggestion'),
                description=suggestion.get('description', ''),
                affected_element_ids=suggestion.get('affected_elements', []),
                suggested_changes={
                    'current': suggestion.get('current_value'),
                    'suggested': suggestion.get('suggested_value'),
                    'impact': suggestion.get('impact')
                }
            )
            created_suggestions.append(db_suggestion)
        
        serializer = AIDesignSuggestionSerializer(created_suggestions, many=True)
        return Response({
            'project_id': project.id,
            'suggestions': serializer.data
        })
        
    except Exception:
        logger.exception("Error getting design suggestions")
        return Response(
            {'error': 'Failed to get design suggestions. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_suggestion(request, suggestion_id):
    """
    Apply a design suggestion to the project
    """
    try:
        suggestion = AIDesignSuggestion.objects.get(
            id=suggestion_id,
            project__user=request.user
        )
    except AIDesignSuggestion.DoesNotExist:
        return Response(
            {'error': 'Suggestion not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Mark as applied
    suggestion.is_applied = True
    suggestion.save()
    
    # The actual application logic would depend on the suggestion type
    # For now, we just return success
    
    return Response({
        'status': 'applied',
        'suggestion_id': suggestion.id
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dismiss_suggestion(request, suggestion_id):
    """
    Dismiss a design suggestion
    """
    try:
        suggestion = AIDesignSuggestion.objects.get(
            id=suggestion_id,
            project__user=request.user
        )
    except AIDesignSuggestion.DoesNotExist:
        return Response(
            {'error': 'Suggestion not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    suggestion.is_dismissed = True
    suggestion.user_feedback = request.data.get('feedback', '')
    suggestion.save()
    
    return Response({
        'status': 'dismissed',
        'suggestion_id': suggestion.id
    })


class DesignTrendViewSet(viewsets.ReadOnlyModelViewSet):
    """View design trends"""
    serializer_class = DesignTrendSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DesignTrend.objects.filter(is_active=True)


class AIDesignSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    """View design suggestions"""
    serializer_class = AIDesignSuggestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AIDesignSuggestion.objects.filter(
            project__user=self.request.user,
            is_dismissed=False
        )
        
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
