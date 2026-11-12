'use client';

import { MainHeader } from '@/components/layout/MainHeader';
import { GeneralAnalyticsDashboard } from '@/components/features/general-analytics/GeneralAnalyticsDashboard';

export default function AnalyticsPage() {
  return <div className="min-h-screen bg-background"><MainHeader /><main className="container mx-auto p-6 space-y-6"><div><h1 className="text-3xl font-bold">Analytics Dashboard</h1><p className="text-muted-foreground">Track your projects, AI usage, and activity.</p></div><GeneralAnalyticsDashboard /></main></div>;
}
