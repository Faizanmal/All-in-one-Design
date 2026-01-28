import { useState, useCallback } from 'react';

const API_BASE = '/api/v1/accessibility';

interface AccessibilityIssue {
  id: string;
  category: string;
  severity: 'error' | 'warning' | 'info';
  title: string;
  description: string;
  element?: string;
  wcag_criteria?: string;
  suggestion?: string;
  is_fixed: boolean;
  is_ignored: boolean;
}

interface AccessibilityTest {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  issues_count: number;
  errors_count: number;
  warnings_count: number;
  created_at: string;
}

interface ContrastResult {
  foreground: string;
  background: string;
  ratio: number;
  aa_normal: boolean;
  aa_large: boolean;
  aaa_normal: boolean;
  aaa_large: boolean;
}

interface ColorBlindnessSimulation {
  id: string;
  simulation_type: string;
  image_url: string;
  confusing_colors: Array<{ original: string; simulated: string; context: string }>;
}

interface ScreenReaderPreview {
  id: string;
  reading_order: string[];
  issues: string[];
}

interface FocusOrderTest {
  id: string;
  focus_order: Array<{ element_id: string; name: string; order: number; has_indicator: boolean }>;
  is_logical: boolean;
  issues: string[];
}

export function useAccessibilityTesting(designId?: string) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [issues, setIssues] = useState<AccessibilityIssue[]>([]);
  const [currentTest, setCurrentTest] = useState<AccessibilityTest | null>(null);

  const runTest = useCallback(async (): Promise<AccessibilityTest> => {
    if (!designId) throw new Error('Design ID required');
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/tests/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design: designId })
      });
      if (!response.ok) throw new Error('Failed to run test');
      const test = await response.json();
      setCurrentTest(test);
      
      // Fetch issues for this test
      const issuesResponse = await fetch(`${API_BASE}/tests/${test.id}/issues/`);
      if (issuesResponse.ok) {
        const issuesData = await issuesResponse.json();
        setIssues(issuesData);
      }
      
      return test;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [designId]);

  const fetchIssues = useCallback(async (testId?: string) => {
    setIsLoading(true);
    try {
      const url = testId 
        ? `${API_BASE}/tests/${testId}/issues/`
        : `${API_BASE}/issues/?design=${designId}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch issues');
      const data = await response.json();
      setIssues(data.results || data);
      return data.results || data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [designId]);

  const fixIssue = useCallback(async (issueId: string): Promise<AccessibilityIssue> => {
    try {
      const response = await fetch(`${API_BASE}/issues/${issueId}/fix/`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to fix issue');
      const issue = await response.json();
      setIssues(prev => prev.map(i => i.id === issueId ? issue : i));
      return issue;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const ignoreIssue = useCallback(async (
    issueId: string, 
    reason?: string
  ): Promise<AccessibilityIssue> => {
    try {
      const response = await fetch(`${API_BASE}/issues/${issueId}/ignore/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });
      if (!response.ok) throw new Error('Failed to ignore issue');
      const issue = await response.json();
      setIssues(prev => prev.map(i => i.id === issueId ? issue : i));
      return issue;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const checkContrast = useCallback(async (
    foreground: string,
    background: string
  ): Promise<ContrastResult> => {
    try {
      const response = await fetch(`${API_BASE}/check-contrast/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ foreground, background })
      });
      if (!response.ok) throw new Error('Contrast check failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const suggestBetterColors = useCallback(async (
    foreground: string,
    background: string,
    targetLevel: 'aa' | 'aaa' = 'aa'
  ): Promise<{ foreground: string; background: string; ratio: number }[]> => {
    try {
      const response = await fetch(`${API_BASE}/suggest-colors/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ foreground, background, target_level: targetLevel })
      });
      if (!response.ok) throw new Error('Color suggestion failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const simulateColorBlindness = useCallback(async (
    simulationType: 'protanopia' | 'deuteranopia' | 'tritanopia' | 'protanomaly' | 'deuteranomaly' | 'tritanomaly' | 'achromatopsia' | 'achromatomaly'
  ): Promise<ColorBlindnessSimulation> => {
    if (!designId) throw new Error('Design ID required');
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/simulate-colorblindness/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design: designId, simulation_type: simulationType })
      });
      if (!response.ok) throw new Error('Simulation failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [designId]);

  const generateScreenReaderPreview = useCallback(async (): Promise<ScreenReaderPreview> => {
    if (!designId) throw new Error('Design ID required');
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/screen-reader-preview/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design: designId })
      });
      if (!response.ok) throw new Error('Preview generation failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [designId]);

  const testFocusOrder = useCallback(async (): Promise<FocusOrderTest> => {
    if (!designId) throw new Error('Design ID required');
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/test-focus-order/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design: designId })
      });
      if (!response.ok) throw new Error('Focus order test failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [designId]);

  const generateReport = useCallback(async (
    testId: string,
    format: 'json' | 'html' | 'pdf' = 'html'
  ): Promise<string> => {
    try {
      const response = await fetch(`${API_BASE}/tests/${testId}/generate_report/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format })
      });
      if (!response.ok) throw new Error('Report generation failed');
      const result = await response.json();
      return result.report_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const getGuidelines = useCallback(async (level: 'a' | 'aa' | 'aaa' = 'aa') => {
    try {
      const response = await fetch(`${API_BASE}/guidelines/?level=${level}`);
      if (!response.ok) throw new Error('Failed to fetch guidelines');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  return {
    isLoading,
    error,
    issues,
    currentTest,
    runTest,
    fetchIssues,
    fixIssue,
    ignoreIssue,
    checkContrast,
    suggestBetterColors,
    simulateColorBlindness,
    generateScreenReaderPreview,
    testFocusOrder,
    generateReport,
    getGuidelines
  };
}

export default useAccessibilityTesting;
