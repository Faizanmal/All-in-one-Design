from rest_framework import serializers
from .models import SocialAccount, ScheduledPost

class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ['id', 'platform', 'account_name', 'connected']
        read_only_fields = ['id']
    
    # We add a connected property computed field for ease of use in the frontend
    connected = serializers.SerializerMethodField()

    def get_connected(self, obj):
        return bool(obj.access_token)

class ScheduledPostSerializer(serializers.ModelSerializer):
    accounts = serializers.PrimaryKeyRelatedField(many=True, queryset=SocialAccount.objects.all())
    
    class Meta:
        model = ScheduledPost
        fields = ['id', 'project_id', 'content', 'media_url', 'scheduled_time', 'status', 'accounts', 'error_message', 'created_at']
        read_only_fields = ['id', 'status', 'error_message', 'created_at']
