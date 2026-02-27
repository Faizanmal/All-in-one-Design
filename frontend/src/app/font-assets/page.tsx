"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Type, 
  Image, 
  Grid3X3, 
  Search, 
  Download, 
  Heart, 
  Plus,
  Filter,
  Star,
  Check,
  Upload,
  FolderOpen,
  Clock,
  Globe,
  Lock
} from 'lucide-react';

// Mock data
const mockFonts = [
  { id: '1', name: 'Inter', family: 'Sans Serif', variants: 9, category: 'sans-serif', popular: true },
  { id: '2', name: 'Playfair Display', family: 'Serif', variants: 6, category: 'serif', popular: true },
  { id: '3', name: 'Roboto', family: 'Sans Serif', variants: 12, category: 'sans-serif', popular: true },
  { id: '4', name: 'Montserrat', family: 'Sans Serif', variants: 18, category: 'sans-serif', popular: true },
  { id: '5', name: 'Lora', family: 'Serif', variants: 4, category: 'serif', popular: false },
  { id: '6', name: 'Open Sans', family: 'Sans Serif', variants: 10, category: 'sans-serif', popular: true },
];

const mockIcons = [
  { id: '1', name: 'Lucide Icons', count: 1500, style: 'Outline', license: 'MIT' },
  { id: '2', name: 'Heroicons', count: 450, style: 'Solid/Outline', license: 'MIT' },
  { id: '3', name: 'Phosphor Icons', count: 6600, style: 'Multiple', license: 'MIT' },
  { id: '4', name: 'Tabler Icons', count: 4000, style: 'Outline', license: 'MIT' },
];

const mockAssets = [
  { id: '1', name: 'Brand Guidelines.pdf', type: 'document', size: '2.4 MB', versions: 3 },
  { id: '2', name: 'Logo Primary.svg', type: 'image', size: '45 KB', versions: 5 },
  { id: '3', name: 'Hero Banner.png', type: 'image', size: '1.8 MB', versions: 2 },
  { id: '4', name: 'Product Photos', type: 'folder', size: '156 MB', versions: 1 },
];

const mockStockProviders = [
  { id: '1', name: 'Unsplash', type: 'Photos', connected: true, quota: 'Unlimited' },
  { id: '2', name: 'Pexels', type: 'Photos & Videos', connected: true, quota: 'Unlimited' },
  { id: '3', name: 'Shutterstock', type: 'Premium', connected: false, quota: 'N/A' },
  { id: '4', name: 'Adobe Stock', type: 'Premium', connected: false, quota: 'N/A' },
];

