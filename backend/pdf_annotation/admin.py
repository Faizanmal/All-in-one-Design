from django.contrib import admin
from .models import PDFDocument, PDFPage, PDFAnnotation, AnnotationImportJob, PDFExport

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'status', 'page_count', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'user__username']

@admin.register(PDFPage)
class PDFPageAdmin(admin.ModelAdmin):
    list_display = ['document', 'page_number', 'width', 'height', 'annotation_count']

@admin.register(PDFAnnotation)
class PDFAnnotationAdmin(admin.ModelAdmin):
    list_display = ['annotation_type', 'page', 'author', 'imported_to_design', 'created_at']
    list_filter = ['annotation_type', 'imported_to_design']

@admin.register(AnnotationImportJob)
class AnnotationImportJobAdmin(admin.ModelAdmin):
    list_display = ['document', 'project', 'status', 'annotations_imported', 'created_at']
    list_filter = ['status']

@admin.register(PDFExport)
class PDFExportAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'page_count', 'created_at']
    list_filter = ['status']
