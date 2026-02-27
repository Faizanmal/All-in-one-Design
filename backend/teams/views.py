from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
import secrets
from datetime import timedelta

from .models import Team, TeamMembership, TeamInvitation, TeamProject, Comment, TeamActivity
from .serializers import (
    TeamSerializer, TeamCreateSerializer, TeamMembershipSerializer,
    TeamInvitationSerializer, TeamInvitationCreateSerializer,
    TeamProjectSerializer, CommentSerializer, CommentCreateSerializer,
    TeamActivitySerializer
)
from .permissions import IsTeamMember, IsTeamAdmin


class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for team management"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamCreateSerializer
        return TeamSerializer
    
    def perform_create(self, serializer):
        team = serializer.save(owner=self.request.user)
        # Auto-add owner as team member
        TeamMembership.objects.create(
            team=team,
            user=self.request.user,
            role='owner'
        )
    
    @action(detail=True, methods=['get'], permission_classes=[IsTeamMember])
    def members(self, request, pk=None):
        """Get all team members"""
        team = self.get_object()
        memberships = team.memberships.filter(is_active=True)
        serializer = TeamMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='my-permissions')
    def my_permissions(self, request, pk=None):
        """Get the current user's permissions for this team"""
        from .permissions import get_user_team_permissions
        team = self.get_object()
        perms = get_user_team_permissions(request.user, team.id)
        return Response(perms)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeamAdmin])
    def invite_member(self, request, pk=None):
        """Invite a user to the team"""
        team = self.get_object()
        serializer = TeamInvitationCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Generate unique token
            token = secrets.token_urlsafe(32)
            expires_at = timezone.now() + timedelta(days=7)
            
            invitation = serializer.save(
                team=team,
                invited_by=request.user,
                token=token,
                expires_at=expires_at
            )
            
            # Send invitation email
            from notifications.email_service import send_team_invitation_email
            send_team_invitation_email.delay(invitation.id)
            
            return Response(
                TeamInvitationSerializer(invitation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeamAdmin])
    def remove_member(self, request, pk=None):
        """Remove a member from the team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cannot remove owner
        if team.owner.id == int(user_id):
            return Response(
                {'error': 'Cannot remove team owner'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = get_object_or_404(
            TeamMembership,
            team=team,
            user_id=user_id
        )
        membership.delete()
        
        # Log activity
        TeamActivity.objects.create(
            team=team,
            user=request.user,
            action='member_left',
            description=f"{membership.user.username} was removed from the team"
        )
        
        return Response({'success': True})
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeamAdmin])
    def update_member_role(self, request, pk=None):
        """Update a member's role"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')
        
        if not user_id or not new_role:
            return Response(
                {'error': 'user_id and role are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = get_object_or_404(
            TeamMembership,
            team=team,
            user_id=user_id
        )
        
        old_role = membership.role
        membership.role = new_role
        membership.save()
        
        # Log activity
        TeamActivity.objects.create(
            team=team,
            user=request.user,
            action='member_role_changed',
            description=f"{membership.user.username}'s role changed from {old_role} to {new_role}"
        )
        
        return Response(TeamMembershipSerializer(membership).data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsTeamMember])
    def projects(self, request, pk=None):
        """Get all team projects"""
        team = self.get_object()
        team_projects = team.team_projects.all()
        serializer = TeamProjectSerializer(team_projects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeamMember])
    def add_project(self, request, pk=None):
        """Add a project to the team"""
        team = self.get_object()
        project_id = request.data.get('project_id')
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from projects.models import Project
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user owns the project
        if project.user != request.user:
            return Response(
                {'error': 'You can only add your own projects'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create team project link
        team_project, created = TeamProject.objects.get_or_create(
            team=team,
            project=project,
            defaults={'created_by': request.user}
        )
        
        if created:
            # Log activity
            TeamActivity.objects.create(
                team=team,
                user=request.user,
                action='project_created',
                project=project,
                description=f"Project '{project.name}' was added to the team"
            )
        
        return Response(
            TeamProjectSerializer(team_project).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], permission_classes=[IsTeamMember])
    def activity(self, request, pk=None):
        """Get team activity feed"""
        team = self.get_object()
        activities = team.activities.all()[:50]  # Last 50 activities
        serializer = TeamActivitySerializer(activities, many=True)
        return Response(serializer.data)


class TeamInvitationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for team invitations"""
    permission_classes = [IsAuthenticated]
    serializer_class = TeamInvitationSerializer
    
    def get_queryset(self):
        user = self.request.user
        return TeamInvitation.objects.filter(
            Q(email=user.email) | Q(invited_by=user)
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept team invitation"""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response(
                {'error': f'Invitation is already {invitation.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invitation.is_expired:
            invitation.status = 'expired'
            invitation.save()
            return Response(
                {'error': 'Invitation has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add user to team
        TeamMembership.objects.create(
            team=invitation.team,
            user=request.user,
            role=invitation.role
        )
        
        invitation.status = 'accepted'
        invitation.responded_at = timezone.now()
        invitation.save()
        
        # Log activity
        TeamActivity.objects.create(
            team=invitation.team,
            user=request.user,
            action='member_joined',
            description=f"{request.user.username} joined the team"
        )
        
        return Response({'success': True, 'team_id': invitation.team.id})
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline team invitation"""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response(
                {'error': f'Invitation is already {invitation.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invitation.status = 'declined'
        invitation.responded_at = timezone.now()
        invitation.save()
        
        return Response({'success': True})


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for project comments"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        if project_id:
            return Comment.objects.filter(project_id=project_id, parent=None)
        return Comment.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return CommentCreateSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        comment = serializer.save(
            user=self.request.user,
            project_id=self.request.data.get('project_id')
        )
        
        # Log activity
        from projects.models import Project
        project = Project.objects.get(id=self.request.data.get('project_id'))
        
        # Find team if project is in a team
        team_project = TeamProject.objects.filter(project=project).first()
        if team_project:
            TeamActivity.objects.create(
                team=team_project.team,
                user=self.request.user,
                action='comment_added',
                project=project,
                comment=comment,
                description=f"Comment added on '{project.name}'"
            )
        
        # Send notifications to mentions
        from notifications.email_service import send_mention_notification_email, send_comment_notification_email
        
        # Notify project owner
        send_comment_notification_email.delay(comment.id)
        
        # Notify mentioned users
        for user in comment.mentions.all():
            send_mention_notification_email.delay(user.id, comment.id)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark comment as resolved"""
        comment = self.get_object()
        comment.is_resolved = True
        comment.resolved_by = request.user
        comment.resolved_at = timezone.now()
        comment.save()
        
        # Log activity
        team_project = TeamProject.objects.filter(project=comment.project).first()
        if team_project:
            TeamActivity.objects.create(
                team=team_project.team,
                user=request.user,
                action='comment_resolved',
                project=comment.project,
                comment=comment,
                description=f"Comment resolved on '{comment.project.name}'"
            )
        
        return Response(CommentSerializer(comment).data)
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """Get all replies to a comment"""
        comment = self.get_object()
        replies = comment.replies.all()
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)


class TeamActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for team activity feed"""
    permission_classes = [IsAuthenticated, IsTeamMember]
    serializer_class = TeamActivitySerializer
    
    def get_queryset(self):
        team_id = self.request.query_params.get('team_id')
        if team_id:
            return TeamActivity.objects.filter(team_id=team_id)
        return TeamActivity.objects.none()
