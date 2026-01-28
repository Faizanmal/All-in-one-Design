"""
Commenting Signals
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, Mention, CommentNotification, Reviewer


@receiver(post_save, sender=Comment)
def notify_thread_participants(sender, instance, created, **kwargs):
    """Notify thread participants when a new comment is added."""
    if not created:
        return
    
    thread = instance.thread
    
    # Get all participants except the author
    participants = set()
    
    # Thread creator
    if thread.created_by != instance.author:
        participants.add(thread.created_by)
    
    # Other commenters
    for comment in thread.comments.exclude(author=instance.author):
        participants.add(comment.author)
    
    # Assignee
    if thread.assignee and thread.assignee != instance.author:
        participants.add(thread.assignee)
    
    # Create notifications
    for user in participants:
        CommentNotification.objects.create(
            user=user,
            notification_type='reply',
            thread=thread,
            comment=instance,
            actor=instance.author
        )


@receiver(post_save, sender=Mention)
def notify_mentioned_user(sender, instance, created, **kwargs):
    """Notify user when mentioned."""
    if not created:
        return
    
    if instance.user == instance.comment.author:
        return  # Don't notify self
    
    CommentNotification.objects.create(
        user=instance.user,
        notification_type='mention',
        thread=instance.comment.thread,
        comment=instance.comment,
        actor=instance.comment.author
    )
    
    instance.notified = True
    instance.save()


@receiver(post_save, sender=Reviewer)
def notify_reviewer_added(sender, instance, created, **kwargs):
    """Notify user when added as reviewer."""
    if not created:
        return
    
    CommentNotification.objects.create(
        user=instance.user,
        notification_type='review_request',
        review=instance.session,
        actor=instance.session.created_by
    )
