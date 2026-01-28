'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import {
  CheckCircle,
  Cloud,
  Code,
  ExternalLink,
  FileText,
  Globe,
  Grid,
  Link2,
  MessageSquare,
  Palette,
  Plus,
  Search,
  Settings,
  Share2,
  Webhook,
} from 'lucide-react';

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  isConnected: boolean;
  isPremium: boolean;
}

interface Webhook {
  id: string;
  name: string;
  url: string;
  events: string[];
  isActive: boolean;
  lastTriggered?: string;
}

export default function IntegrationsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data
  const integrations: Integration[] = [
    {
      id: '1',
      name: 'Slack',
      description: 'Get notifications and share designs directly to Slack channels',
      icon: '💬',
      category: 'collaboration',
      isConnected: true,
      isPremium: false,
    },
    {
      id: '2',
      name: 'Jira',
      description: 'Create and link design tasks with Jira issues',
      icon: '📋',
      category: 'project_management',
      isConnected: true,
      isPremium: false,
    },
    {
      id: '3',
      name: 'Adobe Creative Cloud',
      description: 'Sync with Photoshop, Illustrator, and CC Libraries',
      icon: '🎨',
      category: 'design',
      isConnected: false,
      isPremium: true,
    },
    {
      id: '4',
      name: 'Google Drive',
      description: 'Auto-backup and sync your designs to Google Drive',
      icon: '☁️',
      category: 'cloud_storage',
      isConnected: true,
      isPremium: false,
    },
    {
      id: '5',
      name: 'Notion',
      description: 'Embed designs and sync project data to Notion',
      icon: '📝',
      category: 'collaboration',
      isConnected: false,
      isPremium: false,
    },
    {
      id: '6',
      name: 'Dropbox',
      description: 'Store and share design files on Dropbox',
      icon: '📦',
      category: 'cloud_storage',
      isConnected: false,
      isPremium: false,
    },
    {
      id: '7',
      name: 'WordPress',
      description: 'Publish designs directly to WordPress sites',
      icon: '🌐',
      category: 'cms',
      isConnected: false,
      isPremium: true,
    },
    {
      id: '8',
      name: 'Zapier',
      description: 'Connect with 5000+ apps through Zapier automations',
      icon: '⚡',
      category: 'automation',
      isConnected: true,
      isPremium: false,
    },
  ];

  const webhooks: Webhook[] = [
    {
      id: '1',
      name: 'Design Export Webhook',
      url: 'https://api.example.com/webhook/design-export',
      events: ['design.exported'],
      isActive: true,
      lastTriggered: '2 hours ago',
    },
    {
      id: '2',
      name: 'Comment Notification',
      url: 'https://api.example.com/webhook/comments',
      events: ['comment.added', 'comment.resolved'],
      isActive: true,
      lastTriggered: '1 day ago',
    },
    {
      id: '3',
      name: 'Project Updates',
      url: 'https://api.example.com/webhook/projects',
      events: ['project.created', 'project.updated'],
      isActive: false,
    },
  ];

  const categories = [
    { id: 'all', name: 'All', icon: <Grid className="h-4 w-4" /> },
    { id: 'collaboration', name: 'Collaboration', icon: <MessageSquare className="h-4 w-4" /> },
    { id: 'design', name: 'Design Tools', icon: <Palette className="h-4 w-4" /> },
    { id: 'cloud_storage', name: 'Cloud Storage', icon: <Cloud className="h-4 w-4" /> },
    { id: 'project_management', name: 'Project Management', icon: <FileText className="h-4 w-4" /> },
    { id: 'cms', name: 'CMS', icon: <Globe className="h-4 w-4" /> },
  ];

  const filteredIntegrations = integrations.filter((integration) => {
    const matchesSearch =
      integration.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      integration.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeTab === 'all' || integration.category === activeTab;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Header */}
      <header className="border-b border-white/10 bg-gray-900/50 backdrop-blur-lg">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600">
              <Link2 className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-white">Integrations Hub</h1>
              <p className="text-sm text-gray-400">Connect your favorite tools</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
              <Input
                placeholder="Search integrations..."
                className="w-64 border-white/20 bg-gray-800/50 pl-9 text-white"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Tabs defaultValue="integrations">
          <TabsList className="mb-6 bg-gray-800/50">
            <TabsTrigger value="integrations" className="data-[state=active]:bg-blue-500/20">
              <Link2 className="mr-2 h-4 w-4" />
              Integrations
            </TabsTrigger>
            <TabsTrigger value="webhooks" className="data-[state=active]:bg-blue-500/20">
              <Webhook className="mr-2 h-4 w-4" />
              Webhooks
            </TabsTrigger>
            <TabsTrigger value="api" className="data-[state=active]:bg-blue-500/20">
              <Code className="mr-2 h-4 w-4" />
              API
            </TabsTrigger>
          </TabsList>

          {/* Integrations Tab */}
          <TabsContent value="integrations">
            <div className="grid gap-6 lg:grid-cols-4">
              {/* Categories Sidebar */}
              <div className="lg:col-span-1">
                <Card className="border-white/10 bg-gray-900/50">
                  <CardHeader>
                    <CardTitle className="text-white">Categories</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {categories.map((category) => (
                        <button
                          key={category.id}
                          onClick={() => setActiveTab(category.id)}
                          className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors ${
                            activeTab === category.id
                              ? 'bg-blue-500/20 text-blue-400'
                              : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
                          }`}
                        >
                          {category.icon}
                          <span>{category.name}</span>
                        </button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Integrations Grid */}
              <div className="lg:col-span-3">
                <div className="grid gap-4 md:grid-cols-2">
                  {filteredIntegrations.map((integration) => (
                    <Card key={integration.id} className="border-white/10 bg-gray-900/50">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-4">
                            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-800 text-2xl">
                              {integration.icon}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <h3 className="font-medium text-white">{integration.name}</h3>
                                {integration.isPremium && (
                                  <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
                                    Pro
                                  </Badge>
                                )}
                              </div>
                              <p className="mt-1 text-sm text-gray-400">{integration.description}</p>
                            </div>
                          </div>
                        </div>
                        <div className="mt-4 flex items-center justify-between">
                          {integration.isConnected ? (
                            <div className="flex items-center gap-2 text-green-400">
                              <CheckCircle className="h-4 w-4" />
                              <span className="text-sm">Connected</span>
                            </div>
                          ) : (
                            <span className="text-sm text-gray-500">Not connected</span>
                          )}
                          <Button
                            variant={integration.isConnected ? 'outline' : 'default'}
                            size="sm"
                            className={
                              integration.isConnected
                                ? 'border-white/20 text-white'
                                : 'bg-blue-600 hover:bg-blue-700'
                            }
                          >
                            {integration.isConnected ? (
                              <>
                                <Settings className="mr-2 h-4 w-4" />
                                Settings
                              </>
                            ) : (
                              <>
                                <Plus className="mr-2 h-4 w-4" />
                                Connect
                              </>
                            )}
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Webhooks Tab */}
          <TabsContent value="webhooks">
            <Card className="border-white/10 bg-gray-900/50">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-white">Webhook Endpoints</CardTitle>
                  <CardDescription>Receive real-time updates for design events</CardDescription>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="mr-2 h-4 w-4" />
                  Add Webhook
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {webhooks.map((webhook) => (
                    <div
                      key={webhook.id}
                      className="rounded-lg border border-white/10 bg-gray-800/50 p-4"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/20">
                            <Webhook className="h-5 w-5 text-blue-400" />
                          </div>
                          <div>
                            <h3 className="font-medium text-white">{webhook.name}</h3>
                            <code className="text-sm text-gray-400">{webhook.url}</code>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <Switch checked={webhook.isActive} />
                          <Button variant="ghost" size="sm" className="text-gray-400">
                            <Settings className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="mt-3 flex items-center gap-2">
                        <span className="text-sm text-gray-500">Events:</span>
                        {webhook.events.map((event) => (
                          <Badge key={event} className="bg-gray-700 text-gray-300">
                            {event}
                          </Badge>
                        ))}
                        {webhook.lastTriggered && (
                          <span className="ml-auto text-sm text-gray-500">
                            Last triggered: {webhook.lastTriggered}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* API Tab */}
          <TabsContent value="api">
            <div className="grid gap-6 lg:grid-cols-2">
              <Card className="border-white/10 bg-gray-900/50">
                <CardHeader>
                  <CardTitle className="text-white">API Documentation</CardTitle>
                  <CardDescription>Build custom integrations with our REST API</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="rounded-lg border border-white/10 bg-gray-800/50 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-white">REST API v1</h4>
                        <p className="text-sm text-gray-400">Full access to all resources</p>
                      </div>
                      <Button variant="outline" size="sm">
                        <ExternalLink className="mr-2 h-4 w-4" />
                        View Docs
                      </Button>
                    </div>
                  </div>
                  <div className="rounded-lg border border-white/10 bg-gray-800/50 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-white">GraphQL API</h4>
                        <p className="text-sm text-gray-400">Flexible query interface</p>
                      </div>
                      <Badge className="bg-yellow-500/20 text-yellow-400">Coming Soon</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/10 bg-gray-900/50">
                <CardHeader>
                  <CardTitle className="text-white">API Keys</CardTitle>
                  <CardDescription>Manage your API credentials</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="rounded-lg border border-white/10 bg-gray-800/50 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-white">Production Key</h4>
                        <code className="text-sm text-gray-400">sk_live_****...****8f2d</code>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm">
                          <Share2 className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Settings className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  <Button className="w-full" variant="outline">
                    <Plus className="mr-2 h-4 w-4" />
                    Generate New Key
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
