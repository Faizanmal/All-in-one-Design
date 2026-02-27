"""
API Views for Team collaboration features
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Task, TeamChat, TeamChatMessage
from .collaboration_serializers import (
    TaskSerializer, TeamChatSerializer, TeamChatMessageSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for team tasks"""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        team_id = self.request.query_params.get('team')
        project_id = self.request.query_params.get('project')
        status_filter = self.request.query_params.get('status')
        
        # Get tasks from teams the user is a member of
        queryset = Task.objects.filter(team__members=user)
        
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign task to users"""
        task = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        task.assigned_to.set(user_ids)
        return Response({'status': 'task assigned'})
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update task status"""
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'completed':
                from django.utils import timezone
                task.completed_at = timezone.now()
            task.save()
            return Response({'status': 'task status updated'})
        
        return Response(
            {'error': 'Invalid status'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class TeamChatViewSet(viewsets.ModelViewSet):
    """ViewSet for team chat rooms"""
    serializer_class = TeamChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        team_id = self.request.query_params.get('team')
        
        queryset = TeamChat.objects.filter(team__members=user)
        
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages in a chat room"""
        chat = self.get_object()
        messages = chat.messages.all()
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_messages = messages[start:end]
        serializer = TeamChatMessageSerializer(paginated_messages, many=True)
        
        return Response({
            'count': messages.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in the chat room"""
        chat = self.get_object()
        
        data = request.data.copy()
        data['chat_room'] = chat.id
        
        serializer = TeamChatMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for team chat messages"""
    serializer_class = TeamChatMessageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_queryset(self):
        user = self.request.user
        chat_id = self.request.query_params.get('chat')
        
        queryset = TeamChatMessage.objects.filter(chat_room__team__members=user)
        
        if chat_id:
            queryset = queryset.filter(chat_room_id=chat_id)
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        from django.utils import timezone
        serializer.save(is_edited=True, edited_at=timezone.now())
    
    @action(detail=True, methods=['post'])
    def add_reaction(self, request, pk=None):
        """Add a reaction to a message"""
        message = self.get_object()
        emoji = request.data.get('emoji')
        user_id = request.user.id
        
        reactions = message.reactions.copy()
        if emoji not in reactions:
            reactions[emoji] = []
        
        if user_id not in reactions[emoji]:
            reactions[emoji].append(user_id)
            message.reactions = reactions
            message.save()
        
        return Response({'status': 'reaction added'})
    
    @action(detail=True, methods=['post'])
    def remove_reaction(self, request, pk=None):
        """Remove a reaction from a message"""
        message = self.get_object()
        emoji = request.data.get('emoji')
        user_id = request.user.id
        
        reactions = message.reactions.copy()
        if emoji in reactions and user_id in reactions[emoji]:
            reactions[emoji].remove(user_id)
            if not reactions[emoji]:
                del reactions[emoji]
            message.reactions = reactions
            message.save()
        
        return Response({'status': 'reaction removed'})
