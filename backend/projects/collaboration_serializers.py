"""
Serializers for collaboration, comments, and reviews
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project
from .collaboration_models import (
    CollaborationSession,
    CanvasEdit,
    Comment,
    Review,
    DesignFeedback
)


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user info for collaboration features"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class CollaborationSessionSerializer(serializers.ModelSerializer):
    """Serializer for collaboration sessions"""
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = CollaborationSession
        fields = [
            'id', 'user', 'session_id', 'is_active',
            'cursor_position', 'selected_elements', 'viewport',
            'joined_at', 'last_activity'
        ]
        read_only_fields = ['session_id', 'joined_at', 'last_activity']


class CanvasEditSerializer(serializers.ModelSerializer):
    """Serializer for canvas edits"""
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = CanvasEdit
        fields = [
            'id', 'user', 'edit_type', 'element_id',
            'previous_data', 'new_data', 'vector_clock',
            'parent_edit_id', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    user = UserMinimalSerializer(read_only=True)
    resolved_by = UserMinimalSerializer(read_only=True)
    mentioned_users = UserMinimalSerializer(many=True, read_only=True)
    mentioned_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    replies_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'project', 'user', 'content',
            'anchor_position', 'anchor_element_id',
            'parent_comment', 'is_resolved', 'resolved_by', 'resolved_at',
            'mentioned_users', 'mentioned_user_ids',
            'replies_count', 'replies',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'resolved_by', 'resolved_at', 'created_at', 'updated_at']
    
    def get_replies_count(self, obj):
        return obj.replies.count()
    
    def get_replies(self, obj):
        # Only include direct replies, not nested
        if obj.parent_comment is None:
            replies = obj.replies.all()
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def create(self, validated_data):
        mentioned_user_ids = validated_data.pop('mentioned_user_ids', [])
        comment = Comment.objects.create(**validated_data)
        
        # Add mentioned users
        if mentioned_user_ids:
            mentioned_users = User.objects.filter(id__in=mentioned_user_ids)
            comment.mentioned_users.set(mentioned_users)
        
        return comment
    
    def update(self, instance, validated_data):
        mentioned_user_ids = validated_data.pop('mentioned_user_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update mentioned users if provided
        if mentioned_user_ids is not None:
            mentioned_users = User.objects.filter(id__in=mentioned_user_ids)
            instance.mentioned_users.set(mentioned_users)
        
        return instance


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for design reviews"""
    reviewer = UserMinimalSerializer(read_only=True)
    requested_by = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'project', 'reviewer', 'requested_by',
            'status', 'summary',
            'design_quality', 'creativity', 'usability', 'overall_rating',
            'reviewed_version',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['reviewer', 'requested_by', 'created_at', 'updated_at']
    
    def validate(self, data):
        # Validate ratings are between 1-10
        for field in ['design_quality', 'creativity', 'usability', 'overall_rating']:
            if field in data and data[field] is not None:
                if not 1 <= data[field] <= 10:
                    raise serializers.ValidationError({
                        field: "Rating must be between 1 and 10"
                    })
        return data


class DesignFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for AI-generated design feedback"""
    
    class Meta:
        model = DesignFeedback
        fields = [
            'id', 'project', 'feedback_type', 'feedback_data',
            'is_helpful', 'user_notes',
            'model_used', 'tokens_used', 'processing_time',
            'created_at'
        ]
        read_only_fields = ['model_used', 'tokens_used', 'processing_time', 'created_at']


class CommentResolveSerializer(serializers.Serializer):
    """Serializer for resolving comments"""
    is_resolved = serializers.BooleanField()


class ReviewRequestSerializer(serializers.Serializer):
    """Serializer for requesting reviews"""
    reviewer_id = serializers.IntegerField()
    message = serializers.CharField(max_length=500, required=False, allow_blank=True)
