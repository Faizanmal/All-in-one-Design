from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, DesignComponentViewSet, ExportTemplateViewSet, ExportJobViewSet
from .search_views import (
    search_projects,
    autocomplete,
    search_suggestions,
    popular_searches,
    search_filters
)
from .export_views import (
    export_project_pdf,
    export_project_figma,
    export_project_mp4,
    export_project_svg_optimized,
    batch_export_projects,
    create_export_template,
    export_with_template,
    list_export_templates,
    delete_export_template,
    export_social_media_pack,
    export_print_ready,
    export_formats_info
)
from .template_views import DesignTemplateViewSet, ProjectTagViewSet
from .advanced_search_views import (
    AdvancedProjectSearchView,
    AdvancedAssetSearchView,
    AdvancedTemplateSearchView,
    AdvancedTeamSearchView,
    GlobalSearchView
)
# New enhanced features
from .collaboration_views import (
    CollaborationSessionViewSet,
    CanvasEditViewSet,
    CommentViewSet,
    ReviewViewSet,
    DesignFeedbackViewSet
)
from .enhanced_template_views import TemplateViewSet as EnhancedTemplateViewSet, TemplateComponentViewSet

# Developer handoff and productivity features
from .developer_handoff_views import (
    CodeExportViewSet,
    DesignSystemViewSet,
    export_to_code,
    download_code_export,
    create_design_system,
    export_design_system,
    generate_component_specs
)
from .productivity_views import (
    ABTestViewSet,
    ABTestVariantViewSet,
    track_ab_event,
    PluginViewSet,
    PluginInstallationViewSet,
    PluginReviewViewSet,
    OfflineSyncViewSet,
    UserPreferenceViewSet
)
from .enhanced_collaboration_views import (
    VideoConferenceRoomViewSet,
    GuestAccessViewSet,
    guest_access_view,
    DesignReviewSessionViewSet,
    ReviewAnnotationViewSet,
    CollaborationPresenceViewSet
)
# Version control
from .version_views import ProjectVersionViewSet, compare_versions

# New Phase 2 Features
from .design_tokens_views import (
    DesignTokenLibraryViewSet,
    DesignTokenViewSet,
    DesignThemeViewSet,
    bind_library_to_project,
    sync_tokens_to_project,
    analyze_token_usage
)
from .batch_operations_views import BatchOperationViewSet
from .export_presets_views import (
    ExportPresetViewSet,
    ExportBundleViewSet,
    ScheduledExportViewSet,
    ExportHistoryViewSet,
    ExportViewSet
)
from .keyboard_shortcuts_views import (
    ShortcutsViewSet,
    ShortcutPresetsViewSet,
    LearningModeViewSet
)
from .magic_resize_views import resize_presets, resize_project, resize_preview

router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')
router.register(r'components', DesignComponentViewSet, basename='component')
router.register(r'export-templates', ExportTemplateViewSet, basename='export-template')
router.register(r'export-jobs', ExportJobViewSet, basename='export-job')
router.register(r'templates', DesignTemplateViewSet, basename='design-template')
router.register(r'tags', ProjectTagViewSet, basename='project-tag')

# Enhanced features routers
router.register(r'collaboration/sessions', CollaborationSessionViewSet, basename='collaboration-session')
router.register(r'collaboration/edits', CanvasEditViewSet, basename='canvas-edit')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'feedback', DesignFeedbackViewSet, basename='design-feedback')
router.register(r'enhanced-templates', EnhancedTemplateViewSet, basename='enhanced-template')
router.register(r'template-components', TemplateComponentViewSet, basename='template-component')

# Developer handoff routers
router.register(r'code-exports', CodeExportViewSet, basename='code-export')
router.register(r'design-systems', DesignSystemViewSet, basename='design-system')

# Productivity routers
router.register(r'ab-tests', ABTestViewSet, basename='ab-test')
router.register(r'ab-tests/variants', ABTestVariantViewSet, basename='ab-test-variant')
router.register(r'plugins', PluginViewSet, basename='plugin')
router.register(r'plugin-installations', PluginInstallationViewSet, basename='plugin-installation')
router.register(r'plugin-reviews', PluginReviewViewSet, basename='plugin-review')
router.register(r'offline-syncs', OfflineSyncViewSet, basename='offline-sync')
router.register(r'preferences', UserPreferenceViewSet, basename='user-preference')

# Enhanced collaboration routers
router.register(r'video-conferences', VideoConferenceRoomViewSet, basename='video-conference')
router.register(r'guest-access', GuestAccessViewSet, basename='guest-access')
router.register(r'review-sessions', DesignReviewSessionViewSet, basename='review-session')
router.register(r'review-annotations', ReviewAnnotationViewSet, basename='review-annotation')
router.register(r'presence', CollaborationPresenceViewSet, basename='collaboration-presence')

