/**
 * Workflow Automation Engine API Client
 *
 * TypeScript client for the workflow automation REST API.
 */

import api from './api';

// --- Types ---

export interface Workflow {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'paused' | 'disabled';
  graph_data: Record<string, unknown>;
  max_retries: number;
  retry_delay_seconds: number;
  timeout_seconds: number;
  run_as_async: boolean;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  last_run_at: string | null;
  triggers?: WorkflowTrigger[];
  actions?: WorkflowAction[];
  recent_runs?: WorkflowRun[];
  trigger_count?: number;
  action_count?: number;
  created_at: string;
  updated_at: string;
}

export interface WorkflowTrigger {
  id: string;
  workflow?: string;
  trigger_type: string;
  config: Record<string, unknown>;
  cron_expression: string;
  webhook_secret: string;
  is_active: boolean;
  created_at: string;
}

export interface WorkflowAction {
  id: string;
  workflow?: string;
  action_type: string;
  name: string;
  config: Record<string, unknown>;
  position_x: number;
  position_y: number;
  order: number;
  condition_expression: string;
  next_action_on_success: string | null;
  next_action_on_failure: string | null;
  created_at: string;
}

export interface WorkflowRun {
  id: string;
  workflow: string;
  triggered_by: number | null;
  triggered_by_username: string | null;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'timed_out';
  trigger_type: string;
  trigger_data: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  output: Record<string, unknown>;
  error_message: string;
  retry_count: number;
  action_logs?: WorkflowActionLog[];
  created_at: string;
}

export interface WorkflowActionLog {
  id: string;
  action: string;
  action_name: string;
  action_type: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown>;
  error_message: string;
  created_at: string;
}

export interface TriggerTypeInfo {
  name: string;
  description: string;
  icon: string;
  config_schema: Record<string, string>;
}

export interface ActionTypeInfo {
  name: string;
  description: string;
  icon: string;
  category: string;
  config_schema: Record<string, string>;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  trigger: string;
  actions: string[];
  category: string;
}

// --- API functions ---

const BASE = '/api/notifications';

export const workflowApi = {
  // CRUD
  list: () => api.get<Workflow[]>(`${BASE}/workflows/`),
  get: (id: string) => api.get<Workflow>(`${BASE}/workflows/${id}/`),
  create: (data: Partial<Workflow>) => api.post<Workflow>(`${BASE}/workflows/`, data),
  update: (id: string, data: Partial<Workflow>) => api.patch<Workflow>(`${BASE}/workflows/${id}/`, data),
  delete: (id: string) => api.delete(`${BASE}/workflows/${id}/`),

  // Actions
  execute: (id: string, triggerData?: Record<string, unknown>) =>
    api.post<WorkflowRun>(`${BASE}/workflows/${id}/execute/`, { trigger_data: triggerData }),
  duplicate: (id: string) => api.post<Workflow>(`${BASE}/workflows/${id}/duplicate/`),
  validate: (id: string) => api.post(`${BASE}/workflows/${id}/validate/`),
  toggleStatus: (id: string) => api.post<{ status: string }>(`${BASE}/workflows/${id}/toggle_status/`),
  getRuns: (id: string) => api.get<WorkflowRun[]>(`${BASE}/workflows/${id}/runs/`),

  // Triggers
  listTriggers: (workflowId: string) =>
    api.get<WorkflowTrigger[]>(`${BASE}/workflows/${workflowId}/triggers/`),
  createTrigger: (workflowId: string, data: Partial<WorkflowTrigger>) =>
    api.post<WorkflowTrigger>(`${BASE}/workflows/${workflowId}/triggers/`, data),
  updateTrigger: (workflowId: string, triggerId: string, data: Partial<WorkflowTrigger>) =>
    api.patch<WorkflowTrigger>(`${BASE}/workflows/${workflowId}/triggers/${triggerId}/`, data),
  deleteTrigger: (workflowId: string, triggerId: string) =>
    api.delete(`${BASE}/workflows/${workflowId}/triggers/${triggerId}/`),

  // Actions (nodes)
  listActions: (workflowId: string) =>
    api.get<WorkflowAction[]>(`${BASE}/workflows/${workflowId}/actions/`),
  createAction: (workflowId: string, data: Partial<WorkflowAction>) =>
    api.post<WorkflowAction>(`${BASE}/workflows/${workflowId}/actions/`, data),
  updateAction: (workflowId: string, actionId: string, data: Partial<WorkflowAction>) =>
    api.patch<WorkflowAction>(`${BASE}/workflows/${workflowId}/actions/${actionId}/`, data),
  deleteAction: (workflowId: string, actionId: string) =>
    api.delete(`${BASE}/workflows/${workflowId}/actions/${actionId}/`),

  // Metadata
  getTriggerTypes: () => api.get<Record<string, TriggerTypeInfo>>(`${BASE}/workflow-meta/trigger-types/`),
  getActionTypes: () => api.get<Record<string, ActionTypeInfo>>(`${BASE}/workflow-meta/action-types/`),
  getTemplates: () => api.get<WorkflowTemplate[]>(`${BASE}/workflow-meta/templates/`),
  createFromTemplate: (templateId: string) =>
    api.post<Workflow>(`${BASE}/workflow-meta/create-from-template/`, { template_id: templateId }),
};

export default workflowApi;
