"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Layout, FileImage, Palette, Sparkles } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { MainHeader } from '@/components/layout/MainHeader';

// Mock template data - Replace with actual API call
const mockTemplates = [
  {
    id: 1,
    name: 'Modern Landing Page',
    category: 'ui_ux',
    description: 'Clean and modern landing page design',
    thumbnail: '/templates/landing-page.png',
    tags: ['website', 'landing', 'modern'],
  },
  {
    id: 2,
    name: 'Social Media Post',
    category: 'graphic',
    description: 'Instagram post template',
    thumbnail: '/templates/social-post.png',
    tags: ['social', 'instagram', 'marketing'],
  },
  {
    id: 3,
    name: 'Minimalist Logo',
    category: 'logo',
    description: 'Clean minimalist logo design',
    thumbnail: '/templates/minimalist-logo.png',
    tags: ['logo', 'minimal', 'brand'],
  },
  {
    id: 4,
    name: 'Mobile App UI',
    category: 'ui_ux',
    description: 'Modern mobile app interface',
    thumbnail: '/templates/mobile-app.png',
    tags: ['mobile', 'app', 'ui'],
  },
  {
    id: 5,
    name: 'Event Poster',
    category: 'graphic',
    description: 'Eye-catching event poster design',
    thumbnail: '/templates/event-poster.png',
    tags: ['poster', 'event', 'marketing'],
  },
  {
    id: 6,
    name: 'Tech Startup Logo',
    category: 'logo',
    description: 'Modern tech startup logo',
    thumbnail: '/templates/tech-logo.png',
    tags: ['logo', 'tech', 'startup'],
  },
];

export default function TemplatesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const router = useRouter();
  const { toast } = useToast();

  const filteredTemplates = mockTemplates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const handleUseTemplate = async (templateId: number) => {
    toast({
      title: 'Creating project from template',
      description: 'Please wait...',
    });
    
    // Implement actual template creation API call
    try {
      const response = await fetch('/api/templates/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          name: `Template ${templateId}`,
          category: 'custom',
          data: { templateId },
          is_public: false,
        }),
      });
      
      if (response.ok) {
        const newTemplate = await response.json();
        console.log('Template created:', newTemplate);
      } else {
        console.error('Failed to create template');
      }
    } catch (error) {
      console.error('Error creating template:', error);
    }
    
    router.push(`/editor?template=${templateId}`);
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'ui_ux':
        return <Layout className="h-5 w-5" />;
      case 'graphic':
        return <FileImage className="h-5 w-5" />;
      case 'logo':
        return <Palette className="h-5 w-5" />;
      default:
        return <Sparkles className="h-5 w-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <MainHeader />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Template Gallery</h1>
          <p className="text-gray-600 mt-2">Choose from our collection of professionally designed templates</p>
        </div>
        {/* Search and Filters */}
        <div className="mb-8 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Search templates..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">
                <Sparkles className="h-4 w-4 mr-2" />
                All Templates
              </TabsTrigger>
              <TabsTrigger value="ui_ux">
                <Layout className="h-4 w-4 mr-2" />
                UI/UX Design
              </TabsTrigger>
              <TabsTrigger value="graphic">
                <FileImage className="h-4 w-4 mr-2" />
                Graphic Design
              </TabsTrigger>
              <TabsTrigger value="logo">
                <Palette className="h-4 w-4 mr-2" />
                Logo Design
              </TabsTrigger>
            </TabsList>

            <TabsContent value={selectedCategory} className="mt-6">
              {filteredTemplates.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-12">
                    <Search className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No templates found matching your criteria</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredTemplates.map((template) => (
                    <Card key={template.id} className="hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <div className="aspect-video bg-linear-to-br from-gray-100 to-gray-200 rounded flex items-center justify-center mb-3">
                          {getCategoryIcon(template.category)}
                        </div>
                        <CardTitle className="text-lg">{template.name}</CardTitle>
                        <CardDescription>{template.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {template.tags.map((tag) => (
                            <Badge key={tag} variant="secondary">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                      <CardFooter>
                        <Button 
                          className="w-full" 
                          onClick={() => handleUseTemplate(template.id)}
                        >
                          Use Template
                        </Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}
