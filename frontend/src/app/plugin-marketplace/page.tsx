"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { 
  Puzzle, 
  Search, 
  Download, 
  Star, 
  Code,
  Package,
  TrendingUp,
  Users,
  Settings,
  Plus,
  Check,
  ExternalLink,
  Upload,
  FileCode,
  Terminal,
  BookOpen,
  Webhook,
  Key,
  Eye,
  Heart,
  Filter,
  Trash2,
  Play,
  Zap
} from 'lucide-react';

// Mock data
const mockPlugins = [
  { 
    id: '1', 
    name: 'Smart Layers Pro', 
    author: 'DesignTools Inc',
    description: 'Automatically organize and name layers based on content',
    downloads: 12500,
    rating: 4.8,
    reviews: 234,
    price: 'Free',
    installed: true,
    category: 'Productivity'
  },
  { 
    id: '2', 
    name: 'Color Palette AI', 
    author: 'AI Studio',
    description: 'Generate beautiful color palettes using AI',
    downloads: 8900,
    rating: 4.6,
    reviews: 156,
    price: '$9.99',
    installed: false,
    category: 'Design'
  },
  { 
    id: '3', 
    name: 'Export Master', 
    author: 'DevTeam',
    description: 'Advanced export options for multiple formats and sizes',
    downloads: 15200,
    rating: 4.9,
    reviews: 312,
    price: 'Free',
    installed: true,
    category: 'Export'
  },
  { 
    id: '4', 
    name: 'Lorem Generator', 
    author: 'TextUtils',
    description: 'Generate placeholder text in multiple styles',
    downloads: 6700,
    rating: 4.5,
    reviews: 89,
    price: 'Free',
    installed: false,
    category: 'Content'
  },
  { 
    id: '5', 
    name: 'Animation Studio', 
    author: 'MotionLab',
    description: 'Create complex animations with ease',
    downloads: 11300,
    rating: 4.7,
    reviews: 201,
    price: '$19.99',
    installed: false,
    category: 'Animation'
  },
  { 
    id: '6', 
    name: 'Asset Manager', 
    author: 'DesignOps',
    description: 'Organize and sync assets across projects',
    downloads: 9800,
    rating: 4.4,
    reviews: 143,
    price: '$4.99',
    installed: true,
    category: 'Productivity'
  },
];

const mockCategories = [
  { name: 'All', count: 156 },
  { name: 'Productivity', count: 45 },
  { name: 'Design', count: 38 },
  { name: 'Animation', count: 22 },
  { name: 'Export', count: 18 },
  { name: 'Content', count: 15 },
  { name: 'Integrations', count: 12 },
  { name: 'Developer', count: 6 },
];

const mockMyPlugins = [
  { id: '1', name: 'Smart Layers Pro', status: 'Published', version: '2.3.1', installs: 12500, revenue: '$0' },
  { id: '2', name: 'Quick Export', status: 'In Review', version: '1.0.0', installs: 0, revenue: '$0' },
];

const mockAPIDocs = [
  { title: 'Getting Started', description: 'Learn the basics of plugin development' },
  { title: 'Canvas API', description: 'Interact with the design canvas' },
  { title: 'UI Components', description: 'Build plugin interfaces' },
  { title: 'Storage API', description: 'Persist plugin data' },
  { title: 'Events & Hooks', description: 'React to design changes' },
  { title: 'Publishing Guide', description: 'Submit your plugin' },
];

