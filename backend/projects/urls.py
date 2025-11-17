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

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'components', DesignComponentViewSet, basename='component')
router.register(r'export-templates', ExportTemplateViewSet, basename='export-template')
router.register(r'export-jobs', ExportJobViewSet, basename='export-job')

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
    path('projects/<int:project_id>/export/svg/optimized/', export_project_svg_optimized, name='export-svg-optimized'),
    path('projects/<int:project_id>/export/social-pack/', export_social_media_pack, name='export-social-pack'),
    path('projects/<int:project_id>/export/print-ready/', export_print_ready, name='export-print-ready'),
    path('projects/<int:project_id>/export/template/<int:template_id>/', export_with_template, name='export-with-template'),
    path('projects/export/batch/', batch_export_projects, name='batch-export'),
    path('projects/export/templates/', list_export_templates, name='list-export-templates'),
    path('projects/export/templates/create/', create_export_template, name='create-export-template'),
    path('projects/export/templates/<int:template_id>/', delete_export_template, name='delete-export-template'),
    path('projects/export/formats/', export_formats_info, name='export-formats-info'),
]
