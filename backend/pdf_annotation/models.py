"""
PDF Annotation & Markup Import Models

Import PDFs, extract annotations, and convert markup to design elements.
"""

from django.db import models
from django.conf import settings
import uuid


class PDFDocument(models.Model):
    """Uploaded PDF document."""
    
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pdf_documents')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='pdf_documents', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='pdfs/')
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    error_message = models.TextField(blank=True)
    
    # Metadata
    page_count = models.IntegerField(default=0)
    file_size = models.BigIntegerField(default=0)
    
    # PDF info
    title = models.CharField(max_length=500, blank=True)
    author = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=500, blank=True)
    keywords = models.TextField(blank=True)
    creator = models.CharField(max_length=255, blank=True)
    producer = models.CharField(max_length=255, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    modification_date = models.DateTimeField(null=True, blank=True)
    
    # Dimensions (first page)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class PDFPage(models.Model):
    """Individual page from a PDF."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='pages')
    
    page_number = models.IntegerField()
    
    # Rendered image
    image = models.ImageField(upload_to='pdf_pages/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='pdf_thumbnails/', null=True, blank=True)
    
    # Dimensions
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    rotation = models.IntegerField(default=0)  # 0, 90, 180, 270
    
    # Text content (extracted)
    text_content = models.TextField(blank=True)
    text_blocks = models.JSONField(default=list)  # [{text, x, y, width, height, font}]
    
    # Annotation count
    annotation_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['page_number']
        unique_together = ['document', 'page_number']


class PDFAnnotation(models.Model):
    """Annotation extracted from PDF."""
    
    ANNOTATION_TYPES = [
        ('highlight', 'Highlight'),
        ('underline', 'Underline'),
        ('strikeout', 'Strikeout'),
        ('squiggly', 'Squiggly'),
        ('text', 'Text Note'),
        ('freetext', 'Free Text'),
        ('line', 'Line'),
        ('arrow', 'Arrow'),
        ('rectangle', 'Rectangle'),
        ('circle', 'Circle'),
        ('polygon', 'Polygon'),
        ('polyline', 'Polyline'),
        ('ink', 'Ink/Freehand'),
        ('stamp', 'Stamp'),
        ('caret', 'Caret'),
        ('link', 'Link'),
        ('file_attachment', 'File Attachment'),
        ('sound', 'Sound'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(PDFPage, on_delete=models.CASCADE, related_name='annotations')
    
    annotation_type = models.CharField(max_length=20, choices=ANNOTATION_TYPES)
    
    # Position (in PDF coordinates)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    
    # Content
    content = models.TextField(blank=True)  # Text content or popup content
    subject = models.CharField(max_length=255, blank=True)
    
    # Appearance
    color = models.CharField(max_length=20, blank=True)  # Hex color
    opacity = models.FloatField(default=1.0)
    border_width = models.FloatField(default=1.0)
    
    # For shapes with vertices
    vertices = models.JSONField(default=list)  # [[x1, y1], [x2, y2], ...]
    
    # Metadata from PDF
    author = models.CharField(max_length=255, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    modification_date = models.DateTimeField(null=True, blank=True)
    
    # Rich content
    rich_content = models.TextField(blank=True)  # HTML or rich text
    
    # For highlights - the covered text
    covered_text = models.TextField(blank=True)
    quads = models.JSONField(default=list)  # Text selection quadrilaterals
    
    # Import status
    imported_to_design = models.BooleanField(default=False)
    design_element_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['page__page_number', 'y', 'x']


class AnnotationImportJob(models.Model):
    """Job to import annotations into design."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='import_jobs')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='annotation_import_jobs')
    
    # Import settings
    settings = models.JSONField(default=dict)
    # {
    #   "annotation_types": ["highlight", "text", "rectangle"],
    #   "pages": [1, 2, 3],  # or "all"
    #   "convert_to_comments": true,
    #   "convert_to_shapes": true,
    #   "scale_factor": 1.0
    # }
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.FloatField(default=0)
    
    # Results
    annotations_found = models.IntegerField(default=0)
    annotations_imported = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class MarkupTemplate(models.Model):
    """Template for how annotations should be converted to design elements."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='markup_templates')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Mapping rules
    mappings = models.JSONField(default=list)
    # [
    #   {
    #     "annotation_type": "highlight",
    #     "output_type": "comment",
    #     "style": {"color": "#ffff00", "opacity": 0.3}
    #   },
    #   {
    #     "annotation_type": "rectangle",
    #     "output_type": "shape",
    #     "style": {"stroke_color": "#ff0000", "stroke_width": 2}
    #   }
    # ]
    
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']


class PDFExport(models.Model):
    """Export design as PDF with annotations."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pdf_annotation_exports')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='pdf_annotation_exports')
    
    name = models.CharField(max_length=255)
    
    # Export settings
    settings = models.JSONField(default=dict)
    # {
    #   "frames": ["frame1", "frame2"],  # or "all"
    #   "include_comments": true,
    #   "comments_as_annotations": true,
    #   "include_links": true,
    #   "resolution": 150,  # DPI
    #   "compress_images": true
    # }
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.FloatField(default=0)
    
    # Output
    output_file = models.FileField(upload_to='pdf_exports/', null=True, blank=True)
    page_count = models.IntegerField(default=0)
    file_size = models.BigIntegerField(default=0)
    
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
