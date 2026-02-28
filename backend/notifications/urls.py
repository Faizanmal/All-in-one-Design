from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, WebhookViewSet, UserPreferenceViewSet
from .workflow_views import (
    WorkflowViewSet,
    WorkflowTriggerViewSet,
    WorkflowActionViewSet,
    trigger_types,
    action_types,
    workflow_templates,
    create_from_template,
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'preferences', UserPreferenceViewSet, basename='preference')
router.register(r'workflows', WorkflowViewSet, basename='workflow')

urlpatterns = [
    path('', include(router.urls)),

    # Workflow nested routes
    path('workflows/<uuid:workflow_pk>/triggers/',
         WorkflowTriggerViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='workflow-triggers'),
    path('workflows/<uuid:workflow_pk>/triggers/<uuid:pk>/',
         WorkflowTriggerViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='workflow-trigger-detail'),
    path('workflows/<uuid:workflow_pk>/actions/',
         WorkflowActionViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='workflow-actions'),
    path('workflows/<uuid:workflow_pk>/actions/<uuid:pk>/',
         WorkflowActionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='workflow-action-detail'),

    # Metadata endpoints
    path('workflow-meta/trigger-types/', trigger_types, name='workflow-trigger-types'),
    path('workflow-meta/action-types/', action_types, name='workflow-action-types'),
    path('workflow-meta/templates/', workflow_templates, name='workflow-templates'),
    path('workflow-meta/create-from-template/', create_from_template, name='workflow-create-from-template'),
]
