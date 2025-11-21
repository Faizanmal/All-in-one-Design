from rest_framework import serializers
from .models import Project, DesignComponent, ProjectVersion, ExportTemplate, ExportJob


class DesignComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignComponent
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    components = DesignComponentSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    collaborator_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def get_collaborator_names(self, obj):
        return [user.username for user in obj.collaborators.all()]


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'description', 'project_type', 'canvas_width', 
                 'canvas_height', 'canvas_background', 'ai_prompt')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProjectVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ProjectVersion
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')


class ExportTemplateSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    quality_display = serializers.CharField(source='get_quality_display', read_only=True)
    
    class Meta:
        model = ExportTemplate
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'use_count')


class ExportJobSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True, allow_null=True)
    project_count = serializers.SerializerMethodField()
    progress_percentage = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportJob
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'started_at', 'completed_at', 
                           'total_projects', 'completed_projects', 'failed_projects',
                           'file_size', 'error_message', 'error_details')
    
    def get_project_count(self, obj):
        return obj.projects.count()
    
    def get_file_url(self, obj):
        if obj.output_file:
            return obj.output_file.url
        return None
