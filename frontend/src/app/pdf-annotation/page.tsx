"use client";

import React from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileType } from 'lucide-react';

export default function PdfAnnotationPage() {
  return (
    <div className="flex h-screen">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                <FileType className="h-8 w-8 text-blue-600" />
                PDF Annotation
              </h1>
              <p className="text-gray-600">Annotate and markup PDF documents</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>PDF Annotation Tools</CardTitle>
                <CardDescription>Add notes and markup to PDFs</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Review and annotate PDF designs with comments, highlights, shapes, and drawings. 
                  Collaborate on design reviews with PDF markup tools.
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
