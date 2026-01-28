from django.contrib import admin
from .models import (
    ComponentSet, ComponentProperty, PropertyOption, ComponentVariant,
    VariantOverride, ComponentInstance, InteractiveState, ComponentSlot
)

# Register models with basic admin
admin.site.register(ComponentSet)
admin.site.register(ComponentProperty)
admin.site.register(PropertyOption)
admin.site.register(ComponentVariant)
admin.site.register(VariantOverride)
admin.site.register(ComponentInstance)
admin.site.register(InteractiveState)
admin.site.register(ComponentSlot)