# New Phase 2 Features
router.register(r'design-token-libraries', DesignTokenLibraryViewSet, basename='design-token-library')
router.register(r'design-tokens', DesignTokenViewSet, basename='design-token')
router.register(r'design-themes', DesignThemeViewSet, basename='design-theme')
router.register(r'batch-operations', BatchOperationViewSet, basename='batch-operation')
router.register(r'export-presets', ExportPresetViewSet, basename='export-preset')
router.register(r'export-bundles', ExportBundleViewSet, basename='export-bundle')
router.register(r'scheduled-exports', ScheduledExportViewSet, basename='scheduled-export')
router.register(r'export-history', ExportHistoryViewSet, basename='export-history')
router.register(r'export', ExportViewSet, basename='export')
router.register(r'shortcuts', ShortcutsViewSet, basename='shortcuts')
router.register(r'shortcut-presets', ShortcutPresetsViewSet, basename='shortcut-presets')
router.register(r'shortcuts-learning', LearningModeViewSet, basename='shortcuts-learning')

urlpatterns = [
    path('', include(router.urls)),
    # Advanced search endpoints
    path('search/', search_projects, name='search-projects'),
    path('autocomplete/', autocomplete, name='autocomplete'),
    path('search-suggestions/', search_suggestions, name='search-suggestions'),
    path('popular-searches/', popular_searches, name='popular-searches'),
    path('search-filters/', search_filters, name='search-filters'),
    
    # Advanced export endpoints
    path('projects/<int:project_id>/export/pdf/', export_project_pdf, name='export-pdf'),
    path('projects/<int:project_id>/export/figma/', export_project_figma, name='export-figma'),
    path('projects/<int:project_id>/export/mp4/', export_project_mp4, name='export-mp4'),
    path('projects/<int:project_id>/export/svg/optimized/', export_project_svg_optimized, name='export-svg-optimized'),
    path('projects/<int:project_id>/export/social-pack/', export_social_media_pack, name='export-social-pack'),
    path('projects/<int:project_id>/export/print-ready/', export_print_ready, name='export-print-ready'),
    path('projects/<int:project_id>/export/template/<int:template_id>/', export_with_template, name='export-with-template'),
    path('projects/export/batch/', batch_export_projects, name='batch-export'),
    path('projects/export/templates/', list_export_templates, name='list-export-templates'),
    path('projects/export/templates/create/', create_export_template, name='create-export-template'),
    path('projects/export/templates/<int:template_id>/', delete_export_template, name='delete-export-template'),
    path('projects/export/formats/', export_formats_info, name='export-formats-info'),
    
    # Advanced search endpoints
    path('advanced-search/projects/', AdvancedProjectSearchView.as_view(), name='advanced-search-projects'),
    path('advanced-search/assets/', AdvancedAssetSearchView.as_view(), name='advanced-search-assets'),
    path('advanced-search/templates/', AdvancedTemplateSearchView.as_view(), name='advanced-search-templates'),
    path('advanced-search/teams/', AdvancedTeamSearchView.as_view(), name='advanced-search-teams'),
    path('advanced-search/global/', GlobalSearchView.as_view(), name='global-search'),
    
    # Developer handoff endpoints
    path('projects/<int:project_id>/export-code/', export_to_code, name='export-to-code'),
    path('projects/<int:project_id>/component-specs/', generate_component_specs, name='generate-component-specs'),
    path('projects/<int:project_id>/design-system/', create_design_system, name='create-design-system'),
    path('code-exports/<int:export_id>/download/', download_code_export, name='download-code-export'),
    path('design-systems/<int:system_id>/export/', export_design_system, name='export-design-system'),
    
    # A/B testing endpoints
    path('ab-tests/track/', track_ab_event, name='track-ab-event'),
    
    # Guest access public endpoint
    path('share/<str:token>/', guest_access_view, name='guest-access-view'),
    
    # Version control endpoints
    path('projects/<int:project_id>/versions/', 
         ProjectVersionViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='project-versions'),
    path('projects/<int:project_id>/versions/<int:pk>/', 
         ProjectVersionViewSet.as_view({'get': 'retrieve'}), 
         name='project-version-detail'),
    path('projects/<int:project_id>/versions/<int:pk>/restore/', 
         ProjectVersionViewSet.as_view({'post': 'restore'}), 
         name='project-version-restore'),
    path('projects/<int:project_id>/versions/<int:pk>/comments/', 
         ProjectVersionViewSet.as_view({'get': 'comments', 'post': 'comments'}), 
         name='project-version-comments'),
    path('projects/<int:project_id>/versions/branch/', 
         ProjectVersionViewSet.as_view({'post': 'branch'}), 
         name='project-version-branch'),
    path('projects/<int:project_id>/versions/branches/', 
         ProjectVersionViewSet.as_view({'get': 'branches'}), 
         name='project-version-branches'),
    path('projects/<int:project_id>/versions/diff/', 
         ProjectVersionViewSet.as_view({'post': 'diff'}), 
         name='project-version-diff'),
    path('projects/<int:project_id>/versions/compare/', 
         compare_versions, 
         name='project-version-compare'),
    
    # Design Tokens endpoints
    path('tokens/bind/', bind_library_to_project, name='tokens-bind'),
    path('tokens/sync/', sync_tokens_to_project, name='tokens-sync'),
    path('projects/<int:project_id>/tokens/analyze/', analyze_token_usage, name='tokens-analyze'),
    
    # Magic Resize endpoints
    path('resize/presets/', resize_presets, name='resize-presets'),
    path('resize/preview/', resize_preview, name='resize-preview'),
    path('resize/<int:project_id>/', resize_project, name='resize-project'),
]
