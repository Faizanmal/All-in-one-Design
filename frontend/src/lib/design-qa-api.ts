/**
 * Design QA & Linting API Client
 * Production-ready API for Design QA & Linting feature
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/qa`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Types
export type Severity = 'error' | 'warning' | 'info';
export type IssueStatus = 'open' | 'resolved' | 'ignored' | 'wont_fix';
export type WCAGLevel = 'A' | 'AA' | 'AAA';
export type CheckType = 'color_contrast' | 'text_size' | 'touch_target' | 'alt_text' | 'heading_structure' | 
                        'focus_visible' | 'motion_reduction' | 'color_only' | 'link_purpose' | 'language';

export interface LintRule {
  id: string;
  rule_set: string;
  name: string;
  code: string;
  description: string;
  category: string;
  severity: Severity;
  is_enabled: boolean;
  auto_fixable: boolean;
  fix_description: string;
  configuration: Record<string, unknown>;
  documentation_url: string;
  examples: Array<{
    bad: Record<string, unknown>;
    good: Record<string, unknown>;
    description: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface LintRuleSet {
  id: string;
  name: string;
  description: string;
  is_default: boolean;
  is_system: boolean;
  rules: LintRule[];
  extends: string[];
  icon: string;
  color: string;
  usage_count: number;
  created_by: number | null;
  created_at: string;
  updated_at: string;
}

export interface LintIssue {
  id: string;
  report: string;
  rule: string;
  rule_name: string;
  rule_code: string;
  severity: Severity;
  node_id: string;
  node_type: string;
  node_name: string;
  message: string;
  details: Record<string, unknown>;
  suggestion: string;
  auto_fix_data: Record<string, unknown> | null;
  status: IssueStatus;
  resolved_by: number | null;
  resolved_at: string | null;
  ignored_reason: string;
  created_at: string;
}

export interface DesignLintReport {
  id: string;
  project: number;
  name: string;
  rule_set: string;
  rule_set_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  issues: LintIssue[];
  total_issues: number;
  errors: number;
  warnings: number;
  info: number;
  nodes_checked: number;
  duration_ms: number;
  triggered_by: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface LintIgnoreRule {
  id: string;
  project: number;
  rule: string;
  node_id: string | null;
  node_type: string | null;
  reason: string;
  expires_at: string | null;
  created_by: number;
  created_at: string;
}

export interface AccessibilityCheck {
  id: string;
  rule_set: string;
  name: string;
  code: string;
  description: string;
  check_type: CheckType;
  wcag_criterion: string;
  wcag_level: WCAGLevel;
  is_enabled: boolean;
  severity: Severity;
  configuration: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AccessibilityIssue {
  id: string;
  report: string;
  accessibility_check: string;
  check_name: string;
  wcag_criterion: string;
  node_id: string;
  node_type: string;
  node_name: string;
  severity: Severity;
  message: string;
  impact: string;
  affected_users: string;
  remediation: string;
  code_snippet: string;
  is_resolved: boolean;
  resolved_by: number | null;
  resolved_at: string | null;
  created_at: string;
}

export interface AccessibilityReport {
  id: string;
  project: number;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  issues: AccessibilityIssue[];
  overall_score: number;
  level_a_score: number;
  level_aa_score: number;
  level_aaa_score: number;
  total_issues: number;
  critical_issues: number;
  serious_issues: number;
  moderate_issues: number;
  minor_issues: number;
  nodes_checked: number;
  duration_ms: number;
  wcag_level: WCAGLevel;
  triggered_by: number | null;
  triggered_by_name: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface StyleUsageReport {
  id: string;
  project: number;
  total_styles: number;
  used_styles: number;
  unused_styles: number;
  orphaned_styles: number;
  duplicate_styles: Array<{
    original_id: string;
    duplicates: string[];
    style_type: string;
  }>;
  style_usage: Record<string, {
    count: number;
    nodes: string[];
  }>;
  recommendations: string[];
  created_at: string;
}

export interface QASummary {
  project_id: number;
  last_lint_report: string | null;
  last_accessibility_report: string | null;
  total_issues: number;
  open_issues: number;
  lint_score: number;
  accessibility_score: number;
  trend: 'improving' | 'stable' | 'declining';
  recent_activity: Array<{
    type: string;
    description: string;
    timestamp: string;
  }>;
}

// API Functions
export const designQAApi = {
  // Rule Set operations
  async getRuleSets(options?: {
    is_default?: boolean;
    search?: string;
  }): Promise<LintRuleSet[]> {
    const params = new URLSearchParams();
    if (options?.is_default !== undefined) params.append('is_default', String(options.is_default));
    if (options?.search) params.append('search', options.search);
    const { data } = await apiClient.get(`/rule-sets/?${params}`);
    return data.results || data;
  },

  async getRuleSet(ruleSetId: string): Promise<LintRuleSet> {
    const { data } = await apiClient.get(`/rule-sets/${ruleSetId}/`);
    return data;
  },

  async createRuleSet(ruleSet: Partial<LintRuleSet>): Promise<LintRuleSet> {
    const { data } = await apiClient.post('/rule-sets/', ruleSet);
    return data;
  },

  async updateRuleSet(ruleSetId: string, updates: Partial<LintRuleSet>): Promise<LintRuleSet> {
    const { data } = await apiClient.patch(`/rule-sets/${ruleSetId}/`, updates);
    return data;
  },

  async deleteRuleSet(ruleSetId: string): Promise<void> {
    await apiClient.delete(`/rule-sets/${ruleSetId}/`);
  },

  async duplicateRuleSet(ruleSetId: string, name?: string): Promise<LintRuleSet> {
    const { data } = await apiClient.post(`/rule-sets/${ruleSetId}/duplicate/`, { name });
    return data;
  },

  async setDefaultRuleSet(ruleSetId: string): Promise<LintRuleSet> {
    const { data } = await apiClient.post(`/rule-sets/${ruleSetId}/set_default/`);
    return data;
  },

  async exportRuleSet(ruleSetId: string): Promise<{ download_url: string }> {
    const { data } = await apiClient.post(`/rule-sets/${ruleSetId}/export/`);
    return data;
  },

  async importRuleSet(file: File): Promise<LintRuleSet> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await apiClient.post('/rule-sets/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Lint Rule operations
  async getRules(ruleSetId: string, options?: {
    category?: string;
    severity?: Severity;
    is_enabled?: boolean;
  }): Promise<LintRule[]> {
    const params = new URLSearchParams();
    params.append('rule_set', ruleSetId);
    if (options?.category) params.append('category', options.category);
    if (options?.severity) params.append('severity', options.severity);
    if (options?.is_enabled !== undefined) params.append('is_enabled', String(options.is_enabled));
    const { data } = await apiClient.get(`/rules/?${params}`);
    return data.results || data;
  },

  async getRule(ruleId: string): Promise<LintRule> {
    const { data } = await apiClient.get(`/rules/${ruleId}/`);
    return data;
  },

  async createRule(rule: Partial<LintRule>): Promise<LintRule> {
    const { data } = await apiClient.post('/rules/', rule);
    return data;
  },

  async updateRule(ruleId: string, updates: Partial<LintRule>): Promise<LintRule> {
    const { data } = await apiClient.patch(`/rules/${ruleId}/`, updates);
    return data;
  },

  async deleteRule(ruleId: string): Promise<void> {
    await apiClient.delete(`/rules/${ruleId}/`);
  },

  async toggleRule(ruleId: string): Promise<LintRule> {
    const { data } = await apiClient.post(`/rules/${ruleId}/toggle/`);
    return data;
  },

  async bulkToggleRules(ruleIds: string[], enabled: boolean): Promise<void> {
    await apiClient.post('/rules/bulk_toggle/', {
      rule_ids: ruleIds,
      enabled,
    });
  },

  // Lint Report operations
  async getLintReports(projectId: number, options?: {
    status?: string;
    limit?: number;
  }): Promise<DesignLintReport[]> {
    const params = new URLSearchParams();
    params.append('project', String(projectId));
    if (options?.status) params.append('status', options.status);
    if (options?.limit) params.append('limit', String(options.limit));
    const { data } = await apiClient.get(`/lint-reports/?${params}`);
    return data.results || data;
  },

  async getLintReport(reportId: string): Promise<DesignLintReport> {
    const { data } = await apiClient.get(`/lint-reports/${reportId}/`);
    return data;
  },

  async runLintCheck(projectId: number, options?: {
    rule_set?: string;
    node_ids?: string[];
    categories?: string[];
    fix_auto?: boolean;
  }): Promise<DesignLintReport> {
    const { data } = await apiClient.post('/lint-reports/', {
      project: projectId,
      ...options,
    });
    return data;
  },

  async deleteLintReport(reportId: string): Promise<void> {
    await apiClient.delete(`/lint-reports/${reportId}/`);
  },

  async getReportSummary(reportId: string): Promise<{
    by_category: Record<string, number>;
    by_severity: Record<Severity, number>;
    by_rule: Record<string, number>;
    fixable_count: number;
  }> {
    const { data } = await apiClient.get(`/lint-reports/${reportId}/summary/`);
    return data;
  },

  async exportLintReport(reportId: string, format: 'json' | 'csv' | 'pdf'): Promise<{ download_url: string }> {
    const { data } = await apiClient.post(`/lint-reports/${reportId}/export/`, { format });
    return data;
  },

  // Lint Issue operations
  async getLintIssues(reportId: string, options?: {
    status?: IssueStatus;
    severity?: Severity;
    rule?: string;
    node_id?: string;
  }): Promise<LintIssue[]> {
    const params = new URLSearchParams();
    params.append('report', reportId);
    if (options?.status) params.append('status', options.status);
    if (options?.severity) params.append('severity', options.severity);
    if (options?.rule) params.append('rule', options.rule);
    if (options?.node_id) params.append('node_id', options.node_id);
    const { data } = await apiClient.get(`/lint-issues/?${params}`);
    return data.results || data;
  },

  async getLintIssue(issueId: string): Promise<LintIssue> {
    const { data } = await apiClient.get(`/lint-issues/${issueId}/`);
    return data;
  },

  async resolveIssue(issueId: string): Promise<LintIssue> {
    const { data } = await apiClient.post(`/lint-issues/${issueId}/resolve/`);
    return data;
  },

  async ignoreIssue(issueId: string, reason?: string): Promise<LintIssue> {
    const { data } = await apiClient.post(`/lint-issues/${issueId}/ignore/`, { reason });
    return data;
  },

  async reopenIssue(issueId: string): Promise<LintIssue> {
    const { data } = await apiClient.post(`/lint-issues/${issueId}/reopen/`);
    return data;
  },

  async autoFixIssue(issueId: string): Promise<{
    fixed: boolean;
    changes: Record<string, unknown>;
  }> {
    const { data } = await apiClient.post(`/lint-issues/${issueId}/auto_fix/`);
    return data;
  },

  async bulkResolveIssues(issueIds: string[]): Promise<{ resolved_count: number }> {
    const { data } = await apiClient.post('/lint-issues/bulk_resolve/', { issue_ids: issueIds });
    return data;
  },

  async bulkIgnoreIssues(issueIds: string[], reason?: string): Promise<{ ignored_count: number }> {
    const { data } = await apiClient.post('/lint-issues/bulk_ignore/', {
      issue_ids: issueIds,
      reason,
    });
    return data;
  },

  async bulkAutoFix(issueIds: string[]): Promise<{
    fixed_count: number;
    failed_count: number;
    changes: Array<{
      issue_id: string;
      fixed: boolean;
      changes?: Record<string, unknown>;
      error?: string;
    }>;
  }> {
    const { data } = await apiClient.post('/lint-issues/bulk_auto_fix/', { issue_ids: issueIds });
    return data;
  },

  // Ignore Rule operations
  async getIgnoreRules(projectId: number): Promise<LintIgnoreRule[]> {
    const { data } = await apiClient.get(`/ignore-rules/?project=${projectId}`);
    return data.results || data;
  },

  async createIgnoreRule(ignoreRule: Partial<LintIgnoreRule>): Promise<LintIgnoreRule> {
    const { data } = await apiClient.post('/ignore-rules/', ignoreRule);
    return data;
  },

  async deleteIgnoreRule(ignoreRuleId: string): Promise<void> {
    await apiClient.delete(`/ignore-rules/${ignoreRuleId}/`);
  },

  // Accessibility Check operations
  async getAccessibilityChecks(ruleSetId?: string): Promise<AccessibilityCheck[]> {
    const params = ruleSetId ? `?rule_set=${ruleSetId}` : '';
    const { data } = await apiClient.get(`/accessibility-checks/${params}`);
    return data.results || data;
  },

  async updateAccessibilityCheck(checkId: string, updates: Partial<AccessibilityCheck>): Promise<AccessibilityCheck> {
    const { data } = await apiClient.patch(`/accessibility-checks/${checkId}/`, updates);
    return data;
  },

  async toggleAccessibilityCheck(checkId: string): Promise<AccessibilityCheck> {
    const { data } = await apiClient.post(`/accessibility-checks/${checkId}/toggle/`);
    return data;
  },

  // Accessibility Report operations
  async getAccessibilityReports(projectId: number, options?: {
    status?: string;
    limit?: number;
  }): Promise<AccessibilityReport[]> {
    const params = new URLSearchParams();
    params.append('project', String(projectId));
    if (options?.status) params.append('status', options.status);
    if (options?.limit) params.append('limit', String(options.limit));
    const { data } = await apiClient.get(`/accessibility-reports/?${params}`);
    return data.results || data;
  },

  async getAccessibilityReport(reportId: string): Promise<AccessibilityReport> {
    const { data } = await apiClient.get(`/accessibility-reports/${reportId}/`);
    return data;
  },

  async runAccessibilityCheck(projectId: number, options?: {
    wcag_level?: WCAGLevel;
    node_ids?: string[];
    check_types?: CheckType[];
  }): Promise<AccessibilityReport> {
    const { data } = await apiClient.post('/accessibility-reports/', {
      project: projectId,
      ...options,
    });
    return data;
  },

  async deleteAccessibilityReport(reportId: string): Promise<void> {
    await apiClient.delete(`/accessibility-reports/${reportId}/`);
  },

  async getAccessibilityReportDetails(reportId: string): Promise<{
    by_wcag_level: Record<WCAGLevel, { passed: number; failed: number }>;
    by_check_type: Record<CheckType, number>;
    affected_users_summary: string;
    compliance_percentage: number;
  }> {
    const { data } = await apiClient.get(`/accessibility-reports/${reportId}/details/`);
    return data;
  },

  async exportAccessibilityReport(reportId: string, format: 'json' | 'csv' | 'pdf' | 'vpat'): Promise<{ download_url: string }> {
    const { data } = await apiClient.post(`/accessibility-reports/${reportId}/export/`, { format });
    return data;
  },

  // Accessibility Issue operations
  async getAccessibilityIssues(reportId: string, options?: {
    severity?: Severity;
    wcag_level?: WCAGLevel;
    check_type?: CheckType;
    is_resolved?: boolean;
  }): Promise<AccessibilityIssue[]> {
    const params = new URLSearchParams();
    params.append('report', reportId);
    if (options?.severity) params.append('severity', options.severity);
    if (options?.wcag_level) params.append('wcag_level', options.wcag_level);
    if (options?.check_type) params.append('check_type', options.check_type);
    if (options?.is_resolved !== undefined) params.append('is_resolved', String(options.is_resolved));
    const { data } = await apiClient.get(`/accessibility-issues/?${params}`);
    return data.results || data;
  },

  async resolveAccessibilityIssue(issueId: string): Promise<AccessibilityIssue> {
    const { data } = await apiClient.post(`/accessibility-issues/${issueId}/resolve/`);
    return data;
  },

  async reopenAccessibilityIssue(issueId: string): Promise<AccessibilityIssue> {
    const { data } = await apiClient.post(`/accessibility-issues/${issueId}/reopen/`);
    return data;
  },

  // Style Usage operations
  async getStyleUsageReports(projectId: number): Promise<StyleUsageReport[]> {
    const { data } = await apiClient.get(`/style-usage/?project=${projectId}`);
    return data.results || data;
  },

  async runStyleUsageAnalysis(projectId: number): Promise<StyleUsageReport> {
    const { data } = await apiClient.post('/style-usage/', { project: projectId });
    return data;
  },

  async cleanupUnusedStyles(reportId: string, styleIds: string[]): Promise<{
    removed_count: number;
    removed_styles: string[];
  }> {
    const { data } = await apiClient.post(`/style-usage/${reportId}/cleanup/`, { style_ids: styleIds });
    return data;
  },

  async mergeDuplicateStyles(reportId: string, duplicateGroup: string[]): Promise<{
    merged_to: string;
    merged_count: number;
  }> {
    const { data } = await apiClient.post(`/style-usage/${reportId}/merge_duplicates/`, {
      style_ids: duplicateGroup,
    });
    return data;
  },

  // Summary and utility
  async getQASummary(projectId: number): Promise<QASummary> {
    const { data } = await apiClient.get(`/summary/${projectId}/`);
    return data;
  },

  async getQADashboard(projectId: number): Promise<{
    lint_trend: Array<{ date: string; issues: number; score: number }>;
    accessibility_trend: Array<{ date: string; score: number }>;
    top_issues: LintIssue[];
    recent_reports: Array<{ id: string; type: 'lint' | 'accessibility'; created_at: string; issues: number }>;
  }> {
    const { data } = await apiClient.get(`/dashboard/${projectId}/`);
    return data;
  },

  async scheduleAutomaticCheck(projectId: number, options: {
    frequency: 'daily' | 'weekly' | 'on_commit';
    check_type: 'lint' | 'accessibility' | 'both';
    notify_on_failure: boolean;
  }): Promise<{ schedule_id: string }> {
    const { data } = await apiClient.post(`/schedule/`, {
      project: projectId,
      ...options,
    });
    return data;
  },
};

export default designQAApi;
