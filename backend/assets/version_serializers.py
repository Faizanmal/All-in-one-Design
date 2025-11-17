"""
Serializers for Asset versioning and collaboration
"""
from rest_framework import serializers
from .models import AssetVersion, AssetComment, AssetCollection


class AssetVersionSerializer(serializers.ModelSerializer):
    """Serializer for asset versions"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = AssetVersion
        fields = [
            'id', 'asset', 'version_number', 'file_url', 
            'file_size', 'change_description', 'created_by', 
            'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']


class AssetCommentSerializer(serializers.ModelSerializer):
    """Serializer for asset comments"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetComment
        fields = [
            'id', 'asset', 'user', 'user_name', 'comment',
            'position_x', 'position_y', 'timestamp', 
            'parent_comment', 'replies', 'reply_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return AssetCommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def get_reply_count(self, obj):
        return obj.replies.count()


class AssetCollectionSerializer(serializers.ModelSerializer):
    """Serializer for asset collections"""
    asset_count = serializers.SerializerMethodField()
    subcollection_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetCollection
        fields = [
            'id', 'name', 'description', 'user', 'assets',
            'parent_collection', 'is_public', 'color',
            'asset_count', 'subcollection_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_asset_count(self, obj):
        return obj.assets.count()
    
    def get_subcollection_count(self, obj):
        return obj.subcollections.count()


class AssetCollectionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing collections"""
    asset_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetCollection
        fields = ['id', 'name', 'color', 'is_public', 'asset_count']
    
    def get_asset_count(self, obj):
        return obj.assets.count()
