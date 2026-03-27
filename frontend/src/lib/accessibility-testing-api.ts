// API service for accessibility testing
import api from './api';

// Accessibility Test Types
export interface AccessibilityTest {
  id: number;
  project: number;
  page?: number;
  name: string;
  wcag_level: 'A' | 'AA' | 'AAA';
  status: 'pending' | 'running' | 'completed' | 'failed';
  total_issues: number;
  critical_count: number;
  serious_count: number;
  moderate_count: number;
  minor_count: number;
  pass_rate: number;
  created_by: {
    id: number;
    username: string;
  };
  created_at: string;
  completed_at?: string;
}

// Accessibility Issue Types
export interface AccessibilityIssue {
  id: number;
  test: number;
  element_selector: string;
  element_html?: string;
  issue_type: string;
  category: 'color_contrast' | 'keyboard' | 'screen_reader' | 'touch' | 'motion' | 'text' | 'structure' | 'media' | 'forms' | 'other';
  severity: 'critical' | 'serious' | 'moderate' | 'minor';
  wcag_criteria: string;
  description: string;
  impact: string;
  recommendation: string;
  auto_fixable: boolean;
  is_fixed: boolean;
  fixed_at?: string;
  created_at: string;
}

// Color Blindness Simulation Types
export interface ColorBlindnessSimulation {
  id: number;
  project: number;
  page?: number;
  simulation_type: 'protanopia' | 'deuteranopia' | 'tritanopia' | 'achromatopsia' | 'protanomaly' | 'deuteranomaly' | 'tritanomaly' | 'achromatomaly';
  original_image?: string;
  simulated_image?: string;
  contrast_issues: ContrastIssue[];
  created_at: string;
}

// Contrast Issue Types
export interface ContrastIssue {
  element_selector: string;
  foreground_color: string;
  background_color: string;
  contrast_ratio: number;
  required_ratio: number;
  wcag_level: string;
  passes: boolean;
  suggested_foreground?: string;
  suggested_background?: string;
}

// Screen Reader Preview Types
export interface ScreenReaderPreview {
  id: number;
  project: number;
  page: number;
  elements: ScreenReaderElement[];
  reading_order: number[];
  accessibility_tree: AccessibilityTreeNode;
  issues: string[];
  created_at: string;
}

// Screen Reader Element Types
export interface ScreenReaderElement {
  id: string;
  tag: string;
  role: string;
  name: string;
  description?: string;
  state?: string[];
  level?: number;
  value?: string;
  children?: ScreenReaderElement[];
}

// Accessibility Tree Node Types
export interface AccessibilityTreeNode {
  role: string;
  name: string;
  properties?: Record<string, string>;
  children?: AccessibilityTreeNode[];
}

// Focus Order Test Types
export interface FocusOrderTest {
  id: number;
  project: number;
  page: number;
  elements: FocusableElement[];
  issues: FocusOrderIssue[];
  passes: boolean;
  created_at: string;
}

// Focusable Element Types
export interface FocusableElement {
  id: string;
  tag: string;
  tab_index: number;
  focus_order: number;
  is_interactive: boolean;
  has_visible_focus: boolean;
  selector: string;
}

// Focus Order Issue Types
export interface FocusOrderIssue {
  type: 'skip' | 'trap' | 'invisible' | 'wrong_order' | 'not_focusable';
  element_selector: string;
  description: string;
  recommendation: string;
}

// Contrast Check Types
export interface ContrastCheck {
  id: number;
  foreground: string;
  background: string;
  ratio: number;
  aa_normal: boolean;
  aa_large: boolean;
  aaa_normal: boolean;
  aaa_large: boolean;
  suggestions?: {
    foreground: string[];
    background: string[];
  };
}

// Accessibility Report Types
export interface AccessibilityReport {
  id: number;
  project: number;
  name: string;
  summary: {
    total_pages: number;
    total_issues: number;
    by_severity: Record<string, number>;
    by_category: Record<string, number>;
    overall_score: number;
    compliant_pages: number;
  };
  tests: AccessibilityTest[];
  created_at: string;
  pdf_url?: string;
}

// WCAG Guideline Types
export interface AccessibilityGuideline {
  id: string;
  number: string;
  name: string;
  level: 'A' | 'AA' | 'AAA';
  principle: 'perceivable' | 'operable' | 'understandable' | 'robust';
  description: string;
  techniques: string[];
  failures: string[];
}

