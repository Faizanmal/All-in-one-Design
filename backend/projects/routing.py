"""
WebSocket URL routing for real-time collaboration.
"""
from django.urls import re_path
from . import realtime_consumers

websocket_urlpatterns = [
    re_path(
        r'ws/project/(?P<project_id>\d+)/collaborate/$',
        realtime_consumers.CollaborationConsumer.as_asgi()
    ),
]
