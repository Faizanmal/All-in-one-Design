from django.contrib import admin
from .models import (
    AutoLayoutFrame, AutoLayoutChild, LayoutConstraint,
    ResponsiveBreakpoint, ResponsiveOverride, LayoutPreset
)

# Register models with basic admin
admin.site.register(AutoLayoutFrame)
admin.site.register(AutoLayoutChild)
admin.site.register(LayoutConstraint)
admin.site.register(ResponsiveBreakpoint)
admin.site.register(ResponsiveOverride)
admin.site.register(LayoutPreset)
