"""
Enhanced Collaboration Serializers
Serializers for video conferencing, guest access, and design reviews
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from typing import List, Dict
from .enhanced_collaboration_models import (
    VideoConferenceRoom,
    VideoConferenceParticipant,
    GuestAccess,
    GuestAccessLog,
    DesignReviewSession,
    ReviewSessionParticipant,
    ReviewAnnotation,
    CollaborationPresence
)


class VideoConferenceParticipantSerializer(serializers.ModelSerializer):
    """Serializer for video conference participants"""
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoConferenceParticipant
        fields = [
            'id', 'room', 'user', 'username', 'display_name', 'role',
            'is_active', 'joined_at', 'left_at', 'can_share_screen',
            'can_annotate', 'can_edit_canvas', 'connection_quality'
        ]
        read_only_fields = ['id', 'is_active', 'joined_at', 'left_at', 'connection_quality']
    
    def get_display_name(self, obj) -> str:
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class VideoConferenceRoomSerializer(serializers.ModelSerializer):
    """Serializer for video conference rooms"""
    host_name = serializers.CharField(source='host.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    team_name = serializers.CharField(source='team.name', read_only=True, allow_null=True)
    participants = VideoConferenceParticipantSerializer(many=True, read_only=True)
    active_participant_count = serializers.SerializerMethodField()
    join_url = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoConferenceRoom
        fields = [
            'id', 'host', 'host_name', 'project', 'project_name', 'team', 'team_name',
            'title', 'description', 'room_code', 'status', 'scheduled_start',
            'scheduled_end', 'actual_start', 'actual_end', 'max_participants',
            'is_recording_enabled', 'is_screen_share_enabled', 'is_canvas_sync_enabled',
            'waiting_room_enabled', 'external_provider', 'external_join_url',
            'recording_url', 'participants', 'active_participant_count', 'join_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'room_code', 'actual_start', 'actual_end', 'recording_url',
            'created_at', 'updated_at'
        ]
    
    def get_active_participant_count(self, obj) -> int:
        return obj.participants.filter(is_active=True).count()
    
    def get_join_url(self, obj) -> str:
        request = self.context.get('request')
        if request:
            return f"{request.scheme}://{request.get_host()}/conference/{obj.room_code}"
        return f"/conference/{obj.room_code}"


class VideoConferenceRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating video conference rooms"""
    invite_users = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = VideoConferenceRoom
        fields = [
            'project', 'team', 'title', 'description', 'scheduled_start',
            'scheduled_end', 'max_participants', 'is_recording_enabled',
            'is_screen_share_enabled', 'is_canvas_sync_enabled',
            'waiting_room_enabled', 'invite_users'
        ]


