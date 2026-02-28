"""
WebSocket URL routing for real-time collaboration.
"""
from django.urls import re_path
from . import realtime_consumers
from .crdt_consumer import CRDTCollaborationConsumer

websocket_urlpatterns = [
    re_path(
        r'ws/project/(?P<project_id>\d+)/collaborate/$',
        realtime_consumers.CollaborationConsumer.as_asgi()
    ),
    re_path(
        r'ws/project/(?P<project_id>\d+)/crdt/$',
        CRDTCollaborationConsumer.as_asgi()
    ),
]
