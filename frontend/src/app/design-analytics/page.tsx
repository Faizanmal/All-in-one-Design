"use client";

import React from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity } from 'lucide-react';

export default function DesignAnalyticsPage() {
  return (
    <div className="flex h-screen">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <Activity className="h-8 w-8 text-blue-600" />
                Design Analytics
              </h1>
              <p className="text-gray-600">Track design performance and metrics</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Design Performance Metrics</CardTitle>
                <CardDescription>Understand how your designs perform</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Track views, engagement, conversion rates, and user interactions with your designs. 
                  Get insights to improve design effectiveness and ROI.
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
