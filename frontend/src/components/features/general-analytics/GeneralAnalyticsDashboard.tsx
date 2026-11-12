'use client';

import { useGeneralAnalytics } from '@/hooks/useGeneralAnalytics';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function GeneralAnalyticsDashboard() {
  const { dashboardStats: stats, recentActivities, aiUsageSummary: usage, isLoading, error, refreshStats } = useGeneralAnalytics();
  if (isLoading) return <p role="status" className="p-6">Loading analytics…</p>;
  if (error) return <div role="alert" className="space-y-3 p-6"><p>{error}</p><Button onClick={() => void refreshStats()}>Retry</Button></div>;
  if (!stats || !usage) return null;

  const services = Object.entries(usage.by_service);
  const totalRequests = usage.summary.total_requests;
  const successRate = usage.summary.success_rate;
  const money = (value: number | string | null) => Number(value ?? 0).toFixed(2);
  const chart = stats.daily_chart_data.map(day => ({
    date: day.date, projects: day.projects_created, exports: day.projects_exported, aiRequests: day.ai_generations_count,
  }));
  const mostUsed = [...services].sort((a, b) => b[1].count - a[1].count)[0];
  const activity = (
    <Card>
      <CardHeader><CardTitle>Recent activity</CardTitle><CardDescription>Your events from the last 24 hours</CardDescription></CardHeader>
      <CardContent>
        {recentActivities.length === 0 ? <p className="text-muted-foreground">No recent activity.</p> : (
          <ol className="space-y-4">{recentActivities.map(event => (
            <li key={event.id} className="border-b pb-3 last:border-0">
              <p className="font-medium capitalize">{event.activity_type.replace(/_/g, ' ')}</p>
              <p className="text-sm text-muted-foreground">{Object.entries(event.metadata ?? {}).map(([key, value]) => `${key.replace(/_/g, ' ')}: ${typeof value === 'object' ? JSON.stringify(value) : String(value)}`).join(' · ')}</p>
              <time className="text-xs text-muted-foreground" dateTime={event.timestamp}>{new Date(event.timestamp).toLocaleString()}</time>
            </li>
          ))}</ol>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center gap-4"><p className="text-sm text-muted-foreground">Live account data · Usage totals cover the last 30 days</p><Button variant="outline" onClick={() => void refreshStats()}>Refresh</Button></div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Total projects', value: stats.projects.total, detail: `${stats.projects.this_week} created this week` },
          { label: 'AI requests (30 days)', value: stats.ai_usage.this_month.requests, detail: `${stats.ai_usage.today.requests} today` },
          { label: 'AI cost (30 days)', value: `$${money(stats.ai_usage.this_month.cost)}`, detail: 'Estimated provider cost' },
          { label: 'Storage used', value: `${stats.assets.storage_mb.toFixed(2)} MB`, detail: `${stats.assets.total} assets` },
        ].map(stat => <Card key={stat.label}><CardHeader><CardTitle className="text-sm">{stat.label}</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{stat.value}</p><p className="text-sm text-muted-foreground">{stat.detail}</p></CardContent></Card>)}
      </div>
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid grid-cols-4 w-full"><TabsTrigger value="overview">Overview</TabsTrigger><TabsTrigger value="ai">AI usage</TabsTrigger><TabsTrigger value="activity">Activity</TabsTrigger><TabsTrigger value="insights">Insights</TabsTrigger></TabsList>
        <TabsContent value="overview" className="space-y-6">
          <Card><CardHeader><CardTitle>Daily usage</CardTitle><CardDescription>Projects created, exports, and AI generations recorded in daily summaries</CardDescription></CardHeader><CardContent>
            {chart.length === 0 ? <p className="text-muted-foreground">No daily summaries yet. Usage history appears after the daily analytics task runs.</p> : <ResponsiveContainer width="100%" height={300}><AreaChart data={chart}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis allowDecimals={false} /><Tooltip /><Area type="monotone" dataKey="projects" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.15} /><Area type="monotone" dataKey="aiRequests" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.15} /><Area type="monotone" dataKey="exports" stroke="#10b981" fill="#10b981" fillOpacity={0.15} /></AreaChart></ResponsiveContainer>}
          </CardContent></Card>
          {activity}
        </TabsContent>
        <TabsContent value="ai"><Card><CardHeader><CardTitle>AI usage breakdown</CardTitle><CardDescription>{(usage.summary.total_tokens ?? 0).toLocaleString()} tokens · ${money(usage.summary.total_cost)} estimated cost · Success rate: {successRate === null ? 'No requests yet' : `${(successRate * 100).toFixed(1)}%`}</CardDescription></CardHeader><CardContent>
          {totalRequests === 0 ? <p className="text-muted-foreground">No AI requests in the last 30 days.</p> : <div className="overflow-x-auto"><table className="w-full text-sm text-left"><thead><tr><th className="p-2">Service</th><th className="p-2">Requests</th><th className="p-2">Tokens</th><th className="p-2">Cost</th></tr></thead><tbody>{services.map(([service, data]) => <tr key={service} className="border-t"><td className="p-2 capitalize">{service.replace(/_/g, ' ')}</td><td className="p-2">{data.count}</td><td className="p-2">{(data.tokens ?? 0).toLocaleString()}</td><td className="p-2">${money(data.cost)}</td></tr>)}</tbody></table></div>}
        </CardContent></Card></TabsContent>
        <TabsContent value="activity">{activity}</TabsContent>
        <TabsContent value="insights"><Card><CardHeader><CardTitle>Account insights</CardTitle><CardDescription>Recommendations based on your recorded usage</CardDescription></CardHeader><CardContent><ul className="space-y-3 list-disc pl-5">
          <li>{stats.projects.total === 0 ? 'Create your first project to start tracking design activity.' : `${stats.projects.this_week} of your ${stats.projects.total} projects were created in the last seven days.`}</li>
          <li>{totalRequests === 0 ? 'Use the AI design tools to see request and cost insights here.' : `${mostUsed?.[0].replace(/_/g, ' ')} is your most used AI service (${mostUsed?.[1].count} requests). Average cost per request: $${(Number(usage.summary.total_cost ?? 0) / totalRequests).toFixed(4)}.`}</li>
          {successRate !== null && successRate < 0.95 && <li>Some AI requests failed. Check provider configuration and retry failed generations.</li>}
          <li>{stats.assets.total === 0 ? 'Uploaded assets will appear in your storage totals.' : `Your ${stats.assets.total} assets use ${stats.assets.storage_mb.toFixed(2)} MB. Remove unused assets to reduce storage.`}</li>
        </ul></CardContent></Card></TabsContent>
      </Tabs>
    </div>
  );
}
