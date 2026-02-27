import { useState, useCallback, useEffect } from 'react';

const API_BASE = '/api/v1/analytics';

export interface UserActivity {
    id: string;
    activity_type: string;
    timestamp: string;
    metadata: Record<string, unknown>;
    duration_ms: number;
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
    projects: {
        total: number;
        this_week: number;
        this_month: number;
    };
    ai_usage: {
        today: { requests: number; tokens: number; cost: number };
        this_month: { requests: number; tokens: number; cost: number };
    };
    activity: {
        today: number;
        this_week: number;
    };
    assets: {
        total: number;
        storage_bytes: number;
        storage_mb: number;
    };
    daily_chart_data: Array<{ date: string; value: number;[key: string]: unknown }>;
}

export function useGeneralAnalytics() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
    const [recentActivities, setRecentActivities] = useState<UserActivity[]>([]);
    const [aiUsageSummary, setAiUsageSummary] = useState<Record<string, unknown> | null>(null);

    const fetchDashboardStats = useCallback(async () => {
        try {
            setIsLoading(true);
            const res = await fetch(`${API_BASE}/dashboard/`);
            if (!res.ok) throw new Error('Failed to load dashboard stats');
            const data = await res.json();
            setDashboardStats(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const fetchRecentActivities = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/activities/recent/`);
            if (res.ok) {
                const data = await res.json();
                setRecentActivities(data.results || data);
            }
        } catch (err) {
            console.error(err);
        }
    }, []);

    const fetchAiUsageSummary = useCallback(async (days = 30) => {
        try {
            const res = await fetch(`${API_BASE}/ai-usage/summary/?days=${days}`);
            if (res.ok) {
                const data = await res.json();
                setAiUsageSummary(data);
            }
        } catch (err) {
            console.error(err);
        }
    }, []);

    const trackActivity = useCallback(async (activityType: string, metadata = {}, durationMs?: number) => {
        try {
            await fetch(`${API_BASE}/track/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    activity_type: activityType,
                    metadata,
                    duration_ms: durationMs,
                }),
            });
        } catch (err) {
            console.error('Failed to track activity', err);
        }
    }, []);

    useEffect(() => {
        fetchDashboardStats();
        fetchRecentActivities();
        fetchAiUsageSummary();
    }, [fetchDashboardStats, fetchRecentActivities, fetchAiUsageSummary]);

    return {
        isLoading,
        error,
        dashboardStats,
        recentActivities,
        aiUsageSummary,
        refreshStats: fetchDashboardStats,
        trackActivity,
    };
}
