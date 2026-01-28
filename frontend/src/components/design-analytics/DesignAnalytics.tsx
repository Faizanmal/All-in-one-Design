'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  PieChart,
  Activity,
  Clock,
  Users,
  Layers,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Download,
  Calendar,
  Filter
} from 'lucide-react';

interface ComponentUsage {
  id: string;
  name: string;
  usage_count: number;
  unique_files: number;
  last_used: string;
  trend: 'up' | 'down' | 'stable';
  trend_percent: number;
}

interface StyleUsage {
  id: string;
  name: string;
  type: 'color' | 'typography' | 'effect';
  value: string;
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
  affected_count: number;
}

interface DesignAnalyticsProps {
  designSystemId?: string;
  onExport?: (data: unknown) => void;
}

export function DesignAnalytics({ designSystemId, onExport }: DesignAnalyticsProps) {
  const [activeView, setActiveView] = useState<'overview' | 'components' | 'styles' | 'deprecations'>('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [dateRange, setDateRange] = useState('30d');
  const [healthScore, setHealthScore] = useState<HealthScore>({
    overall: 87,
    adoption: 92,
    consistency: 85,
    coverage: 78,
    freshness: 90,
    documentation: 88
  });
  const [topComponents, setTopComponents] = useState<ComponentUsage[]>([
    { id: '1', name: 'Button/Primary', usage_count: 156, unique_files: 23, last_used: '2h ago', trend: 'up', trend_percent: 12 },
    { id: '2', name: 'Card/Default', usage_count: 124, unique_files: 18, last_used: '5h ago', trend: 'up', trend_percent: 8 },
    { id: '3', name: 'Input/Text', usage_count: 98, unique_files: 15, last_used: '1h ago', trend: 'stable', trend_percent: 0 },
    { id: '4', name: 'Avatar/Circle', usage_count: 67, unique_files: 12, last_used: '1d ago', trend: 'down', trend_percent: -5 },
    { id: '5', name: 'Modal/Confirm', usage_count: 45, unique_files: 8, last_used: '3d ago', trend: 'down', trend_percent: -15 },
  ]);
  const [styleUsage, setStyleUsage] = useState<StyleUsage[]>([
    { id: '1', name: 'Primary Blue', type: 'color', value: '#3b82f6', usage_count: 234, consistency_score: 95 },
    { id: '2', name: 'Heading/H1', type: 'typography', value: 'Inter 32px Bold', usage_count: 89, consistency_score: 88 },
    { id: '3', name: 'Shadow/Medium', type: 'effect', value: '0 4px 12px rgba(0,0,0,0.1)', usage_count: 156, consistency_score: 92 },
  ]);
  const [deprecations, setDeprecations] = useState<DeprecationNotice[]>([
    { id: '1', component_name: 'Button/Old', reason: 'Replaced with new design system', replacement: 'Button/Primary', deadline: '2024-03-01', affected_count: 23 },
    { id: '2', component_name: 'Card/Legacy', reason: 'Accessibility issues', replacement: 'Card/Accessible', deadline: '2024-02-15', affected_count: 12 },
  ]);

  const handleRefresh = useCallback(async () => {
    setIsLoading(true);
    try {
      // Fetch fresh data from API
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error('Refresh error:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-500';
    if (score >= 70) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Design System Analytics</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Track adoption, usage patterns, and health metrics
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
            <button
              onClick={handleRefresh}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              <RefreshCw className={`w-5 h-5 text-gray-500 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => onExport?.({})}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* View Tabs */}
        <div className="flex gap-1 mt-4">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'components', label: 'Components', icon: Layers },
            { id: 'styles', label: 'Styles', icon: PieChart },
            { id: 'deprecations', label: 'Deprecations', icon: AlertTriangle },
          ].map(view => (
            <button
              key={view.id}
              onClick={() => setActiveView(view.id as 'overview' | 'components' | 'styles' | 'deprecations')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeView === view.id
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <view.icon className="w-4 h-4" />
              {view.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeView === 'overview' && (
          <div className="space-y-6">
            {/* Health Score Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Health</h3>
              <div className="grid grid-cols-6 gap-4">
                {[
                  { key: 'overall', label: 'Overall', icon: Activity },
                  { key: 'adoption', label: 'Adoption', icon: Users },
                  { key: 'consistency', label: 'Consistency', icon: CheckCircle },
                  { key: 'coverage', label: 'Coverage', icon: Layers },
                  { key: 'freshness', label: 'Freshness', icon: Clock },
                  { key: 'documentation', label: 'Docs', icon: Activity },
                ].map(metric => {
                  const score = healthScore[metric.key as keyof HealthScore];
                  return (
                    <div key={metric.key} className="text-center">
                      <div className="relative inline-flex">
                        <svg className="w-20 h-20">
                          <circle
                            cx="40"
                            cy="40"
                            r="35"
                            fill="none"
                            stroke="#e5e7eb"
                            strokeWidth="6"
                          />
                          <circle
                            cx="40"
                            cy="40"
                            r="35"
                            fill="none"
                            stroke={score >= 90 ? '#22c55e' : score >= 70 ? '#eab308' : '#ef4444'}
                            strokeWidth="6"
                            strokeDasharray={`${(score / 100) * 220} 220`}
                            strokeLinecap="round"
                            transform="rotate(-90 40 40)"
                          />
                        </svg>
                        <span className={`absolute inset-0 flex items-center justify-center font-bold text-lg ${getScoreColor(score)}`}>
                          {score}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">{metric.label}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-4 gap-4">
              {[
                { label: 'Total Components', value: '156', change: '+12', trend: 'up' },
                { label: 'Active Users', value: '34', change: '+5', trend: 'up' },
                { label: 'Files Using DS', value: '89', change: '+23', trend: 'up' },
                { label: 'Detached Instances', value: '12', change: '-3', trend: 'down' },
              ].map((stat, i) => (
                <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                  <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
                  <div className="flex items-end gap-2 mt-1">
                    <span className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</span>
                    <span className={`text-sm flex items-center ${stat.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                      {stat.trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                      {stat.change}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Usage Timeline Chart (Placeholder) */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Usage Timeline</h3>
              <div className="h-64 flex items-end gap-2">
                {Array.from({ length: 30 }).map((_, i) => (
                  <div
                    key={i}
                    className="flex-1 bg-blue-500 rounded-t"
                    style={{ height: `${Math.random() * 80 + 20}%` }}
                  />
                ))}
              </div>
              <div className="flex justify-between mt-2 text-xs text-gray-500">
                <span>30 days ago</span>
                <span>Today</span>
              </div>
            </div>
          </div>
        )}

        {activeView === 'components' && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white">Component Usage</h3>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {topComponents.map((component, i) => (
                <div key={component.id} className="p-4 flex items-center gap-4">
                  <span className="text-lg font-bold text-gray-400 w-8">{i + 1}</span>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 dark:text-white">{component.name}</h4>
                    <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                      <span>{component.unique_files} files</span>
                      <span>Last used {component.last_used}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      {component.usage_count}
                    </div>
                    <div className={`text-sm flex items-center justify-end gap-1 ${
                      component.trend === 'up' ? 'text-green-500' : 
                      component.trend === 'down' ? 'text-red-500' : 'text-gray-500'
                    }`}>
                      {component.trend === 'up' && <TrendingUp className="w-4 h-4" />}
                      {component.trend === 'down' && <TrendingDown className="w-4 h-4" />}
                      {component.trend_percent !== 0 && `${component.trend_percent > 0 ? '+' : ''}${component.trend_percent}%`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeView === 'styles' && (
          <div className="space-y-4">
            {['color', 'typography', 'effect'].map(type => (
              <div key={type} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="font-semibold text-gray-900 dark:text-white capitalize">{type} Styles</h3>
                </div>
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {styleUsage.filter(s => s.type === type).map(style => (
                    <div key={style.id} className="p-4 flex items-center gap-4">
                      {type === 'color' && (
                        <div
                          className="w-10 h-10 rounded-lg shadow-inner"
                          style={{ backgroundColor: style.value }}
                        />
                      )}
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 dark:text-white">{style.name}</h4>
                        <p className="text-sm text-gray-500 font-mono">{style.value}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {style.usage_count} uses
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className={getScoreBg(style.consistency_score)}
                              style={{ width: `${style.consistency_score}%`, height: '100%' }}
                            />
                          </div>
                          <span className={`text-xs ${getScoreColor(style.consistency_score)}`}>
                            {style.consistency_score}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeView === 'deprecations' && (
          <div className="space-y-4">
            {deprecations.length > 0 ? (
              deprecations.map(dep => (
                <div key={dep.id} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-yellow-200 dark:border-yellow-800">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                      <AlertTriangle className="w-5 h-5 text-yellow-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-gray-900 dark:text-white">{dep.component_name}</h4>
                        {dep.deadline && (
                          <span className="text-sm text-red-500">
                            <Calendar className="w-4 h-4 inline mr-1" />
                            Due: {dep.deadline}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{dep.reason}</p>
                      {dep.replacement && (
                        <p className="text-sm text-green-600 mt-2">
                          <CheckCircle className="w-4 h-4 inline mr-1" />
                          Replace with: <strong>{dep.replacement}</strong>
                        </p>
                      )}
                      <div className="mt-3 flex items-center justify-between">
                        <span className="text-sm text-gray-500">
                          {dep.affected_count} instances affected
                        </span>
                        <button className="text-sm text-blue-600 hover:underline">
                          View affected files →
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-gray-500">
                <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500 opacity-50" />
                <p className="font-medium">No deprecation notices</p>
                <p className="text-sm">All components are up to date</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default DesignAnalytics;
