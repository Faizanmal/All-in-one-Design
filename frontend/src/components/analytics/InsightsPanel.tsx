'use client';

import React, { useState, useEffect, useCallback } from 'react';

interface DesignInsight {
  id: string;
  type: 'performance' | 'suggestion' | 'trend' | 'alert';
  severity: 'info' | 'warning' | 'success' | 'critical';
  title: string;
  description: string;
  metric?: string;
  value?: number;
  change?: number;
  action?: {
    label: string;
    url: string;
  };
  created_at: string;
}

interface TrendData {
  metric: string;
  current: number;
  previous: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
}

interface AIRecommendation {
  id: string;
  category: string;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
}

export function InsightsPanel() {
  const [insights, setInsights] = useState<DesignInsight[]>([]);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<'all' | DesignInsight['type']>('all');

  const fetchInsights = useCallback(async () => {
    setLoading(true);
    try {
      const [insightsRes, trendsRes, recsRes] = await Promise.all([
        fetch('/api/analytics/advanced/insights/'),
        fetch('/api/analytics/advanced/trends/'),
        fetch('/api/analytics/advanced/recommendations/'),
      ]);

      if (insightsRes.ok) setInsights((await insightsRes.json()).results || []);
      if (trendsRes.ok) setTrends((await trendsRes.json()).data || []);
      if (recsRes.ok) setRecommendations((await recsRes.json()).results || []);
    } catch (error) {
      console.error('Failed to fetch insights:', error);
      // Mock data
      setInsights([
        {
          id: '1',
          type: 'performance',
          severity: 'success',
          title: 'Design Output Increased',
          description: 'Your team created 25% more designs this week compared to last week. Great productivity!',
          metric: 'designs_created',
          value: 45,
          change: 25,
          created_at: '2024-02-25T10:00:00Z',
        },
        {
          id: '2',
          type: 'suggestion',
          severity: 'info',
          title: 'Try AI-Powered Backgrounds',
          description: 'Teams using AI backgrounds save an average of 15 minutes per design. You haven\'t used this feature recently.',
          action: { label: 'Learn More', url: '/features/ai-backgrounds' },
          created_at: '2024-02-24T14:30:00Z',
        },
        {
          id: '3',
          type: 'trend',
          severity: 'info',
          title: 'Social Media Designs Trending',
          description: 'Instagram Story templates are your most popular category, making up 40% of exports.',
          metric: 'export_category',
          value: 40,
          created_at: '2024-02-24T09:00:00Z',
        },
        {
          id: '4',
          type: 'alert',
          severity: 'warning',
          title: 'Storage Approaching Limit',
          description: 'You\'ve used 85% of your storage. Consider upgrading or archiving old projects.',
          metric: 'storage_used',
          value: 85,
          action: { label: 'Manage Storage', url: '/settings/storage' },
          created_at: '2024-02-23T16:00:00Z',
        },
        {
          id: '5',
          type: 'performance',
          severity: 'warning',
          title: 'Export Time Increased',
          description: 'Average export time has increased by 30%. Large file sizes may be causing delays.',
          metric: 'export_time',
          change: 30,
          created_at: '2024-02-22T11:00:00Z',
        },
      ]);
      setTrends([
        { metric: 'Designs Created', current: 156, previous: 142, change: 9.86, trend: 'up' },
        { metric: 'AI Generations', current: 234, previous: 187, change: 25.13, trend: 'up' },
        { metric: 'Exports', current: 89, previous: 95, change: -6.32, trend: 'down' },
        { metric: 'Avg Design Time', current: 42, previous: 48, change: -12.5, trend: 'down' },
        { metric: 'Collaborators', current: 12, previous: 10, change: 20, trend: 'up' },
      ]);
      setRecommendations([
        {
          id: '1',
          category: 'Productivity',
          title: 'Enable Keyboard Shortcuts',
          description: 'Users who use keyboard shortcuts complete designs 35% faster on average.',
          impact: 'high',
          effort: 'low',
        },
        {
          id: '2',
          category: 'Collaboration',
          title: 'Set Up Design Reviews',
          description: 'Implement a formal review process to reduce revision rounds by 40%.',
          impact: 'high',
          effort: 'medium',
        },
        {
          id: '3',
          category: 'AI Features',
          title: 'Use Smart Templates',
          description: 'AI-generated templates based on your brand can speed up initial design by 50%.',
          impact: 'medium',
          effort: 'low',
        },
        {
          id: '4',
          category: 'Organization',
          title: 'Create Project Folders',
          description: 'Organize designs into project folders to improve team navigation and reduce search time.',
          impact: 'medium',
          effort: 'low',
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  const getSeverityStyles = (severity: DesignInsight['severity']) => {
    switch (severity) {
      case 'success':
        return { bg: 'bg-green-50', border: 'border-green-200', icon: '✓', iconBg: 'bg-green-100', iconColor: 'text-green-600' };
      case 'warning':
        return { bg: 'bg-yellow-50', border: 'border-yellow-200', icon: '⚠', iconBg: 'bg-yellow-100', iconColor: 'text-yellow-600' };
      case 'critical':
        return { bg: 'bg-red-50', border: 'border-red-200', icon: '!', iconBg: 'bg-red-100', iconColor: 'text-red-600' };
      default:
        return { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'i', iconBg: 'bg-blue-100', iconColor: 'text-blue-600' };
    }
  };

  const getTypeIcon = (type: DesignInsight['type']) => {
    switch (type) {
      case 'performance':
        return '📊';
      case 'suggestion':
        return '💡';
      case 'trend':
        return '📈';
      case 'alert':
        return '🔔';
      default:
        return '📌';
    }
  };

  const getImpactBadge = (impact: AIRecommendation['impact']) => {
    const styles = {
      high: 'bg-red-100 text-red-700',
      medium: 'bg-yellow-100 text-yellow-700',
      low: 'bg-green-100 text-green-700',
    };
    return <span className={`px-2 py-0.5 text-xs font-medium rounded ${styles[impact]}`}>{impact} impact</span>;
  };

  const getEffortBadge = (effort: AIRecommendation['effort']) => {
    const styles = {
      high: 'bg-gray-200 text-gray-700',
      medium: 'bg-gray-150 text-gray-600',
      low: 'bg-gray-100 text-gray-500',
    };
    return <span className={`px-2 py-0.5 text-xs font-medium rounded ${styles[effort]}`}>{effort} effort</span>;
  };

  const filteredInsights = activeFilter === 'all' 
    ? insights 
    : insights.filter((i) => i.type === activeFilter);

  const INSIGHT_FILTERS = [
    { value: 'all', label: 'All', icon: '📋' },
    { value: 'performance', label: 'Performance', icon: '📊' },
    { value: 'suggestion', label: 'Suggestions', icon: '💡' },
    { value: 'trend', label: 'Trends', icon: '📈' },
    { value: 'alert', label: 'Alerts', icon: '🔔' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Insights & Recommendations</h1>
            <p className="text-gray-500">AI-powered insights to improve your design workflow</p>
          </div>
          <button
            onClick={fetchInsights}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700"
          >
            Refresh Insights
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Insights */}
          <div className="lg:col-span-2 space-y-6">
            {/* Filter Tabs */}
            <div className="bg-white rounded-lg shadow-sm p-2 flex gap-1">
              {INSIGHT_FILTERS.map((filter) => (
                <button
                  key={filter.value}
                  onClick={() => setActiveFilter(filter.value as typeof activeFilter)}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeFilter === filter.value
                      ? 'bg-purple-100 text-purple-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <span>{filter.icon}</span>
                  <span className="hidden md:inline">{filter.label}</span>
                </button>
              ))}
            </div>

            {/* Insights List */}
            <div className="space-y-4">
              {filteredInsights.map((insight) => {
                const styles = getSeverityStyles(insight.severity);
                return (
                  <div
                    key={insight.id}
                    className={`${styles.bg} border ${styles.border} rounded-lg p-4`}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`${styles.iconBg} w-10 h-10 rounded-lg flex items-center justify-center text-lg`}>
                        {getTypeIcon(insight.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-gray-900">{insight.title}</h3>
                          {insight.change !== undefined && (
                            <span
                              className={`text-sm font-medium ${
                                insight.change > 0 ? 'text-green-600' : 'text-red-600'
                              }`}
                            >
                              {insight.change > 0 ? '↑' : '↓'} {Math.abs(insight.change)}%
                            </span>
                          )}
                        </div>
                        <p className="text-gray-600 text-sm mb-2">{insight.description}</p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-400">
                            {new Date(insight.created_at).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                          {insight.action && (
                            <a
                              href={insight.action.url}
                              className="text-sm text-purple-600 font-medium hover:underline"
                            >
                              {insight.action.label} →
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}

              {filteredInsights.length === 0 && (
                <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                  <p className="text-gray-500">No insights found for this filter.</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* Key Trends */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Key Trends</h3>
              <div className="space-y-4">
                {trends.map((trend, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">{trend.metric}</p>
                      <p className="text-lg font-semibold text-gray-900">{trend.current}</p>
                    </div>
                    <div className="text-right">
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded text-sm font-medium ${
                          trend.trend === 'up'
                            ? 'bg-green-100 text-green-700'
                            : trend.trend === 'down'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {trend.trend === 'up' ? '↑' : trend.trend === 'down' ? '↓' : '→'}
                        {Math.abs(trend.change).toFixed(1)}%
                      </span>
                      <p className="text-xs text-gray-400 mt-1">vs prev. period</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Recommendations */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-4">AI Recommendations</h3>
              <div className="space-y-4">
                {recommendations.map((rec) => (
                  <div key={rec.id} className="border-b pb-4 last:border-0 last:pb-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-gray-500 uppercase">
                        {rec.category}
                      </span>
                    </div>
                    <h4 className="font-medium text-gray-900 text-sm mb-1">{rec.title}</h4>
                    <p className="text-xs text-gray-500 mb-2">{rec.description}</p>
                    <div className="flex items-center gap-2">
                      {getImpactBadge(rec.impact)}
                      {getEffortBadge(rec.effort)}
                    </div>
                  </div>
                ))}
              </div>
              <button className="w-full mt-4 px-4 py-2 bg-purple-50 text-purple-600 rounded-lg text-sm font-medium hover:bg-purple-100 transition-colors">
                View All Recommendations
              </button>
            </div>

            {/* Quick Actions */}
            <div className="bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg p-6 text-white">
              <h3 className="font-semibold mb-2">Get Personalized Insights</h3>
              <p className="text-sm text-purple-100 mb-4">
                Schedule a weekly insights report delivered to your inbox.
              </p>
              <button className="w-full px-4 py-2 bg-white text-purple-600 rounded-lg font-medium hover:bg-purple-50 transition-colors">
                Set Up Reports
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
