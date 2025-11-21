/**
 * Template Sidebar Component
 * Browse and apply design templates
 */
'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, TrendingUp, Star, Grid } from 'lucide-react';

interface Template {
  id: number;
  name: string;
  description: string;
  category: string;
  thumbnail_url?: string;
  use_count: number;
  tags: string[];
  is_premium: boolean;
}

export function TemplateSidebar({ 
  onTemplateSelect 
}: { 
  onTemplateSelect?: (template: Template) => void 
}) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTemplates();
  }, [selectedCategory, searchQuery]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      let url = '/api/projects/enhanced-templates/';
      const params = new URLSearchParams();
      
      if (selectedCategory !== 'all') {
        params.append('category', selectedCategory);
      }
      if (searchQuery) {
        params.append('search', searchQuery);
      }
      
      if (params.toString()) {
        url += '?' + params.toString();
      }

      const res = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (res.ok) {
        const data = await res.json();
        setTemplates(Array.isArray(data) ? data : data.results || []);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPopularTemplates = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/projects/enhanced-templates/popular/?limit=20', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (res.ok) {
        const data = await res.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Failed to fetch popular templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFeaturedTemplates = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/projects/enhanced-templates/featured/?limit=20', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (res.ok) {
        const data = await res.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Failed to fetch featured templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { value: 'all', label: 'All' },
    { value: 'social_media', label: 'Social Media' },
    { value: 'presentation', label: 'Presentation' },
    { value: 'poster', label: 'Poster' },
    { value: 'ui_kit', label: 'UI Kit' },
    { value: 'web_design', label: 'Web Design' },
    { value: 'logo', label: 'Logo' }
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold mb-4">Templates</h2>
        
        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Tabs */}
        <Tabs defaultValue="all" className="w-full">
          <TabsList className="w-full grid grid-cols-3">
            <TabsTrigger 
              value="all" 
              onClick={() => {
                setSelectedCategory('all');
                fetchTemplates();
              }}
            >
              <Grid className="w-4 h-4 mr-1" />
              All
            </TabsTrigger>
            <TabsTrigger 
              value="popular"
              onClick={fetchPopularTemplates}
            >
              <TrendingUp className="w-4 h-4 mr-1" />
              Popular
            </TabsTrigger>
            <TabsTrigger 
              value="featured"
              onClick={fetchFeaturedTemplates}
            >
              <Star className="w-4 h-4 mr-1" />
              Featured
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Category Filter */}
      <div className="p-4 border-b">
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <Badge
              key={cat.value}
              variant={selectedCategory === cat.value ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setSelectedCategory(cat.value)}
            >
              {cat.label}
            </Badge>
          ))}
        </div>
      </div>

      {/* Templates List */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : templates.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No templates found
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {templates.map((template) => (
              <Card 
                key={template.id}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => onTemplateSelect?.(template)}
              >
                {/* Thumbnail */}
                {template.thumbnail_url ? (
                  <div className="aspect-video bg-gray-200 dark:bg-gray-700 rounded-t-lg overflow-hidden">
                    <img
                      src={template.thumbnail_url}
                      alt={template.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ) : (
                  <div className="aspect-video bg-gradient-to-br from-blue-500 to-purple-600 rounded-t-lg flex items-center justify-center">
                    <Grid className="w-12 h-12 text-white opacity-50" />
                  </div>
                )}

                <CardContent className="p-3">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-sm line-clamp-1">
                      {template.name}
                    </h3>
                    {template.is_premium && (
                      <Badge variant="secondary" className="text-xs">
                        Pro
                      </Badge>
                    )}
                  </div>

                  <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
                    {template.description}
                  </p>

                  {/* Tags */}
                  {template.tags && template.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {template.tags.slice(0, 3).map((tag, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* Usage Stats */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{template.use_count} uses</span>
                    <Button size="sm" variant="ghost" className="h-7 text-xs">
                      Use Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
