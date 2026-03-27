"use client";

/* eslint-disable @next/next/no-img-element */

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  ShoppingCart,
  Search,
  Star,
  Heart,
  Download,
  Eye,
  Grid,
  List,
  TrendingUp,
  Sparkles,
  Crown,
  CheckCircle,
  Package,
  Bookmark,
  Share2,
  MoreVertical,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface TemplateCategory {
  id: number;
  name: string;
  slug: string;
  icon: string;
  template_count: number;
}

interface TemplateCreator {
  id: number;
  username: string;
  avatar?: string;
  is_verified: boolean;
  total_sales: number;
}

interface Template {
  id: number;
  title: string;
  slug: string;
  thumbnail: string;
  preview_images: string[];
  category: TemplateCategory;
  creator: TemplateCreator;
  price: number;
  is_free: boolean;
  is_premium: boolean;
  is_featured: boolean;
  rating: number;
  reviews_count: number;
  downloads: number;
  likes: number;
  is_liked: boolean;
  is_purchased: boolean;
  tags: string[];
  created_at: string;
}

// Mock Data
const mockCategories: TemplateCategory[] = [
  { id: 1, name: 'All Templates', slug: 'all', icon: 'Grid', template_count: 1240 },
  { id: 2, name: 'Social Media', slug: 'social-media', icon: 'Share2', template_count: 456 },
  { id: 3, name: 'Presentations', slug: 'presentations', icon: 'Monitor', template_count: 234 },
  { id: 4, name: 'Marketing', slug: 'marketing', icon: 'TrendingUp', template_count: 189 },
  { id: 5, name: 'Print', slug: 'print', icon: 'Printer', template_count: 167 },
  { id: 6, name: 'UI Kits', slug: 'ui-kits', icon: 'Layers', template_count: 98 },
  { id: 7, name: 'Logos', slug: 'logos', icon: 'Hexagon', template_count: 96 },
];

const mockTemplates: Template[] = [
  {
    id: 1, title: 'Modern Business Presentation', slug: 'modern-business-presentation',
    thumbnail: 'https://picsum.photos/seed/t1/400/300',
    preview_images: ['https://picsum.photos/seed/t1a/800/600', 'https://picsum.photos/seed/t1b/800/600'],
    category: mockCategories[2],
    creator: { id: 1, username: 'DesignPro', is_verified: true, total_sales: 1234 },
    price: 29, is_free: false, is_premium: true, is_featured: true,
    rating: 4.8, reviews_count: 156, downloads: 2340, likes: 567, is_liked: false, is_purchased: false,
    tags: ['business', 'corporate', 'professional', 'minimal'],
    created_at: '2024-02-10T10:00:00Z',
  },
  {
    id: 2, title: 'Instagram Story Pack', slug: 'instagram-story-pack',
    thumbnail: 'https://picsum.photos/seed/t2/400/300',
    preview_images: ['https://picsum.photos/seed/t2a/800/600'],
    category: mockCategories[1],
    creator: { id: 2, username: 'SocialMaster', is_verified: true, total_sales: 987 },
    price: 0, is_free: true, is_premium: false, is_featured: false,
    rating: 4.5, reviews_count: 89, downloads: 5670, likes: 1234, is_liked: true, is_purchased: true,
    tags: ['instagram', 'story', 'social', 'trendy'],
    created_at: '2024-02-08T15:30:00Z',
  },
  {
    id: 3, title: 'E-commerce Landing Page Kit', slug: 'ecommerce-landing-kit',
    thumbnail: 'https://picsum.photos/seed/t3/400/300',
    preview_images: ['https://picsum.photos/seed/t3a/800/600'],
    category: mockCategories[5],
    creator: { id: 3, username: 'UIExpert', is_verified: true, total_sales: 2345 },
    price: 49, is_free: false, is_premium: true, is_featured: true,
    rating: 4.9, reviews_count: 234, downloads: 1890, likes: 890, is_liked: false, is_purchased: false,
    tags: ['ecommerce', 'landing', 'ui', 'web'],
    created_at: '2024-02-05T09:00:00Z',
  },
  {
    id: 4, title: 'Marketing Flyer Bundle', slug: 'marketing-flyer-bundle',
    thumbnail: 'https://picsum.photos/seed/t4/400/300',
    preview_images: ['https://picsum.photos/seed/t4a/800/600'],
    category: mockCategories[3],
    creator: { id: 4, username: 'PrintPro', is_verified: false, total_sales: 456 },
    price: 19, is_free: false, is_premium: false, is_featured: false,
    rating: 4.3, reviews_count: 67, downloads: 890, likes: 234, is_liked: false, is_purchased: false,
    tags: ['flyer', 'marketing', 'print', 'promotional'],
    created_at: '2024-02-01T12:00:00Z',
  },
  {
    id: 5, title: 'Minimalist Logo Collection', slug: 'minimalist-logo-collection',
    thumbnail: 'https://picsum.photos/seed/t5/400/300',
    preview_images: ['https://picsum.photos/seed/t5a/800/600'],
    category: mockCategories[6],
    creator: { id: 1, username: 'DesignPro', is_verified: true, total_sales: 1234 },
    price: 39, is_free: false, is_premium: true, is_featured: false,
    rating: 4.7, reviews_count: 123, downloads: 1234, likes: 456, is_liked: true, is_purchased: false,
    tags: ['logo', 'minimal', 'brand', 'identity'],
    created_at: '2024-01-28T14:00:00Z',
  },
  {
    id: 6, title: 'YouTube Thumbnail Pack', slug: 'youtube-thumbnail-pack',
    thumbnail: 'https://picsum.photos/seed/t6/400/300',
    preview_images: ['https://picsum.photos/seed/t6a/800/600'],
    category: mockCategories[1],
    creator: { id: 5, username: 'CreatorHub', is_verified: true, total_sales: 3456 },
    price: 0, is_free: true, is_premium: false, is_featured: true,
    rating: 4.6, reviews_count: 345, downloads: 8900, likes: 2345, is_liked: false, is_purchased: true,
    tags: ['youtube', 'thumbnail', 'video', 'creator'],
    created_at: '2024-01-25T11:00:00Z',
  },
];

