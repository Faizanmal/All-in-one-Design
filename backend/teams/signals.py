from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TeamMembership, Comment, TeamActivity
from notifications.signals import create_notification


@receiver(post_save, sender=TeamMembership)
def team_membership_created(sender, instance, created, **kwargs):
    """Send notification when user is added to team"""
    if created:
        create_notification(
            user=instance.user,
            notification_type='team_invite',
            title='Added to Team',
            message=f'You have been added to {instance.team.name} as {instance.get_role_display()}',
            metadata={
                'team_id': instance.team.id,
                'team_name': instance.team.name,
                'role': instance.role
            }
        )


@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    """Send notifications for comments and mentions"""
    if created:
        # Notify project owner
        if instance.user != instance.project.user:
            create_notification(
                user=instance.project.user,
                notification_type='info',
                title='New Comment',
                message=f'{instance.user.username} commented on your project "{instance.project.name}"',
                metadata={
                    'project_id': instance.project.id,
                    'comment_id': instance.id
                }
            )
        
        # Notify mentioned users
        for mentioned_user in instance.mentions.all():
            if mentioned_user != instance.user:
                create_notification(
                    user=mentioned_user,
                    notification_type='info',
                    title='Mentioned in Comment',
                    message=f'{instance.user.username} mentioned you in a comment',
                    metadata={
                        'project_id': instance.project.id,
                        'comment_id': instance.id
                    }
                )


@receiver(post_delete, sender=TeamMembership)
def team_membership_deleted(sender, instance, **kwargs):
    """Log when member leaves team"""
    TeamActivity.objects.create(
        team=instance.team,
        user=instance.user,
        action='member_left',
        description=f"{instance.user.username} left the team"
    )
