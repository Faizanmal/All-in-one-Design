import { useState, useCallback, useEffect } from 'react';

const API_BASE = '/api/v1/design-analytics';

interface ComponentUsage {
  id: string;
  component_name: string;
  usage_count: number;
  unique_files: number;
  last_used: string;
}

interface StyleUsage {
  id: string;
  style_name: string;
  style_type: string;
  usage_count: number;
  consistency_score: number;
}

interface HealthScore {
  overall: number;
  adoption: number;
  consistency: number;
  coverage: number;
  freshness: number;
  documentation: number;
}

interface DeprecationNotice {
  id: string;
  component_name: string;
  reason: string;
  replacement?: string;
  deadline?: string;
  status: string;
}

interface UsageTimeline {
  date: string;
  insertions: number;
  updates: number;
  deletions: number;
}

export function useDesignAnalytics(designSystemId?: string) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [healthScore, setHealthScore] = useState<HealthScore | null>(null);
  const [componentUsage, setComponentUsage] = useState<ComponentUsage[]>([]);
  const [styleUsage, setStyleUsage] = useState<StyleUsage[]>([]);
  const [deprecations, setDeprecations] = useState<DeprecationNotice[]>([]);

  const fetchAnalyticsSummary = useCallback(async () => {
    if (!designSystemId) return;
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/summary/?design_system=${designSystemId}`);
      if (response.ok) {
        const data = await response.json();
        setComponentUsage(data.top_components || []);
        setStyleUsage(data.style_usage || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [designSystemId]);

  const calculateHealthScore = useCallback(async (): Promise<HealthScore> => {
    if (!designSystemId) throw new Error('Design system ID required');
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/health/${designSystemId}/calculate/`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to calculate health score');
      const health = await response.json();
      setHealthScore(health);
      return health;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [designSystemId]);

  const getTopComponents = useCallback(async (limit: number = 10): Promise<ComponentUsage[]> => {
    if (!designSystemId) return [];
    try {
      const response = await fetch(
        `${API_BASE}/component-usage/?design_system=${designSystemId}&ordering=-usage_count&limit=${limit}`
      );
      if (!response.ok) throw new Error('Failed to fetch component usage');
      const data = await response.json();
      setComponentUsage(data.results || data);
      return data.results || data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, [designSystemId]);

  const getUnusedComponents = useCallback(async (): Promise<ComponentUsage[]> => {
    if (!designSystemId) return [];
    try {
      const response = await fetch(
        `${API_BASE}/component-usage/?design_system=${designSystemId}&usage_count=0`
      );
      if (!response.ok) throw new Error('Failed to fetch unused components');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, [designSystemId]);

  const trackUsage = useCallback(async (
    componentId: string,
    eventType: 'insert' | 'update' | 'delete' | 'detach' | 'swap',
    metadata?: Record<string, unknown>
  ) => {
    try {
      await fetch(`${API_BASE}/track-usage/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          design_system: designSystemId,
          component_id: componentId,
          event_type: eventType,
          metadata
        })
      });
    } catch (err) {
      console.error('Usage tracking failed:', err);
    }
  }, [designSystemId]);

  const getUsageTimeline = useCallback(async (
    startDate: string,
    endDate: string,
    granularity: 'day' | 'week' | 'month' = 'day'
  ): Promise<UsageTimeline[]> => {
    if (!designSystemId) return [];
    try {
      const response = await fetch(
        `${API_BASE}/usage-timeline/?design_system=${designSystemId}&start_date=${startDate}&end_date=${endDate}&granularity=${granularity}`
      );
      if (!response.ok) throw new Error('Failed to fetch usage timeline');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, [designSystemId]);

  const getDeprecations = useCallback(async (): Promise<DeprecationNotice[]> => {
    if (!designSystemId) return [];
    try {
      const response = await fetch(
        `${API_BASE}/deprecations/?design_system=${designSystemId}&status=active`
      );
      if (!response.ok) throw new Error('Failed to fetch deprecations');
      const data = await response.json();
      setDeprecations(data.results || data);
      return data.results || data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, [designSystemId]);

  const createDeprecation = useCallback(async (
    componentName: string,
    reason: string,
    replacement?: string,
    deadline?: string
  ): Promise<DeprecationNotice> => {
    try {
      const response = await fetch(`${API_BASE}/deprecations/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          design_system: designSystemId,
          component_name: componentName,
          reason,
          replacement_component: replacement,
          deadline
        })
      });
      if (!response.ok) throw new Error('Failed to create deprecation notice');
      const deprecation = await response.json();
      setDeprecations(prev => [...prev, deprecation]);
      return deprecation;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, [designSystemId]);

  const runComplianceCheck = useCallback(async (projectId: string) => {
    try {
      const response = await fetch(`${API_BASE}/compliance-check/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          design_system: designSystemId,
          project_id: projectId
        })
      });
      if (!response.ok) throw new Error('Compliance check failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, [designSystemId]);

  const exportReport = useCallback(async (format: 'json' | 'csv' | 'pdf' = 'json') => {
    if (!designSystemId) throw new Error('Design system ID required');
    try {
      const response = await fetch(
        `${API_BASE}/export/?design_system=${designSystemId}&format=${format}`
      );
      if (!response.ok) throw new Error('Export failed');
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-report.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, [designSystemId]);

  useEffect(() => {
    if (designSystemId) {
      fetchAnalyticsSummary();
      getDeprecations();
    }
  }, [designSystemId, fetchAnalyticsSummary, getDeprecations]);

  return {
    isLoading,
    error,
    healthScore,
    componentUsage,
    styleUsage,
    deprecations,
    calculateHealthScore,
    getTopComponents,
    getUnusedComponents,
    trackUsage,
    getUsageTimeline,
    getDeprecations,
    createDeprecation,
    runComplianceCheck,
    exportReport,
    refresh: fetchAnalyticsSummary
  };
}

export default useDesignAnalytics;
