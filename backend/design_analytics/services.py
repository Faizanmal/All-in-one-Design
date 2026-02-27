"""
Design Analytics Services
"""

from typing import Dict, List, Optional
from datetime import timedelta
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone


class AnalyticsService:
    """Main analytics calculation service."""
    
    @staticmethod
    def calculate_adoption_rate(design_system_id: str, project_id: Optional[int] = None) -> Dict:
        """Calculate design system adoption rate."""
        from .models import AdoptionMetric
        
        # Get recent metrics
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        metrics = AdoptionMetric.objects.filter(
            design_system_id=design_system_id,
            period_start__gte=start_date,
            period_end__lte=end_date
        )
        
        if project_id:
            metrics = metrics.filter(project_id=project_id)
        
        if not metrics.exists():
            return {
                'adoption_rate': 0,
                'style_consistency': 0,
                'component_consistency': 0,
                'trend': 'stable'
            }
        
        avg = metrics.aggregate(
            avg_adoption=Avg('adoption_rate'),
            avg_style=Avg('style_consistency'),
            avg_component=Avg('component_consistency')
        )
        
        # Calculate trend
        first_half = metrics.filter(period_start__lt=start_date + timedelta(days=15))
        second_half = metrics.filter(period_start__gte=start_date + timedelta(days=15))
        
        first_avg = first_half.aggregate(Avg('adoption_rate'))['adoption_rate__avg'] or 0
        second_avg = second_half.aggregate(Avg('adoption_rate'))['adoption_rate__avg'] or 0
        
        if second_avg > first_avg * 1.1:
            trend = 'increasing'
        elif second_avg < first_avg * 0.9:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'adoption_rate': round(avg['avg_adoption'] or 0, 2),
            'style_consistency': round(avg['avg_style'] or 0, 2),
            'component_consistency': round(avg['avg_component'] or 0, 2),
            'trend': trend
        }
    
    @staticmethod
    def get_top_components(design_system_id: str, limit: int = 10) -> List[Dict]:
        """Get most used components."""
        from .models import ComponentUsage
        
        components = ComponentUsage.objects.filter(
            design_system_id=design_system_id
        ).order_by('-usage_count')[:limit]
        
        return [
            {
                'component_id': c.component_id,
                'name': c.component_name,
                'type': c.component_type,
                'usage_count': c.usage_count,
                'project_count': c.project_count,
                'override_rate': round(c.override_count / c.usage_count * 100, 1) if c.usage_count > 0 else 0
            }
            for c in components
        ]
    
    @staticmethod
    def get_unused_components(design_system_id: str, days: int = 30) -> List[Dict]:
        """Get components not used recently."""
        from .models import ComponentUsage
        
        cutoff = timezone.now() - timedelta(days=days)
        
        components = ComponentUsage.objects.filter(
            design_system_id=design_system_id
        ).filter(
            models.Q(last_used_at__lt=cutoff) | models.Q(last_used_at__isnull=True)
        ).order_by('last_used_at')
        
        return [
            {
                'component_id': c.component_id,
                'name': c.component_name,
                'last_used': c.last_used_at,
                'usage_count': c.usage_count
            }
            for c in components
        ]
    
    @staticmethod
    def get_style_consistency_report(design_system_id: str) -> Dict:
        """Analyze style consistency."""
        from .models import StyleUsage
        
        styles = StyleUsage.objects.filter(design_system_id=design_system_id)
        
        report = {
            'colors': {'consistent': 0, 'hardcoded': 0, 'total': 0},
            'typography': {'consistent': 0, 'hardcoded': 0, 'total': 0},
            'effects': {'consistent': 0, 'hardcoded': 0, 'total': 0},
        }
        
        for style in styles:
            category = None
            if style.style_type == 'color':
                category = 'colors'
            elif style.style_type == 'typography':
                category = 'typography'
            elif style.style_type in ['effect', 'shadow']:
                category = 'effects'
            
            if category:
                report[category]['consistent'] += style.direct_usage
                report[category]['hardcoded'] += style.hardcoded_usage
                report[category]['total'] += style.direct_usage + style.hardcoded_usage
        
        # Calculate percentages
        for category in report:
            total = report[category]['total']
            if total > 0:
                report[category]['consistency_rate'] = round(
                    report[category]['consistent'] / total * 100, 1
                )
            else:
                report[category]['consistency_rate'] = 100
        
        return report
    
    @staticmethod
    def calculate_health_score(design_system_id: str) -> Dict:
        """Calculate overall design system health."""
        from .models import ComponentUsage, UsageEvent
        
        scores = {
            'adoption': 0,
            'consistency': 0,
            'coverage': 0,
            'freshness': 0,
            'documentation': 0
        }
        
        issues = []
        recommendations = []
        
        # Adoption score - based on usage events
        recent_events = UsageEvent.objects.filter(
            design_system_id=design_system_id,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        if recent_events > 100:
            scores['adoption'] = 100
        elif recent_events > 50:
            scores['adoption'] = 80
        elif recent_events > 20:
            scores['adoption'] = 60
        else:
            scores['adoption'] = max(recent_events * 3, 0)
            if scores['adoption'] < 50:
                issues.append('Low adoption in the past week')
                recommendations.append('Promote design system usage in team meetings')
        
        # Consistency score - based on overrides and hardcoded styles
        components = ComponentUsage.objects.filter(design_system_id=design_system_id)
        total_usage = sum(c.usage_count for c in components)
        total_overrides = sum(c.override_count for c in components)
        
        if total_usage > 0:
            override_rate = total_overrides / total_usage
            scores['consistency'] = max(0, 100 - (override_rate * 200))
            
            if override_rate > 0.3:
                issues.append('High component override rate')
                recommendations.append('Review commonly overridden components for needed variants')
        else:
            scores['consistency'] = 50
        
        # Coverage score - based on component variety
        component_count = components.count()
        if component_count > 50:
            scores['coverage'] = 100
        elif component_count > 30:
            scores['coverage'] = 80
        elif component_count > 15:
            scores['coverage'] = 60
        else:
            scores['coverage'] = max(component_count * 4, 0)
            issues.append('Limited component coverage')
            recommendations.append('Add more common UI components to the system')
        
        # Freshness score — based on ratio of components updated in the last 30 days
        recently_updated = components.filter(
            updated_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        if component_count > 0:
            scores['freshness'] = min(round((recently_updated / component_count) * 100), 100)
        else:
            scores['freshness'] = 0

        # Documentation score — based on components that have a non-empty description
        documented = components.exclude(description='').exclude(description__isnull=True).count()
        if component_count > 0:
            scores['documentation'] = min(round((documented / component_count) * 100), 100)
        else:
            scores['documentation'] = 0
        
        # Calculate overall
        overall = sum(scores.values()) / len(scores)
        
        return {
            'overall_score': round(overall, 1),
            'scores': {k: round(v, 1) for k, v in scores.items()},
            'issues': issues,
            'recommendations': recommendations
        }
    
    @staticmethod
    def get_usage_timeline(design_system_id: str, days: int = 30, group_by: str = 'day') -> List[Dict]:
        """Get usage timeline data."""
        from .models import UsageEvent
        
        start_date = timezone.now() - timedelta(days=days)
        
        events = UsageEvent.objects.filter(
            design_system_id=design_system_id,
            created_at__gte=start_date
        )
        
        if group_by == 'week':
            events = events.annotate(period=TruncWeek('created_at'))
        elif group_by == 'month':
            events = events.annotate(period=TruncMonth('created_at'))
        else:
            events = events.annotate(period=TruncDate('created_at'))
        
        timeline = events.values('period').annotate(
            count=Count('id'),
            inserts=Count('id', filter=models.Q(event_type='insert')),
            detaches=Count('id', filter=models.Q(event_type='detach'))
        ).order_by('period')
        
        return list(timeline)


class ComplianceChecker:
    """Check design compliance."""
    
    @staticmethod
    def check_project_compliance(project_id: int, design_system_id: str) -> Dict:
        """Check a project's compliance with design system."""
        from .models import StyleUsage

        issues: list = []
        suggestions: list = []

        # Count style usages that are detached (not linked to system)
        total_usages = StyleUsage.objects.filter(
            project_id=project_id,
            design_system_id=design_system_id,
        ).count()

        detached = StyleUsage.objects.filter(
            project_id=project_id,
            design_system_id=design_system_id,
            is_detached=True,
        ).count()

        hardcoded_colors = StyleUsage.objects.filter(
            project_id=project_id,
            design_system_id=design_system_id,
            style_type='color',
            is_detached=True,
        ).count()

        if hardcoded_colors > 0:
            issues.append({'type': 'hardcoded_color', 'count': hardcoded_colors, 'severity': 'warning'})
            suggestions.append(f'Replace {hardcoded_colors} hardcoded colors with style references')

        if detached > 0:
            issues.append({'type': 'detached_component', 'count': detached, 'severity': 'info'})
            suggestions.append(f'Consider reattaching {detached} detached components')

        # Compliance = % of usages that are NOT detached
        if total_usages > 0:
            score = round(((total_usages - detached) / total_usages) * 100)
        else:
            score = 100  # No usages → fully compliant by default

        return {
            'compliance_score': score,
            'total_usages': total_usages,
            'issues': issues,
            'suggestions': suggestions,
        }
    
    @staticmethod
    def find_style_violations(project_id: int, design_system_id: str) -> List[Dict]:
        """Find elements not using design system styles."""
        # In production, this would analyze project elements
        return []


# Import models at module level for type hints
from django.db import models
