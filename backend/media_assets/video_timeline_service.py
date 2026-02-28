"""
Video Editing Timeline Service

Provides video editing capabilities including:
- Timeline-based editing with multiple tracks
- Clip trimming, splitting, reordering
- Transitions between clips
- Text overlays and effects
- Export to multiple video formats
"""

import os
import io
import uuid
import logging
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class VideoTimelineService:
    """Core video timeline editing service."""

    # Supported video formats
    SUPPORTED_INPUT_FORMATS = {'mp4', 'webm', 'mov', 'avi', 'mkv', 'gif'}
    SUPPORTED_OUTPUT_FORMATS = {'mp4', 'webm', 'gif'}

    # Preset transitions
    TRANSITIONS = {
        'cut': {'name': 'Cut', 'duration': 0, 'description': 'Instant cut'},
        'crossfade': {'name': 'Crossfade', 'duration': 1.0, 'description': 'Smooth blend'},
        'fade_black': {'name': 'Fade to Black', 'duration': 0.5, 'description': 'Fade out then in through black'},
        'fade_white': {'name': 'Fade to White', 'duration': 0.5, 'description': 'Fade out then in through white'},
        'slide_left': {'name': 'Slide Left', 'duration': 0.5, 'description': 'Slide transition'},
        'slide_right': {'name': 'Slide Right', 'duration': 0.5, 'description': 'Slide transition'},
        'zoom_in': {'name': 'Zoom In', 'duration': 0.5, 'description': 'Zoom transition'},
        'wipe': {'name': 'Wipe', 'duration': 0.5, 'description': 'Wipe transition'},
        'dissolve': {'name': 'Dissolve', 'duration': 1.0, 'description': 'Pixel dissolve'},
    }

    # Text effect presets
    TEXT_EFFECTS = {
        'none': {'name': 'None', 'animation': None},
        'fade_in': {'name': 'Fade In', 'animation': 'opacity', 'duration': 0.5},
        'slide_up': {'name': 'Slide Up', 'animation': 'translateY', 'duration': 0.5},
        'typewriter': {'name': 'Typewriter', 'animation': 'characters', 'duration': 2.0},
        'bounce': {'name': 'Bounce', 'animation': 'scale', 'duration': 0.5},
        'glow': {'name': 'Glow', 'animation': 'shadow', 'duration': 1.0},
    }

    # Export presets
    EXPORT_PRESETS = {
        'web_hd': {
            'name': 'Web HD',
            'width': 1920, 'height': 1080,
            'fps': 30, 'bitrate': '5M',
            'format': 'mp4', 'codec': 'h264',
        },
        'web_4k': {
            'name': 'Web 4K',
            'width': 3840, 'height': 2160,
            'fps': 30, 'bitrate': '15M',
            'format': 'mp4', 'codec': 'h264',
        },
        'social_square': {
            'name': 'Social (Square)',
            'width': 1080, 'height': 1080,
            'fps': 30, 'bitrate': '4M',
            'format': 'mp4', 'codec': 'h264',
        },
        'social_story': {
            'name': 'Social (Story)',
            'width': 1080, 'height': 1920,
            'fps': 30, 'bitrate': '4M',
            'format': 'mp4', 'codec': 'h264',
        },
        'social_landscape': {
            'name': 'Social (Landscape)',
            'width': 1280, 'height': 720,
            'fps': 30, 'bitrate': '3M',
            'format': 'mp4', 'codec': 'h264',
        },
        'gif_small': {
            'name': 'GIF (Small)',
            'width': 480, 'height': 270,
            'fps': 15, 'bitrate': None,
            'format': 'gif', 'codec': None,
        },
        'gif_medium': {
            'name': 'GIF (Medium)',
            'width': 640, 'height': 360,
            'fps': 15, 'bitrate': None,
            'format': 'gif', 'codec': None,
        },
    }

    def create_timeline(self, project_id: int, user_id: int, settings: dict = None) -> dict:
        """Create a new video timeline for a project."""
        timeline_id = str(uuid.uuid4())
        default_settings = {
            'width': 1920,
            'height': 1080,
            'fps': 30,
            'duration': 0,
            'background_color': '#000000',
        }
        if settings:
            default_settings.update(settings)

        return {
            'id': timeline_id,
            'project_id': project_id,
            'user_id': user_id,
            'settings': default_settings,
            'tracks': [],
            'markers': [],
            'audio_tracks': [],
            'playhead_position': 0,
        }

    def add_track(self, timeline: dict, track_type: str = 'video', name: str = '') -> dict:
        """Add a track to the timeline."""
        valid_types = ['video', 'audio', 'text', 'effect', 'image']
        if track_type not in valid_types:
            raise ValueError(f"Invalid track type. Must be one of: {valid_types}")

        track_id = str(uuid.uuid4())
        track = {
            'id': track_id,
            'type': track_type,
            'name': name or f'{track_type.title()} Track {len(timeline.get("tracks", [])) + 1}',
            'clips': [],
            'muted': False,
            'locked': False,
            'visible': True,
            'volume': 1.0,
            'opacity': 1.0,
            'order': len(timeline.get('tracks', [])),
        }
        timeline.setdefault('tracks', []).append(track)
        return track

    def add_clip(self, track: dict, clip_data: dict) -> dict:
        """Add a clip to a track."""
        clip_id = str(uuid.uuid4())
        clip = {
            'id': clip_id,
            'type': track['type'],
            'source_url': clip_data.get('source_url', ''),
            'start_time': clip_data.get('start_time', 0),
            'end_time': clip_data.get('end_time', 5),
            'in_point': clip_data.get('in_point', 0),
            'out_point': clip_data.get('out_point', None),
            'duration': clip_data.get('duration', 5),
            'name': clip_data.get('name', 'Untitled Clip'),
            'volume': clip_data.get('volume', 1.0),
            'opacity': clip_data.get('opacity', 1.0),
            'speed': clip_data.get('speed', 1.0),
            'filters': clip_data.get('filters', []),
            'transform': {
                'x': 0, 'y': 0,
                'scale_x': 1.0, 'scale_y': 1.0,
                'rotation': 0,
                'anchor_x': 0.5, 'anchor_y': 0.5,
            },
            'transition_in': None,
            'transition_out': None,
            'keyframes': [],
        }
        if clip_data.get('transform'):
            clip['transform'].update(clip_data['transform'])

        track.setdefault('clips', []).append(clip)
        return clip

    def trim_clip(self, clip: dict, new_start: float = None, new_end: float = None) -> dict:
        """Trim clip in/out points."""
        if new_start is not None:
            clip['in_point'] = max(0, new_start)
        if new_end is not None:
            clip['out_point'] = new_end
        clip['duration'] = (clip.get('out_point') or clip['end_time']) - clip['in_point']
        return clip

    def split_clip(self, track: dict, clip_id: str, split_point: float) -> tuple:
        """Split a clip into two at the specified time point."""
        clip = next((c for c in track['clips'] if c['id'] == clip_id), None)
        if not clip:
            raise ValueError(f"Clip {clip_id} not found")

        if split_point <= clip['start_time'] or split_point >= clip['end_time']:
            raise ValueError("Split point must be within clip range")

        # Create second half
        clip_b = {
            **clip,
            'id': str(uuid.uuid4()),
            'name': f"{clip['name']} (split)",
            'start_time': split_point,
            'in_point': split_point - clip['start_time'] + clip['in_point'],
        }

        # Adjust first half
        clip['end_time'] = split_point
        clip['out_point'] = split_point - clip['start_time'] + clip['in_point']
        clip['duration'] = clip['end_time'] - clip['start_time']
        clip_b['duration'] = clip_b['end_time'] - clip_b['start_time']

        # Insert after original
        idx = track['clips'].index(clip)
        track['clips'].insert(idx + 1, clip_b)

        return clip, clip_b

    def set_transition(self, clip: dict, position: str, transition_type: str,
                       duration: float = None) -> dict:
        """Set a transition on a clip."""
        if transition_type not in self.TRANSITIONS:
            raise ValueError(f"Unknown transition: {transition_type}")

        transition_info = self.TRANSITIONS[transition_type].copy()
        if duration is not None:
            transition_info['duration'] = duration

        if position == 'in':
            clip['transition_in'] = transition_info
        elif position == 'out':
            clip['transition_out'] = transition_info
        else:
            raise ValueError("Position must be 'in' or 'out'")

        return clip

    def add_text_overlay(self, timeline: dict, text_data: dict) -> dict:
        """Add a text overlay to the timeline."""
        text_track = None
        for track in timeline.get('tracks', []):
            if track['type'] == 'text':
                text_track = track
                break

        if not text_track:
            text_track = self.add_track(timeline, 'text', 'Text Overlays')

        text_clip = {
            'id': str(uuid.uuid4()),
            'type': 'text',
            'text': text_data.get('text', ''),
            'font_family': text_data.get('font_family', 'Inter'),
            'font_size': text_data.get('font_size', 48),
            'font_weight': text_data.get('font_weight', 'bold'),
            'color': text_data.get('color', '#FFFFFF'),
            'background_color': text_data.get('background_color', ''),
            'padding': text_data.get('padding', 10),
            'alignment': text_data.get('alignment', 'center'),
            'position': text_data.get('position', {'x': 0.5, 'y': 0.5}),
            'start_time': text_data.get('start_time', 0),
            'end_time': text_data.get('end_time', 5),
            'duration': text_data.get('duration', 5),
            'effect': text_data.get('effect', 'none'),
            'opacity': text_data.get('opacity', 1.0),
            'shadow': text_data.get('shadow', None),
            'outline': text_data.get('outline', None),
        }
        text_track['clips'].append(text_clip)
        return text_clip

    def add_keyframe(self, clip: dict, time: float, property_name: str, value) -> dict:
        """Add a keyframe to a clip for property animation."""
        keyframe = {
            'id': str(uuid.uuid4()),
            'time': time,
            'property': property_name,
            'value': value,
            'easing': 'ease-in-out',
        }
        clip.setdefault('keyframes', []).append(keyframe)
        clip['keyframes'].sort(key=lambda k: k['time'])
        return keyframe

    def get_timeline_duration(self, timeline: dict) -> float:
        """Calculate the total duration of the timeline."""
        max_end = 0
        for track in timeline.get('tracks', []):
            for clip in track.get('clips', []):
                max_end = max(max_end, clip.get('end_time', 0))
        return max_end

    def get_available_transitions(self):
        """Get all available transitions."""
        return self.TRANSITIONS

    def get_export_presets(self):
        """Get all available export presets."""
        return self.EXPORT_PRESETS

    def get_text_effects(self):
        """Get all available text effects."""
        return self.TEXT_EFFECTS

    def validate_timeline(self, timeline: dict) -> dict:
        """Validate timeline structure and return issues."""
        issues = []

        if not timeline.get('tracks'):
            issues.append({'type': 'warning', 'message': 'Timeline has no tracks'})

        for track in timeline.get('tracks', []):
            if not track.get('clips'):
                issues.append({
                    'type': 'info',
                    'message': f'Track "{track.get("name", "Untitled")}" is empty'
                })

            # Check for overlapping clips
            clips = sorted(track.get('clips', []), key=lambda c: c.get('start_time', 0))
            for i in range(len(clips) - 1):
                if clips[i].get('end_time', 0) > clips[i + 1].get('start_time', 0):
                    issues.append({
                        'type': 'error',
                        'message': f'Overlapping clips in track "{track.get("name", "")}"',
                        'clips': [clips[i]['id'], clips[i + 1]['id']],
                    })

        return {
            'valid': not any(i['type'] == 'error' for i in issues),
            'issues': issues,
            'duration': self.get_timeline_duration(timeline),
        }

    def generate_preview_frames(self, timeline: dict, count: int = 10) -> list:
        """Generate thumbnail frames from the timeline."""
        duration = self.get_timeline_duration(timeline)
        if duration == 0:
            return []

        interval = duration / count
        frames = []
        for i in range(count):
            time = i * interval
            active_clips = []
            for track in timeline.get('tracks', []):
                if track.get('muted') or not track.get('visible', True):
                    continue
                for clip in track.get('clips', []):
                    if clip.get('start_time', 0) <= time < clip.get('end_time', 0):
                        active_clips.append({
                            'clip_id': clip['id'],
                            'track_type': track['type'],
                            'clip_name': clip.get('name', ''),
                        })
            frames.append({
                'time': round(time, 2),
                'frame_number': i,
                'active_clips': active_clips,
            })
        return frames
