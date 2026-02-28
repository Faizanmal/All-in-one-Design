"use client";

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Search, Layout, FileImage, Palette, Sparkles,
  Heart, Eye, Download, Star, Filter, X, ArrowRight, Crown, Loader2,
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from 'sonner';
import { MainHeader } from '@/components/layout/MainHeader';

interface Template {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  category: { id: number; name: string; slug: string } | null;
  tags: string[];
  thumbnail: string;
  preview_images: string[];
  pricing_type: 'free' | 'paid' | 'subscription';
  price: string;
  sale_price: string | null;
  downloads: number;
  views: number;
  favorites: number;
  average_rating: string;
  rating_count: number;
  is_featured: boolean;
  is_editors_choice: boolean;
  canvas_width: number;
  canvas_height: number;
  creator: { username: string } | null;
}

// Fallback template data for when the API is not available
const fallbackTemplates: Template[] = [
  {
    id: 1, title: 'Modern Landing Page', slug: 'modern-landing', description: 'Clean landing page design with hero section, features, and CTA.',
    short_description: 'Clean and modern landing page', category: { id: 1, name: 'UI/UX Design', slug: 'ui_ux' },
    tags: ['website', 'landing', 'modern', 'saas'], thumbnail: '', preview_images: [],
    pricing_type: 'free', price: '0.00', sale_price: null, downloads: 2340, views: 12500,
    favorites: 890, average_rating: '4.80', rating_count: 156, is_featured: true,
    is_editors_choice: true, canvas_width: 1440, canvas_height: 900, creator: { username: 'designpro' },
  },
  {
    id: 2, title: 'Instagram Post Bundle', slug: 'instagram-bundle', description: 'Pack of 10 Instagram post templates for social media marketing.',
    short_description: 'Instagram post template pack', category: { id: 2, name: 'Social Media', slug: 'graphic' },
    tags: ['social', 'instagram', 'marketing', 'post'], thumbnail: '', preview_images: [],
    pricing_type: 'free', price: '0.00', sale_price: null, downloads: 5670, views: 23400,
    favorites: 1200, average_rating: '4.90', rating_count: 234, is_featured: true,
    is_editors_choice: false, canvas_width: 1080, canvas_height: 1080, creator: { username: 'socialdesigner' },
  },
  {
    id: 3, title: 'Minimalist Logo Pack', slug: 'minimalist-logos', description: 'Collection of 20 minimalist logo templates for modern brands.',
    short_description: 'Clean minimalist logo designs', category: { id: 3, name: 'Logo Design', slug: 'logo' },
    tags: ['logo', 'minimal', 'brand', 'identity'], thumbnail: '', preview_images: [],
    pricing_type: 'free', price: '0.00', sale_price: null, downloads: 3450, views: 18900,
    favorites: 980, average_rating: '4.70', rating_count: 189, is_featured: false,
    is_editors_choice: true, canvas_width: 800, canvas_height: 800, creator: { username: 'logocreator' },
  },
  {
    id: 4, title: 'Mobile App UI Kit', slug: 'mobile-ui-kit', description: 'Complete mobile app UI kit with 50+ screens for iOS and Android.',
    short_description: 'Mobile app interface kit', category: { id: 1, name: 'UI/UX Design', slug: 'ui_ux' },
    tags: ['mobile', 'app', 'ui-kit', 'ios', 'android'], thumbnail: '', preview_images: [],
    pricing_type: 'paid', price: '29.99', sale_price: '19.99', downloads: 1890, views: 15600,
    favorites: 760, average_rating: '4.85', rating_count: 145, is_featured: true,
    is_editors_choice: true, canvas_width: 375, canvas_height: 812, creator: { username: 'appdesigner' },
  },
  {
    id: 5, title: 'Event Poster Collection', slug: 'event-posters', description: 'Eye-catching event poster designs for concerts, conferences, and meetups.',
    short_description: 'Event poster designs', category: { id: 4, name: 'Print Design', slug: 'graphic' },
    tags: ['poster', 'event', 'marketing', 'print'], thumbnail: '', preview_images: [],
    pricing_type: 'free', price: '0.00', sale_price: null, downloads: 4230, views: 19800,
    favorites: 890, average_rating: '4.60', rating_count: 167, is_featured: false,
    is_editors_choice: false, canvas_width: 1080, canvas_height: 1920, creator: { username: 'printmaster' },
  },
  {
    id: 6, title: 'Tech Startup Logo', slug: 'tech-logo', description: 'Modern tech startup logo with gradient and geometric design.',
    short_description: 'Modern tech startup logo', category: { id: 3, name: 'Logo Design', slug: 'logo' },
    tags: ['logo', 'tech', 'startup', 'gradient'], thumbnail: '', preview_images: [],
    pricing_type: 'free', price: '0.00', sale_price: null, downloads: 2100, views: 11200,
    favorites: 540, average_rating: '4.50', rating_count: 98, is_featured: false,
    is_editors_choice: false, canvas_width: 800, canvas_height: 800, creator: { username: 'logocreator' },
  },
  {
    id: 7, title: 'Dashboard UI Template', slug: 'dashboard-ui', description: 'Admin dashboard template with charts, tables, and dark mode support.',
    short_description: 'SaaS dashboard template', category: { id: 1, name: 'UI/UX Design', slug: 'ui_ux' },
    tags: ['dashboard', 'admin', 'saas', 'dark-mode'], thumbnail: '', preview_images: [],
    pricing_type: 'paid', price: '39.99', sale_price: null, downloads: 1560, views: 13400,
    favorites: 670, average_rating: '4.90', rating_count: 112, is_featured: true,
    is_editors_choice: true, canvas_width: 1920, canvas_height: 1080, creator: { username: 'uiexpert' },
  },
  {
    id: 8, title: 'YouTube Thumbnail Pack', slug: 'youtube-thumbnails', description: 'Bold YouTube thumbnail templates designed for maximum click-through rate.',
    short_description: 'YouTube thumbnail templates', category: { id: 2, name: 'Social Media', slug: 'graphic' },
    tags: ['youtube', 'thumbnail', 'video', 'social'], thumbnail: '', preview_images: [],
    pricing_type: 'free', price: '0.00', sale_price: null, downloads: 7800, views: 34500,
    favorites: 2100, average_rating: '4.75', rating_count: 298, is_featured: true,
    is_editors_choice: false, canvas_width: 1280, canvas_height: 720, creator: { username: 'videodesigner' },
  },
  {
    id: 9, title: 'Business Card Designer', slug: 'business-cards', description: 'Professional business card templates with print-ready bleed settings.',
    short_description: 'Professional business cards', category: { id: 4, name: 'Print Design', slug: 'graphic' },
    tags: ['business-card', 'print', 'professional', 'corporate'], thumbnail: '', preview_images: [],
    pricing_type: 'free', price: '0.00', sale_price: null, downloads: 3200, views: 16700,
    favorites: 780, average_rating: '4.65', rating_count: 134, is_featured: false,
    is_editors_choice: true, canvas_width: 1050, canvas_height: 600, creator: { username: 'printmaster' },
  },
];

