"use client";

import React from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Database } from 'lucide-react';

export default function AdvancedIntegrationsPage() {
  return (
    <div className="flex h-screen">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <Database className="h-8 w-8 text-blue-600" />
                Advanced Integrations
              </h1>
              <p className="text-gray-600">API, webhooks, and custom integrations</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Developer Integration Tools</CardTitle>
                <CardDescription>Build custom integrations with our API</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Access our powerful API, configure webhooks, and build custom integrations. 
                  Perfect for enterprises and developers needing advanced automation.
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
