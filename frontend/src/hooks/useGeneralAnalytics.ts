import { useState, useCallback, useEffect, useRef } from 'react';
import apiClient from '@/lib/design-api';

export interface UserActivity {
  id: string;
  activity_type: string;
  timestamp: string;
  metadata: Record<string, unknown>;
  duration_ms: number | null;
}

export interface AIUsageMetrics {
  id: string;
  service_type: string;
  tokens_used: number;
  estimated_cost: number;
  success: boolean;
  timestamp: string;
}

export interface DashboardStats {
  projects: { total: number; this_week: number; this_month: number };
  ai_usage: {
    today: { requests: number; tokens: number | null; cost: number | string | null };
    this_month: { requests: number; tokens: number | null; cost: number | string | null };
  };
  activity: { today: number; this_week: number };
  assets: { total: number; storage_bytes: number; storage_mb: number };
  daily_chart_data: Array<{
    date: string;
    projects_created: number;
    projects_exported: number;
    ai_generations_count: number;
  }>;
}

export interface AIUsageSummary {
  summary: {
    total_requests: number;
    total_tokens: number | null;
    total_cost: number | string | null;
    // The API returns a fraction between zero and one.
    success_rate: number | null;
  };
  by_service: Record<string, { count: number; tokens: number | null; cost: number | string | null }>;
}

export function useGeneralAnalytics() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [recentActivities, setRecentActivities] = useState<UserActivity[]>([]);
  const [aiUsageSummary, setAiUsageSummary] = useState<AIUsageSummary | null>(null);
  const requestId = useRef(0);

  const refreshStats = useCallback(async () => {
    const id = ++requestId.current;
    setIsLoading(true);
    setError(null);
    try {
      const [dashboard, activities, usage] = await Promise.all([
        apiClient.get<DashboardStats>('/v1/analytics/dashboard/'),
        apiClient.get<UserActivity[] | { results: UserActivity[] }>('/v1/analytics/activities/recent/'),
        apiClient.get<AIUsageSummary>('/v1/analytics/ai-usage/summary/?days=30'),
      ]);
      if (id !== requestId.current) return;
      setDashboardStats(dashboard.data);
      setRecentActivities(Array.isArray(activities.data) ? activities.data : activities.data.results);
      setAiUsageSummary(usage.data);
    } catch {
      if (id !== requestId.current) return;
      setError('Unable to load analytics. Please try again.');
    } finally {
      if (id === requestId.current) setIsLoading(false);
    }
  }, []);

  const trackActivity = useCallback(async (activityType: string, metadata = {}, durationMs?: number) => {
    await apiClient.post('/v1/analytics/track/', {
      activity_type: activityType, metadata, duration_ms: durationMs,
    });
  }, []);

  useEffect(() => {
    void refreshStats();
    return () => { requestId.current += 1; };
  }, [refreshStats]);

  return { isLoading, error, dashboardStats, recentActivities, aiUsageSummary, refreshStats, trackActivity };
}
