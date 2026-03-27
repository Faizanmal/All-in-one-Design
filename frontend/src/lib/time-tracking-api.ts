// API service for time tracking
import api from './api';

// Time Tracker Types
export interface TimeTracker {
  id: number;
  user: {
    id: number;
    username: string;
    avatar?: string;
  };
  project?: {
    id: number;
    name: string;
  };
  task?: {
    id: number;
    title: string;
  };
  description: string;
  start_time: string;
  end_time?: string;
  duration?: number;
  is_running: boolean;
  is_billable: boolean;
  hourly_rate?: number;
  created_at: string;
}

// Time Entry Types
export interface TimeEntry {
  id: number;
  user: {
    id: number;
    username: string;
    avatar?: string;
  };
  project: {
    id: number;
    name: string;
    color?: string;
  };
  task?: {
    id: number;
    title: string;
  };
  description: string;
  date: string;
  start_time: string;
  end_time: string;
  duration: number;
  is_billable: boolean;
  hourly_rate?: number;
  amount?: number;
  tags: string[];
  created_at: string;
  updated_at: string;
}

// Task Types for Time Tracking
export interface TimeTask {
  id: number;
  title: string;
  description?: string;
  project: number;
  status: 'todo' | 'in_progress' | 'review' | 'done';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  estimated_hours?: number;
  logged_hours: number;
  due_date?: string;
  assigned_to?: {
    id: number;
    username: string;
    avatar?: string;
  };
  created_by: {
    id: number;
    username: string;
  };
  created_at: string;
  updated_at: string;
}

// Project Estimate Types
export interface ProjectEstimate {
  id: number;
  project: {
    id: number;
    name: string;
  };
  name: string;
  description?: string;
  estimated_hours: number;
  logged_hours: number;
  remaining_hours: number;
  progress_percentage: number;
  tasks: TimeTask[];
  created_at: string;
  updated_at: string;
}

// Invoice Types
export interface Invoice {
  id: number;
  invoice_number: string;
  client: {
    id: number;
    name: string;
    email: string;
  };
  project?: {
    id: number;
    name: string;
  };
  status: 'draft' | 'sent' | 'viewed' | 'paid' | 'overdue' | 'cancelled';
  issue_date: string;
  due_date: string;
  subtotal: number;
  tax_rate?: number;
  tax_amount?: number;
  total: number;
  currency: string;
  line_items: InvoiceLineItem[];
  notes?: string;
  pdf_url?: string;
  created_at: string;
  paid_at?: string;
}

// Invoice Line Item Types
export interface InvoiceLineItem {
  id: number;
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
  time_entries?: number[];
}

// Time Report Types
export interface TimeReport {
  id: number;
  name: string;
  report_type: 'summary' | 'detailed' | 'project' | 'user' | 'client';
  date_range: {
    start: string;
    end: string;
  };
  filters: {
    projects?: number[];
    users?: number[];
    clients?: number[];
    billable_only?: boolean;
  };
  data: TimeReportData;
  created_at: string;
}

// Time Report Data Types
export interface TimeReportData {
  total_hours: number;
  billable_hours: number;
  non_billable_hours: number;
  total_amount: number;
  by_project?: { project: string; hours: number; amount: number }[];
  by_user?: { user: string; hours: number; amount: number }[];
  by_date?: { date: string; hours: number }[];
  entries?: TimeEntry[];
}

// Weekly Goal Types
export interface WeeklyGoal {
  id: number;
  user: number;
  week_start: string;
  target_hours: number;
  logged_hours: number;
  progress_percentage: number;
  is_achieved: boolean;
}

// Dashboard Summary Types
export interface TimeDashboard {
  today: {
    hours: number;
    entries_count: number;
    active_tracker?: TimeTracker;
  };
  this_week: {
    hours: number;
    billable_hours: number;
    goal?: WeeklyGoal;
  };
  this_month: {
    hours: number;
    billable_hours: number;
    amount: number;
  };
  recent_entries: TimeEntry[];
  active_projects: { project: string; hours: number }[];
}

// Time Trackers API
export const timeTrackersApi = {
  list: () =>
    api.get<TimeTracker[]>('/v1/time-tracking/trackers/'),

  getCurrent: () =>
    api.get<TimeTracker | null>('/v1/time-tracking/trackers/current/'),

  start: (data: {
    project?: number;
    task?: number;
    description?: string;
    is_billable?: boolean;
  }) =>
    api.post<TimeTracker>('/v1/time-tracking/trackers/start/', data),

  stop: (trackerId: number) =>
    api.post<TimeEntry>(`/v1/time-tracking/trackers/${trackerId}/stop/`),

  update: (trackerId: number, data: Partial<TimeTracker>) =>
    api.patch<TimeTracker>(`/v1/time-tracking/trackers/${trackerId}/`, data),

  discard: (trackerId: number) =>
    api.delete(`/v1/time-tracking/trackers/${trackerId}/`),
};

