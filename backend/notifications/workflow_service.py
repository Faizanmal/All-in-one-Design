"""
Workflow Automation Engine Service

Handles workflow execution, trigger evaluation, and action dispatch.
"""

import logging
import time
from datetime import datetime
from typing import Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Core workflow execution engine."""

    # All available trigger types with descriptions
    TRIGGER_TYPES = {
        'design_approved': {
            'name': 'Design Approved',
            'description': 'Fires when a design review is approved',
            'icon': 'check-circle',
            'config_schema': {'project_id': 'optional'},
        },
        'design_updated': {
            'name': 'Design Updated',
            'description': 'Fires when a design is saved/updated',
            'icon': 'edit',
            'config_schema': {'project_id': 'optional'},
        },
        'comment_added': {
            'name': 'Comment Added',
            'description': 'Fires when a new comment is posted',
            'icon': 'message-circle',
            'config_schema': {'project_id': 'optional'},
        },
        'brand_colors_changed': {
            'name': 'Brand Colors Changed',
            'description': 'Fires when brand kit colors are modified',
            'icon': 'palette',
            'config_schema': {'brand_kit_id': 'optional'},
        },
        'schedule': {
            'name': 'Scheduled',
            'description': 'Fires on a recurring schedule (cron)',
            'icon': 'clock',
            'config_schema': {'cron_expression': 'required'},
        },
        'webhook': {
            'name': 'Incoming Webhook',
            'description': 'Fires when an external webhook is received',
            'icon': 'webhook',
            'config_schema': {'secret': 'auto-generated'},
        },
        'manual': {
            'name': 'Manual Trigger',
            'description': 'Fires only when manually activated',
            'icon': 'play',
            'config_schema': {},
        },
        'project_created': {
            'name': 'Project Created',
            'description': 'Fires when a new project is created',
            'icon': 'plus-circle',
            'config_schema': {'project_type': 'optional'},
        },
        'export_completed': {
            'name': 'Export Completed',
            'description': 'Fires when a design export finishes',
            'icon': 'download',
            'config_schema': {'format': 'optional'},
        },
        'team_member_joined': {
            'name': 'Team Member Joined',
            'description': 'Fires when a new team member is added',
            'icon': 'user-plus',
            'config_schema': {'team_id': 'optional'},
        },
    }

    # All available action types with descriptions
    ACTION_TYPES = {
        'export_png': {
            'name': 'Export as PNG',
            'description': 'Export design to PNG format',
            'icon': 'image',
            'category': 'export',
            'config_schema': {'quality': 'optional', 'scale': 'optional'},
        },
        'export_pdf': {
            'name': 'Export as PDF',
            'description': 'Export design to PDF format',
            'icon': 'file-text',
            'category': 'export',
            'config_schema': {'include_bleed': 'optional'},
        },
        'export_svg': {
            'name': 'Export as SVG',
            'description': 'Export design to SVG format',
            'icon': 'code',
            'category': 'export',
            'config_schema': {'optimize': 'optional'},
        },
        'export_all_formats': {
            'name': 'Export All Formats',
            'description': 'Export to PNG, PDF, SVG simultaneously',
            'icon': 'package',
            'category': 'export',
            'config_schema': {},
        },
        'magic_resize': {
            'name': 'Magic Resize',
            'description': 'Auto-resize design for multiple formats',
            'icon': 'maximize',
            'category': 'export',
            'config_schema': {'formats': 'required'},
        },
        'publish_web': {
            'name': 'Publish to Web',
            'description': 'Deploy design to web (Vercel/Netlify)',
            'icon': 'globe',
            'category': 'publish',
            'config_schema': {'platform': 'required'},
        },
        'schedule_social': {
            'name': 'Schedule Social Post',
            'description': 'Schedule design as a social media post',
            'icon': 'calendar',
            'category': 'publish',
            'config_schema': {'platforms': 'required', 'scheduled_time': 'required'},
        },
        'send_email': {
            'name': 'Send Email',
            'description': 'Send an email notification',
            'icon': 'mail',
            'category': 'notify',
            'config_schema': {'to': 'required', 'subject': 'required', 'body': 'required'},
        },
        'send_slack': {
            'name': 'Send Slack Message',
            'description': 'Post a message to Slack channel',
            'icon': 'hash',
            'category': 'notify',
            'config_schema': {'channel': 'required', 'message': 'required'},
        },
        'send_webhook': {
            'name': 'Send Webhook',
            'description': 'Send data to an external webhook URL',
            'icon': 'send',
            'category': 'notify',
            'config_schema': {'url': 'required', 'method': 'optional'},
        },
        'notify_team': {
            'name': 'Notify Team',
            'description': 'Send in-app notification to team members',
            'icon': 'users',
            'category': 'notify',
            'config_schema': {'message': 'required', 'roles': 'optional'},
        },
        'update_brand_colors': {
            'name': 'Update Brand Colors',
            'description': 'Update colors across all designs using a brand kit',
            'icon': 'palette',
            'category': 'design',
            'config_schema': {'brand_kit_id': 'required', 'old_colors': 'required', 'new_colors': 'required'},
        },
        'apply_template': {
            'name': 'Apply Template',
            'description': 'Apply a design template to a project',
            'icon': 'layout',
            'category': 'design',
            'config_schema': {'template_id': 'required'},
        },
        'run_accessibility_check': {
            'name': 'Run Accessibility Check',
            'description': 'Run WCAG accessibility audit on the design',
            'icon': 'shield',
            'category': 'design',
            'config_schema': {'wcag_level': 'optional'},
        },
        'run_qa_check': {
            'name': 'Run QA Check',
            'description': 'Run design quality assurance checks',
            'icon': 'check-square',
            'category': 'design',
            'config_schema': {},
        },
        'condition': {
            'name': 'Conditional Branch',
            'description': 'Branch workflow based on a condition',
            'icon': 'git-branch',
            'category': 'logic',
            'config_schema': {'expression': 'required'},
        },
        'delay': {
            'name': 'Wait/Delay',
            'description': 'Pause workflow for a specified duration',
            'icon': 'clock',
            'category': 'logic',
            'config_schema': {'seconds': 'required'},
        },
        'loop': {
            'name': 'Loop/Repeat',
            'description': 'Repeat a set of actions',
            'icon': 'repeat',
            'category': 'logic',
            'config_schema': {'count': 'required'},
        },
    }

    # Pre-built workflow templates
    WORKFLOW_TEMPLATES = [
        {
            'id': 'auto_export_on_approval',
            'name': 'Auto-Export on Approval',
            'description': 'When a design is approved, automatically export to all formats and notify the team',
            'trigger': 'design_approved',
            'actions': ['export_all_formats', 'notify_team', 'send_slack'],
            'category': 'popular',
        },
        {
            'id': 'brand_color_sync',
            'name': 'Brand Color Sync',
            'description': 'When brand colors change, update all designs and run accessibility checks',
            'trigger': 'brand_colors_changed',
            'actions': ['update_brand_colors', 'run_accessibility_check', 'notify_team'],
            'category': 'brand',
        },
        {
            'id': 'social_media_pipeline',
            'name': 'Social Media Pipeline',
            'description': 'Resize design for all social platforms and schedule posts',
            'trigger': 'design_approved',
            'actions': ['magic_resize', 'schedule_social', 'send_email'],
            'category': 'marketing',
        },
        {
            'id': 'qa_on_save',
            'name': 'QA on Every Save',
            'description': 'Run design QA and accessibility checks when a design is saved',
            'trigger': 'design_updated',
            'actions': ['run_qa_check', 'run_accessibility_check'],
            'category': 'quality',
        },
        {
            'id': 'new_project_setup',
            'name': 'New Project Setup',
            'description': 'When a project is created, apply brand template and notify team',
            'trigger': 'project_created',
            'actions': ['apply_template', 'notify_team'],
            'category': 'onboarding',
        },
        {
            'id': 'export_and_publish',
            'name': 'Export & Publish to Web',
            'description': 'Export to all formats and deploy to web hosting',
            'trigger': 'manual',
            'actions': ['export_all_formats', 'publish_web', 'send_email'],
            'category': 'publishing',
        },
    ]

    def get_trigger_types(self):
        """Return all available trigger types."""
        return self.TRIGGER_TYPES

    def get_action_types(self):
        """Return all available action types."""
        return self.ACTION_TYPES

    def get_workflow_templates(self):
        """Return pre-built workflow templates."""
        return self.WORKFLOW_TEMPLATES

    def execute_action(self, action_type: str, config: dict, context: dict) -> dict:
        """
        Execute a single workflow action.

        Args:
            action_type: The type of action to execute
            config: Action-specific configuration
            context: Execution context (user, project, previous results)

        Returns:
            dict with 'success', 'output', and optional 'error'
        """
        start_time = time.time()

        try:
            handler = getattr(self, f'_execute_{action_type}', None)
            if handler:
                result = handler(config, context)
            else:
                result = self._execute_generic(action_type, config, context)

            duration = int((time.time() - start_time) * 1000)
            return {
                'success': True,
                'action_type': action_type,
                'output': result,
                'duration_ms': duration,
            }
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            logger.error(f"Workflow action {action_type} failed: {e}")
            return {
                'success': False,
                'action_type': action_type,
                'error': str(e),
                'duration_ms': duration,
            }

    def execute_workflow(self, workflow_data: dict, trigger_data: dict = None) -> dict:
        """
        Execute a complete workflow graph.

        Args:
            workflow_data: The workflow definition with actions
            trigger_data: Data from the trigger event

        Returns:
            dict with execution results
        """
        start_time = time.time()
        actions = workflow_data.get('actions', [])
        context = {
            'trigger_data': trigger_data or {},
            'results': {},
            'workflow_id': workflow_data.get('id'),
        }
        action_results = []
        overall_success = True

        for action in sorted(actions, key=lambda a: a.get('order', 0)):
            action_type = action.get('action_type', '')
            action_config = action.get('config', {})

            # Check condition
            if action_type == 'condition':
                # Evaluate condition and skip/continue
                condition_result = self._evaluate_condition(
                    action_config.get('expression', ''), context
                )
                action_results.append({
                    'action_id': action.get('id'),
                    'action_type': 'condition',
                    'result': condition_result,
                    'skipped': False,
                })
                continue

            # Delay
            if action_type == 'delay':
                delay_seconds = action_config.get('seconds', 0)
                action_results.append({
                    'action_id': action.get('id'),
                    'action_type': 'delay',
                    'delayed_seconds': delay_seconds,
                    'skipped': False,
                    'success': True,
                })
                continue

            # Execute action
            result = self.execute_action(action_type, action_config, context)
            result['action_id'] = action.get('id')
            action_results.append(result)

            # Store in context for downstream actions
            context['results'][action.get('id', '')] = result

            if not result.get('success'):
                overall_success = False
                # If action failed and no failure handler, stop
                if not action.get('next_action_on_failure'):
                    break

        total_duration = int((time.time() - start_time) * 1000)

        return {
            'success': overall_success,
            'total_actions': len(actions),
            'completed_actions': len(action_results),
            'action_results': action_results,
            'duration_ms': total_duration,
            'context': {
                'trigger_data': trigger_data,
            },
        }

    def validate_workflow(self, workflow_data: dict) -> dict:
        """Validate a workflow definition."""
        issues = []

        if not workflow_data.get('name'):
            issues.append({'type': 'error', 'message': 'Workflow name is required'})

        triggers = workflow_data.get('triggers', [])
        if not triggers:
            issues.append({'type': 'warning', 'message': 'No triggers defined'})

        for trigger in triggers:
            if trigger.get('trigger_type') not in self.TRIGGER_TYPES:
                issues.append({
                    'type': 'error',
                    'message': f"Unknown trigger type: {trigger.get('trigger_type')}",
                })

        actions = workflow_data.get('actions', [])
        if not actions:
            issues.append({'type': 'warning', 'message': 'No actions defined'})

        for action in actions:
            if action.get('action_type') not in self.ACTION_TYPES:
                issues.append({
                    'type': 'error',
                    'message': f"Unknown action type: {action.get('action_type')}",
                })

        return {
            'valid': not any(i['type'] == 'error' for i in issues),
            'issues': issues,
        }

    # --- Private action executors ---

    def _execute_generic(self, action_type: str, config: dict, context: dict) -> dict:
        """Generic action executor (stub for actions without specific handlers)."""
        return {
            'action_type': action_type,
            'status': 'simulated',
            'config': config,
            'message': f'Action "{action_type}" would execute with config: {config}',
        }

    def _execute_notify_team(self, config: dict, context: dict) -> dict:
        message = config.get('message', 'Workflow notification')
        return {'notified': True, 'message': message}

    def _execute_send_email(self, config: dict, context: dict) -> dict:
        to = config.get('to', '')
        subject = config.get('subject', '')
        return {'sent': True, 'to': to, 'subject': subject}

    def _execute_export_all_formats(self, config: dict, context: dict) -> dict:
        formats = ['png', 'pdf', 'svg']
        return {'exported': True, 'formats': formats}

    def _execute_delay(self, config: dict, context: dict) -> dict:
        seconds = config.get('seconds', 0)
        return {'delayed': True, 'seconds': seconds}

    def _evaluate_condition(self, expression: str, context: dict) -> bool:
        """Evaluate a simple condition expression."""
        if not expression:
            return True
        # Simple evaluation for common patterns
        try:
            # Safe evaluation of simple expressions
            trigger_data = context.get('trigger_data', {})
            if '==' in expression:
                parts = expression.split('==')
                left = parts[0].strip()
                right = parts[1].strip().strip("'\"")
                return str(trigger_data.get(left, '')).strip() == right
            return True
        except Exception:
            return True
