from django.contrib import admin
from .models import (
    Presentation, PresentationSlide, SlideAnnotation, PresentationViewer,
    DevModeProject, DevModeInspection, CodeExportConfig, CodeExportHistory,
    MeasurementOverlay, AssetExportQueue
)

# Register models with basic admin
admin.site.register(Presentation)
admin.site.register(PresentationSlide)
admin.site.register(SlideAnnotation)
admin.site.register(PresentationViewer)
admin.site.register(DevModeProject)
admin.site.register(DevModeInspection)
admin.site.register(CodeExportConfig)
admin.site.register(CodeExportHistory)
admin.site.register(MeasurementOverlay)
admin.site.register(AssetExportQueue)