// Time Entries API
export const timeEntriesApi = {
  list: (params?: {
    project?: number;
    user?: number;
    date_from?: string;
    date_to?: string;
    is_billable?: boolean;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) =>
    api.get<{ results: TimeEntry[]; count: number }>(
      '/v1/time-tracking/entries/',
      { params }
    ),

  get: (entryId: number) =>
    api.get<TimeEntry>(`/v1/time-tracking/entries/${entryId}/`),

  create: (data: {
    project: number;
    task?: number;
    description: string;
    date: string;
    start_time: string;
    end_time: string;
    is_billable?: boolean;
    tags?: string[];
  }) =>
    api.post<TimeEntry>('/v1/time-tracking/entries/', data),

  update: (entryId: number, data: Partial<TimeEntry>) =>
    api.patch<TimeEntry>(`/v1/time-tracking/entries/${entryId}/`, data),

  delete: (entryId: number) =>
    api.delete(`/v1/time-tracking/entries/${entryId}/`),

  bulkCreate: (entries: Omit<TimeEntry, 'id' | 'created_at' | 'updated_at' | 'user'>[]) =>
    api.post<TimeEntry[]>('/v1/time-tracking/entries/bulk/', entries),

  getSummary: (params: { date_from: string; date_to: string; group_by?: string }) =>
    api.get<TimeReportData>('/v1/time-tracking/entries/summary/', { params }),
};

// Tasks API
export const timeTasksApi = {
  list: (params?: { project?: number; status?: string; assigned_to?: number }) =>
    api.get<TimeTask[]>('/v1/time-tracking/tasks/', { params }),

  get: (taskId: number) =>
    api.get<TimeTask>(`/v1/time-tracking/tasks/${taskId}/`),

  create: (data: {
    title: string;
    description?: string;
    project: number;
    estimated_hours?: number;
    due_date?: string;
    assigned_to?: number;
  }) =>
    api.post<TimeTask>('/v1/time-tracking/tasks/', data),

  update: (taskId: number, data: Partial<TimeTask>) =>
    api.patch<TimeTask>(`/v1/time-tracking/tasks/${taskId}/`, data),

  delete: (taskId: number) =>
    api.delete(`/v1/time-tracking/tasks/${taskId}/`),
};

// Project Estimates API
export const projectEstimatesApi = {
  list: () =>
    api.get<ProjectEstimate[]>('/v1/time-tracking/estimates/'),

  get: (estimateId: number) =>
    api.get<ProjectEstimate>(`/v1/time-tracking/estimates/${estimateId}/`),

  create: (data: {
    project: number;
    name: string;
    description?: string;
    estimated_hours: number;
  }) =>
    api.post<ProjectEstimate>('/v1/time-tracking/estimates/', data),

  update: (estimateId: number, data: Partial<ProjectEstimate>) =>
    api.patch<ProjectEstimate>(`/v1/time-tracking/estimates/${estimateId}/`, data),

  delete: (estimateId: number) =>
    api.delete(`/v1/time-tracking/estimates/${estimateId}/`),
};

// Invoices API
export const invoicesApi = {
  list: (params?: { status?: string; client?: number }) =>
    api.get<Invoice[]>('/v1/time-tracking/invoices/', { params }),

  get: (invoiceId: number) =>
    api.get<Invoice>(`/v1/time-tracking/invoices/${invoiceId}/`),

  create: (data: {
    client: number;
    project?: number;
    due_date: string;
    line_items: Omit<InvoiceLineItem, 'id'>[];
    tax_rate?: number;
    notes?: string;
  }) =>
    api.post<Invoice>('/v1/time-tracking/invoices/', data),

  createFromEntries: (data: {
    client: number;
    time_entry_ids: number[];
    due_date: string;
    notes?: string;
  }) =>
    api.post<Invoice>('/v1/time-tracking/invoices/from-entries/', data),

  update: (invoiceId: number, data: Partial<Invoice>) =>
    api.patch<Invoice>(`/v1/time-tracking/invoices/${invoiceId}/`, data),

  delete: (invoiceId: number) =>
    api.delete(`/v1/time-tracking/invoices/${invoiceId}/`),

  send: (invoiceId: number) =>
    api.post(`/v1/time-tracking/invoices/${invoiceId}/send/`),

  markPaid: (invoiceId: number) =>
    api.post(`/v1/time-tracking/invoices/${invoiceId}/mark-paid/`),

  downloadPdf: (invoiceId: number) =>
    api.get(`/v1/time-tracking/invoices/${invoiceId}/pdf/`, { responseType: 'blob' }),
};

// Time Reports API
export const timeReportsApi = {
  list: () =>
    api.get<TimeReport[]>('/v1/time-tracking/reports/'),

  get: (reportId: number) =>
    api.get<TimeReport>(`/v1/time-tracking/reports/${reportId}/`),

  generate: (data: {
    name?: string;
    report_type: string;
    date_range: { start: string; end: string };
    filters?: {
      projects?: number[];
      users?: number[];
      billable_only?: boolean;
    };
  }) =>
    api.post<TimeReport>('/v1/time-tracking/reports/', data),

  export: (reportId: number, format: 'csv' | 'pdf' | 'xlsx') =>
    api.get(`/v1/time-tracking/reports/${reportId}/export/`, {
      params: { format },
      responseType: 'blob'
    }),
};

// Weekly Goals API
export const weeklyGoalsApi = {
  getCurrent: () =>
    api.get<WeeklyGoal>('/v1/time-tracking/goals/current/'),

  set: (data: { target_hours: number; week_start?: string }) =>
    api.post<WeeklyGoal>('/v1/time-tracking/goals/', data),

  update: (data: { target_hours: number }) =>
    api.patch<WeeklyGoal>('/v1/time-tracking/goals/current/', data),
};

// Dashboard API
export const timeDashboardApi = {
  get: () =>
    api.get<TimeDashboard>('/v1/time-tracking/dashboard/'),
};
