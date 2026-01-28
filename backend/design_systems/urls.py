from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import (
    DesignSystemViewSet, DesignTokenViewSet, ComponentDefinitionViewSet,
    StyleGuideViewSet, DocumentationPageViewSet,
    public_design_system, get_token_categories
)

router = DefaultRouter()
router.register(r'systems', DesignSystemViewSet, basename='design-system')

# Nested routes for design system resources
design_system_router = nested_routers.NestedDefaultRouter(router, r'systems', lookup='design_system')
design_system_router.register(r'tokens', DesignTokenViewSet, basename='design-token')
design_system_router.register(r'components', ComponentDefinitionViewSet, basename='component-definition')
design_system_router.register(r'style-guide', StyleGuideViewSet, basename='style-guide')
design_system_router.register(r'docs', DocumentationPageViewSet, basename='documentation-page')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(design_system_router.urls)),
    path('public/<uuid:pk>/', public_design_system, name='public-design-system'),
    path('token-categories/', get_token_categories, name='token-categories'),
]
