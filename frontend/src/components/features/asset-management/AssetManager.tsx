"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Image, FileImage, Folder, Search, Upload, Grid3x3, List, Star, Clock } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface Asset {
  id: number;
  name: string;
  type: 'image' | 'svg' | 'video';
  size: string;
  tags: string[];
  starred: boolean;
  thumbnail: string;
}

export const AssetManager: React.FC = () => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  
  const assets: Asset[] = [
    { id: 1, name: 'hero-banner.png', type: 'image', size: '2.4 MB', tags: ['banner', 'hero'], starred: true, thumbnail: '' },
    { id: 2, name: 'logo.svg', type: 'svg', size: '45 KB', tags: ['logo', 'brand'], starred: false, thumbnail: '' },
    { id: 3, name: 'product-demo.mp4', type: 'video', size: '15 MB', tags: ['video', 'demo'], starred: true, thumbnail: '' },
    { id: 4, name: 'icon-set.svg', type: 'svg', size: '120 KB', tags: ['icons'], starred: false, thumbnail: '' },
  ];

  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || asset.type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileImage className="h-5 w-5" />
              Asset Manager
            </CardTitle>
            <CardDescription>Manage and organize your design assets</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}>
              {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid3x3 className="h-4 w-4" />}
            </Button>
            <Button size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Upload
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search assets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="image">Images</SelectItem>
              <SelectItem value="svg">SVG</SelectItem>
              <SelectItem value="video">Videos</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <ScrollArea className="h-[400px]">
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-4 gap-4">
              {filteredAssets.map((asset) => (
                <AssetCard key={asset.id} asset={asset} />
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredAssets.map((asset) => (
                <div key={asset.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent">
                  <div className="flex items-center gap-3">
                    <FileImage className="h-8 w-8 text-muted-foreground" />
                    <div>
                      <p className="font-medium">{asset.name}</p>
                      <p className="text-sm text-muted-foreground">{asset.size}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {asset.tags.map(tag => (
                      <Badge key={tag} variant="secondary">{tag}</Badge>
                    ))}
                    {asset.starred && <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export const AssetCard: React.FC<{ asset: Asset }> = ({ asset }) => {
  return (
    <Card className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow">
      <div className="aspect-square bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center">
        {asset.type === 'image' ? <Image className="h-12 w-12 text-slate-400" /> : <FileImage className="h-12 w-12 text-slate-400" />}
      </div>
      <CardContent className="p-3">
        <div className="flex items-start justify-between mb-2">
          <p className="text-sm font-medium truncate flex-1">{asset.name}</p>
          {asset.starred && <Star className="h-4 w-4 fill-yellow-500 text-yellow-500 flex-shrink-0" />}
        </div>
        <p className="text-xs text-muted-foreground">{asset.size}</p>
        <div className="flex gap-1 mt-2">
          {asset.tags.slice(0, 2).map(tag => (
            <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export const AIAssetSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const { toast } = useToast();

  const handleSearch = () => {
    toast({ title: "Searching...", description: "AI is analyzing your assets" });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI-Powered Asset Search</CardTitle>
        <CardDescription>Search using natural language or visual similarity</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Input
            placeholder="e.g., 'blue gradient backgrounds' or 'icons for mobile app'"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <Button className="w-full" onClick={handleSearch}>
            <Search className="h-4 w-4 mr-2" />
            AI Search
          </Button>
        </div>
        <div className="pt-4 border-t">
          <p className="text-sm font-medium mb-2">Recent AI Searches</p>
          <div className="space-y-1">
            {['blue gradients', 'mobile icons', 'hero images'].map((term) => (
              <Button key={term} variant="ghost" size="sm" className="w-full justify-start">
                <Clock className="h-4 w-4 mr-2" />
                {term}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const SmartFolderDialog: React.FC = () => {
  const [folderName, setFolderName] = useState('');
  const { toast } = useToast();

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Folder className="h-4 w-4 mr-2" />
          Create Smart Folder
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Smart Folder</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Folder Name</label>
            <Input
              placeholder="e.g., Recent Images"
              value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
            />
          </div>
          <Tabs defaultValue="rules">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="rules">Rules</TabsTrigger>
              <TabsTrigger value="preview">Preview</TabsTrigger>
            </TabsList>
            <TabsContent value="rules" className="space-y-3">
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="File type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="image">Images</SelectItem>
                  <SelectItem value="svg">SVG</SelectItem>
                  <SelectItem value="video">Videos</SelectItem>
                </SelectContent>
              </Select>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Modified date" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="today">Today</SelectItem>
                  <SelectItem value="week">This week</SelectItem>
                  <SelectItem value="month">This month</SelectItem>
                </SelectContent>
              </Select>
            </TabsContent>
            <TabsContent value="preview">
              <p className="text-sm text-muted-foreground">24 assets match your criteria</p>
            </TabsContent>
          </Tabs>
          <Button className="w-full" onClick={() => {
            toast({ title: "Smart folder created", description: `Created "${folderName}"` });
          }}>
            Create Folder
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};