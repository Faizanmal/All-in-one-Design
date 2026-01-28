from django.contrib import admin
from .models import (
    Whiteboard, WhiteboardCollaborator, StickyNote, StickyNoteVote,
    WhiteboardShape, Connector, WhiteboardText, WhiteboardImage,
    WhiteboardGroup, WhiteboardSection, Timer, WhiteboardComment,
    WhiteboardEmoji, WhiteboardTemplate
)

# Register models with basic admin
admin.site.register(Whiteboard)
admin.site.register(WhiteboardCollaborator)
admin.site.register(StickyNote)
admin.site.register(StickyNoteVote)
admin.site.register(WhiteboardShape)
admin.site.register(Connector)
admin.site.register(WhiteboardText)
admin.site.register(WhiteboardImage)
admin.site.register(WhiteboardGroup)
admin.site.register(WhiteboardSection)
admin.site.register(Timer)
admin.site.register(WhiteboardComment)
admin.site.register(WhiteboardEmoji)
admin.site.register(WhiteboardTemplate)
