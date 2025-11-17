"""
Serializers for Team collaboration features
"""
from rest_framework import serializers
from .models import Task, TeamChat, TeamChatMessage


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for team tasks"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    assigned_to_names = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'team', 'project', 'title', 'description',
            'created_by', 'created_by_name', 'assigned_to', 'assigned_to_names',
            'status', 'priority', 'due_date', 'completed_at',
            'tags', 'attachments', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_assigned_to_names(self, obj):
        return [user.username for user in obj.assigned_to.all()]
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        if obj.due_date and obj.status not in ['completed', 'cancelled']:
            return timezone.now() > obj.due_date
        return False


class TeamChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for team chat messages"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    reaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamChatMessage
        fields = [
            'id', 'chat_room', 'user', 'user_name', 'message',
            'attachments', 'reactions', 'reaction_count', 'reply_to',
            'is_edited', 'edited_at', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_reaction_count(self, obj):
        total = 0
        for users in obj.reactions.values():
            total += len(users)
        return total


class TeamChatSerializer(serializers.ModelSerializer):
    """Serializer for team chat rooms"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    member_count = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamChat
        fields = [
            'id', 'team', 'name', 'description', 'project',
            'is_private', 'members', 'created_by', 'created_by_name',
            'member_count', 'message_count', 'last_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'user_name': last_msg.user.username,
                'message': last_msg.message[:100],
                'created_at': last_msg.created_at
            }
        return None
