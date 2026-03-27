"use client";

import React from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Smartphone } from 'lucide-react';

export default function MobileApiPage() {
  return (
    <div className="flex h-screen">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <Smartphone className="h-8 w-8 text-blue-600" />
                Mobile API
              </h1>
              <p className="text-gray-600">Mobile SDK and API for app integration</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Mobile Development SDK</CardTitle>
                <CardDescription>Build mobile apps with our SDK</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Integrate design capabilities into your mobile apps with our iOS and Android SDKs. 
                  Access the full power of our platform from native mobile applications.
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
