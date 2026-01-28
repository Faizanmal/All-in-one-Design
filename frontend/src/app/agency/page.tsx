'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Building2,
  ChevronRight,
  CreditCard,
  FileText,
  Globe,
  Key,
  Link2,
  Mail,
  MessageSquare,
  Palette,
  Plus,
  Search,
  Settings,
  Share2,
  Users,

} from 'lucide-react';

interface Client {
  id: string;
  name: string;
  email: string;
  company: string;
  projects: number;
  status: 'active' | 'pending' | 'inactive';
  avatar?: string;
}

interface Invoice {
  id: string;
  client: string;
  amount: number;
  status: 'paid' | 'pending' | 'overdue';
  date: string;
}

export default function AgencyPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data
  const clients: Client[] = [
    {
      id: '1',
      name: 'Acme Corp',
      email: 'contact@acme.com',
      company: 'Acme Corporation',
      projects: 5,
      status: 'active',
    },
    {
      id: '2',
      name: 'TechStart Inc',
      email: 'hello@techstart.io',
      company: 'TechStart',
      projects: 3,
      status: 'active',
    },
    {
      id: '3',
      name: 'Global Media',
      email: 'info@globalmedia.com',
      company: 'Global Media Group',
      projects: 8,
      status: 'pending',
    },
  ];

  const invoices: Invoice[] = [
    { id: 'INV-001', client: 'Acme Corp', amount: 2500, status: 'paid', date: '2024-01-15' },
    { id: 'INV-002', client: 'TechStart Inc', amount: 1800, status: 'pending', date: '2024-01-20' },
    { id: 'INV-003', client: 'Global Media', amount: 4200, status: 'overdue', date: '2024-01-01' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'paid':
        return 'bg-green-500/20 text-green-400';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400';
      case 'overdue':
      case 'inactive':
        return 'bg-red-500/20 text-red-400';
      default:
        return 'bg-gray-500/20 text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Header */}
      <header className="border-b border-white/10 bg-gray-900/50 backdrop-blur-lg">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-red-600">
              <Building2 className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-white">Agency Dashboard</h1>
              <p className="text-sm text-gray-400">White-label management</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">
              <Palette className="mr-2 h-4 w-4" />
              Customize Branding
            </Button>
            <Button className="bg-gradient-to-r from-orange-500 to-red-600 text-white">
              <Plus className="mr-2 h-4 w-4" />
              Add Client
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6 bg-gray-800/50">
            <TabsTrigger value="overview" className="data-[state=active]:bg-orange-500/20">
              <Building2 className="mr-2 h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="clients" className="data-[state=active]:bg-orange-500/20">
              <Users className="mr-2 h-4 w-4" />
              Clients
            </TabsTrigger>
            <TabsTrigger value="portals" className="data-[state=active]:bg-orange-500/20">
              <Globe className="mr-2 h-4 w-4" />
              Client Portals
            </TabsTrigger>
            <TabsTrigger value="billing" className="data-[state=active]:bg-orange-500/20">
              <CreditCard className="mr-2 h-4 w-4" />
              Billing
            </TabsTrigger>
            <TabsTrigger value="branding" className="data-[state=active]:bg-orange-500/20">
              <Palette className="mr-2 h-4 w-4" />
              Branding
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid gap-6 md:grid-cols-4">
              <Card className="border-white/10 bg-gray-900/50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/20">
                      <Users className="h-6 w-6 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">{clients.length}</p>
                      <p className="text-sm text-gray-400">Active Clients</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/10 bg-gray-900/50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-500/20">
                      <FileText className="h-6 w-6 text-green-400" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">16</p>
                      <p className="text-sm text-gray-400">Active Projects</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/10 bg-gray-900/50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-500/20">
                      <MessageSquare className="h-6 w-6 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">8</p>
                      <p className="text-sm text-gray-400">Pending Feedback</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/10 bg-gray-900/50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-orange-500/20">
                      <CreditCard className="h-6 w-6 text-orange-400" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">$8,500</p>
                      <p className="text-sm text-gray-400">This Month</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="mt-6 border-white/10 bg-gray-900/50">
              <CardHeader>
                <CardTitle className="text-white">Recent Activity</CardTitle>
                <CardDescription>Latest updates from your clients</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { action: 'New feedback received', client: 'Acme Corp', time: '2 hours ago' },
                    { action: 'Project approved', client: 'TechStart Inc', time: '5 hours ago' },
                    { action: 'Invoice paid', client: 'Global Media', time: '1 day ago' },
                  ].map((activity, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-lg border border-white/10 bg-gray-800/50 p-4"
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-2 w-2 rounded-full bg-green-400" />
                        <div>
                          <p className="text-white">{activity.action}</p>
                          <p className="text-sm text-gray-400">{activity.client}</p>
                        </div>
                      </div>
                      <span className="text-sm text-gray-500">{activity.time}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Clients Tab */}
          <TabsContent value="clients">
            <Card className="border-white/10 bg-gray-900/50">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-white">Client Management</CardTitle>
                  <CardDescription>Manage your agency clients</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
                    <Input
                      placeholder="Search clients..."
                      className="w-64 border-white/20 bg-gray-800/50 pl-9 text-white"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <Button className="bg-orange-600 hover:bg-orange-700">
                    <Plus className="mr-2 h-4 w-4" />
                    Add Client
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {clients.map((client) => (
                    <div
                      key={client.id}
                      className="flex items-center justify-between rounded-lg border border-white/10 bg-gray-800/50 p-4"
                    >
                      <div className="flex items-center gap-4">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={client.avatar} />
                          <AvatarFallback className="bg-orange-500/20 text-orange-400">
                            {client.name.substring(0, 2).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <h3 className="font-medium text-white">{client.name}</h3>
                          <p className="text-sm text-gray-400">{client.email}</p>
                          <p className="text-xs text-gray-500">{client.projects} projects</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge className={getStatusColor(client.status)}>{client.status}</Badge>
                        <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                          <Link2 className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                          <Mail className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                          <Settings className="h-4 w-4" />
                        </Button>
                        <ChevronRight className="h-5 w-5 text-gray-500" />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Client Portals Tab */}
          <TabsContent value="portals">
            <div className="grid gap-6 md:grid-cols-2">
              {clients.map((client) => (
                <Card key={client.id} className="border-white/10 bg-gray-900/50">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarFallback className="bg-orange-500/20 text-orange-400">
                          {client.name.substring(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <CardTitle className="text-lg text-white">{client.name}</CardTitle>
                        <CardDescription>Portal active</CardDescription>
                      </div>
                    </div>
                    <Badge className="bg-green-500/20 text-green-400">Active</Badge>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between rounded-lg bg-gray-800/50 p-3">
                        <span className="text-sm text-gray-400">Portal URL</span>
                        <div className="flex items-center gap-2">
                          <code className="text-xs text-orange-400">
                            portal.agency.com/{client.id}
                          </code>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <Share2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex items-center justify-between rounded-lg bg-gray-800/50 p-3">
                        <span className="text-sm text-gray-400">Visible Projects</span>
                        <span className="text-white">{client.projects}</span>
                      </div>
                      <div className="flex items-center justify-between rounded-lg bg-gray-800/50 p-3">
                        <span className="text-sm text-gray-400">Comments Enabled</span>
                        <Badge className="bg-green-500/20 text-green-400">Yes</Badge>
                      </div>
                    </div>
                    <div className="mt-4 flex gap-2">
                      <Button className="flex-1" variant="outline">
                        <Key className="mr-2 h-4 w-4" />
                        Regenerate Link
                      </Button>
                      <Button className="flex-1 bg-orange-600 hover:bg-orange-700">
                        <Settings className="mr-2 h-4 w-4" />
                        Configure
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Billing Tab */}
          <TabsContent value="billing">
            <Card className="border-white/10 bg-gray-900/50">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-white">Invoices</CardTitle>
                  <CardDescription>Manage client billing</CardDescription>
                </div>
                <Button className="bg-orange-600 hover:bg-orange-700">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Invoice
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {invoices.map((invoice) => (
                    <div
                      key={invoice.id}
                      className="flex items-center justify-between rounded-lg border border-white/10 bg-gray-800/50 p-4"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-700">
                          <FileText className="h-5 w-5 text-gray-400" />
                        </div>
                        <div>
                          <h3 className="font-medium text-white">{invoice.id}</h3>
                          <p className="text-sm text-gray-400">{invoice.client}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-lg font-semibold text-white">
                          ${invoice.amount.toLocaleString()}
                        </span>
                        <Badge className={getStatusColor(invoice.status)}>{invoice.status}</Badge>
                        <span className="text-sm text-gray-500">{invoice.date}</span>
                        <ChevronRight className="h-5 w-5 text-gray-500" />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Branding Tab */}
          <TabsContent value="branding">
            <div className="grid gap-6 lg:grid-cols-2">
              <Card className="border-white/10 bg-gray-900/50">
                <CardHeader>
                  <CardTitle className="text-white">Brand Identity</CardTitle>
                  <CardDescription>Customize your white-label appearance</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-300">
                      Agency Logo
                    </label>
                    <div className="flex h-24 items-center justify-center rounded-lg border-2 border-dashed border-white/20 bg-gray-800/50">
                      <Button variant="ghost" className="text-gray-400">
                        <Plus className="mr-2 h-4 w-4" />
                        Upload Logo
                      </Button>
                    </div>
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-300">
                      Primary Color
                    </label>
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-orange-500" />
                      <Input
                        defaultValue="#f97316"
                        className="border-white/20 bg-gray-800/50 text-white"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-300">
                      Custom Domain
                    </label>
                    <div className="flex items-center gap-2">
                      <Input
                        placeholder="design.youragency.com"
                        className="border-white/20 bg-gray-800/50 text-white"
                      />
                      <Button variant="outline">
                        <Globe className="mr-2 h-4 w-4" />
                        Verify
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/10 bg-gray-900/50">
                <CardHeader>
                  <CardTitle className="text-white">API Keys</CardTitle>
                  <CardDescription>Manage integration credentials</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="rounded-lg border border-white/10 bg-gray-800/50 p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-white">Production Key</h4>
                          <code className="text-sm text-gray-400">ak_live_****...****8f2d</code>
                        </div>
                        <Button variant="ghost" size="sm">
                          <Key className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="rounded-lg border border-white/10 bg-gray-800/50 p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-white">Test Key</h4>
                          <code className="text-sm text-gray-400">ak_test_****...****3a1c</code>
                        </div>
                        <Button variant="ghost" size="sm">
                          <Key className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <Button className="w-full" variant="outline">
                      <Plus className="mr-2 h-4 w-4" />
                      Generate New Key
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
