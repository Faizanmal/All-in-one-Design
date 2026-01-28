from django.contrib import admin
from .models import (
    LintRuleSet, LintRule, DesignLintReport, LintIssue,
    AccessibilityCheck, AccessibilityReport, AccessibilityIssue,
    StyleUsageReport, LintIgnoreRule
)

# Register models with basic admin
admin.site.register(LintRuleSet)
admin.site.register(LintRule)
admin.site.register(DesignLintReport)
admin.site.register(LintIssue)
admin.site.register(AccessibilityCheck)
admin.site.register(AccessibilityReport)
admin.site.register(AccessibilityIssue)
admin.site.register(StyleUsageReport)
admin.site.register(LintIgnoreRule)
