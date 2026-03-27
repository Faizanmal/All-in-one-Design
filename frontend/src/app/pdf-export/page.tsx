"use client";

import React from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileDown } from 'lucide-react';

export default function PdfExportPage() {
  return (
    <div className="flex h-screen">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <FileDown className="h-8 w-8 text-blue-600" />
                PDF Export
              </h1>
              <p className="text-gray-600">Export designs to high-quality PDFs</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>PDF Export Tools</CardTitle>
                <CardDescription>Create print-ready PDF files</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Export your designs to PDF with customizable settings for quality, compression, 
                  color profiles, and bleed. Perfect for print and digital distribution.
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
