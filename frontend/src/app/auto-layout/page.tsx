"use client";

import React from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Grid } from 'lucide-react';

export default function AutoLayoutPage() {
  return (
    <div className="flex h-screen">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <Grid className="h-8 w-8 text-blue-600" />
                Auto Layout
              </h1>
              <p className="text-gray-600">Smart layout system for responsive designs</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Auto Layout System</CardTitle>
                <CardDescription>Intelligent layout that adapts to content</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Create responsive designs that automatically adjust to content changes. 
                  Use auto layout constraints, padding, and spacing for professional results.
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