export default function FontAssetsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [favorites, setFavorites] = useState<string[]>(['1', '3']);

  const toggleFavorite = (id: string) => {
    setFavorites(prev => 
      prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Font & Asset Hub</h1>
              <p className="text-sm text-gray-500">Manage fonts, icons, and assets in one place</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                <Upload className="h-4 w-4 mr-2" />
                Upload Assets
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Collection
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="fonts" className="space-y-6">
          <TabsList className="grid grid-cols-4 w-full max-w-lg">
            <TabsTrigger value="fonts" className="flex items-center gap-2">
              <Type className="h-4 w-4" />
              Fonts
            </TabsTrigger>
            <TabsTrigger value="icons" className="flex items-center gap-2">
              <Grid3X3 className="h-4 w-4" />
              Icons
            </TabsTrigger>
            <TabsTrigger value="assets" className="flex items-center gap-2">
              <FolderOpen className="h-4 w-4" />
              Assets
            </TabsTrigger>
            <TabsTrigger value="stock" className="flex items-center gap-2">
              {/* eslint-disable-next-line jsx-a11y/alt-text */}
              <Image className="h-4 w-4" aria-hidden="true" />
              Stock
            </TabsTrigger>
          </TabsList>

          {/* Fonts Tab */}
          <TabsContent value="fonts" className="space-y-6">
            {/* Search and Filters */}
            <div className="flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search fonts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex gap-2">
                {['all', 'sans-serif', 'serif', 'display', 'handwriting'].map((cat) => (
                  <Button
                    key={cat}
                    variant={selectedCategory === cat ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat.charAt(0).toUpperCase() + cat.slice(1).replace('-', ' ')}
                  </Button>
                ))}
              </div>
            </div>

            {/* Font Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {mockFonts.map((font) => (
                <Card key={font.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{font.name}</CardTitle>
                        <CardDescription>{font.family} • {font.variants} variants</CardDescription>
                      </div>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        onClick={() => toggleFavorite(font.id)}
                      >
                        <Heart 
                          className={`h-4 w-4 ${favorites.includes(font.id) ? 'fill-red-500 text-red-500' : ''}`} 
                        />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div 
                      className="text-2xl py-4 border-t border-b"
                      style={{ fontFamily: font.name }}
                    >
                      The quick brown fox jumps over the lazy dog
                    </div>
                    <div className="flex gap-2 mt-3">
                      {font.popular && (
                        <Badge variant="secondary">
                          <Star className="h-3 w-3 mr-1" />
                          Popular
                        </Badge>
                      )}
                      <Badge variant="outline">{font.category}</Badge>
                    </div>
                  </CardContent>
                  <CardFooter className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      Preview
                    </Button>
                    <Button size="sm" className="flex-1">
                      <Download className="h-4 w-4 mr-2" />
                      Add to Project
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>

            {/* Font Collections */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">Your Collections</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="border-dashed cursor-pointer hover:bg-gray-50">
                  <CardContent className="flex flex-col items-center justify-center py-8">
                    <Plus className="h-8 w-8 text-gray-400 mb-2" />
                    <p className="text-sm text-gray-500">Create Collection</p>
                  </CardContent>
                </Card>
                <Card className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardContent className="py-4">
                    <h4 className="font-medium">Brand Fonts</h4>
                    <p className="text-sm text-gray-500">4 fonts</p>
                  </CardContent>
                </Card>
                <Card className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardContent className="py-4">
                    <h4 className="font-medium">Web Projects</h4>
                    <p className="text-sm text-gray-500">8 fonts</p>
                  </CardContent>
                </Card>
                <Card className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardContent className="py-4">
                    <h4 className="font-medium">Print Materials</h4>
                    <p className="text-sm text-gray-500">3 fonts</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Icons Tab */}
          <TabsContent value="icons" className="space-y-6">
            <div className="flex gap-4 mb-6">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input placeholder="Search icons..." className="pl-10" />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </Button>
            </div>

            {/* Icon Sets */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockIcons.map((iconSet) => (
                <Card key={iconSet.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle>{iconSet.name}</CardTitle>
                        <CardDescription>{iconSet.count.toLocaleString()} icons • {iconSet.style}</CardDescription>
                      </div>
                      <Badge variant="outline">{iconSet.license}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-8 gap-2 p-4 bg-gray-50 rounded-lg">
                      {Array(16).fill(null).map((_, i) => (
                        <div key={i} className="w-8 h-8 bg-gray-200 rounded flex items-center justify-center">
                          <Grid3X3 className="h-4 w-4 text-gray-500" />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                  <CardFooter className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      Browse All
                    </Button>
                    <Button size="sm" className="flex-1">
                      <Check className="h-4 w-4 mr-2" />
                      Install
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>

            {/* Recently Used Icons */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">Recently Used</h3>
              <Card>
                <CardContent className="py-4">
                  <div className="grid grid-cols-12 gap-4">
                    {Array(24).fill(null).map((_, i) => (
                      <div 
                        key={i} 
                        className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors"
                      >
                        <Grid3X3 className="h-5 w-5 text-gray-600" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Assets Tab */}
          <TabsContent value="assets" className="space-y-6">
            <div className="flex justify-between items-center">
              <div className="flex gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input placeholder="Search assets..." className="pl-10 w-64" />
                </div>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Filters
                </Button>
              </div>
              <div className="flex gap-2">
                <Button variant="outline">
                  <FolderOpen className="h-4 w-4 mr-2" />
                  New Folder
                </Button>
                <Button>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload
                </Button>
              </div>
            </div>

            {/* Asset Libraries */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="col-span-1 md:col-span-4 bg-linear-to-r from-blue-50 to-purple-50">
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">Asset Library</h3>
                      <p className="text-sm text-gray-600">234 assets • 1.2 GB used</p>
                    </div>
                    <Button variant="outline">Manage Storage</Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Asset List */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">All Assets</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {mockAssets.map((asset) => (
                    <div 
                      key={asset.id}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        {asset.type === 'folder' ? (
                          <FolderOpen className="h-8 w-8 text-yellow-500" />
                        ) : asset.type === 'document' ? (
                          <div className="w-8 h-8 bg-red-100 rounded flex items-center justify-center">
                            <span className="text-xs font-bold text-red-600">PDF</span>
                          </div>
                        ) : (
                          <div className="w-8 h-8 bg-gray-200 rounded" role="img" aria-label="Asset thumbnail"></div>
                        )}
                        <div>
                          <p className="font-medium">{asset.name}</p>
                          <p className="text-sm text-gray-500">{asset.size}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1 text-sm text-gray-500">
                          <Clock className="h-4 w-4" />
                          {asset.versions} versions
                        </div>
                        <Button variant="ghost" size="sm">
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Version History */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Recent Updates</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-green-500 mt-2"></div>
                    <div>
                      <p className="font-medium">Logo Primary.svg updated</p>
                      <p className="text-sm text-gray-500">Version 5 • 2 hours ago by John</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-2"></div>
                    <div>
                      <p className="font-medium">Brand Guidelines.pdf uploaded</p>
                      <p className="text-sm text-gray-500">Version 3 • Yesterday by Sarah</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Stock Tab */}
          <TabsContent value="stock" className="space-y-6">
            <div className="flex gap-4 mb-6">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input placeholder="Search stock photos, videos, and illustrations..." className="pl-10" />
              </div>
              <Button>
                <Search className="h-4 w-4 mr-2" />
                Search All
              </Button>
            </div>

            {/* Stock Providers */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockStockProviders.map((provider) => (
                <Card key={provider.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {provider.name}
                          {provider.connected && (
                            <Badge variant="default" className="bg-green-100 text-green-700">
                              <Check className="h-3 w-3 mr-1" />
                              Connected
                            </Badge>
                          )}
                        </CardTitle>
                        <CardDescription>{provider.type}</CardDescription>
                      </div>
                      {provider.connected ? (
                        <Globe className="h-5 w-5 text-green-500" />
                      ) : (
                        <Lock className="h-5 w-5 text-gray-400" />
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-4 gap-2">
                      {Array(8).fill(null).map((_, i) => (
                        <div key={i} className="aspect-square bg-gray-200 rounded" role="img" aria-label={`Stock image preview ${i + 1}`}></div>
                      ))}
                    </div>
                    <p className="text-sm text-gray-500 mt-3">
                      Quota: {provider.quota}
                    </p>
                  </CardContent>
                  <CardFooter>
                    <Button 
                      variant={provider.connected ? 'outline' : 'default'} 
                      className="w-full"
                    >
                      {provider.connected ? 'Browse Library' : 'Connect Account'}
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>

            {/* Licensed Assets */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">Your Licensed Assets</h3>
              <Card>
                <CardContent className="py-8 text-center">
                  {/* eslint-disable-next-line jsx-a11y/alt-text */}
                  <Image className="h-12 w-12 text-gray-400 mx-auto mb-4" aria-hidden="true" />
                  <p className="text-gray-500">Assets you license will appear here for easy access.</p>
                  <Button variant="outline" className="mt-4">
                    Browse Stock Libraries
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