class GuestAccessSerializer(serializers.ModelSerializer):
    """Serializer for guest access"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True, allow_null=True)
    share_url = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    is_view_limit_reached = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = GuestAccess
        fields = [
            'id', 'project', 'project_name', 'asset', 'asset_name',
            'created_by', 'created_by_name', 'guest_email', 'access_token',
            'access_level', 'password_protected', 'max_views', 'view_count',
            'expires_at', 'allow_download', 'allow_copy', 'watermark_enabled',
            'is_active', 'share_url', 'is_expired', 'is_view_limit_reached',
            'created_at', 'last_accessed_at'
        ]
        read_only_fields = [
            'id', 'access_token', 'view_count', 'created_at', 'last_accessed_at'
        ]
        extra_kwargs = {
            'password_protected': {'write_only': True}
        }
    
    def get_share_url(self, obj) -> str:
        request = self.context.get('request')
        if request:
            return f"{request.scheme}://{request.get_host()}/share/{obj.access_token}"
        return f"/share/{obj.access_token}"


class GuestAccessCreateSerializer(serializers.Serializer):
    """Serializer for creating guest access"""
    project = serializers.IntegerField(required=False, allow_null=True)
    asset = serializers.IntegerField(required=False, allow_null=True)
    guest_email = serializers.EmailField(required=False, allow_blank=True)
    access_level = serializers.ChoiceField(
        choices=['view', 'comment', 'edit', 'full'],
        default='view'
    )
    password = serializers.CharField(required=False, allow_blank=True)
    max_views = serializers.IntegerField(required=False, allow_null=True)
    expires_in_hours = serializers.IntegerField(required=False, allow_null=True)
    allow_download = serializers.BooleanField(default=False)
    allow_copy = serializers.BooleanField(default=False)
    watermark_enabled = serializers.BooleanField(default=False)
    
    def validate(self, data):
        if not data.get('project') and not data.get('asset'):
            raise serializers.ValidationError(
                "Either project or asset must be specified"
            )
        return data


class GuestAccessLogSerializer(serializers.ModelSerializer):
    """Serializer for guest access logs"""
    
    class Meta:
        model = GuestAccessLog
        fields = [
            'id', 'guest_access', 'event_type', 'ip_address', 
            'user_agent', 'referrer', 'event_data', 'created_at'
        ]
        read_only_fields = fields


class ReviewAnnotationSerializer(serializers.ModelSerializer):
    """Serializer for review annotations"""
    participant_name = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewAnnotation
        fields = [
            'id', 'session', 'participant', 'participant_name', 'annotation_type',
            'position_data', 'comment', 'parent', 'is_resolved', 'resolved_by',
            'resolved_at', 'replies', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'resolved_by', 'resolved_at', 'created_at', 'updated_at']
    
    def get_participant_name(self, obj) -> str:
        if obj.participant.user:
            return obj.participant.user.username
        return obj.participant.guest_name or obj.participant.guest_email
    
    def get_replies(self, obj) -> List[Dict]:
        if obj.replies.exists():
            return ReviewAnnotationSerializer(obj.replies.all(), many=True).data
        return []


class ReviewSessionParticipantSerializer(serializers.ModelSerializer):
    """Serializer for review session participants"""
    username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    display_name = serializers.SerializerMethodField()
    annotations = ReviewAnnotationSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReviewSessionParticipant
        fields = [
            'id', 'session', 'user', 'username', 'guest_email', 'guest_name',
            'display_name', 'role', 'decision', 'feedback', 'is_notified',
            'reviewed_at', 'annotations'
        ]
        read_only_fields = ['id', 'invite_token', 'is_notified', 'reviewed_at']
    
    def get_display_name(self, obj) -> str:
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return obj.guest_name or obj.guest_email


class DesignReviewSessionSerializer(serializers.ModelSerializer):
    """Serializer for design review sessions"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    participants = ReviewSessionParticipantSerializer(many=True, read_only=True)
    approval_status = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignReviewSession
        fields = [
            'id', 'project', 'project_name', 'created_by', 'created_by_name',
            'title', 'description', 'version_number', 'status', 'deadline',
            'require_all_approvals', 'allow_anonymous_feedback', 'participants',
            'approval_status', 'created_at', 'updated_at', 'closed_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'closed_at']
    
    def get_approval_status(self, obj) -> Dict:
        participants = obj.participants.all()
        total = participants.count()
        approved = participants.filter(decision__in=['approved', 'approved_with_comments']).count()
        rejected = participants.filter(decision='rejected').count()
        pending = participants.filter(decision='pending').count()
        
        return {
            'total': total,
            'approved': approved,
            'rejected': rejected,
            'pending': pending,
            'changes_requested': total - approved - rejected - pending
        }


class DesignReviewSessionCreateSerializer(serializers.Serializer):
    """Serializer for creating design review sessions"""
    project = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    version_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    deadline = serializers.DateTimeField(required=False, allow_null=True)
    require_all_approvals = serializers.BooleanField(default=False)
    allow_anonymous_feedback = serializers.BooleanField(default=False)
    
    # Participants to invite
    reviewers = serializers.ListField(
        child=serializers.JSONField(),
        required=False
    )
    # [{"user_id": 1, "role": "approver"}, {"email": "guest@example.com", "name": "Guest", "role": "reviewer"}]


class CollaborationPresenceSerializer(serializers.ModelSerializer):
    """Serializer for collaboration presence"""
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.SerializerMethodField()
    is_online = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CollaborationPresence
        fields = [
            'id', 'user', 'username', 'display_name', 'project', 'session_id',
            'cursor_x', 'cursor_y', 'selected_elements', 'activity_status',
            'color', 'is_online', 'last_heartbeat', 'connected_at'
        ]
        read_only_fields = ['id', 'connected_at']
    
    def get_display_name(self, obj) -> str:
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class InviteReviewerSerializer(serializers.Serializer):
    """Serializer for inviting reviewers"""
    user_id = serializers.IntegerField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    role = serializers.ChoiceField(
        choices=['approver', 'reviewer', 'viewer'],
        default='reviewer'
    )
    
    def validate(self, data):
        if not data.get('user_id') and not data.get('email'):
            raise serializers.ValidationError(
                "Either user_id or email must be provided"
            )
        return data
