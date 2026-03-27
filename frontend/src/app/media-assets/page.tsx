"use client";

import React from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ImageIcon } from 'lucide-react';

export default function MediaAssetsPage() {
  return (
    <div className="flex h-screen">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <ImageIcon className="h-8 w-8 text-blue-600" />
                Media Assets
              </h1>
              <p className="text-gray-600">Stock photos, videos, and media library</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Media Asset Library</CardTitle>
                <CardDescription>Access millions of stock photos and videos</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Browse and use high-quality stock photos, videos, illustrations, and icons. 
                  Upload and manage your own media assets in one place.
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