// Color palettes for template card backgrounds
const gradients = [
  'from-blue-500/20 to-purple-500/20',
  'from-emerald-500/20 to-teal-500/20',
  'from-orange-500/20 to-red-500/20',
  'from-pink-500/20 to-rose-500/20',
  'from-indigo-500/20 to-blue-500/20',
  'from-yellow-500/20 to-amber-500/20',
  'from-violet-500/20 to-fuchsia-500/20',
  'from-cyan-500/20 to-sky-500/20',
  'from-lime-500/20 to-green-500/20',
];

export default function TemplatesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('popular');
  const [previewTemplate, setPreviewTemplate] = useState<Template | null>(null);
  const router = useRouter();
  const queryClient = useQueryClient();

  // Fetch templates from marketplace API
  const { data: templatesData, isLoading } = useQuery({
    queryKey: ['marketplace-templates', selectedCategory, sortBy],
    queryFn: async () => {
      try {
        const params: Record<string, string> = {};
        if (selectedCategory !== 'all') params.category = selectedCategory;
        if (sortBy === 'popular') params.ordering = '-downloads';
        else if (sortBy === 'newest') params.ordering = '-created_at';
        else if (sortBy === 'rating') params.ordering = '-average_rating';
        const response = await apiClient.get('/v1/marketplace/templates/', { params });
        return response.data?.results || response.data || [];
      } catch {
        return fallbackTemplates;
      }
    },
    staleTime: 1000 * 60 * 5,
  });

  const templates: Template[] = templatesData || fallbackTemplates;

  const filteredTemplates = useMemo(() => {
    return templates.filter((t) => {
      const matchSearch = !searchQuery || 
        t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.short_description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchCat = selectedCategory === 'all' ||
        t.category?.slug === selectedCategory ||
        (selectedCategory === 'featured' && t.is_featured);

      return matchSearch && matchCat;
    });
  }, [templates, searchQuery, selectedCategory]);

  // Use template
  const useTemplateMutation = useMutation({
    mutationFn: async (templateId: number) => {
      const response = await apiClient.post(`/v1/marketplace/templates/${templateId}/use/`);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success('Project created from template!');
      router.push(`/editor?project=${data.project_id || data.id}`);
    },
    onError: () => {
      toast.error('Failed to create project from template');
    },
  });

  const handleUseTemplate = (template: Template) => {
    useTemplateMutation.mutate(template.id);
  };

  const getCategoryIcon = (slug: string | undefined) => {
    switch (slug) {
      case 'ui_ux': return <Layout className="h-5 w-5" />;
      case 'graphic': return <FileImage className="h-5 w-5" />;
      case 'logo': return <Palette className="h-5 w-5" />;
      default: return <Sparkles className="h-5 w-5" />;
    }
  };

  const formatNumber = (n: number) => {
    if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
    return n.toString();
  };

  return (
    <div className="min-h-screen bg-background">
      <MainHeader />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-3">
            Template Gallery
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Start with a professionally designed template and customize it to match your brand.
            Thousands of templates across every category.
          </p>
        </div>

        {/* Search + Filters */}
        <div className="mb-8 space-y-4">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                placeholder="Search templates by name, tag, or keyword..."
                className="pl-10 h-12"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  onClick={() => setSearchQuery('')}
                >
                  <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
                </button>
              )}
            </div>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-[160px] h-12">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="popular">Most Popular</SelectItem>
                <SelectItem value="newest">Newest</SelectItem>
                <SelectItem value="rating">Highest Rated</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
            <TabsList className="flex-wrap h-auto gap-1 p-1">
              <TabsTrigger value="all">
                <Sparkles className="h-4 w-4 mr-1" /> All
              </TabsTrigger>
              <TabsTrigger value="featured">
                <Crown className="h-4 w-4 mr-1" /> Featured
              </TabsTrigger>
              <TabsTrigger value="ui_ux">
                <Layout className="h-4 w-4 mr-1" /> UI/UX
              </TabsTrigger>
              <TabsTrigger value="graphic">
                <FileImage className="h-4 w-4 mr-1" /> Graphics
              </TabsTrigger>
              <TabsTrigger value="logo">
                <Palette className="h-4 w-4 mr-1" /> Logos
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Results count */}
        <div className="mb-4 text-sm text-muted-foreground">
          {isLoading ? 'Loading...' : `${filteredTemplates.length} templates found`}
        </div>

        {/* Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="p-0">
                  <Skeleton className="aspect-[4/3] w-full rounded-t-lg" />
                  <div className="p-4 space-y-2">
                    <Skeleton className="h-5 w-3/4" />
                    <Skeleton className="h-4 w-full" />
                    <div className="flex gap-1">
                      <Skeleton className="h-5 w-16" />
                      <Skeleton className="h-5 w-16" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredTemplates.length === 0 ? (
          <Card>
            <CardContent className="text-center py-16">
              <Search className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium">No templates found</p>
              <p className="text-muted-foreground mt-1">Try different keywords or browse all categories</p>
              <Button variant="outline" className="mt-4" onClick={() => { setSearchQuery(''); setSelectedCategory('all'); }}>
                Clear filters
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template, idx) => (
              <Card
                key={template.id}
                className="group overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer border-2 hover:border-primary/30"
                onClick={() => setPreviewTemplate(template)}
              >
                <CardContent className="p-0">
                  {/* Thumbnail */}
                  <div className={`relative aspect-[4/3] bg-gradient-to-br ${gradients[idx % gradients.length]} flex items-center justify-center overflow-hidden`}>
                    {template.thumbnail ? (
                      <img
                        src={template.thumbnail}
                        alt={template.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        loading="lazy"
                      />
                    ) : (
                      <div className="flex flex-col items-center gap-2 text-muted-foreground/50">
                        {getCategoryIcon(template.category?.slug)}
                        <span className="text-xs font-medium">{template.canvas_width}×{template.canvas_height}</span>
                      </div>
                    )}

                    {/* Overlay actions */}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center gap-3">
                      <Button
                        size="sm"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => { e.stopPropagation(); setPreviewTemplate(template); }}
                      >
                        <Eye className="w-4 h-4 mr-1" /> Preview
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => { e.stopPropagation(); handleUseTemplate(template); }}
                      >
                        <ArrowRight className="w-4 h-4 mr-1" /> Use
                      </Button>
                    </div>

                    {/* Badges */}
                    <div className="absolute top-2 left-2 flex gap-1">
                      {template.is_editors_choice && (
                        <Badge className="bg-yellow-500/90 text-white text-xs">
                          <Star className="w-3 h-3 mr-0.5 fill-current" /> Editor&apos;s Choice
                        </Badge>
                      )}
                      {template.pricing_type === 'paid' && (
                        <Badge variant="secondary" className="text-xs">
                          {template.sale_price ? (
                            <><s className="opacity-60">${template.price}</s> ${template.sale_price}</>
                          ) : (
                            `$${template.price}`
                          )}
                        </Badge>
                      )}
                      {template.pricing_type === 'free' && (
                        <Badge variant="secondary" className="text-xs bg-green-500/10 text-green-700">
                          Free
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Info */}
                  <div className="p-4">
                    <h3 className="font-semibold text-sm truncate">{template.title}</h3>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                      {template.short_description || template.description}
                    </p>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mt-2">
                      {template.tags.slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs px-1.5 py-0">
                          {tag}
                        </Badge>
                      ))}
                      {template.tags.length > 3 && (
                        <span className="text-xs text-muted-foreground">+{template.tags.length - 3}</span>
                      )}
                    </div>

                    {/* Stats */}
                    <div className="flex items-center gap-3 mt-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Download className="w-3 h-3" /> {formatNumber(template.downloads)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Heart className="w-3 h-3" /> {formatNumber(template.favorites)}
                      </span>
                      {parseFloat(template.average_rating) > 0 && (
                        <span className="flex items-center gap-1">
                          <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
                          {parseFloat(template.average_rating).toFixed(1)}
                        </span>
                      )}
                      <span className="ml-auto">
                        by {template.creator?.username || 'AI Design Tool'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>

      {/* Preview Dialog */}
      <Dialog open={!!previewTemplate} onOpenChange={(open) => !open && setPreviewTemplate(null)}>
        {previewTemplate && (
          <DialogContent className="max-w-3xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                {previewTemplate.title}
                {previewTemplate.is_editors_choice && (
                  <Badge className="bg-yellow-500/90 text-white text-xs">
                    <Star className="w-3 h-3 mr-0.5 fill-current" /> Editor&apos;s Choice
                  </Badge>
                )}
              </DialogTitle>
              <DialogDescription>{previewTemplate.description}</DialogDescription>
            </DialogHeader>

            {/* Preview */}
            <div className={`aspect-video bg-gradient-to-br ${gradients[previewTemplate.id % gradients.length]} rounded-lg flex items-center justify-center overflow-hidden`}>
              {previewTemplate.thumbnail ? (
                <img
                  src={previewTemplate.thumbnail}
                  alt={previewTemplate.title}
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="text-center text-muted-foreground/50">
                  {getCategoryIcon(previewTemplate.category?.slug)}
                  <p className="mt-2 text-sm">
                    {previewTemplate.canvas_width}×{previewTemplate.canvas_height}px
                  </p>
                </div>
              )}
            </div>

            {/* Details */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Canvas Size:</span>{' '}
                {previewTemplate.canvas_width}×{previewTemplate.canvas_height}px
              </div>
              <div>
                <span className="text-muted-foreground">Category:</span>{' '}
                {previewTemplate.category?.name || 'General'}
              </div>
              <div>
                <span className="text-muted-foreground">Downloads:</span>{' '}
                {previewTemplate.downloads.toLocaleString()}
              </div>
              <div>
                <span className="text-muted-foreground">Rating:</span>{' '}
                {parseFloat(previewTemplate.average_rating).toFixed(1)} ({previewTemplate.rating_count} reviews)
              </div>
            </div>

            <div className="flex flex-wrap gap-1">
              {previewTemplate.tags.map((tag) => (
                <Badge key={tag} variant="outline">{tag}</Badge>
              ))}
            </div>

            <DialogFooter className="gap-2">
              <Button variant="outline" onClick={() => setPreviewTemplate(null)}>
                Cancel
              </Button>
              <Button
                onClick={() => handleUseTemplate(previewTemplate)}
                disabled={useTemplateMutation.isPending}
              >
                {useTemplateMutation.isPending ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Creating...</>
                ) : (
                  <><ArrowRight className="w-4 h-4 mr-2" /> Use This Template</>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
}
