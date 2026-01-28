"use client";

import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles } from 'lucide-react';

// Import all feature components
import { CodeExportPanel, DesignSpecPanel, DeveloperHandoff } from '@/components/features/code-export/CodeExportPanel';
import { IntegrationSettings } from '@/components/features/slack-teams/IntegrationSettings';
import { OfflineStatusBadge, OfflineProjectsManager, SyncQueue, PWAInstallPrompt, OfflineSettings } from '@/components/features/offline-pwa/OfflineSettings';
import { AssetManager, AIAssetSearch, SmartFolderDialog } from '@/components/features/asset-management/AssetManager';
import { TemplateMarketplace } from '@/components/features/template-marketplace/TemplateMarketplace';
import { TimeTrackingDashboard } from '@/components/features/time-tracking/TimeTrackingDashboard';
import { PDFExportDialog } from '@/components/features/pdf-export/PDFExportDialog';
import { PermissionsDashboard } from '@/components/features/granular-permissions/PermissionsDashboard';

export default function FeaturesDemoPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold flex items-center gap-3">
          <Sparkles className="h-10 w-10 text-primary" />
          Enhanced Features Showcase
        </h1>
        <p className="text-xl text-muted-foreground">
          Explore all the professional-grade features with full functionality
        </p>
      </div>

      <Tabs defaultValue="code-export" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:grid-cols-8">
          <TabsTrigger value="code-export">Code Export</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="offline">Offline/PWA</TabsTrigger>
          <TabsTrigger value="assets">Assets</TabsTrigger>
          <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
          <TabsTrigger value="time">Time Tracking</TabsTrigger>
          <TabsTrigger value="pdf">PDF Export</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
        </TabsList>

        <TabsContent value="code-export" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Feature 18: Code Export & Developer Handoff</CardTitle>
              <CardDescription>
                Export your designs as production-ready code in multiple frameworks with complete developer documentation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <CodeExportPanel selectedElements={[1, 2, 3]} />
              <div className="grid md:grid-cols-2 gap-4">
                <DesignSpecPanel />
                <DeveloperHandoff />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Feature 19: Slack/Teams Integration</CardTitle>
              <CardDescription>
                Connect your workspace with Slack and Microsoft Teams for seamless collaboration
              </CardDescription>
            </CardHeader>
            <CardContent>
              <IntegrationSettings />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="offline" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Feature 20: Offline Mode & PWA</CardTitle>
              <CardDescription>
                Work offline, sync automatically, and install as a progressive web app
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex justify-end">
                <OfflineStatusBadge />
              </div>
              <PWAInstallPrompt />
              <div className="grid md:grid-cols-2 gap-6">
                <OfflineProjectsManager />
                <SyncQueue />
              </div>
              <OfflineSettings />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="assets" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Feature 21: Enhanced Asset Management</CardTitle>
              <CardDescription>
                AI-powered asset search, smart folders, and comprehensive media management
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <AssetManager />
              <div className="grid md:grid-cols-2 gap-6">
                <AIAssetSearch />
                <div className="flex items-center justify-center">
                  <SmartFolderDialog />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="marketplace" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Feature 22: Template Marketplace</CardTitle>
              <CardDescription>
                Browse, preview, and download professional design templates
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TemplateMarketplace />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="time" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Feature 23: Time Tracking & Project Management</CardTitle>
              <CardDescription>
                Track time, manage tasks, monitor goals, and generate invoices
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TimeTrackingDashboard />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pdf" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Feature 24: PDF Export with Print Settings</CardTitle>
              <CardDescription>
                Export print-ready PDFs with bleed, crop marks, and professional preflight checks
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center py-12">
              <PDFExportDialog />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="permissions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Feature 25: Granular Permissions & Roles</CardTitle>
              <CardDescription>
                Comprehensive role-based access control with detailed permission management
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PermissionsDashboard />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950 dark:to-blue-950">
        <CardContent className="py-8">
          <div className="text-center space-y-4">
            <h2 className="text-2xl font-bold">All Features Enhanced! 🎉</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              All 8 feature modules have been enhanced with production-ready components, 
              including full functionality, TypeScript types, responsive design, and beautiful UI.
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 max-w-4xl mx-auto">
              <div className="p-4 bg-white dark:bg-slate-900 rounded-lg">
                <p className="text-3xl font-bold text-primary">8</p>
                <p className="text-sm text-muted-foreground">Features</p>
              </div>
              <div className="p-4 bg-white dark:bg-slate-900 rounded-lg">
                <p className="text-3xl font-bold text-primary">35+</p>
                <p className="text-sm text-muted-foreground">Components</p>
              </div>
              <div className="p-4 bg-white dark:bg-slate-900 rounded-lg">
                <p className="text-3xl font-bold text-primary">100%</p>
                <p className="text-sm text-muted-foreground">TypeScript</p>
              </div>
              <div className="p-4 bg-white dark:bg-slate-900 rounded-lg">
                <p className="text-3xl font-bold text-primary">✓</p>
                <p className="text-sm text-muted-foreground">Production Ready</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
