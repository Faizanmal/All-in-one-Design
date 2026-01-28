"""
PDF Annotation Serializers
"""

from rest_framework import serializers
from .models import (
    PDFDocument, PDFPage, PDFAnnotation,
    AnnotationImportJob, MarkupTemplate, PDFExport
)


class PDFAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFAnnotation
        fields = [
            'id', 'page', 'annotation_type',
            'x', 'y', 'width', 'height',
            'content', 'subject', 'color', 'opacity', 'border_width',
            'vertices', 'author', 'creation_date', 'modification_date',
            'covered_text', 'quads',
            'imported_to_design', 'design_element_id',
            'created_at'
        ]


class PDFPageSerializer(serializers.ModelSerializer):
    annotations = PDFAnnotationSerializer(many=True, read_only=True)
    
    class Meta:
        model = PDFPage
        fields = [
            'id', 'document', 'page_number',
            'image', 'thumbnail',
            'width', 'height', 'rotation',
            'text_content', 'text_blocks',
            'annotation_count', 'annotations',
            'created_at'
        ]


class PDFPageListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views."""
    
    class Meta:
        model = PDFPage
        fields = [
            'id', 'page_number', 'thumbnail',
            'width', 'height', 'annotation_count'
        ]


class PDFDocumentSerializer(serializers.ModelSerializer):
    pages = PDFPageListSerializer(many=True, read_only=True)
    
    class Meta:
        model = PDFDocument
        fields = [
            'id', 'project', 'name', 'file',
            'status', 'error_message',
            'page_count', 'file_size',
            'title', 'author', 'subject',
            'width', 'height',
            'pages', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'error_message', 'page_count', 'file_size',
            'title', 'author', 'subject', 'width', 'height',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AnnotationImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnotationImportJob
        fields = [
            'id', 'document', 'project', 'settings',
            'status', 'progress',
            'annotations_found', 'annotations_imported',
            'error_message',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'progress',
            'annotations_found', 'annotations_imported',
            'error_message', 'started_at', 'completed_at', 'created_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MarkupTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkupTemplate
        fields = [
            'id', 'name', 'description',
            'mappings', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PDFExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFExport
        fields = [
            'id', 'project', 'name', 'settings',
            'status', 'progress',
            'output_file', 'page_count', 'file_size',
            'error_message',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'progress',
            'output_file', 'page_count', 'file_size',
            'error_message', 'started_at', 'completed_at', 'created_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Request Serializers

class UploadPDFSerializer(serializers.Serializer):
    file = serializers.FileField()
    project_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)


class ImportAnnotationsSerializer(serializers.Serializer):
    document_id = serializers.UUIDField()
    project_id = serializers.IntegerField()
    annotation_types = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    pages = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    convert_to_comments = serializers.BooleanField(default=True)
    convert_to_shapes = serializers.BooleanField(default=True)
    template_id = serializers.UUIDField(required=False)


class ExportPDFSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    frames = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    include_comments = serializers.BooleanField(default=True)
    comments_as_annotations = serializers.BooleanField(default=True)
    include_links = serializers.BooleanField(default=True)
    resolution = serializers.IntegerField(default=150, min_value=72, max_value=300)
    compress_images = serializers.BooleanField(default=True)
