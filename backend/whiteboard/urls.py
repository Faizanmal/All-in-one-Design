"""
URL configuration for Whiteboard app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WhiteboardViewSet, PublicWhiteboardViewSet,
    WhiteboardCollaboratorViewSet, StickyNoteViewSet,
    WhiteboardShapeViewSet, ConnectorViewSet,
    WhiteboardTextViewSet, WhiteboardImageViewSet,
    WhiteboardGroupViewSet, WhiteboardSectionViewSet,
    TimerViewSet, WhiteboardCommentViewSet,
    WhiteboardEmojiViewSet, WhiteboardTemplateViewSet
)

app_name = 'whiteboard'

router = DefaultRouter()
router.register(r'whiteboards', WhiteboardViewSet, basename='whiteboard')
router.register(r'public', PublicWhiteboardViewSet, basename='public-whiteboard')
router.register(r'collaborators', WhiteboardCollaboratorViewSet, basename='collaborator')
router.register(r'sticky-notes', StickyNoteViewSet, basename='sticky-note')
router.register(r'shapes', WhiteboardShapeViewSet, basename='shape')
router.register(r'connectors', ConnectorViewSet, basename='connector')
router.register(r'texts', WhiteboardTextViewSet, basename='text')
router.register(r'images', WhiteboardImageViewSet, basename='image')
router.register(r'groups', WhiteboardGroupViewSet, basename='group')
router.register(r'sections', WhiteboardSectionViewSet, basename='section')
router.register(r'timers', TimerViewSet, basename='timer')
router.register(r'comments', WhiteboardCommentViewSet, basename='comment')
router.register(r'emojis', WhiteboardEmojiViewSet, basename='emoji')
router.register(r'templates', WhiteboardTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
]
