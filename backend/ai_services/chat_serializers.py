"""
Serializers for AI Chat features
"""
from rest_framework import serializers
from .models import ChatConversation, ChatMessage, AIFeedback


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'conversation', 'sender_type', 'message', 
            'metadata', 'tokens_used', 'model_used', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ChatConversationSerializer(serializers.ModelSerializer):
    """Serializer for chat conversations"""
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatConversation
        fields = [
            'id', 'user', 'title', 'context_data', 
            'is_active', 'created_at', 'updated_at',
            'messages', 'message_count'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ChatConversationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing conversations"""
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatConversation
        fields = [
            'id', 'title', 'is_active', 'created_at', 
            'updated_at', 'last_message', 'message_count'
        ]
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'sender_type': last_msg.sender_type,
                'message': last_msg.message[:100],
                'created_at': last_msg.created_at
            }
        return None
    
    def get_message_count(self, obj):
        return obj.messages.count()


class AIFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for AI feedback"""
    
    class Meta:
        model = AIFeedback
        fields = [
            'id', 'user', 'ai_request', 'chat_message',
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
