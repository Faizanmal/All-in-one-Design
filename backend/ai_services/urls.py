from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIGenerationRequestViewSet,
    AIPromptTemplateViewSet,
    generate_layout,
    generate_logo,
    generate_color_palette,
    suggest_fonts,
    refine_design,
    generate_image,
    # AI Design Assistant endpoints
    critique_design,
    generate_color_harmony,
    suggest_typography,
    optimize_layout,
    analyze_design_trends,
    suggest_improvements,
    list_industries,
)
from .chat_views import ChatConversationViewSet, AIFeedbackViewSet
from .enhanced_ai_views import EnhancedAIViewSet
from .advanced_ai_views import (
    DesignTrendViewSet,
    AIDesignSuggestionViewSet,
    image_to_design,
    apply_style_transfer,
    voice_to_design,
    generate_from_voice_transcription,
    analyze_design_trends as analyze_trends,
    get_current_trends,
    get_design_suggestions,
    apply_suggestion,
    dismiss_suggestion
)
from .accessibility_views import (
    audit_project,
    apply_auto_fixes,
    check_contrast,
    analyze_palette,
)
from .auto_layout_views import (
    AutoLayoutViewSet,
    get_layout_presets
)
from .background_remover_views import (
    remove_background as bg_remove,
    replace_background as bg_replace,
    remover_info as bg_info,
)

router = DefaultRouter()
router.register(r'requests', AIGenerationRequestViewSet, basename='ai-request')
router.register(r'templates', AIPromptTemplateViewSet, basename='ai-template')
router.register(r'chat', ChatConversationViewSet, basename='chat')
router.register(r'feedback', AIFeedbackViewSet, basename='ai-feedback')
router.register(r'enhanced', EnhancedAIViewSet, basename='enhanced-ai')

# Advanced AI routers
router.register(r'trends', DesignTrendViewSet, basename='design-trend')
router.register(r'suggestions', AIDesignSuggestionViewSet, basename='design-suggestion')
router.register(r'layout', AutoLayoutViewSet, basename='auto-layout')

urlpatterns = [
    path('', include(router.urls)),
    # Original AI generation endpoints
    path('generate-layout/', generate_layout, name='generate-layout'),
    path('generate-logo/', generate_logo, name='generate-logo'),
    path('generate-color-palette/', generate_color_palette, name='generate-color-palette'),
    path('suggest-fonts/', suggest_fonts, name='suggest-fonts'),
    path('refine-design/', refine_design, name='refine-design'),
    path('generate-image/', generate_image, name='generate-image'),
    
    # AI Design Assistant endpoints
    path('critique-design/', critique_design, name='critique-design'),
    path('generate-color-harmony/', generate_color_harmony, name='generate-color-harmony'),
    path('suggest-typography/', suggest_typography, name='suggest-typography'),
    path('optimize-layout/', optimize_layout, name='optimize-layout'),
    path('analyze-design-trends/', analyze_design_trends, name='analyze-design-trends'),
    path('suggest-improvements/', suggest_improvements, name='suggest-improvements'),
    path('industries/', list_industries, name='list-industries'),
    
    # Advanced AI endpoints
    path('advanced/image-to-design/', image_to_design, name='advanced-image-to-design'),
    path('advanced/style-transfer/', apply_style_transfer, name='advanced-style-transfer'),
    path('advanced/voice-to-design/', voice_to_design, name='advanced-voice-to-design'),
    path('advanced/voice-to-design/<int:request_id>/generate/', generate_from_voice_transcription, name='advanced-voice-generate'),
    path('advanced/current-trends/', get_current_trends, name='advanced-current-trends'),
    path('projects/<int:project_id>/design-suggestions/', get_design_suggestions, name='get-design-suggestions'),
    path('projects/<int:project_id>/analyze-trends/', analyze_trends, name='analyze-trends'),
    path('suggestions/<int:suggestion_id>/apply/', apply_suggestion, name='apply-suggestion'),
    path('suggestions/<int:suggestion_id>/dismiss/', dismiss_suggestion, name='dismiss-suggestion'),
    
    # Accessibility audit endpoints
    path('accessibility/projects/<int:project_id>/audit/', audit_project, name='accessibility-audit'),
    path('accessibility/projects/<int:project_id>/fix/', apply_auto_fixes, name='accessibility-fix'),
    path('accessibility/check-contrast/', check_contrast, name='accessibility-check-contrast'),
    path('accessibility/analyze-palette/', analyze_palette, name='accessibility-analyze-palette'),
    
    # Auto-layout endpoints
    path('layout/presets/', get_layout_presets, name='layout-presets'),
    
    # Background remover endpoints
    path('background-remover/remove/', bg_remove, name='bg-remove'),
    path('background-remover/replace/', bg_replace, name='bg-replace'),
    path('background-remover/info/', bg_info, name='bg-info'),
]
