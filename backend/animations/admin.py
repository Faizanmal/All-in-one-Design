from django.contrib import admin
from .models import (
    Animation, Keyframe, LottieAnimation, MicroInteraction,
    AnimationPreset, AnimationTimeline, TimelineItem
)


@admin.register(Animation)
class AnimationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'animation_type', 'duration', 'is_preset', 'created_at']
    list_filter = ['animation_type', 'is_preset', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Keyframe)
class KeyframeAdmin(admin.ModelAdmin):
    list_display = ['animation', 'position', 'easing']
    list_filter = ['animation']


@admin.register(LottieAnimation)
class LottieAnimationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'frame_rate', 'layer_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['id', 'file_size', 'version', 'frame_rate', 'in_point', 'out_point',
                       'width', 'height', 'asset_count', 'layer_count', 'created_at', 'updated_at']


@admin.register(MicroInteraction)
class MicroInteractionAdmin(admin.ModelAdmin):
    list_display = ['name', 'interaction_type', 'is_premium', 'usage_count', 'created_at']
    list_filter = ['interaction_type', 'is_premium', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'usage_count', 'created_at', 'updated_at']


@admin.register(AnimationPreset)
class AnimationPresetAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_premium', 'usage_count', 'created_at']
    list_filter = ['category', 'is_premium', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'usage_count', 'created_at']


@admin.register(AnimationTimeline)
class AnimationTimelineAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'duration', 'frame_rate', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TimelineItem)
class TimelineItemAdmin(admin.ModelAdmin):
    list_display = ['timeline', 'animation', 'lottie', 'track_index', 'start_time', 'end_time']
    list_filter = ['timeline']
