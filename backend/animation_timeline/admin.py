from django.contrib import admin
from .models import (
    AnimationProject, AnimationComposition, AnimationLayer,
    AnimationTrack, AnimationKeyframe, EasingPreset, AnimationEffect,
    LottieExport, AnimationSequence
)

# Register models with basic admin
admin.site.register(AnimationProject)
admin.site.register(AnimationComposition)
admin.site.register(AnimationLayer)
admin.site.register(AnimationTrack)
admin.site.register(AnimationKeyframe)
admin.site.register(EasingPreset)
admin.site.register(AnimationEffect)
admin.site.register(LottieExport)
admin.site.register(AnimationSequence)
