from django.apps import AppConfig


class PdfExportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pdf_export'
    verbose_name = 'PDF Export with Bleed'