// Accessibility Tests API
export const accessibilityTestsApi = {
  list: (params?: { project?: number; status?: string; wcag_level?: string }) =>
    api.get<AccessibilityTest[]>('/v1/accessibility-testing/tests/', { params }),

  get: (testId: number) =>
    api.get<AccessibilityTest>(`/v1/accessibility-testing/tests/${testId}/`),

  create: (data: { project: number; page?: number; name: string; wcag_level?: string }) =>
    api.post<AccessibilityTest>('/v1/accessibility-testing/tests/', data),

  run: (testId: number) =>
    api.post<AccessibilityTest>(`/v1/accessibility-testing/tests/${testId}/run/`),

  delete: (testId: number) =>
    api.delete(`/v1/accessibility-testing/tests/${testId}/`),
};

// Accessibility Issues API
export const accessibilityIssuesApi = {
  list: (testId: number, params?: { severity?: string; category?: string; is_fixed?: boolean }) =>
    api.get<AccessibilityIssue[]>(`/v1/accessibility-testing/tests/${testId}/issues/`, { params }),

  get: (testId: number, issueId: number) =>
    api.get<AccessibilityIssue>(`/v1/accessibility-testing/tests/${testId}/issues/${issueId}/`),

  markFixed: (testId: number, issueId: number) =>
    api.post(`/v1/accessibility-testing/tests/${testId}/issues/${issueId}/mark-fixed/`),

  autoFix: (testId: number, issueId: number) =>
    api.post<{ success: boolean; fixed_html?: string }>(
      `/v1/accessibility-testing/tests/${testId}/issues/${issueId}/auto-fix/`
    ),

  bulkAutoFix: (testId: number, issueIds: number[]) =>
    api.post<{ fixed_count: number; failed_count: number }>(
      `/v1/accessibility-testing/tests/${testId}/issues/bulk-auto-fix/`,
      { issue_ids: issueIds }
    ),
};

// Color Blindness Simulation API
export const colorBlindnessApi = {
  list: (projectId: number) =>
    api.get<ColorBlindnessSimulation[]>(
      '/v1/accessibility-testing/simulations/',
      { params: { project: projectId } }
    ),

  simulate: (data: { project: number; page?: number; simulation_type: string }) =>
    api.post<ColorBlindnessSimulation>('/v1/accessibility-testing/simulations/simulate/', data),

  simulateImage: (data: FormData) =>
    api.post<{ original: string; simulated: string }>(
      '/v1/accessibility-testing/simulations/simulate-image/',
      data,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    ),
};

// Screen Reader Preview API
export const screenReaderApi = {
  generate: (data: { project: number; page: number }) =>
    api.post<ScreenReaderPreview>('/v1/accessibility-testing/screen-reader/preview/', data),

  getReadingOrder: (data: { project: number; page: number }) =>
    api.post<ScreenReaderElement[]>('/v1/accessibility-testing/screen-reader/reading-order/', data),

  getAccessibilityTree: (data: { project: number; page: number }) =>
    api.post<AccessibilityTreeNode>('/v1/accessibility-testing/screen-reader/tree/', data),
};

// Focus Order Test API
export const focusOrderApi = {
  test: (data: { project: number; page: number }) =>
    api.post<FocusOrderTest>('/v1/accessibility-testing/focus-order/test/', data),

  getFocusableElements: (data: { project: number; page: number }) =>
    api.post<FocusableElement[]>('/v1/accessibility-testing/focus-order/elements/', data),
};

// Contrast Check API
export const contrastCheckApi = {
  check: (data: { foreground: string; background: string }) =>
    api.post<ContrastCheck>('/v1/accessibility-testing/contrast/check/', data),

  checkPage: (data: { project: number; page: number }) =>
    api.post<ContrastIssue[]>('/v1/accessibility-testing/contrast/check-page/', data),

  suggest: (data: { foreground: string; background: string; target_ratio: number }) =>
    api.post<{ foreground_suggestions: string[]; background_suggestions: string[] }>(
      '/v1/accessibility-testing/contrast/suggest/',
      data
    ),
};

// Accessibility Reports API
export const accessibilityReportsApi = {
  list: (projectId?: number) =>
    api.get<AccessibilityReport[]>('/v1/accessibility-testing/reports/', {
      params: projectId ? { project: projectId } : undefined
    }),

  get: (reportId: number) =>
    api.get<AccessibilityReport>(`/v1/accessibility-testing/reports/${reportId}/`),

  generate: (data: { project: number; name?: string }) =>
    api.post<AccessibilityReport>('/v1/accessibility-testing/reports/', data),

  downloadPdf: (reportId: number) =>
    api.get(`/v1/accessibility-testing/reports/${reportId}/pdf/`, { responseType: 'blob' }),
};

// WCAG Guidelines API
export const wcagGuidelinesApi = {
  list: (params?: { level?: string; principle?: string }) =>
    api.get<AccessibilityGuideline[]>('/v1/accessibility-testing/guidelines/', { params }),

  get: (guidelineId: string) =>
    api.get<AccessibilityGuideline>(`/v1/accessibility-testing/guidelines/${guidelineId}/`),
};