export default function PluginMarketplacePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [favorites, setFavorites] = useState<string[]>(['1', '3']);

  const toggleFavorite = (id: string) => {
    setFavorites(prev => 
      prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]
    );
  };

  const filteredPlugins = mockPlugins.filter(plugin => 
    (selectedCategory === 'All' || plugin.category === selectedCategory) &&
    (plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
     plugin.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Plugin Marketplace</h1>
              <p className="text-sm text-gray-500">Extend your design workflow with powerful plugins</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Manage Plugins
              </Button>
              <Button>
                <Code className="h-4 w-4 mr-2" />
                Developer Portal
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="browse" className="space-y-6">
          <TabsList className="grid grid-cols-4 w-full max-w-lg">
            <TabsTrigger value="browse" className="flex items-center gap-2">
              <Puzzle className="h-4 w-4" />
              Browse
            </TabsTrigger>
            <TabsTrigger value="installed" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Installed
            </TabsTrigger>
            <TabsTrigger value="develop" className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              Develop
            </TabsTrigger>
            <TabsTrigger value="my-plugins" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              My Plugins
            </TabsTrigger>
          </TabsList>

          {/* Browse Tab */}
          <TabsContent value="browse" className="space-y-6">
            {/* Search and Filters */}
            <div className="flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search plugins..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </Button>
            </div>

            {/* Featured Section */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
              <div className="flex justify-between items-center">
                <div>
                  <Badge className="bg-white/20 text-white mb-2">Featured Plugin</Badge>
                  <h2 className="text-2xl font-bold">Animation Studio</h2>
                  <p className="text-white/80 mt-2">Create stunning animations with our most popular plugin</p>
                  <Button className="mt-4 bg-white text-blue-600 hover:bg-white/90">
                    <Download className="h-4 w-4 mr-2" />
                    Install Now
                  </Button>
                </div>
                <Zap className="h-24 w-24 text-white/30" />
              </div>
            </div>

            <div className="grid grid-cols-12 gap-6">
              {/* Categories Sidebar */}
              <div className="col-span-3">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Categories</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-1">
                    {mockCategories.map((category) => (
                      <button
                        key={category.name}
                        className={`w-full flex justify-between items-center px-3 py-2 rounded-lg text-left text-sm ${
                          selectedCategory === category.name 
                            ? 'bg-blue-50 text-blue-600' 
                            : 'hover:bg-gray-50'
                        }`}
                        onClick={() => setSelectedCategory(category.name)}
                      >
                        <span>{category.name}</span>
                        <Badge variant="secondary">{category.count}</Badge>
                      </button>
                    ))}
                  </CardContent>
                </Card>

                <Card className="mt-4">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Trending</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {mockPlugins.slice(0, 3).map((plugin, index) => (
                      <div key={plugin.id} className="flex items-center gap-3">
                        <span className="text-lg font-bold text-gray-300">{index + 1}</span>
                        <div className="flex-1">
                          <p className="font-medium text-sm">{plugin.name}</p>
                          <p className="text-xs text-gray-500">{plugin.downloads.toLocaleString()} installs</p>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>

              {/* Plugin Grid */}
              <div className="col-span-9">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredPlugins.map((plugin) => (
                    <Card key={plugin.id} className="hover:shadow-lg transition-shadow">
                      <CardHeader className="pb-2">
                        <div className="flex justify-between items-start">
                          <div className="flex items-start gap-3">
                            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                              <Puzzle className="h-6 w-6 text-white" />
                            </div>
                            <div>
                              <CardTitle className="text-base">{plugin.name}</CardTitle>
                              <CardDescription>by {plugin.author}</CardDescription>
                            </div>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={() => toggleFavorite(plugin.id)}
                          >
                            <Heart 
                              className={`h-4 w-4 ${favorites.includes(plugin.id) ? 'fill-red-500 text-red-500' : ''}`} 
                            />
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-600 mb-3">{plugin.description}</p>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                            {plugin.rating} ({plugin.reviews})
                          </span>
                          <span className="flex items-center gap-1">
                            <Download className="h-4 w-4" />
                            {plugin.downloads.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex gap-2 mt-3">
                          <Badge variant="outline">{plugin.category}</Badge>
                          <Badge variant={plugin.price === 'Free' ? 'secondary' : 'default'}>
                            {plugin.price}
                          </Badge>
                        </div>
                      </CardContent>
                      <CardFooter className="flex gap-2">
                        <Button variant="outline" size="sm" className="flex-1">
                          <Eye className="h-4 w-4 mr-2" />
                          Preview
                        </Button>
                        <Button 
                          size="sm" 
                          className="flex-1"
                          variant={plugin.installed ? 'outline' : 'default'}
                        >
                          {plugin.installed ? (
                            <>
                              <Check className="h-4 w-4 mr-2" />
                              Installed
                            </>
                          ) : (
                            <>
                              <Download className="h-4 w-4 mr-2" />
                              Install
                            </>
                          )}
                        </Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Installed Tab */}
          <TabsContent value="installed" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Installed Plugins ({mockPlugins.filter(p => p.installed).length})</h3>
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {mockPlugins.filter(p => p.installed).map((plugin) => (
                <Card key={plugin.id}>
                  <CardHeader className="pb-2">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                        <Puzzle className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-base">{plugin.name}</CardTitle>
                        <CardDescription>v1.0.0 • Up to date</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">{plugin.description}</p>
                  </CardContent>
                  <CardFooter className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Settings className="h-4 w-4 mr-2" />
                      Configure
                    </Button>
                    <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Develop Tab */}
          <TabsContent value="develop" className="space-y-6">
            {/* Quick Start */}
            <Card className="bg-gradient-to-r from-gray-900 to-gray-800 text-white">
              <CardContent className="py-8">
                <div className="flex justify-between items-center">
                  <div>
                    <h2 className="text-2xl font-bold mb-2">Start Building Plugins</h2>
                    <p className="text-gray-300 mb-4">Create powerful extensions for the design platform</p>
                    <div className="flex gap-2">
                      <Button className="bg-white text-gray-900 hover:bg-gray-100">
                        <FileCode className="h-4 w-4 mr-2" />
                        Create New Plugin
                      </Button>
                      <Button variant="outline" className="border-white text-white hover:bg-white/10">
                        <BookOpen className="h-4 w-4 mr-2" />
                        Read Docs
                      </Button>
                    </div>
                  </div>
                  <Terminal className="h-24 w-24 text-white/20" />
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* API Documentation */}
              <Card>
                <CardHeader>
                  <CardTitle>API Documentation</CardTitle>
                  <CardDescription>Everything you need to build plugins</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {mockAPIDocs.map((doc, index) => (
                    <div 
                      key={index}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <div>
                        <p className="font-medium">{doc.title}</p>
                        <p className="text-sm text-gray-500">{doc.description}</p>
                      </div>
                      <ExternalLink className="h-4 w-4 text-gray-400" />
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Developer Tools */}
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Developer Tools</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button variant="outline" className="w-full justify-start">
                      <Key className="h-4 w-4 mr-2" />
                      API Keys
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Webhook className="h-4 w-4 mr-2" />
                      Webhooks
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Terminal className="h-4 w-4 mr-2" />
                      CLI Tools
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Play className="h-4 w-4 mr-2" />
                      Plugin Sandbox
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Quick Create</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <Input placeholder="Plugin name" />
                      <Textarea placeholder="Description" rows={3} />
                      <Button className="w-full">
                        <Plus className="h-4 w-4 mr-2" />
                        Create Plugin
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* My Plugins Tab */}
          <TabsContent value="my-plugins" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">My Published Plugins</h3>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Submit New Plugin
              </Button>
            </div>

            {mockMyPlugins.length > 0 ? (
              <div className="space-y-4">
                {mockMyPlugins.map((plugin) => (
                  <Card key={plugin.id}>
                    <CardContent className="py-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                            <Puzzle className="h-6 w-6 text-white" />
                          </div>
                          <div>
                            <h4 className="font-semibold">{plugin.name}</h4>
                            <p className="text-sm text-gray-500">Version {plugin.version}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-6">
                          <div className="text-center">
                            <p className="text-sm text-gray-500">Status</p>
                            <Badge 
                              variant={plugin.status === 'Published' ? 'default' : 'secondary'}
                            >
                              {plugin.status}
                            </Badge>
                          </div>
                          <div className="text-center">
                            <p className="text-sm text-gray-500">Installs</p>
                            <p className="font-semibold">{plugin.installs.toLocaleString()}</p>
                          </div>
                          <div className="text-center">
                            <p className="text-sm text-gray-500">Revenue</p>
                            <p className="font-semibold">{plugin.revenue}</p>
                          </div>
                          <Button variant="outline" size="sm">
                            <Settings className="h-4 w-4 mr-2" />
                            Manage
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="py-12 text-center">
                  <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">You haven&apos;t published any plugins yet</p>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Plugin
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Analytics Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6 text-center">
                  <Download className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                  <div className="text-2xl font-bold">12,500</div>
                  <p className="text-sm text-gray-500">Total Installs</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6 text-center">
                  <Users className="h-6 w-6 text-green-500 mx-auto mb-2" />
                  <div className="text-2xl font-bold">8,234</div>
                  <p className="text-sm text-gray-500">Active Users</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6 text-center">
                  <Star className="h-6 w-6 text-yellow-500 mx-auto mb-2" />
                  <div className="text-2xl font-bold">4.8</div>
                  <p className="text-sm text-gray-500">Avg Rating</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6 text-center">
                  <TrendingUp className="h-6 w-6 text-purple-500 mx-auto mb-2" />
                  <div className="text-2xl font-bold">$0</div>
                  <p className="text-sm text-gray-500">Total Revenue</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
