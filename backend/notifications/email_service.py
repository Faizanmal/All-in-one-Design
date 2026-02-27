"""
Email Service
Comprehensive email notification system with templates and delivery tracking
"""
import logging
from typing import List, Dict, Optional
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from celery import shared_task

logger = logging.getLogger(__name__)


class EmailTemplate:
    """Email template definitions"""
    
    # Team/Collaboration Templates
    TEAM_INVITATION = 'team_invitation'
    TEAM_MEMBER_JOINED = 'team_member_joined'
    TEAM_MEMBER_LEFT = 'team_member_left'
    
    # Project Templates
    PROJECT_SHARED = 'project_shared'
    PROJECT_COMMENT = 'project_comment'
    PROJECT_MENTION = 'project_mention'
    
    # Review Templates
    REVIEW_SESSION_INVITE = 'review_session_invite'
    REVIEW_FEEDBACK_ADDED = 'review_feedback_added'
    REVIEW_APPROVED = 'review_approved'
    
    # Subscription Templates
    SUBSCRIPTION_WELCOME = 'subscription_welcome'
    SUBSCRIPTION_UPGRADED = 'subscription_upgraded'
    SUBSCRIPTION_CANCELLED = 'subscription_cancelled'
    PAYMENT_SUCCEEDED = 'payment_succeeded'
    PAYMENT_FAILED = 'payment_failed'
    TRIAL_ENDING = 'trial_ending'
    
    # Export Templates
    EXPORT_READY = 'export_ready'
    EXPORT_FAILED = 'export_failed'
    
    # AI Templates
    AI_GENERATION_COMPLETE = 'ai_generation_complete'
    
    # System Templates
    PASSWORD_RESET = 'password_reset'
    EMAIL_VERIFICATION = 'email_verification'
    SECURITY_ALERT = 'security_alert'


EMAIL_SUBJECTS = {
    EmailTemplate.TEAM_INVITATION: "You've been invited to join {team_name}",
    EmailTemplate.TEAM_MEMBER_JOINED: "{username} joined your team",
    EmailTemplate.TEAM_MEMBER_LEFT: "{username} left your team",
    EmailTemplate.PROJECT_SHARED: "{username} shared a project with you",
    EmailTemplate.PROJECT_COMMENT: "New comment on {project_name}",
    EmailTemplate.PROJECT_MENTION: "{username} mentioned you in {project_name}",
    EmailTemplate.REVIEW_SESSION_INVITE: "You're invited to review {project_name}",
    EmailTemplate.REVIEW_FEEDBACK_ADDED: "New feedback on {project_name}",
    EmailTemplate.REVIEW_APPROVED: "{project_name} has been approved",
    EmailTemplate.SUBSCRIPTION_WELCOME: "Welcome to {tier_name}!",
    EmailTemplate.SUBSCRIPTION_UPGRADED: "Your subscription has been upgraded",
    EmailTemplate.SUBSCRIPTION_CANCELLED: "Your subscription has been cancelled",
    EmailTemplate.PAYMENT_SUCCEEDED: "Payment received - Thank you!",
    EmailTemplate.PAYMENT_FAILED: "Payment failed - Action required",
    EmailTemplate.TRIAL_ENDING: "Your trial ends in {days} days",
    EmailTemplate.EXPORT_READY: "Your export is ready for download",
    EmailTemplate.EXPORT_FAILED: "Export failed - {error_message}",
    EmailTemplate.AI_GENERATION_COMPLETE: "Your AI design is ready!",
    EmailTemplate.PASSWORD_RESET: "Reset your password",
    EmailTemplate.EMAIL_VERIFICATION: "Verify your email address",
    EmailTemplate.SECURITY_ALERT: "Security alert for your account",
}


