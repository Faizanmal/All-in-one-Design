from django.contrib import admin
from .models import (
    InteractiveComponent, ComponentState, ComponentInteraction,
    ComponentVariable, CarouselItem, DropdownOption,
    AccordionSection, TabItem, InteractiveTemplate
)


class ComponentStateInline(admin.TabularInline):
    model = ComponentState
    extra = 0


class ComponentInteractionInline(admin.TabularInline):
    model = ComponentInteraction
    extra = 0


@admin.register(InteractiveComponent)
class InteractiveComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'component_type', 'project', 'user', 'created_at']
    list_filter = ['component_type', 'created_at']
    search_fields = ['name', 'user__username', 'project__name']
    inlines = [ComponentStateInline, ComponentInteractionInline]


@admin.register(InteractiveTemplate)
class InteractiveTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'component_type', 'is_premium', 'created_at']
    list_filter = ['category', 'component_type', 'is_premium']
    search_fields = ['name', 'description']
