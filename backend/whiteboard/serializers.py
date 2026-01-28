"""
Serializers for Whiteboard app.
"""
from rest_framework import serializers
from .models import (
    Whiteboard, WhiteboardCollaborator, StickyNote, StickyNoteVote,
    WhiteboardShape, Connector, WhiteboardText, WhiteboardImage,
    WhiteboardGroup, WhiteboardSection, Timer, WhiteboardComment,
    WhiteboardEmoji, WhiteboardTemplate
)


class StickyNoteVoteSerializer(serializers.ModelSerializer):
    """Serializer for sticky note votes."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = StickyNoteVote
        fields = ['id', 'sticky_note', 'user', 'user_name', 'vote_type', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class StickyNoteSerializer(serializers.ModelSerializer):
    """Serializer for sticky notes."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    vote_count = serializers.SerializerMethodField()
    votes = StickyNoteVoteSerializer(many=True, read_only=True)
    
    class Meta:
        model = StickyNote
        fields = [
            'id', 'whiteboard', 'content', 'color', 'position_x', 'position_y',
            'width', 'height', 'rotation', 'font_size', 'text_align',
            'author_visible', 'is_locked', 'group', 'section', 'created_by',
            'created_by_name', 'created_at', 'updated_at', 'vote_count', 'votes'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_vote_count(self, obj):
        return obj.votes.filter(vote_type='upvote').count() - obj.votes.filter(vote_type='downvote').count()


class WhiteboardShapeSerializer(serializers.ModelSerializer):
    """Serializer for whiteboard shapes."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = WhiteboardShape
        fields = [
            'id', 'whiteboard', 'shape_type', 'position_x', 'position_y',
            'width', 'height', 'rotation', 'fill_color', 'stroke_color',
            'stroke_width', 'opacity', 'corner_radius', 'points',
            'is_locked', 'group', 'section', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ConnectorSerializer(serializers.ModelSerializer):
    """Serializer for connectors."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Connector
        fields = [
            'id', 'whiteboard', 'start_node_id', 'start_node_type',
            'start_anchor', 'end_node_id', 'end_node_type', 'end_anchor',
            'connector_type', 'stroke_color', 'stroke_width', 'stroke_style',
            'start_arrow', 'end_arrow', 'label', 'label_position',
            'control_points', 'is_locked', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class WhiteboardTextSerializer(serializers.ModelSerializer):
    """Serializer for whiteboard text."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = WhiteboardText
        fields = [
            'id', 'whiteboard', 'content', 'position_x', 'position_y',
            'width', 'rotation', 'font_family', 'font_size', 'font_weight',
            'font_style', 'text_color', 'text_align', 'line_height',
            'is_locked', 'group', 'section', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class WhiteboardImageSerializer(serializers.ModelSerializer):
    """Serializer for whiteboard images."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = WhiteboardImage
        fields = [
            'id', 'whiteboard', 'image_url', 'thumbnail_url', 'position_x',
            'position_y', 'width', 'height', 'rotation', 'opacity',
            'crop_data', 'is_locked', 'group', 'section', 'created_by',
            'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class WhiteboardGroupSerializer(serializers.ModelSerializer):
    """Serializer for whiteboard groups."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WhiteboardGroup
        fields = [
            'id', 'whiteboard', 'name', 'color', 'is_locked', 'created_by',
            'created_by_name', 'created_at', 'member_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def get_member_count(self, obj):
        return (
            obj.sticky_notes.count() +
            obj.shapes.count() +
            obj.texts.count() +
            obj.images.count()
        )


class WhiteboardSectionSerializer(serializers.ModelSerializer):
    """Serializer for whiteboard sections."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = WhiteboardSection
        fields = [
            'id', 'whiteboard', 'title', 'description', 'position_x',
            'position_y', 'width', 'height', 'background_color', 'is_collapsed',
            'is_locked', 'order', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class TimerSerializer(serializers.ModelSerializer):
    """Serializer for timers."""
    started_by_name = serializers.CharField(source='started_by.username', read_only=True, allow_null=True)
    remaining_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = Timer
        fields = [
            'id', 'whiteboard', 'duration_seconds', 'remaining_seconds',
            'is_running', 'started_at', 'paused_at', 'started_by',
            'started_by_name', 'sound_enabled', 'visible_to_all', 'created_at'
        ]
        read_only_fields = ['id', 'started_by', 'created_at']
    
    def get_remaining_seconds(self, obj):
        if not obj.is_running or not obj.started_at:
            return obj.duration_seconds
        
        from django.utils import timezone
        elapsed = (timezone.now() - obj.started_at).total_seconds()
        return max(0, obj.duration_seconds - int(elapsed))


class WhiteboardCommentSerializer(serializers.ModelSerializer):
    """Serializer for whiteboard comments."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = WhiteboardComment
        fields = [
            'id', 'whiteboard', 'parent_comment', 'author', 'author_name',
            'content', 'position_x', 'position_y', 'attached_to_id',
            'attached_to_type', 'is_resolved', 'resolved_by', 'resolved_at',
            'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return WhiteboardCommentSerializer(obj.replies.all(), many=True).data
        return []


class WhiteboardEmojiSerializer(serializers.ModelSerializer):
    """Serializer for whiteboard emojis."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = WhiteboardEmoji
        fields = [
            'id', 'whiteboard', 'emoji', 'position_x', 'position_y',
            'user', 'user_name', 'is_reaction', 'attached_to_id',
            'attached_to_type', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class WhiteboardCollaboratorSerializer(serializers.ModelSerializer):
    """Serializer for whiteboard collaborators."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = WhiteboardCollaborator
        fields = [
            'id', 'whiteboard', 'user', 'user_name', 'user_email',
            'role', 'cursor_x', 'cursor_y', 'cursor_color', 'is_online',
            'joined_at', 'last_active'
        ]
        read_only_fields = ['id', 'joined_at', 'last_active']


class WhiteboardSerializer(serializers.ModelSerializer):
    """Serializer for whiteboards."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    collaborator_count = serializers.SerializerMethodField()
    element_count = serializers.SerializerMethodField()
    online_collaborators = serializers.SerializerMethodField()
    
    class Meta:
        model = Whiteboard
        fields = [
            'id', 'project', 'name', 'description', 'whiteboard_type',
            'background_color', 'background_pattern', 'grid_size', 'snap_to_grid',
            'show_grid', 'canvas_width', 'canvas_height', 'zoom_level',
            'pan_x', 'pan_y', 'is_template', 'is_public', 'share_link',
            'allow_anonymous_edit', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'collaborator_count', 'element_count',
            'online_collaborators'
        ]
        read_only_fields = ['id', 'share_link', 'created_by', 'created_at', 'updated_at']
    
    def get_collaborator_count(self, obj):
        return obj.collaborators.count()
    
    def get_element_count(self, obj):
        return (
            obj.sticky_notes.count() +
            obj.shapes.count() +
            obj.connectors.count() +
            obj.texts.count() +
            obj.images.count()
        )
    
    def get_online_collaborators(self, obj):
        online = obj.collaborators.filter(is_online=True)
        return WhiteboardCollaboratorSerializer(online, many=True).data


class WhiteboardListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for whiteboard lists."""
    element_count = serializers.SerializerMethodField()
    online_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Whiteboard
        fields = [
            'id', 'name', 'whiteboard_type', 'is_public', 'updated_at',
            'element_count', 'online_count'
        ]
    
    def get_element_count(self, obj):
        return obj.sticky_notes.count() + obj.shapes.count()
    
    def get_online_count(self, obj):
        return obj.collaborators.filter(is_online=True).count()


class WhiteboardTemplateSerializer(serializers.ModelSerializer):
    """Serializer for whiteboard templates."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = WhiteboardTemplate
        fields = [
            'id', 'name', 'description', 'category', 'thumbnail',
            'template_data', 'is_system', 'usage_count', 'created_by',
            'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_by', 'created_at']


class CreateFromTemplateSerializer(serializers.Serializer):
    """Serializer for creating whiteboard from template."""
    name = serializers.CharField(max_length=200)
    template_id = serializers.UUIDField()


class InviteCollaboratorSerializer(serializers.Serializer):
    """Serializer for inviting collaborators."""
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=['viewer', 'editor', 'admin'],
        default='editor'
    )


class UpdateCursorSerializer(serializers.Serializer):
    """Serializer for updating cursor position."""
    x = serializers.FloatField()
    y = serializers.FloatField()
