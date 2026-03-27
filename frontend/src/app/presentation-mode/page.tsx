"use client";

import React from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Presentation } from 'lucide-react';

export default function PresentationModePage() {
  return (
    <div className="flex h-screen">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <Presentation className="h-8 w-8 text-blue-600" />
                Presentation Mode
              </h1>
              <p className="text-gray-600">Present your designs professionally</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Design Presentations</CardTitle>
                <CardDescription>Showcase your work to clients and stakeholders</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Present your designs in fullscreen mode with navigation controls, annotations, 
                  and presenter notes. Perfect for client reviews and design showcases.
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
