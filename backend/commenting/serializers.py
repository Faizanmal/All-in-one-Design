"""
Commenting Serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    CommentThread, Comment, Mention, Reaction,
    ReviewSession, Reviewer, CommentNotification, CommentTemplate
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class MentionSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Mention
        fields = ['id', 'user', 'start_index', 'end_index', 'read']


class ReactionSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Reaction
        fields = ['id', 'emoji', 'user', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    mentions = MentionSerializer(many=True, read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    reaction_counts = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'thread', 'parent', 'comment_type',
            'content', 'media_file', 'media_duration', 'thumbnail',
            'annotation_data', 'author', 'is_edited', 'edited_at',
            'is_internal', 'mentions', 'reactions', 'reaction_counts',
            'reply_count', 'created_at'
        ]
        read_only_fields = ['id', 'author', 'is_edited', 'edited_at', 'created_at']
    
    def get_reaction_counts(self, obj):
        counts = {}
        for reaction in obj.reactions.all():
            counts[reaction.emoji] = counts.get(reaction.emoji, 0) + 1
        return counts
    
    def get_reply_count(self, obj):
        return obj.replies.count()
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class CommentThreadSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    assignee = UserBasicSerializer(read_only=True)
    resolved_by = UserBasicSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()
    latest_comment = serializers.SerializerMethodField()
    
    class Meta:
        model = CommentThread
        fields = [
            'id', 'project', 'frame_id', 'element_id', 'x', 'y',
            'status', 'assignee', 'priority', 'label', 'tags',
            'created_by', 'resolved_by', 'resolved_at',
            'version_id', 'comment_count', 'latest_comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'resolved_by', 'resolved_at', 'created_at', 'updated_at']
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_latest_comment(self, obj):
        comment = obj.comments.order_by('-created_at').first()
        if comment:
            return {
                'content': comment.content[:100] if comment.content else '',
                'author': comment.author.username,
                'created_at': comment.created_at
            }
        return None
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CommentThreadDetailSerializer(CommentThreadSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta(CommentThreadSerializer.Meta):
        fields = CommentThreadSerializer.Meta.fields + ['comments']


class ReviewerSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Reviewer
        fields = [
            'id', 'user', 'user_id', 'decision', 'feedback',
            'decided_at', 'invited_at', 'reminded_at'
        ]
        read_only_fields = ['id', 'decided_at', 'invited_at', 'reminded_at']


class ReviewSessionSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    reviewers = ReviewerSerializer(many=True, read_only=True)
    approval_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewSession
        fields = [
            'id', 'project', 'title', 'description',
            'frame_ids', 'version_id',
            'require_all_approvals', 'approval_count_needed',
            'status', 'due_date', 'started_at', 'completed_at',
            'created_by', 'reviewers', 'approval_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'started_at', 'completed_at', 'created_at', 'updated_at']
    
    def get_approval_count(self, obj):
        return obj.reviewers.filter(decision='approved').count()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CommentNotificationSerializer(serializers.ModelSerializer):
    actor = UserBasicSerializer(read_only=True)
    thread_data = serializers.SerializerMethodField()
    
    class Meta:
        model = CommentNotification
        fields = [
            'id', 'notification_type', 'thread', 'comment', 'review',
            'actor', 'thread_data', 'read', 'read_at', 'created_at'
        ]
    
    def get_thread_data(self, obj):
        if obj.thread:
            return {
                'id': str(obj.thread.id),
                'project_id': obj.thread.project_id,
                'frame_id': obj.thread.frame_id
            }
        return None


class CommentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentTemplate
        fields = [
            'id', 'name', 'content', 'shortcut',
            'category', 'is_shared', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Request Serializers

class CreateCommentSerializer(serializers.Serializer):
    thread_id = serializers.UUIDField(required=False)
    parent_id = serializers.UUIDField(required=False)
    
    # Thread creation (if thread_id not provided)
    project_id = serializers.IntegerField(required=False)
    frame_id = serializers.CharField(required=False, allow_blank=True)
    element_id = serializers.CharField(required=False, allow_blank=True)
    x = serializers.FloatField(required=False, default=0)
    y = serializers.FloatField(required=False, default=0)
    
    # Comment content
    comment_type = serializers.ChoiceField(
        choices=['text', 'voice', 'video', 'annotation', 'emoji'],
        default='text'
    )
    content = serializers.CharField(required=False, allow_blank=True)
    annotation_data = serializers.JSONField(required=False)
    is_internal = serializers.BooleanField(default=False)
    
    # Mentioned users (by username or ID)
    mentions = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class ResolveThreadSerializer(serializers.Serializer):
    resolution_comment = serializers.CharField(required=False, allow_blank=True)


class AssignThreadSerializer(serializers.Serializer):
    assignee_id = serializers.IntegerField(required=False, allow_null=True)


class AddReactionSerializer(serializers.Serializer):
    emoji = serializers.CharField(max_length=10)


class ReviewDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=['approved', 'rejected', 'changes_requested'])
    feedback = serializers.CharField(required=False, allow_blank=True)
