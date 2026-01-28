from django.contrib import admin
from .models import (
    MobileDevice, MobileSession, OfflineCache, MobileAnnotation,
    MobileNotification, MobilePreference, MobileAppVersion
)

# Register models with basic admin
admin.site.register(MobileDevice)
admin.site.register(MobileSession)
admin.site.register(OfflineCache)
admin.site.register(MobileAnnotation)
admin.site.register(MobileNotification)
admin.site.register(MobilePreference)
admin.site.register(MobileAppVersion)
