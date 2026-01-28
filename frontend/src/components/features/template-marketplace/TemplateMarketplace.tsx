"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Star, Download, Eye, TrendingUp, Sparkles, Layout } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface Template {
  id: number;
  name: string;
  category: string;
  price: number;
  rating: number;
  downloads: number;
  author: string;
  thumbnail: string;
  featured: boolean;
}

export const TemplateMarketplace: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);

  const templates: Template[] = [
    { id: 1, name: 'Modern Dashboard', category: 'Dashboard', price: 49, rating: 4.8, downloads: 1234, author: 'DesignCo', thumbnail: '', featured: true },
    { id: 2, name: 'E-commerce UI Kit', category: 'E-commerce', price: 0, rating: 4.6, downloads: 3421, author: 'UIStudio', thumbnail: '', featured: false },
    { id: 3, name: 'Landing Page Pro', category: 'Landing', price: 29, rating: 4.9, downloads: 892, author: 'WebDesigns', thumbnail: '', featured: true },
    { id: 4, name: 'Mobile App Template', category: 'Mobile', price: 39, rating: 4.7, downloads: 2156, author: 'AppMasters', thumbnail: '', featured: false },
    { id: 5, name: 'Admin Panel', category: 'Dashboard', price: 0, rating: 4.5, downloads: 5432, author: 'FreeUI', thumbnail: '', featured: false },
    { id: 6, name: 'Portfolio Showcase', category: 'Portfolio', price: 19, rating: 4.8, downloads: 678, author: 'CreativeHub', thumbnail: '', featured: true },
  ];

  const filteredTemplates = templates.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || t.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Layout className="h-6 w-6" />
                Template Marketplace
              </CardTitle>
              <CardDescription>Browse and download professional design templates</CardDescription>
            </div>
            <Badge variant="secondary">{templates.length} Templates</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline">
              <TrendingUp className="h-4 w-4 mr-2" />
              Trending
            </Button>
          </div>

          <CategoryFilter selected={selectedCategory} onSelect={setSelectedCategory} />

          <div className="grid grid-cols-3 gap-4">
            {filteredTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onClick={() => setSelectedTemplate(template)}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {selectedTemplate && (
        <TemplateDetailModal
          template={selectedTemplate}
          onClose={() => setSelectedTemplate(null)}
        />
      )}
    </div>
  );
};

export const TemplateCard: React.FC<{ template: Template; onClick: () => void }> = ({ template, onClick }) => {
  return (
    <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={onClick}>
      <div className="aspect-video bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center relative">
        {template.featured && (
          <Badge className="absolute top-2 left-2">
            <Sparkles className="h-3 w-3 mr-1" />
            Featured
          </Badge>
        )}
        <Layout className="h-16 w-16 text-purple-300" />
      </div>
      <CardContent className="p-4">
        <h3 className="font-semibold mb-2">{template.name}</h3>
        <div className="flex items-center justify-between mb-2">
          <Badge variant="outline">{template.category}</Badge>
          <span className="text-lg font-bold">
            {template.price === 0 ? 'Free' : `$${template.price}`}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
            {template.rating}
          </div>
          <div className="flex items-center gap-1">
            <Download className="h-4 w-4" />
            {template.downloads}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const TemplateDetailModal: React.FC<{ template: Template; onClose: () => void }> = ({ template, onClose }) => {
  const { toast } = useToast();

  const handleUse = () => {
    toast({ title: "Template added", description: `${template.name} added to your workspace` });
    onClose();
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>{template.name}</DialogTitle>
          <DialogDescription>by {template.author}</DialogDescription>
        </DialogHeader>
        <div className="space-y-6">
          <div className="aspect-video bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg flex items-center justify-center">
            <Layout className="h-32 w-32 text-purple-300" />
          </div>

          <Tabs defaultValue="overview">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="features">Features</TabsTrigger>
              <TabsTrigger value="reviews">Reviews</TabsTrigger>
            </TabsList>
            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <Star className="h-5 w-5 mx-auto mb-2 fill-yellow-500 text-yellow-500" />
                  <p className="text-2xl font-bold">{template.rating}</p>
                  <p className="text-sm text-muted-foreground">Rating</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <Download className="h-5 w-5 mx-auto mb-2" />
                  <p className="text-2xl font-bold">{template.downloads}</p>
                  <p className="text-sm text-muted-foreground">Downloads</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <Layout className="h-5 w-5 mx-auto mb-2" />
                  <p className="text-2xl font-bold">12</p>
                  <p className="text-sm text-muted-foreground">Screens</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <Eye className="h-5 w-5 mx-auto mb-2" />
                  <p className="text-2xl font-bold">2.1K</p>
                  <p className="text-sm text-muted-foreground">Views</p>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Description</h4>
                <p className="text-muted-foreground">
                  A modern and professional template perfect for your next project. 
                  Includes all the essential components and screens you need to get started quickly.
                </p>
              </div>
            </TabsContent>
            <TabsContent value="features" className="space-y-2">
              {['Responsive design', 'Dark mode support', 'Component library', 'Clean code', 'Documentation included'].map((feature) => (
                <div key={feature} className="flex items-center gap-2 p-2">
                  <div className="h-2 w-2 bg-green-500 rounded-full" />
                  <span>{feature}</span>
                </div>
              ))}
            </TabsContent>
            <TabsContent value="reviews">
              <p className="text-muted-foreground">No reviews yet. Be the first to review!</p>
            </TabsContent>
          </Tabs>

          <div className="flex justify-between items-center pt-4 border-t">
            <div className="text-3xl font-bold">
              {template.price === 0 ? 'Free' : `$${template.price}`}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={onClose}>Cancel</Button>
              <Button onClick={handleUse}>
                {template.price === 0 ? 'Use Template' : 'Purchase & Use'}
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export const CategoryFilter: React.FC<{ selected: string; onSelect: (category: string) => void }> = ({ selected, onSelect }) => {
  const categories = ['all', 'Dashboard', 'E-commerce', 'Landing', 'Mobile', 'Portfolio'];

  return (
    <div className="flex gap-2">
      {categories.map((category) => (
        <Button
          key={category}
          variant={selected === category ? 'default' : 'outline'}
          size="sm"
          onClick={() => onSelect(category)}
        >
          {category.charAt(0).toUpperCase() + category.slice(1)}
        </Button>
      ))}
    </div>
  );
};