from django.contrib import admin
from .models import CommentThread, Comment, ReviewSession, CommentNotification

@admin.register(CommentThread)
class CommentThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'status', 'priority', 'created_by', 'assignee', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['project__name']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'thread', 'comment_type', 'author', 'created_at']
    list_filter = ['comment_type', 'is_internal']
    search_fields = ['content', 'author__username']

@admin.register(ReviewSession)
class ReviewSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'created_by', 'due_date', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'project__name']

@admin.register(CommentNotification)
class CommentNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'read', 'created_at']
    list_filter = ['notification_type', 'read']