class EmailService:
    """Email delivery service"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@aidesign.io')
        self.app_name = getattr(settings, 'APP_NAME', 'AI Design Tool')
        self.app_url = getattr(settings, 'FRONTEND_URL', 'https://aidesign.io')
    
    def send_email(
        self,
        to_emails: List[str],
        template: str,
        context: Dict,
        attachments: Optional[List] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email using the specified template
        
        Args:
            to_emails: List of recipient email addresses
            template: Template name from EmailTemplate
            context: Context data for the template
            attachments: Optional list of attachments
            cc: Optional CC recipients
            bcc: Optional BCC recipients
            
        Returns:
            True if email was sent successfully
        """
        try:
            # Add common context
            context.update({
                'app_name': self.app_name,
                'app_url': self.app_url,
                'current_year': '2026',
            })
            
            # Get subject
            subject_template = EMAIL_SUBJECTS.get(template, "Notification from {app_name}")
            subject = subject_template.format(**context, app_name=self.app_name)
            
            # Render templates
            html_content = self._render_template(template, context)
            text_content = strip_tags(html_content)
            
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=to_emails,
                cc=cc,
                bcc=bcc
            )
            email.attach_alternative(html_content, 'text/html')
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    email.attach(
                        attachment['filename'],
                        attachment['content'],
                        attachment.get('content_type', 'application/octet-stream')
                    )
            
            # Send
            email.send(fail_silently=False)
            
            logger.info(f"Email sent: {template} to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email {template} to {to_emails}: {str(e)}")
            return False
    
    def _render_template(self, template: str, context: Dict) -> str:
        """Render email template with context"""
        try:
            return render_to_string(f'emails/{template}.html', context)
        except Exception:
            # Fallback to basic template
            return self._generate_basic_template(template, context)
    
    def _generate_basic_template(self, template: str, context: Dict) -> str:
        """Generate a basic HTML email template"""
        app_name = context.get('app_name', 'AI Design Tool')
        app_url = context.get('app_url', '#')
        
        # Get template-specific content
        content = self._get_template_content(template, context)
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{app_name}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 8px;
                    padding: 40px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #0066FF;
                }}
                .button {{
                    display: inline-block;
                    background: #0066FF;
                    color: white !important;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background: #0052CC;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎨 {app_name}</div>
                </div>
                
                {content}
                
                <div class="footer">
                    <p>© 2026 {app_name}. All rights reserved.</p>
                    <p>
                        <a href="{app_url}">Visit Website</a> |
                        <a href="{app_url}/settings/notifications">Manage Notifications</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        '''
    
    def _get_template_content(self, template: str, context: Dict) -> str:
        """Get content for specific template type"""
        
        if template == EmailTemplate.TEAM_INVITATION:
            return f'''
            <h2>You're Invited!</h2>
            <p>Hi there,</p>
            <p><strong>{context.get('invited_by', 'A team member')}</strong> has invited you to join 
            <strong>{context.get('team_name', 'their team')}</strong> on {context.get('app_name')}.</p>
            <p style="text-align: center;">
                <a href="{context.get('invite_url', '#')}" class="button">Accept Invitation</a>
            </p>
            <p>This invitation will expire in 7 days.</p>
            '''
        
        elif template == EmailTemplate.PROJECT_SHARED:
            return f'''
            <h2>A Project Was Shared With You</h2>
            <p>{context.get('username', 'Someone')} shared a project with you:</p>
            <p style="font-size: 18px; font-weight: bold;">{context.get('project_name', 'Untitled Project')}</p>
            <p style="text-align: center;">
                <a href="{context.get('project_url', '#')}" class="button">View Project</a>
            </p>
            '''
        
        elif template == EmailTemplate.PROJECT_COMMENT:
            return f'''
            <h2>New Comment</h2>
            <p><strong>{context.get('username', 'Someone')}</strong> commented on 
            <strong>{context.get('project_name', 'your project')}</strong>:</p>
            <blockquote style="border-left: 3px solid #0066FF; padding-left: 15px; color: #666;">
                {context.get('comment_text', '')}
            </blockquote>
            <p style="text-align: center;">
                <a href="{context.get('project_url', '#')}" class="button">View Comment</a>
            </p>
            '''
        
        elif template == EmailTemplate.PROJECT_MENTION:
            return f'''
            <h2>You Were Mentioned</h2>
            <p><strong>{context.get('username', 'Someone')}</strong> mentioned you in a comment on 
            <strong>{context.get('project_name', 'a project')}</strong>:</p>
            <blockquote style="border-left: 3px solid #0066FF; padding-left: 15px; color: #666;">
                {context.get('comment_text', '')}
            </blockquote>
            <p style="text-align: center;">
                <a href="{context.get('project_url', '#')}" class="button">View Comment</a>
            </p>
            '''
        
        elif template == EmailTemplate.REVIEW_SESSION_INVITE:
            return f'''
            <h2>Design Review Invitation</h2>
            <p>You've been invited to review:</p>
            <p style="font-size: 18px; font-weight: bold;">{context.get('project_name', 'Design')}</p>
            <p>Invited by: {context.get('invited_by', 'A team member')}</p>
            <p>Deadline: {context.get('deadline', 'No deadline specified')}</p>
            <p style="text-align: center;">
                <a href="{context.get('review_url', '#')}" class="button">Start Review</a>
            </p>
            '''
        
        elif template == EmailTemplate.PAYMENT_FAILED:
            return f'''
            <h2>Payment Failed</h2>
            <p>We couldn't process your payment for your {context.get('tier_name', 'subscription')}.</p>
            <p>Please update your payment method to continue enjoying our services.</p>
            <p style="text-align: center;">
                <a href="{context.get('billing_url', '#')}" class="button">Update Payment Method</a>
            </p>
            <p style="color: #666;">If you have any questions, please contact our support team.</p>
            '''
        
        elif template == EmailTemplate.PAYMENT_SUCCEEDED:
            return f'''
            <h2>Payment Received</h2>
            <p>Thank you for your payment!</p>
            <p>Amount: <strong>${context.get('amount', '0.00')}</strong></p>
            <p>Plan: <strong>{context.get('tier_name', 'Subscription')}</strong></p>
            <p>Next billing date: {context.get('next_billing_date', 'N/A')}</p>
            <p style="text-align: center;">
                <a href="{context.get('billing_url', '#')}" class="button">View Invoice</a>
            </p>
            '''
        
        elif template == EmailTemplate.SUBSCRIPTION_WELCOME:
            return f'''
            <h2>Welcome to {context.get('tier_name', 'Your New Plan')}!</h2>
            <p>Thank you for upgrading your account.</p>
            <p>You now have access to:</p>
            <ul>
                {''.join(f'<li>{feature}</li>' for feature in context.get('features', ['Premium features']))}
            </ul>
            <p style="text-align: center;">
                <a href="{context.get('app_url', '#')}" class="button">Start Creating</a>
            </p>
            '''
        
        elif template == EmailTemplate.EXPORT_READY:
            return f'''
            <h2>Your Export is Ready!</h2>
            <p>Your export for <strong>{context.get('project_name', 'your project')}</strong> is ready to download.</p>
            <p>Format: {context.get('format', 'PNG')}</p>
            <p style="text-align: center;">
                <a href="{context.get('download_url', '#')}" class="button">Download Now</a>
            </p>
            <p style="color: #666; font-size: 12px;">This download link will expire in 24 hours.</p>
            '''
        
        elif template == EmailTemplate.AI_GENERATION_COMPLETE:
            return f'''
            <h2>Your AI Design is Ready!</h2>
            <p>Great news! Your AI-generated design is complete.</p>
            <p>Prompt: <em>"{context.get('prompt', 'Your design')}"</em></p>
            <p style="text-align: center;">
                <a href="{context.get('project_url', '#')}" class="button">View Design</a>
            </p>
            '''
        
        elif template == EmailTemplate.TRIAL_ENDING:
            return f'''
            <h2>Your Trial is Ending Soon</h2>
            <p>Your free trial ends in <strong>{context.get('days', '3')} days</strong>.</p>
            <p>Upgrade now to keep access to all features:</p>
            <ul>
                <li>Unlimited AI generations</li>
                <li>Advanced export options</li>
                <li>Team collaboration</li>
                <li>Priority support</li>
            </ul>
            <p style="text-align: center;">
                <a href="{context.get('upgrade_url', '#')}" class="button">Upgrade Now</a>
            </p>
            '''
        
        else:
            # Generic notification
            return f'''
            <h2>{context.get('title', 'Notification')}</h2>
            <p>{context.get('message', 'You have a new notification.')}</p>
            <p style="text-align: center;">
                <a href="{context.get('action_url', context.get('app_url', '#'))}" class="button">
                    {context.get('action_text', 'View Details')}
                </a>
            </p>
            '''


# Singleton instance
email_service = EmailService()


# Celery tasks for async email sending
@shared_task(bind=True, max_retries=3)
def send_email_async(self, to_emails: List[str], template: str, context: Dict):
    """Send email asynchronously via Celery"""
    try:
        success = email_service.send_email(to_emails, template, context)
        if not success:
            raise Exception("Email sending failed")
        return {'status': 'sent', 'to': to_emails, 'template': template}
    except Exception as e:
        logger.error(f"Email task failed: {e}")
        self.retry(countdown=60 * (self.request.retries + 1))


@shared_task
def send_team_invitation_email(invitation_id: int):
    """Send team invitation email"""
    from teams.models import TeamInvitation
    
    try:
        invitation = TeamInvitation.objects.select_related('team', 'invited_by').get(id=invitation_id)
        
        context = {
            'team_name': invitation.team.name,
            'invited_by': invitation.invited_by.get_full_name() or invitation.invited_by.username,
            'invite_url': f"{email_service.app_url}/teams/invite/{invitation.token}",
        }
        
        return email_service.send_email(
            to_emails=[invitation.email],
            template=EmailTemplate.TEAM_INVITATION,
            context=context
        )
    except TeamInvitation.DoesNotExist:
        logger.error(f"Team invitation {invitation_id} not found")
        return False


@shared_task
def send_project_shared_email(user_id: int, project_id: int, shared_by_id: int):
    """Send project shared notification email"""
    from django.contrib.auth.models import User
    from projects.models import Project
    
    try:
        user = User.objects.get(id=user_id)
        project = Project.objects.get(id=project_id)
        shared_by = User.objects.get(id=shared_by_id)
        
        context = {
            'username': shared_by.get_full_name() or shared_by.username,
            'project_name': project.name,
            'project_url': f"{email_service.app_url}/projects/{project.id}",
        }
        
        return email_service.send_email(
            to_emails=[user.email],
            template=EmailTemplate.PROJECT_SHARED,
            context=context
        )
    except Exception as e:
        logger.error(f"Failed to send project shared email: {e}")
        return False


@shared_task
def send_comment_notification_email(comment_id: int):
    """Send comment notification email"""
    from teams.models import Comment
    
    try:
        comment = Comment.objects.select_related('user', 'project', 'project__user').get(id=comment_id)
        
        # Don't notify the comment author
        if comment.project.user.id == comment.user.id:
            return True
        
        context = {
            'username': comment.user.get_full_name() or comment.user.username,
            'project_name': comment.project.name,
            'comment_text': comment.content[:200],
            'project_url': f"{email_service.app_url}/projects/{comment.project.id}#comment-{comment.id}",
        }
        
        return email_service.send_email(
            to_emails=[comment.project.user.email],
            template=EmailTemplate.PROJECT_COMMENT,
            context=context
        )
    except Exception as e:
        logger.error(f"Failed to send comment notification email: {e}")
        return False


@shared_task
def send_mention_notification_email(mentioned_user_id: int, comment_id: int):
    """Send mention notification email"""
    from django.contrib.auth.models import User
    from teams.models import Comment
    
    try:
        user = User.objects.get(id=mentioned_user_id)
        comment = Comment.objects.select_related('user', 'project').get(id=comment_id)
        
        context = {
            'username': comment.user.get_full_name() or comment.user.username,
            'project_name': comment.project.name,
            'comment_text': comment.content[:200],
            'project_url': f"{email_service.app_url}/projects/{comment.project.id}#comment-{comment.id}",
        }
        
        return email_service.send_email(
            to_emails=[user.email],
            template=EmailTemplate.PROJECT_MENTION,
            context=context
        )
    except Exception as e:
        logger.error(f"Failed to send mention notification email: {e}")
        return False


@shared_task
def send_review_session_invite_email(session_id: int, participant_email: str):
    """Send review session invitation email"""
    from projects.enhanced_collaboration_models import DesignReviewSession
    
    try:
        session = DesignReviewSession.objects.select_related('project', 'created_by').get(id=session_id)
        
        context = {
            'project_name': session.project.name,
            'invited_by': session.created_by.get_full_name() or session.created_by.username,
            'deadline': session.deadline.strftime('%B %d, %Y') if session.deadline else 'No deadline',
            'review_url': f"{email_service.app_url}/reviews/{session.id}",
        }
        
        return email_service.send_email(
            to_emails=[participant_email],
            template=EmailTemplate.REVIEW_SESSION_INVITE,
            context=context
        )
    except Exception as e:
        logger.error(f"Failed to send review session invite email: {e}")
        return False


@shared_task
def send_payment_failed_email(subscription_id: int):
    """Send payment failed notification email"""
    from subscriptions.models import Subscription
    
    try:
        subscription = Subscription.objects.select_related('user', 'tier').get(id=subscription_id)
        
        context = {
            'tier_name': subscription.tier.name,
            'billing_url': f"{email_service.app_url}/settings/billing",
        }
        
        return email_service.send_email(
            to_emails=[subscription.user.email],
            template=EmailTemplate.PAYMENT_FAILED,
            context=context
        )
    except Exception as e:
        logger.error(f"Failed to send payment failed email: {e}")
        return False


@shared_task
def send_payment_succeeded_email(subscription_id: int, amount: float):
    """Send payment succeeded notification email"""
    from subscriptions.models import Subscription
    
    try:
        subscription = Subscription.objects.select_related('user', 'tier').get(id=subscription_id)
        
        context = {
            'tier_name': subscription.tier.name,
            'amount': f"{amount:.2f}",
            'next_billing_date': subscription.next_billing_date.strftime('%B %d, %Y') if subscription.next_billing_date else 'N/A',
            'billing_url': f"{email_service.app_url}/settings/billing",
        }
        
        return email_service.send_email(
            to_emails=[subscription.user.email],
            template=EmailTemplate.PAYMENT_SUCCEEDED,
            context=context
        )
    except Exception as e:
        logger.error(f"Failed to send payment succeeded email: {e}")
        return False


@shared_task
def send_export_ready_email(user_id: int, project_name: str, format: str, download_url: str):
    """Send export ready notification email"""
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        context = {
            'project_name': project_name,
            'format': format.upper(),
            'download_url': download_url,
        }
        
        return email_service.send_email(
            to_emails=[user.email],
            template=EmailTemplate.EXPORT_READY,
            context=context
        )
    except Exception as e:
        logger.error(f"Failed to send export ready email: {e}")
        return False


@shared_task
def send_ai_generation_complete_email(user_id: int, prompt: str, project_url: str):
    """Send AI generation complete notification email"""
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        context = {
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'project_url': project_url,
        }
        
        return email_service.send_email(
            to_emails=[user.email],
            template=EmailTemplate.AI_GENERATION_COMPLETE,
            context=context
        )
    except Exception as e:
        logger.error(f"Failed to send AI generation complete email: {e}")
        return False


@shared_task
def send_trial_ending_emails():
    """Send trial ending reminder emails (run daily)"""
    from subscriptions.models import Subscription
    from django.utils import timezone
    from datetime import timedelta
    
    # Find subscriptions with trial ending in 3 days
    trial_end_date = timezone.now() + timedelta(days=3)
    trial_start = trial_end_date - timedelta(hours=24)
    
    subscriptions = Subscription.objects.filter(
        status='trial',
        trial_end_date__range=(trial_start, trial_end_date)
    ).select_related('user')
    
    sent_count = 0
    for subscription in subscriptions:
        days_remaining = (subscription.trial_end_date - timezone.now()).days
        
        context = {
            'days': days_remaining,
            'upgrade_url': f"{email_service.app_url}/pricing",
        }
        
        if email_service.send_email(
            to_emails=[subscription.user.email],
            template=EmailTemplate.TRIAL_ENDING,
            context=context
        ):
            sent_count += 1
    
    logger.info(f"Sent {sent_count} trial ending reminder emails")
    return sent_count
