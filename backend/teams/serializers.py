from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, TeamMembership, TeamInvitation, TeamProject, Comment, TeamActivity


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = TeamMembership
        fields = '__all__'
        read_only_fields = ['joined_at', 'updated_at']


class TeamSerializer(serializers.ModelSerializer):
    owner = UserBasicSerializer(read_only=True)
    member_count = serializers.ReadOnlyField()
    project_count = serializers.ReadOnlyField()
    memberships = TeamMembershipSerializer(many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'owner']


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'slug', 'description', 'max_members']


class TeamInvitationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = TeamInvitation
        fields = '__all__'
        read_only_fields = ['token', 'status', 'created_at', 'expires_at', 'responded_at', 'invited_by']


class TeamInvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInvitation
        fields = ['email', 'role', 'message']


class TeamProjectSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = TeamProject
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class CommentSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    resolved_by = UserBasicSerializer(read_only=True)
    reply_count = serializers.ReadOnlyField()
    mentions = UserBasicSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at', 'resolved_by', 'resolved_at']
    
    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.all()[:5]  # Limit to 5 replies
            return CommentSerializer(replies, many=True).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    mention_usernames = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Comment
        fields = ['content', 'parent', 'position_x', 'position_y', 'mention_usernames']
    
    def create(self, validated_data):
        mention_usernames = validated_data.pop('mention_usernames', [])
        comment = Comment.objects.create(**validated_data)
        
        # Add mentions
        if mention_usernames:
            users = User.objects.filter(username__in=mention_usernames)
            comment.mentions.set(users)
        
        return comment


class TeamActivitySerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    
    class Meta:
        model = TeamActivity
        fields = '__all__'
        read_only_fields = ['created_at']
