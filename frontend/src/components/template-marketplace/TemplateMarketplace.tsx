'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  Store, Search, Star, Heart, ShoppingCart, Download,
  Filter, Grid, List, Eye, DollarSign, Tag, User,
  ChevronRight, ChevronDown, X, Check, Clock, Sparkles,
  TrendingUp, Award, Package, MessageSquare, Share2
} from 'lucide-react';

// Types
interface Template {
  id: string;
  name: string;
  description: string;
  thumbnailUrl: string;
  previewImages: string[];
  category: string;
  tags: string[];
  price: number;
  isFree: boolean;
  creator: {
    id: string;
    name: string;
    avatar: string;
    verified: boolean;
  };
  rating: number;
  reviewCount: number;
  downloadCount: number;
  isFavorite: boolean;
  isPurchased: boolean;
  createdAt: string;
  updatedAt: string;
}

interface Category {
  id: string;
  name: string;
  slug: string;
  icon: string;
  templateCount: number;
}

interface Review {
  id: string;
  userId: string;
  userName: string;
  userAvatar: string;
  rating: number;
  comment: string;
  createdAt: string;
  helpful: number;
}

// Template Card Component
export function TemplateCard({
  template,
  onView,
  onFavorite,
  onPurchase,
}: {
  template: Template;
  onView: () => void;
  onFavorite: () => void;
  onPurchase: () => void;
}) {
  return (
    <div className="group bg-gray-800 rounded-xl overflow-hidden transition-all hover:ring-2 hover:ring-blue-500">
      {/* Thumbnail */}
      <div className="aspect-video bg-gray-700 relative overflow-hidden">
        <img
          src={template.thumbnailUrl || '/placeholder.png'}
          alt={template.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        
        {/* Overlay */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button
            onClick={onView}
            className="p-3 bg-white/20 hover:bg-white/30 rounded-full"
          >
            <Eye className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Price Badge */}
        <div className="absolute top-3 left-3">
          {template.isFree ? (
            <span className="px-2 py-1 bg-green-600 text-white text-sm rounded-full font-medium">
              Free
            </span>
          ) : (
            <span className="px-2 py-1 bg-blue-600 text-white text-sm rounded-full font-medium">
              ${template.price}
            </span>
          )}
        </div>

        {/* Favorite Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onFavorite();
          }}
          className="absolute top-3 right-3 p-2 bg-black/50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Heart
            className={`w-5 h-5 ${
              template.isFavorite ? 'text-red-500 fill-red-500' : 'text-white'
            }`}
          />
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-white mb-1 truncate">{template.name}</h3>
        
        <div className="flex items-center gap-2 mb-3">
          <img
            src={template.creator.avatar || '/default-avatar.png'}
            alt={template.creator.name}
            className="w-5 h-5 rounded-full"
          />
          <span className="text-sm text-gray-400">{template.creator.name}</span>
          {template.creator.verified && (
            <Check className="w-4 h-4 text-blue-400" />
          )}
        </div>

        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-1 text-yellow-400">
            <Star className="w-4 h-4 fill-yellow-400" />
            <span>{template.rating.toFixed(1)}</span>
            <span className="text-gray-500">({template.reviewCount})</span>
          </div>
          <div className="flex items-center gap-1 text-gray-400">
            <Download className="w-4 h-4" />
            <span>{template.downloadCount}</span>
          </div>
        </div>

        <button
          onClick={onPurchase}
          className={`w-full mt-4 py-2 rounded-lg font-medium transition-colors ${
            template.isPurchased
              ? 'bg-gray-700 text-gray-400'
              : template.isFree
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
          disabled={template.isPurchased}
        >
          {template.isPurchased
            ? 'Purchased'
            : template.isFree
            ? 'Get Free'
            : `Buy for $${template.price}`}
        </button>
      </div>
    </div>
  );
}

// Template Detail Modal
export function TemplateDetailModal({
  template,
  isOpen,
  onClose,
  onPurchase,
}: {
  template: Template | null;
  isOpen: boolean;
  onClose: () => void;
  onPurchase: () => void;
}) {
  const [activeImage, setActiveImage] = useState(0);
  const [reviews, setReviews] = useState<Review[]>([
    {
      id: '1',
      userId: '1',
      userName: 'John Doe',
      userAvatar: '/avatars/john.jpg',
      rating: 5,
      comment: 'Excellent template! Easy to customize and looks great.',
      createdAt: new Date().toISOString(),
      helpful: 12,
    },
    {
      id: '2',
      userId: '2',
      userName: 'Jane Smith',
      userAvatar: '/avatars/jane.jpg',
      rating: 4,
      comment: 'Good quality, minor improvements could be made to responsiveness.',
      createdAt: new Date().toISOString(),
      helpful: 8,
    },
  ]);
  const [newReview, setNewReview] = useState({ rating: 5, comment: '' });

  useEffect(() => {
    if (template) {
      // Reviews are already loaded in initial state
    }
  }, [template]);

  if (!isOpen || !template) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">{template.name}</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-lg">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
            {/* Gallery */}
            <div>
              <div className="aspect-video bg-gray-700 rounded-xl overflow-hidden mb-4">
                <img
                  src={template.previewImages[activeImage] || template.thumbnailUrl}
                  alt={`Preview ${activeImage + 1}`}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex gap-2 overflow-x-auto pb-2">
                {(template.previewImages.length > 0 ? template.previewImages : [template.thumbnailUrl]).map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveImage(idx)}
                    className={`flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 ${
                      activeImage === idx ? 'border-blue-500' : 'border-transparent'
                    }`}
                  >
                    <img src={img} alt="" className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            </div>

            {/* Details */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <img
                  src={template.creator.avatar}
                  alt={template.creator.name}
                  className="w-12 h-12 rounded-full"
                />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-white">{template.creator.name}</span>
                    {template.creator.verified && (
                      <span className="px-2 py-0.5 bg-blue-600 text-xs rounded text-white">
                        Verified
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-400">Template Creator</div>
                </div>
              </div>

              <p className="text-gray-300 mb-4">{template.description}</p>

              <div className="flex flex-wrap gap-2 mb-4">
                {template.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-gray-800 text-gray-400 rounded text-sm"
                  >
                    #{tag}
                  </span>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gray-800 rounded-xl">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-yellow-400 mb-1">
                    <Star className="w-5 h-5 fill-yellow-400" />
                    <span className="text-lg font-semibold">{template.rating.toFixed(1)}</span>
                  </div>
                  <div className="text-xs text-gray-400">{template.reviewCount} reviews</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-white mb-1">
                    {template.downloadCount}
                  </div>
                  <div className="text-xs text-gray-400">Downloads</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-white mb-1">
                    {template.isFree ? 'Free' : `$${template.price}`}
                  </div>
                  <div className="text-xs text-gray-400">Price</div>
                </div>
              </div>

              <button
                onClick={onPurchase}
                disabled={template.isPurchased}
                className={`w-full py-3 rounded-xl font-semibold text-lg transition-colors ${
                  template.isPurchased
                    ? 'bg-gray-700 text-gray-400'
                    : template.isFree
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {template.isPurchased
                  ? '✓ Already in your library'
                  : template.isFree
                  ? 'Get Template Free'
                  : `Purchase for $${template.price}`}
              </button>
            </div>
          </div>

          {/* Reviews Section */}
          <div className="p-6 border-t border-gray-700">
            <h3 className="font-semibold text-lg text-white mb-4">Reviews</h3>
            <div className="space-y-4">
              {reviews.map((review) => (
                <div key={review.id} className="p-4 bg-gray-800 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <img
                        src={review.userAvatar}
                        alt={review.userName}
                        className="w-8 h-8 rounded-full"
                      />
                      <div>
                        <div className="font-medium text-white">{review.userName}</div>
                        <div className="flex items-center gap-1">
                          {Array.from({ length: 5 }).map((_, i) => (
                            <Star
                              key={i}
                              className={`w-3 h-3 ${
                                i < review.rating
                                  ? 'text-yellow-400 fill-yellow-400'
                                  : 'text-gray-600'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-gray-400">
                      {new Date(review.createdAt).toLocaleDateString()}
                    </div>
                  </div>
                  <p className="text-gray-300">{review.comment}</p>
                  <div className="mt-2 text-sm text-gray-400">
                    {review.helpful} people found this helpful
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Category Filter Component
export function CategoryFilter({
  categories,
  selectedCategory,
  onSelect,
}: {
  categories: Category[];
  selectedCategory: string | null;
  onSelect: (category: string | null) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onSelect(null)}
        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
          selectedCategory === null
            ? 'bg-blue-600 text-white'
            : 'bg-gray-800 text-gray-400 hover:text-white'
        }`}
      >
        All
      </button>
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onSelect(cat.slug)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors flex items-center gap-2 ${
            selectedCategory === cat.slug
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:text-white'
          }`}
        >
          <span>{cat.icon}</span>
          {cat.name}
          <span className="text-xs opacity-70">({cat.templateCount})</span>
        </button>
      ))}
    </div>
  );
}

// Main Marketplace Component
export function TemplateMarketplace() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'popular' | 'newest' | 'price-low' | 'price-high' | 'rating'>('popular');
  const [priceFilter, setPriceFilter] = useState<'all' | 'free' | 'paid'>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadTemplates();
    loadCategories();
  }, [selectedCategory, sortBy, priceFilter]);

  const loadTemplates = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedCategory) params.set('category', selectedCategory);
      params.set('ordering', sortBy === 'popular' ? '-download_count' : sortBy === 'newest' ? '-created_at' : sortBy === 'rating' ? '-rating' : sortBy === 'price-low' ? 'price' : '-price');
      if (priceFilter === 'free') params.set('is_free', 'true');
      if (priceFilter === 'paid') params.set('is_free', 'false');

      const response = await fetch(`/api/v1/marketplace/templates/?${params}`);
      const data = await response.json();
      setTemplates(data.results || data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await fetch('/api/v1/marketplace/categories/');
      const data = await response.json();
      setCategories(data.results || data);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const toggleFavorite = async (templateId: string) => {
    setTemplates(prev =>
      prev.map(t =>
        t.id === templateId ? { ...t, isFavorite: !t.isFavorite } : t
      )
    );

    try {
      await fetch(`/api/v1/marketplace/templates/${templateId}/favorite/`, {
        method: 'POST',
      });
    } catch (error) {
      console.error('Failed to toggle favorite', error);
    }
  };

  const purchaseTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`/api/v1/marketplace/templates/${templateId}/purchase/`, {
        method: 'POST',
      });
      const data = await response.json();
      
      setTemplates(prev =>
        prev.map(t =>
          t.id === templateId ? { ...t, isPurchased: true } : t
        )
      );
      
      if (selectedTemplate?.id === templateId) {
        setSelectedTemplate({ ...selectedTemplate, isPurchased: true });
      }
    } catch (error) {
      console.error('Failed to purchase', error);
    }
  };

  const filteredTemplates = templates.filter(t =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-linear-to-r from-blue-600 to-purple-600 py-16 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-4xl font-bold mb-4">Template Marketplace</h1>
          <p className="text-lg text-white/80 mb-8">
            Discover thousands of professional templates created by designers worldwide
          </p>
          
          <div className="max-w-2xl mx-auto relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search templates..."
              className="w-full pl-12 pr-4 py-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl text-white placeholder-white/50"
            />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="max-w-6xl mx-auto px-6 py-6 space-y-4">
        <CategoryFilter
          categories={categories}
          selectedCategory={selectedCategory}
          onSelect={setSelectedCategory}
        />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <select
              value={priceFilter}
              onChange={(e) => setPriceFilter(e.target.value as 'all' | 'free' | 'paid')}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
            >
              <option value="all">All Prices</option>
              <option value="free">Free Only</option>
              <option value="paid">Paid Only</option>
            </select>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'popular' | 'newest' | 'rating' | 'price-low' | 'price-high')}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
            >
              <option value="popular">Most Popular</option>
              <option value="newest">Newest</option>
              <option value="rating">Top Rated</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-gray-800' : ''}`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-gray-800' : ''}`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="max-w-6xl mx-auto px-6 pb-12">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onView={() => setSelectedTemplate(template)}
                onFavorite={() => toggleFavorite(template.id)}
                onPurchase={() => purchaseTemplate(template.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Template Detail Modal */}
      <TemplateDetailModal
        template={selectedTemplate}
        isOpen={!!selectedTemplate}
        onClose={() => setSelectedTemplate(null)}
        onPurchase={() => selectedTemplate && purchaseTemplate(selectedTemplate.id)}
      />
    </div>
  );
}

export default TemplateMarketplace;
