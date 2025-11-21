from django.urls import re_path
from . import consumers
from projects.collaboration_consumer import CollaborativeCanvasConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/activity/$', consumers.ActivityConsumer.as_asgi()),
    re_path(r'ws/canvas/(?P<project_id>\d+)/$', CollaborativeCanvasConsumer.as_asgi()),
]