// Template Card Component
function TemplateCard({ template, onView, onLike, onPurchase }: {
  template: Template;
  onView: (template: Template) => void;
  onLike: (id: number) => void;
  onPurchase: (template: Template) => void;
}) {
  return (
    <div className="group bg-white rounded-xl border border-gray-200 overflow-hidden transition-all hover:shadow-xl hover:border-gray-300">
      {/* Thumbnail */}
      <div className="relative aspect-[4/3] bg-gray-100 overflow-hidden">
        <img src={template.thumbnail} alt={template.title} className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
        
        {/* Overlay */}
        <div className="absolute inset-0 bg-linear-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="absolute bottom-3 left-3 right-3 flex justify-center gap-2">
            <Button size="sm" variant="secondary" className="h-9" onClick={() => onView(template)}>
              <Eye className="h-4 w-4 mr-1" />Preview
            </Button>
            <Button size="sm" className="h-9" onClick={() => onPurchase(template)}>
              {template.is_purchased ? <><CheckCircle className="h-4 w-4 mr-1" />Owned</> : template.is_free ? <><Download className="h-4 w-4 mr-1" />Download</> : <><ShoppingCart className="h-4 w-4 mr-1" />${template.price}</>}
            </Button>
          </div>
        </div>

        {/* Badges */}
        <div className="absolute top-3 left-3 flex gap-1.5">
          {template.is_featured && <Badge className="bg-amber-500 text-white border-0"><Sparkles className="h-3 w-3 mr-1" />Featured</Badge>}
          {template.is_premium && <Badge className="bg-purple-600 text-white border-0"><Crown className="h-3 w-3 mr-1" />Premium</Badge>}
          {template.is_free && <Badge className="bg-green-600 text-white border-0">Free</Badge>}
        </div>

        {/* Like Button */}
        <button onClick={() => onLike(template.id)} className="absolute top-3 right-3 p-2 rounded-full bg-white/90 hover:bg-white shadow-sm transition-colors">
          <Heart className={`h-4 w-4 ${template.is_liked ? 'fill-red-500 text-red-500' : 'text-gray-600'}`} />
        </button>
      </div>

      {/* Info */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="font-semibold text-gray-900 leading-tight line-clamp-1">{template.title}</h3>
          <DropdownMenu>
            <DropdownMenuTrigger asChild><Button variant="ghost" size="sm" className="h-7 w-7 p-0 shrink-0"><MoreVertical className="h-4 w-4" /></Button></DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem><Bookmark className="h-4 w-4 mr-2" />Save to Collection</DropdownMenuItem>
              <DropdownMenuItem><Share2 className="h-4 w-4 mr-2" />Share</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Category & Creator */}
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
          <span>{template.category.name}</span>
          <span>•</span>
          <span className="flex items-center gap-1">
            by {template.creator.username}
            {template.creator.is_verified && <CheckCircle className="h-3.5 w-3.5 text-blue-500 fill-blue-100" />}
          </span>
        </div>

        {/* Rating & Stats */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 text-sm">
            <span className="flex items-center gap-1 text-amber-500">
              <Star className="h-4 w-4 fill-current" />{template.rating}
              <span className="text-gray-400">({template.reviews_count})</span>
            </span>
            <span className="flex items-center gap-1 text-gray-400">
              <Download className="h-3.5 w-3.5" />{template.downloads.toLocaleString()}
            </span>
          </div>
          <div className="text-right">
            {template.is_free ? <span className="text-green-600 font-semibold">Free</span> : <span className="text-gray-900 font-bold">${template.price}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TemplateMarketplacePage() {
  const { toast } = useToast();
  const [templates, setTemplates] = useState<Template[]>(mockTemplates);
  const [categories] = useState<TemplateCategory[]>(mockCategories);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('featured');
  const [priceFilter, setPriceFilter] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);

  const toggleLike = (id: number) => {
    setTemplates(prev => prev.map(t => t.id === id ? { ...t, is_liked: !t.is_liked, likes: t.is_liked ? t.likes - 1 : t.likes + 1 } : t));
    toast({ title: 'Updated', description: 'Template added to favorites' });
  };

  const handlePurchase = (template: Template) => {
    if (template.is_purchased) {
      toast({ title: 'Already Owned', description: 'Open this template in the editor' });
    } else if (template.is_free) {
      setTemplates(prev => prev.map(t => t.id === template.id ? { ...t, is_purchased: true, downloads: t.downloads + 1 } : t));
      toast({ title: 'Downloaded!', description: 'Template added to your library' });
    } else {
      setSelectedTemplate(template);
      setShowPreviewDialog(true);
    }
  };

  const handleView = (template: Template) => {
    setSelectedTemplate(template);
    setShowPreviewDialog(true);
  };

  const filteredTemplates = templates.filter(t => {
    if (searchTerm && !t.title.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    if (selectedCategory !== 'all' && t.category.slug !== selectedCategory) return false;
    if (priceFilter === 'free' && !t.is_free) return false;
    if (priceFilter === 'premium' && !t.is_premium) return false;
    if (priceFilter === 'paid' && t.is_free) return false;
    return true;
  });

  const stats = {
    totalTemplates: templates.length,
    freeTemplates: templates.filter(t => t.is_free).length,
    premiumTemplates: templates.filter(t => t.is_premium).length,
    myDownloads: templates.filter(t => t.is_purchased).length,
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-hidden flex flex-col">
          {/* Header */}
          <div className="bg-linear-to-r from-purple-600 to-blue-600 text-white px-8 py-8">
            <div className="max-w-7xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h1 className="text-3xl font-bold mb-2">Template Marketplace</h1>
                  <p className="text-purple-100">Discover thousands of professional design templates</p>
                </div>
                <div className="flex gap-3">
                  <Button variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-0">
                    <Package className="h-4 w-4 mr-2" />My Purchases
                  </Button>
                  <Button className="bg-white text-purple-600 hover:bg-gray-100">
                    <TrendingUp className="h-4 w-4 mr-2" />Sell Templates
                  </Button>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                  <div className="text-2xl font-bold">{stats.totalTemplates.toLocaleString()}</div>
                  <div className="text-purple-200 text-sm">Total Templates</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                  <div className="text-2xl font-bold">{stats.freeTemplates}</div>
                  <div className="text-purple-200 text-sm">Free Templates</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                  <div className="text-2xl font-bold">{stats.premiumTemplates}</div>
                  <div className="text-purple-200 text-sm">Premium Templates</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                  <div className="text-2xl font-bold">{stats.myDownloads}</div>
                  <div className="text-purple-200 text-sm">My Downloads</div>
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden flex">
            {/* Categories Sidebar */}
            <div className="w-56 border-r border-gray-200 bg-white p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Categories</h3>
              <div className="space-y-1">
                {categories.map(cat => (
                  <button key={cat.id} onClick={() => setSelectedCategory(cat.slug)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                      selectedCategory === cat.slug ? 'bg-purple-100 text-purple-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
                    }`}>
                    <span>{cat.name}</span>
                    <span className="text-xs text-gray-400">{cat.template_count}</span>
                  </button>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Price</h3>
                <div className="space-y-1">
                  {[{ value: 'all', label: 'All Prices' }, { value: 'free', label: 'Free Only' }, { value: 'paid', label: 'Paid Only' }, { value: 'premium', label: 'Premium' }].map(opt => (
                    <button key={opt.value} onClick={() => setPriceFilter(opt.value)}
                      className={`w-full flex items-center px-3 py-2 rounded-lg text-sm transition-colors ${
                        priceFilter === opt.value ? 'bg-purple-100 text-purple-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
                      }`}>
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Template Grid */}
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Toolbar */}
              <div className="bg-white border-b border-gray-200 p-4">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="relative flex-1 max-w-md">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input placeholder="Search templates..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-9" />
                    </div>
                    <Button variant="outline" size="sm"><Sparkles className="h-4 w-4 mr-2 text-purple-500" />AI Recommend</Button>
                  </div>
                  <div className="flex items-center gap-3">
                    <Select value={sortBy} onValueChange={setSortBy}>
                      <SelectTrigger className="w-[160px]"><SelectValue placeholder="Sort by" /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="featured">Featured</SelectItem>
                        <SelectItem value="popular">Most Popular</SelectItem>
                        <SelectItem value="newest">Newest</SelectItem>
                        <SelectItem value="rating">Highest Rated</SelectItem>
                        <SelectItem value="price-low">Price: Low to High</SelectItem>
                        <SelectItem value="price-high">Price: High to Low</SelectItem>
                      </SelectContent>
                    </Select>
                    <div className="flex items-center border border-gray-200 rounded-lg p-0.5">
                      <Button variant={viewMode === 'grid' ? 'secondary' : 'ghost'} size="sm" className="h-8 px-2" onClick={() => setViewMode('grid')}><Grid className="h-4 w-4" /></Button>
                      <Button variant={viewMode === 'list' ? 'secondary' : 'ghost'} size="sm" className="h-8 px-2" onClick={() => setViewMode('list')}><List className="h-4 w-4" /></Button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Templates */}
              <ScrollArea className="flex-1 p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {filteredTemplates.map(template => (
                    <TemplateCard key={template.id} template={template} onView={handleView} onLike={toggleLike} onPurchase={handlePurchase} />
                  ))}
                </div>
                {filteredTemplates.length === 0 && (
                  <div className="text-center py-16">
                    <Package className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-1">No templates found</h3>
                    <p className="text-gray-500">Try adjusting your search or filters</p>
                  </div>
                )}
              </ScrollArea>
            </div>
          </div>
        </main>
      </div>

      {/* Preview Dialog */}
      <Dialog open={showPreviewDialog} onOpenChange={setShowPreviewDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
          {selectedTemplate && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  {selectedTemplate.title}
                  {selectedTemplate.is_premium && <Badge className="bg-purple-600"><Crown className="h-3 w-3 mr-1" />Premium</Badge>}
                </DialogTitle>
                <DialogDescription>
                  by {selectedTemplate.creator.username} • {selectedTemplate.category.name}
                </DialogDescription>
              </DialogHeader>
              <div className="flex-1 overflow-auto">
                <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden mb-4">
                  <img src={selectedTemplate.thumbnail} alt={selectedTemplate.title} className="w-full h-full object-cover" />
                </div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1 text-amber-500"><Star className="h-5 w-5 fill-current" /><span className="font-semibold">{selectedTemplate.rating}</span><span className="text-gray-400">({selectedTemplate.reviews_count} reviews)</span></span>
                    <span className="flex items-center gap-1 text-gray-500"><Download className="h-4 w-4" />{selectedTemplate.downloads.toLocaleString()} downloads</span>
                    <span className="flex items-center gap-1 text-gray-500"><Heart className="h-4 w-4" />{selectedTemplate.likes.toLocaleString()} likes</span>
                  </div>
                  <div className="text-2xl font-bold">{selectedTemplate.is_free ? <span className="text-green-600">Free</span> : `$${selectedTemplate.price}`}</div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.tags.map((tag, i) => <Badge key={i} variant="secondary">{tag}</Badge>)}
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowPreviewDialog(false)}>Close</Button>
                <Button onClick={() => { handlePurchase(selectedTemplate); setShowPreviewDialog(false); }}>
                  {selectedTemplate.is_purchased ? 'Open in Editor' : selectedTemplate.is_free ? 'Download Free' : `Purchase for $${selectedTemplate.price}`}
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
