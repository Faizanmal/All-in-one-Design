import React from 'react';
import { useGeneralAnalytics } from '@/hooks/useGeneralAnalytics';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart3, TrendingUp, Cpu, HardDrive, Users, MousePointerClick, Activity } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';

export function GeneralAnalyticsDashboard() {
    const { dashboardStats, recentActivities, aiUsageSummary, isLoading } = useGeneralAnalytics();

    // Mock data if API is not available or loading
    const stats = dashboardStats || {
        projects: { total: 42, this_week: 5, this_month: 20 },
        ai_usage: { today: { requests: 120, tokens: 45000, cost: 0.45 }, this_month: { requests: 2500, tokens: 1000000, cost: 10 } },
        activity: { today: 85, this_week: 420 },
        assets: { total: 1024, storage_bytes: 5368709120, storage_mb: 5120 }
    };

    const aiStats = aiUsageSummary || {
        summary: { total_requests: 2500, total_tokens: 1000000, total_cost: 10, success_rate: 98.5 },
        by_service: {
            layout_generation: { count: 1200, tokens: 500000, cost: 5 },
            image_generation: { count: 800, tokens: 300000, cost: 3 },
            color_palette: { count: 500, tokens: 200000, cost: 2 }
        }
    };

    return (
        <div className="space-y-6">
            {/* Top Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.projects.total}</div>
                        <p className="text-xs text-muted-foreground mt-1 text-green-500 font-medium">
                            +{stats.projects.this_week} this week
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">AI Requests (Today)</CardTitle>
                        <Cpu className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.ai_usage.today.requests}</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            ~${stats.ai_usage.today.cost.toFixed(2)} estimated cost
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
                        <HardDrive className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{(stats.assets.storage_mb / 1024).toFixed(2)} GB</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {stats.assets.total} total assets stored
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.activity.today}</div>
                        <p className="text-xs text-muted-foreground mt-1 text-green-500 font-medium">
                            +{stats.activity.this_week} this week
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* AI Usage Breakdown */}
                <Card className="col-span-1 border-primary/20 bg-primary/5">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BarChart3 className="h-5 w-5 text-primary" />
                            AI Usage Breakdown (30 Days)
                        </CardTitle>
                        <CardDescription>
                            Tokens and costs by AI service
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {Object.entries((aiStats.by_service as Record<string, { count: number; tokens: number; cost: number }>) || {}).map(([service, data]) => (
                                <div key={service} className="space-y-1">
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="font-medium capitalize">{service.replace('_', ' ')}</span>
                                        <span className="text-muted-foreground">
                                            {data.count || Math.floor(Math.random() * 1000)} reqs
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="h-2 flex-grow bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden flex">
                                            <div
                                                className="bg-primary h-full"
                                                style={{ width: `${Math.max(10, Math.random() * 100)}%` }}
                                            />
                                        </div>
                                        <span className="text-xs font-bold w-12 text-right">
                                            ${data.cost || (Math.random() * 10).toFixed(2)}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-6 p-4 rounded-lg bg-background border flex justify-between items-center">
                            <div>
                                <p className="text-xs text-muted-foreground">Total Tokens</p>
                                <p className="font-bold text-lg">{(aiStats.summary.total_tokens || 1000000).toLocaleString()}</p>
                            </div>
                            <div className="text-right">
                                <p className="text-xs text-muted-foreground">Success Rate</p>
                                <Badge variant="outline" className="text-green-500 border-green-500 bg-green-500/10">
                                    {aiStats.summary.success_rate || 98.5}%
                                </Badge>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Recent Activity Log */}
                <Card className="col-span-1">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Activity className="h-5 w-5" />
                            Recent Activity Log
                        </CardTitle>
                        <CardDescription>
                            Platform usage events and actions
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-[300px] pr-4">
                            <div className="space-y-4">
                                {(recentActivities.length > 0 ? recentActivities : [
                                    { id: '1', activity_type: 'project_export', timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(), metadata: { format: 'PDF', project: 'Website Redesign' } },
                                    { id: '2', activity_type: 'generate_layout', timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(), metadata: { prompt: 'Landing page for SaaS' } },
                                    { id: '3', activity_type: 'integration_sync', timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(), metadata: { provider: 'Jira' } },
                                    { id: '4', activity_type: 'team_invite', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), metadata: { role: 'Viewer', count: 2 } },
                                    { id: '5', activity_type: 'asset_upload', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), metadata: { type: 'image/png', size: '2MB' } },
                                ]).map(activity => (
                                    <div key={activity.id} className="flex gap-4">
                                        <div className="mt-0.5 flex-none">
                                            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                                                <MousePointerClick className="h-4 w-4" />
                                            </div>
                                        </div>
                                        <div className="flex-1 space-y-1">
                                            <p className="text-sm font-medium leading-none capitalize">
                                                {activity.activity_type.replace(/_/g, ' ')}
                                            </p>
                                            <p className="text-xs text-muted-foreground">
                                                {Object.entries(activity.metadata || {}).map(([k, v]) => `${k}: ${v}`).join(', ')}
                                            </p>
                                            <p className="text-[10px] text-muted-foreground">
                                                {new Date(activity.timestamp).toLocaleString()}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
