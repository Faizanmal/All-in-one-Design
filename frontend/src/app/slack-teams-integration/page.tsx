"use client";

import React from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Slack } from 'lucide-react';

export default function SlackTeamsIntegrationPage() {
  return (
    <div className="flex h-screen">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <Slack className="h-8 w-8 text-blue-600" />
                Slack & Teams Integration
              </h1>
              <p className="text-gray-600">Connect with Slack and Microsoft Teams</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Workspace Integration</CardTitle>
                <CardDescription>Sync with your team collaboration tools</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Receive notifications, share designs, and collaborate directly from Slack or 
                  Microsoft Teams. Keep your team in sync with real-time updates.
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
