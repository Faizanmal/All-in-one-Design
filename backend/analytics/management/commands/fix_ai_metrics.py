"""
Management command to fix AIUsageMetrics integrity issues
"""
from django.core.management.base import BaseCommand
from django.db import models
from ai_services.models import AIGenerationRequest
from analytics.models import AIUsageMetrics


class Command(BaseCommand):
    help = 'Fix AIUsageMetrics integrity issues'

    def handle(self, *args, **options):
        # Find completed requests with null tokens_used
        null_tokens_requests = AIGenerationRequest.objects.filter(
            tokens_used__isnull=True,
            status='completed'
        )

        self.stdout.write(f'Found {null_tokens_requests.count()} requests with null tokens_used')

        for request in null_tokens_requests:
            # Set default tokens_used
            request.tokens_used = 0
            request.save()
            self.stdout.write(f'Fixed request {request.id}')

        # Find any duplicate AIUsageMetrics
        duplicates = AIUsageMetrics.objects.values('generation_request').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)

        for dup in duplicates:
            # Keep the first one, delete others
            metrics = AIUsageMetrics.objects.filter(generation_request=dup['generation_request'])
            to_delete = metrics[1:]
            for metric in to_delete:
                metric.delete()
                self.stdout.write(f'Deleted duplicate metric {metric.id}')

        self.stdout.write('Fix completed')