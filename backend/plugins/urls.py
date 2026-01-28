from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import (
    PluginCategoryViewSet, PluginViewSet, PluginVersionViewSet,
    PluginInstallationViewSet, PluginReviewViewSet, DeveloperProfileViewSet,
    APIEndpointViewSet, WebhookSubscriptionViewSet, PluginSandboxViewSet,
    PluginLogViewSet, execute_plugin, trigger_plugin_event, get_plugin_capabilities
)

router = DefaultRouter()
router.register(r'categories', PluginCategoryViewSet, basename='category')
router.register(r'plugins', PluginViewSet, basename='plugin')
router.register(r'installations', PluginInstallationViewSet, basename='installation')
router.register(r'developer', DeveloperProfileViewSet, basename='developer')
router.register(r'api-docs', APIEndpointViewSet, basename='api-docs')
router.register(r'webhooks', WebhookSubscriptionViewSet, basename='webhook')
router.register(r'sandboxes', PluginSandboxViewSet, basename='sandbox')

# Nested routes
plugins_router = nested_routers.NestedDefaultRouter(router, r'plugins', lookup='plugin')
plugins_router.register(r'versions', PluginVersionViewSet, basename='plugin-version')
plugins_router.register(r'reviews', PluginReviewViewSet, basename='plugin-review')

installations_router = nested_routers.NestedDefaultRouter(router, r'installations', lookup='installation')
installations_router.register(r'logs', PluginLogViewSet, basename='installation-log')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(plugins_router.urls)),
    path('', include(installations_router.urls)),
    
    # Plugin runtime execution
    path('installations/<int:installation_id>/execute/', execute_plugin, name='plugin-execute'),
    path('installations/<int:installation_id>/trigger-event/', trigger_plugin_event, name='plugin-trigger-event'),
    path('installations/<int:installation_id>/capabilities/', get_plugin_capabilities, name='plugin-capabilities'),
]
