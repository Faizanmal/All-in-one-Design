'use client';

import type { FabricCanvas, FabricObject, FabricEvent } from '@/types/fabric';
import { Rect, Text, Group } from 'fabric';
/**
 * Component Library Browser
 * Reusable design components and templates
 */

import React, { useState } from 'react';
import { 
  Box, Layers, Star, Search, Grid3x3, Smartphone, 
  Monitor, Mail, Share2, Copy, Heart
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface Component {
  id: string;
  name: string;
  category: string;
  thumbnail?: string;
  tags: string[];
  popular?: boolean;
  data: unknown;
}

const components: Component[] = [
  {
    id: 'btn-primary',
    name: 'Primary Button',
    category: 'Buttons',
    tags: ['button', 'cta', 'primary'],
    popular: true,
    data: { type: 'button', variant: 'primary' }
  },
  {
    id: 'btn-secondary',
    name: 'Secondary Button',
    category: 'Buttons',
    tags: ['button', 'secondary'],
    data: { type: 'button', variant: 'secondary' }
  },
  {
    id: 'card-product',
    name: 'Product Card',
    category: 'Cards',
    tags: ['card', 'product', 'ecommerce'],
    popular: true,
    data: { type: 'card', variant: 'product' }
  },
  {
    id: 'nav-bar',
    name: 'Navigation Bar',
    category: 'Navigation',
    tags: ['nav', 'header', 'menu'],
    popular: true,
    data: { type: 'navigation', variant: 'top' }
  },
  {
    id: 'hero-section',
    name: 'Hero Section',
    category: 'Sections',
    tags: ['hero', 'landing', 'header'],
    popular: true,
    data: { type: 'section', variant: 'hero' }
  },
  {
    id: 'form-contact',
    name: 'Contact Form',
    category: 'Forms',
    tags: ['form', 'contact', 'input'],
    data: { type: 'form', variant: 'contact' }
  },
  {
    id: 'footer-links',
    name: 'Footer with Links',
    category: 'Footers',
    tags: ['footer', 'links', 'bottom'],
    data: { type: 'footer', variant: 'links' }
  },
  {
    id: 'icon-grid',
    name: 'Icon Grid',
    category: 'Grids',
    tags: ['grid', 'icons', 'features'],
    data: { type: 'grid', variant: 'icons' }
  },
];

interface ComponentLibraryProps {
  canvas?: FabricCanvas | null;
  onInsertComponent?: (component: Component) => void;
}

export function ComponentLibrary({ canvas, onInsertComponent }: ComponentLibraryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

  // Get unique categories
  const categories = ['all', ...Array.from(new Set(components.map(c => c.category)))];

  // Filter components
  const filteredComponents = components.filter(component => {
    const matchesSearch = 
      component.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      component.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || component.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  // Toggle favorite
  const toggleFavorite = (componentId: string) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(componentId)) {
        newFavorites.delete(componentId);
      } else {
        newFavorites.add(componentId);
      }
      return newFavorites;
    });
  };

  // Insert component
  const handleInsertComponent = (component: Component) => {
    onInsertComponent?.(component);

    // Add to canvas (basic implementation)
    if (canvas) {
      // Create a placeholder rectangle
      const rect = new Rect({
        left: 100,
        top: 100,
        width: 200,
        height: 100,
        fill: '#3B82F6',
        stroke: '#1E40AF',
        strokeWidth: 2,
      });
      
      const text = new Text(component.name, {
        left: 110,
        top: 125,
        fontSize: 14,
        fill: '#FFFFFF',
      });

      const group = new Group([rect, text], {
        left: 100,
        top: 100,
      });

      canvas.add(group);
      canvas.renderAll();
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Box className="w-4 h-4" />
          Components
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 p-0 overflow-hidden flex flex-col">
        {/* Search */}
        <div className="p-3 border-b">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search components..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8"
            />
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="all" className="flex-1 flex flex-col">
          <TabsList className="w-full justify-start rounded-none border-b px-3">
            <TabsTrigger value="all" className="text-xs">All</TabsTrigger>
            <TabsTrigger value="popular" className="text-xs">
              <Star className="w-3 h-3 mr-1" />
              Popular
            </TabsTrigger>
            <TabsTrigger value="favorites" className="text-xs">
              <Heart className="w-3 h-3 mr-1" />
              Favorites
            </TabsTrigger>
          </TabsList>

          {/* All Components */}
          <TabsContent value="all" className="flex-1 m-0">
            {/* Category filters */}
            <ScrollArea className="h-12 border-b">
              <div className="flex gap-2 px-3 py-2">
                {categories.map(category => (
                  <Badge
                    key={category}
                    variant={selectedCategory === category ? 'default' : 'outline'}
                    className="cursor-pointer whitespace-nowrap"
                    onClick={() => setSelectedCategory(category)}
                  >
                    {category}
                  </Badge>
                ))}
              </div>
            </ScrollArea>

            {/* Component grid */}
            <ScrollArea className="flex-1">
              <div className="grid grid-cols-2 gap-3 p-3">
                {filteredComponents.map(component => (
                  <Card 
                    key={component.id}
                    className="group cursor-pointer hover:shadow-md transition-shadow overflow-hidden"
                    onClick={() => handleInsertComponent(component)}
                  >
                    {/* Thumbnail */}
                    <div className="aspect-video bg-linear-to-br from-primary/20 to-secondary/20 relative">
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Layers className="w-8 h-8 text-muted-foreground/50" />
                      </div>
                      {/* Favorite button */}
                      <Button
                        size="sm"
                        variant="ghost"
                        className="absolute top-2 right-2 h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleFavorite(component.id);
                        }}
                      >
                        <Heart 
                          className={cn(
                            "w-3.5 h-3.5",
                            favorites.has(component.id) && "fill-red-500 text-red-500"
                          )}
                        />
                      </Button>
                    </div>
                    
                    {/* Info */}
                    <div className="p-2">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-medium truncate">
                            {component.name}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {component.category}
                          </div>
                        </div>
                        {component.popular && (
                          <Star className="w-3 h-3 text-yellow-500 fill-yellow-500 flex-shrink-0 ml-1" />
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {filteredComponents.length === 0 && (
                <div className="text-center py-12 text-muted-foreground text-sm">
                  No components found
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          {/* Popular Components */}
          <TabsContent value="popular" className="flex-1 m-0">
            <ScrollArea className="h-full">
              <div className="grid grid-cols-2 gap-3 p-3">
                {components.filter(c => c.popular).map(component => (
                  <Card 
                    key={component.id}
                    className="cursor-pointer hover:shadow-md transition-shadow overflow-hidden"
                    onClick={() => handleInsertComponent(component)}
                  >
                    <div className="aspect-video bg-linear-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                      <Layers className="w-8 h-8 text-muted-foreground/50" />
                    </div>
                    <div className="p-2">
                      <div className="text-xs font-medium truncate">{component.name}</div>
                      <div className="text-xs text-muted-foreground">{component.category}</div>
                    </div>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </TabsContent>

          {/* Favorites */}
          <TabsContent value="favorites" className="flex-1 m-0">
            <ScrollArea className="h-full">
              {favorites.size === 0 ? (
                <div className="text-center py-12 text-muted-foreground text-sm">
                  No favorites yet
                  <div className="text-xs mt-2">
                    Click the <Heart className="w-3 h-3 inline" /> icon to add components
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-3 p-3">
                  {components.filter(c => favorites.has(c.id)).map(component => (
                    <Card 
                      key={component.id}
                      className="cursor-pointer hover:shadow-md transition-shadow overflow-hidden"
                      onClick={() => handleInsertComponent(component)}
                    >
                      <div className="aspect-video bg-linear-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                        <Layers className="w-8 h-8 text-muted-foreground/50" />
                      </div>
                      <div className="p-2">
                        <div className="text-xs font-medium truncate">{component.name}</div>
                        <div className="text-xs text-muted-foreground">{component.category}</div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
