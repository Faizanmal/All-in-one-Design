from rest_framework import serializers
from .models import Model3D, Scene3D, SceneModel, Prototype3D, ARPreview, Conversion3DTo2D


class Model3DSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Model3D
        fields = [
            'id', 'user', 'project', 'name', 'description',
            'file', 'file_url', 'file_format', 'file_size',
            'thumbnail', 'thumbnail_url',
            'vertex_count', 'face_count', 'material_count', 'texture_count', 'animation_count',
            'bbox_min_x', 'bbox_min_y', 'bbox_min_z', 'bbox_max_x', 'bbox_max_y', 'bbox_max_z',
            'ar_enabled', 'ar_scale', 'ar_anchor_type',
            'tags', 'category',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'file_size', 'vertex_count', 'face_count', 
                          'material_count', 'texture_count', 'animation_count',
                          'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None


class Model3DUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model3D
        fields = ['file', 'name', 'description', 'project', 'tags', 'category']
    
    def validate_file(self, value):
        # Check file extension
        allowed_extensions = ['gltf', 'glb', 'obj', 'fbx', 'stl', 'usdz']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (max 100MB)
        max_size = 100 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 100MB")
        
        return value


class SceneModelSerializer(serializers.ModelSerializer):
    model_name = serializers.ReadOnlyField(source='model.name')
    model_thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = SceneModel
        fields = [
            'id', 'model', 'model_name', 'model_thumbnail',
            'position_x', 'position_y', 'position_z',
            'rotation_x', 'rotation_y', 'rotation_z',
            'scale_x', 'scale_y', 'scale_z',
            'visible', 'cast_shadow', 'receive_shadow',
            'material_overrides', 'layer', 'created_at'
        ]
    
    def get_model_thumbnail(self, obj):
        if obj.model.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.model.thumbnail.url)
            return obj.model.thumbnail.url
        return None


class Scene3DSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    scene_models = SceneModelSerializer(many=True, read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Scene3D
        fields = [
            'id', 'user', 'project', 'name', 'description',
            'scene_data', 'camera_settings', 'lighting_settings', 'environment_settings',
            'thumbnail', 'thumbnail_url', 'scene_models',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None


class Scene3DCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scene3D
        fields = ['name', 'description', 'project', 'scene_data', 
                  'camera_settings', 'lighting_settings', 'environment_settings']


class Prototype3DSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    scene_name = serializers.ReadOnlyField(source='scene.name')
    
    class Meta:
        model = Prototype3D
        fields = [
            'id', 'user', 'scene', 'scene_name', 'name', 'description',
            'interactions', 'animations', 'states', 'triggers',
            'preview_mode', 'auto_play', 'loop',
            'is_public', 'share_link', 'password',
            'view_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'share_link', 'view_count', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class ARPreviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    usdz_url = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ARPreview
        fields = [
            'id', 'user', 'model_3d', 'scene_3d', 'project', 'name',
            'ar_type', 'tracking_image',
            'scale', 'offset_x', 'offset_y', 'offset_z',
            'allow_scale', 'allow_rotate', 'allow_move',
            'usdz_file', 'usdz_url', 'qr_code', 'qr_code_url',
            'is_public', 'share_link',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'usdz_file', 'qr_code', 'share_link', 'created_at', 'updated_at']
    
    def get_usdz_url(self, obj):
        if obj.usdz_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.usdz_file.url)
            return obj.usdz_file.url
        return None
    
    def get_qr_code_url(self, obj):
        if obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
            return obj.qr_code.url
        return None


class Conversion3DTo2DSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    output_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversion3DTo2D
        fields = [
            'id', 'user', 'model_3d', 'scene_3d',
            'view', 'width', 'height', 'transparent_background',
            'camera_position', 'camera_target',
            'output_format', 'status', 'output_file', 'output_url',
            'error_message', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'output_file', 'error_message', 
                          'created_at', 'completed_at']
    
    def get_output_url(self, obj):
        if obj.output_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.output_file.url)
            return obj.output_file.url
        return None
    
    def validate(self, data):
        if not data.get('model_3d') and not data.get('scene_3d'):
            raise serializers.ValidationError("Either model_3d or scene_3d must be provided")
        return data
