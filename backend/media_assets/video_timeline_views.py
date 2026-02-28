"""
Video Editing Timeline API Views

Provides REST API for video timeline editing operations.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .video_timeline_service import VideoTimelineService

service = VideoTimelineService()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_timeline(request):
    """
    Create a new video editing timeline.

    POST /api/v1/media/timeline/create/
    Body: { "project_id": 1, "settings": { "width": 1920, "height": 1080, "fps": 30 } }
    """
    project_id = request.data.get('project_id')
    if not project_id:
        return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    timeline_settings = request.data.get('settings', {})
    timeline = service.create_timeline(
        project_id=project_id,
        user_id=request.user.id,
        settings=timeline_settings,
    )
    return Response(timeline, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_track(request):
    """
    Add a track to a timeline.

    POST /api/v1/media/timeline/track/
    Body: { "timeline": {...}, "track_type": "video", "name": "Main Video" }
    """
    timeline = request.data.get('timeline')
    if not timeline:
        return Response({'error': 'timeline data is required'}, status=status.HTTP_400_BAD_REQUEST)

    track_type = request.data.get('track_type', 'video')
    name = request.data.get('name', '')

    try:
        track = service.add_track(timeline, track_type, name)
        return Response({'track': track, 'timeline': timeline})
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_clip(request):
    """
    Add a clip to a track.

    POST /api/v1/media/timeline/clip/
    Body: { "track": {...}, "clip_data": { "source_url": "...", "start_time": 0, "duration": 5 } }
    """
    track = request.data.get('track')
    clip_data = request.data.get('clip_data')
    if not track or not clip_data:
        return Response({'error': 'track and clip_data are required'}, status=status.HTTP_400_BAD_REQUEST)

    clip = service.add_clip(track, clip_data)
    return Response({'clip': clip, 'track': track})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def split_clip(request):
    """
    Split a clip into two parts.

    POST /api/v1/media/timeline/clip/split/
    Body: { "track": {...}, "clip_id": "uuid", "split_point": 2.5 }
    """
    track = request.data.get('track')
    clip_id = request.data.get('clip_id')
    split_point = request.data.get('split_point')

    if not all([track, clip_id, split_point]):
        return Response({'error': 'track, clip_id, and split_point are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        clip_a, clip_b = service.split_clip(track, clip_id, float(split_point))
        return Response({'clip_a': clip_a, 'clip_b': clip_b, 'track': track})
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trim_clip(request):
    """
    Trim a clip's in/out points.

    POST /api/v1/media/timeline/clip/trim/
    Body: { "clip": {...}, "new_start": 1.0, "new_end": 4.0 }
    """
    clip = request.data.get('clip')
    if not clip:
        return Response({'error': 'clip data is required'}, status=status.HTTP_400_BAD_REQUEST)

    new_start = request.data.get('new_start')
    new_end = request.data.get('new_end')

    result = service.trim_clip(clip, new_start=new_start, new_end=new_end)
    return Response({'clip': result})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_transition(request):
    """
    Set a transition on a clip.

    POST /api/v1/media/timeline/clip/transition/
    Body: { "clip": {...}, "position": "in", "transition_type": "crossfade", "duration": 1.0 }
    """
    clip = request.data.get('clip')
    position = request.data.get('position', 'in')
    transition_type = request.data.get('transition_type')
    duration = request.data.get('duration')

    if not clip or not transition_type:
        return Response({'error': 'clip and transition_type are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        result = service.set_transition(clip, position, transition_type, duration)
        return Response({'clip': result})
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_text_overlay(request):
    """
    Add a text overlay to the timeline.

    POST /api/v1/media/timeline/text/
    Body: { "timeline": {...}, "text_data": { "text": "Hello", "font_size": 48 } }
    """
    timeline = request.data.get('timeline')
    text_data = request.data.get('text_data')

    if not timeline or not text_data:
        return Response({'error': 'timeline and text_data are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    text_clip = service.add_text_overlay(timeline, text_data)
    return Response({'text_clip': text_clip, 'timeline': timeline})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_keyframe(request):
    """
    Add a keyframe to a clip.

    POST /api/v1/media/timeline/keyframe/
    Body: { "clip": {...}, "time": 1.5, "property": "opacity", "value": 0.5 }
    """
    clip = request.data.get('clip')
    time = request.data.get('time')
    prop = request.data.get('property')
    value = request.data.get('value')

    if not clip or time is None or not prop:
        return Response({'error': 'clip, time, and property are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    keyframe = service.add_keyframe(clip, float(time), prop, value)
    return Response({'keyframe': keyframe, 'clip': clip})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_timeline(request):
    """
    Validate a timeline structure.

    POST /api/v1/media/timeline/validate/
    Body: { "timeline": {...} }
    """
    timeline = request.data.get('timeline')
    if not timeline:
        return Response({'error': 'timeline data is required'}, status=status.HTTP_400_BAD_REQUEST)

    result = service.validate_timeline(timeline)
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transitions(request):
    """Get all available transitions."""
    return Response({
        'transitions': service.get_available_transitions(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_export_presets(request):
    """Get all available export presets."""
    return Response({
        'presets': service.get_export_presets(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_text_effects(request):
    """Get all available text effects."""
    return Response({
        'effects': service.get_text_effects(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preview_frames(request):
    """
    Generate preview frame list for a timeline.

    POST /api/v1/media/timeline/preview/
    Body: { "timeline": {...}, "count": 10 }
    """
    timeline = request.data.get('timeline')
    count = request.data.get('count', 10)

    if not timeline:
        return Response({'error': 'timeline data is required'}, status=status.HTTP_400_BAD_REQUEST)

    frames = service.generate_preview_frames(timeline, int(count))
    return Response({'frames': frames, 'total_duration': service.get_timeline_duration(timeline)})
