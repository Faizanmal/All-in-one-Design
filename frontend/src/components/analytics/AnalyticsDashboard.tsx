'use client';

import React, { useState, useEffect, useCallback } from 'react';

interface AnalyticsOverview {
  totalProjects: number;
  activeProjects: number;
  totalDesigns: number;
  totalExports: number;
  avgDesignTime: number;
  collaborators: number;
  aiGenerations: number;
  storageUsed: number;
  storageLimit: number;
}

interface ChartData {
  label: string;
  value: number;
}

interface ActivityData {
  date: string;
  designs_created: number;
  exports: number;
  ai_requests: number;
}

interface PopularDesign {
  id: string;
  name: string;
  views: number;
  exports: number;
  shares: number;
  thumbnail: string;
}

interface TeamMember {
  id: string;
  name: string;
  avatar: string;
  designs: number;
  exports: number;
  active: boolean;
}

type TimeRange = '7d' | '30d' | '90d' | '1y';

export function AnalyticsDashboard() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [activityData, setActivityData] = useState<ActivityData[]>([]);
  const [popularDesigns, setPopularDesigns] = useState<PopularDesign[]>([]);
  const [teamActivity, setTeamActivity] = useState<TeamMember[]>([]);
  const [categoryBreakdown, setCategoryBreakdown] = useState<ChartData[]>([]);
  const [timeRange, setTimeRange] = useState<TimeRange>('30d');
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ time_range: timeRange });
      
      const [overviewRes, activityRes, designsRes, teamRes, categoryRes] = await Promise.all([
        fetch(`/api/analytics/advanced/overview/?${params}`),
        fetch(`/api/analytics/advanced/activity/?${params}`),
        fetch(`/api/analytics/advanced/popular-designs/?${params}`),
        fetch(`/api/analytics/advanced/team-activity/?${params}`),
        fetch(`/api/analytics/advanced/category-breakdown/?${params}`),
      ]);

      if (overviewRes.ok) setOverview(await overviewRes.json());
      if (activityRes.ok) setActivityData((await activityRes.json()).data || []);
      if (designsRes.ok) setPopularDesigns((await designsRes.json()).results || []);
      if (teamRes.ok) setTeamActivity((await teamRes.json()).results || []);
      if (categoryRes.ok) setCategoryBreakdown((await categoryRes.json()).data || []);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      // Mock data
      setOverview({
        totalProjects: 24,
        activeProjects: 8,
        totalDesigns: 156,
        totalExports: 89,
        avgDesignTime: 45,
        collaborators: 12,
        aiGenerations: 234,
        storageUsed: 2.5,
        storageLimit: 10,
      });
      setActivityData([
        { date: '2024-02-19', designs_created: 5, exports: 3, ai_requests: 12 },
        { date: '2024-02-20', designs_created: 8, exports: 5, ai_requests: 18 },
        { date: '2024-02-21', designs_created: 3, exports: 2, ai_requests: 8 },
        { date: '2024-02-22', designs_created: 12, exports: 8, ai_requests: 25 },
        { date: '2024-02-23', designs_created: 7, exports: 4, ai_requests: 15 },
        { date: '2024-02-24', designs_created: 9, exports: 6, ai_requests: 20 },
        { date: '2024-02-25', designs_created: 11, exports: 7, ai_requests: 22 },
      ]);
      setPopularDesigns([
        { id: '1', name: 'Homepage Hero Banner', views: 245, exports: 23, shares: 12, thumbnail: '/designs/hero.jpg' },
        { id: '2', name: 'Product Launch Social', views: 189, exports: 18, shares: 8, thumbnail: '/designs/launch.jpg' },
        { id: '3', name: 'Newsletter Template', views: 156, exports: 15, shares: 5, thumbnail: '/designs/newsletter.jpg' },
        { id: '4', name: 'Team Presentation', views: 134, exports: 12, shares: 7, thumbnail: '/designs/presentation.jpg' },
      ]);
      setTeamActivity([
        { id: '1', name: 'John Doe', avatar: '/avatars/john.jpg', designs: 45, exports: 28, active: true },
        { id: '2', name: 'Jane Smith', avatar: '/avatars/jane.jpg', designs: 38, exports: 22, active: true },
        { id: '3', name: 'Mike Johnson', avatar: '/avatars/mike.jpg', designs: 31, exports: 19, active: false },
        { id: '4', name: 'Sarah Williams', avatar: '/avatars/sarah.jpg', designs: 42, exports: 20, active: true },
      ]);
      setCategoryBreakdown([
        { label: 'Social Media', value: 45 },
        { label: 'Presentations', value: 25 },
        { label: 'Marketing', value: 15 },
        { label: 'Web Design', value: 10 },
        { label: 'Print', value: 5 },
      ]);
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const TIME_RANGES = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' },
    { value: '1y', label: 'Last year' },
  ];

  const maxActivity = Math.max(
    ...activityData.map((d) => Math.max(d.designs_created, d.exports, d.ai_requests)),
    1
  );

  const categoryColors = ['bg-purple-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-red-500'];
  const totalCategoryValue = categoryBreakdown.reduce((sum, c) => sum + c.value, 0);

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
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-500">Track your design performance and team productivity</p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as TimeRange)}
              className="px-4 py-2 border rounded-lg bg-white focus:ring-2 focus:ring-purple-500"
            >
              {TIME_RANGES.map((range) => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>
            <button className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700">
              Export Report
            </button>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Designs</p>
                <p className="text-3xl font-bold text-gray-900">{overview?.totalDesigns || 0}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🎨</span>
              </div>
            </div>
            <div className="mt-2 flex items-center text-sm">
              <span className="text-green-600">↑ 12%</span>
              <span className="text-gray-400 ml-2">vs last period</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Exports</p>
                <p className="text-3xl font-bold text-gray-900">{overview?.totalExports || 0}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📤</span>
              </div>
            </div>
            <div className="mt-2 flex items-center text-sm">
              <span className="text-green-600">↑ 8%</span>
              <span className="text-gray-400 ml-2">vs last period</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">AI Generations</p>
                <p className="text-3xl font-bold text-gray-900">{overview?.aiGenerations || 0}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🤖</span>
              </div>
            </div>
            <div className="mt-2 flex items-center text-sm">
              <span className="text-green-600">↑ 25%</span>
              <span className="text-gray-400 ml-2">vs last period</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg. Design Time</p>
                <p className="text-3xl font-bold text-gray-900">{overview?.avgDesignTime || 0}m</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">⏱️</span>
              </div>
            </div>
            <div className="mt-2 flex items-center text-sm">
              <span className="text-red-600">↓ 5%</span>
              <span className="text-gray-400 ml-2">faster than before</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Activity Chart */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Activity Overview</h3>
            <div className="flex items-center gap-4 mb-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-purple-500 rounded" />
                <span className="text-sm text-gray-600">Designs</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded" />
                <span className="text-sm text-gray-600">Exports</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded" />
                <span className="text-sm text-gray-600">AI Requests</span>
              </div>
            </div>
            <div className="h-64 flex items-end gap-2">
              {activityData.map((data, index) => (
                <div key={index} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full flex gap-1 items-end" style={{ height: '200px' }}>
                    <div
                      className="flex-1 bg-purple-500 rounded-t"
                      style={{ height: `${(data.designs_created / maxActivity) * 100}%`, minHeight: '4px' }}
                    />
                    <div
                      className="flex-1 bg-blue-500 rounded-t"
                      style={{ height: `${(data.exports / maxActivity) * 100}%`, minHeight: '4px' }}
                    />
                    <div
                      className="flex-1 bg-green-500 rounded-t"
                      style={{ height: `${(data.ai_requests / maxActivity) * 100}%`, minHeight: '4px' }}
                    />
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(data.date).toLocaleDateString('en-US', { weekday: 'short' })}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Design Categories</h3>
            {/* Simple Pie Chart Visualization */}
            <div className="relative w-48 h-48 mx-auto mb-4">
              <svg viewBox="0 0 100 100" className="transform -rotate-90">
                {categoryBreakdown.reduce((acc, category, index) => {
                  const prevTotal = categoryBreakdown.slice(0, index).reduce((s, c) => s + c.value, 0);
                  const percentage = (category.value / totalCategoryValue) * 100;
                  const offset = (prevTotal / totalCategoryValue) * 100;
                  const colors = ['#8B5CF6', '#3B82F6', '#10B981', '#F59E0B', '#EF4444'];
                  
                  acc.push(
                    <circle
                      key={category.label}
                      cx="50"
                      cy="50"
                      r="40"
                      fill="transparent"
                      stroke={colors[index % colors.length]}
                      strokeWidth="20"
                      strokeDasharray={`${percentage * 2.51} ${251 - percentage * 2.51}`}
                      strokeDashoffset={`${-offset * 2.51}`}
                    />
                  );
                  return acc;
                }, [] as React.ReactNode[])}
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{totalCategoryValue}</p>
                  <p className="text-xs text-gray-500">Total</p>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              {categoryBreakdown.map((category, index) => (
                <div key={category.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded ${categoryColors[index % categoryColors.length]}`} />
                    <span className="text-sm text-gray-600">{category.label}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {((category.value / totalCategoryValue) * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Popular Designs */}
          <div className="bg-white rounded-lg shadow-sm">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold text-gray-900">Popular Designs</h3>
              <a href="/designs" className="text-sm text-purple-600 hover:underline">
                View All
              </a>
            </div>
            <div className="divide-y">
              {popularDesigns.map((design, index) => (
                <div key={design.id} className="flex items-center gap-4 p-4">
                  <span className="text-lg font-bold text-gray-300 w-6">{index + 1}</span>
                  <div className="w-12 h-9 bg-gray-100 rounded flex items-center justify-center">
                    <span className="text-xs text-gray-400">IMG</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">{design.name}</h4>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>{design.views} views</span>
                      <span>{design.exports} exports</span>
                      <span>{design.shares} shares</span>
                    </div>
                  </div>
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Team Activity */}
          <div className="bg-white rounded-lg shadow-sm">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold text-gray-900">Team Activity</h3>
              <a href="/team" className="text-sm text-purple-600 hover:underline">
                Manage Team
              </a>
            </div>
            <div className="divide-y">
              {teamActivity.map((member) => (
                <div key={member.id} className="flex items-center gap-4 p-4">
                  <div className="relative">
                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center text-sm font-medium">
                      {member.name.split(' ').map((n) => n[0]).join('')}
                    </div>
                    {member.active && (
                      <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-white" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">{member.name}</h4>
                    <p className="text-xs text-gray-500">
                      {member.designs} designs • {member.exports} exports
                    </p>
                  </div>
                  <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-purple-500 rounded-full"
                      style={{ width: `${(member.designs / 50) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Storage Usage */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-gray-900">Storage Usage</h3>
              <p className="text-sm text-gray-500">
                {overview?.storageUsed?.toFixed(1) || 0} GB of {overview?.storageLimit || 10} GB used
              </p>
            </div>
            <button className="text-sm text-purple-600 hover:underline">Upgrade Storage</button>
          </div>
          <div className="w-full h-4 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-linear-to-r from-purple-500 to-indigo-500 rounded-full transition-all duration-500"
              style={{
                width: `${((overview?.storageUsed || 0) / (overview?.storageLimit || 10)) * 100}%`,
              }}
            />
          </div>
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>0 GB</span>
            <span>{overview?.storageLimit || 10} GB</span>
          </div>
        </div>
      </div>
    </div>
  );
}
