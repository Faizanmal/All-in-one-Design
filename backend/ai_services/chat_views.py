"""
API Views for Chat functionality
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ChatConversation, AIFeedback
from .chat_serializers import (
    ChatConversationSerializer, ChatConversationListSerializer,
    ChatMessageSerializer, AIFeedbackSerializer
)


class ChatConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat conversations"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChatConversationListSerializer
        return ChatConversationSerializer
    
    def get_queryset(self):
        return ChatConversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in the conversation"""
        conversation = self.get_object()
        
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(conversation=conversation, sender_type='user')
            
            # Here you would integrate with your AI service
            # For now, we'll just return the saved message
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in a conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a conversation"""
        conversation = self.get_object()
        conversation.is_active = False
        conversation.save()
        return Response({'status': 'conversation archived'})


class AIFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for AI feedback"""
    serializer_class = AIFeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIFeedback.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
