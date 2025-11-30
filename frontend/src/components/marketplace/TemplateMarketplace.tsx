'use client';

import React, { useState, useEffect, useCallback } from 'react';

interface MarketplaceTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  isFree: boolean;
  thumbnail: string;
  creator: {
    id: string;
    name: string;
    avatar: string;
    verified: boolean;
  };
  stats: {
    downloads: number;
    rating: number;
    reviews: number;
  };
  tags: string[];
  preview_images: string[];
  created_at: string;
  updated_at: string;
}

interface TemplateCategory {
  id: string;
  name: string;
  icon: string;
  count: number;
}

const CATEGORIES: TemplateCategory[] = [
  { id: 'all', name: 'All Templates', icon: '📦', count: 0 },
  { id: 'social-media', name: 'Social Media', icon: '📱', count: 0 },
  { id: 'presentation', name: 'Presentations', icon: '📊', count: 0 },
  { id: 'marketing', name: 'Marketing', icon: '📢', count: 0 },
  { id: 'web-design', name: 'Web Design', icon: '🌐', count: 0 },
  { id: 'print', name: 'Print', icon: '🖨️', count: 0 },
  { id: 'branding', name: 'Branding', icon: '🎨', count: 0 },
  { id: 'infographic', name: 'Infographics', icon: '📈', count: 0 },
];

const SORT_OPTIONS = [
  { value: 'popular', label: 'Most Popular' },
  { value: 'newest', label: 'Newest' },
  { value: 'rating', label: 'Highest Rated' },
  { value: 'price-low', label: 'Price: Low to High' },
  { value: 'price-high', label: 'Price: High to Low' },
];

export function TemplateMarketplace() {
  const [templates, setTemplates] = useState<MarketplaceTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('popular');
  const [priceFilter, setPriceFilter] = useState<'all' | 'free' | 'premium'>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<MarketplaceTemplate | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        category: selectedCategory,
        search: searchQuery,
        sort: sortBy,
        price_filter: priceFilter,
      });

      const response = await fetch(`/api/marketplace/templates/?${params}`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.results || []);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
      // Mock data for demonstration
      setTemplates([
        {
          id: '1',
          name: 'Social Media Pack Pro',
          description: 'Complete social media template pack with 50+ designs for Instagram, Facebook, Twitter, and LinkedIn.',
          category: 'social-media',
          price: 29.99,
          isFree: false,
          thumbnail: '/templates/social-pack.jpg',
          creator: {
            id: 'c1',
            name: 'Design Studio',
            avatar: '/avatars/studio.jpg',
            verified: true,
          },
          stats: { downloads: 15420, rating: 4.8, reviews: 342 },
          tags: ['instagram', 'facebook', 'social media', 'marketing'],
          preview_images: ['/previews/social-1.jpg', '/previews/social-2.jpg'],
          created_at: '2024-01-15',
          updated_at: '2024-02-20',
        },
        {
          id: '2',
          name: 'Minimalist Presentation',
          description: 'Clean and modern presentation template with 40 unique slides.',
          category: 'presentation',
          price: 0,
          isFree: true,
          thumbnail: '/templates/presentation.jpg',
          creator: {
            id: 'c2',
            name: 'Alex Designer',
            avatar: '/avatars/alex.jpg',
            verified: false,
          },
          stats: { downloads: 28500, rating: 4.6, reviews: 567 },
          tags: ['presentation', 'minimalist', 'business', 'pitch deck'],
          preview_images: ['/previews/pres-1.jpg', '/previews/pres-2.jpg'],
          created_at: '2024-02-01',
          updated_at: '2024-02-25',
        },
        {
          id: '3',
          name: 'Brand Identity Kit',
          description: 'Complete branding kit with logo templates, business cards, letterheads, and social media assets.',
          category: 'branding',
          price: 49.99,
          isFree: false,
          thumbnail: '/templates/branding.jpg',
          creator: {
            id: 'c3',
            name: 'Brand Masters',
            avatar: '/avatars/brand.jpg',
            verified: true,
          },
          stats: { downloads: 8750, rating: 4.9, reviews: 198 },
          tags: ['branding', 'logo', 'identity', 'business'],
          preview_images: ['/previews/brand-1.jpg', '/previews/brand-2.jpg'],
          created_at: '2024-01-20',
          updated_at: '2024-02-18',
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, searchQuery, sortBy, priceFilter]);

  useEffect(() => {
    const debounce = setTimeout(fetchTemplates, 300);
    return () => clearTimeout(debounce);
  }, [fetchTemplates]);

  const handleUseTemplate = async (template: MarketplaceTemplate) => {
    try {
      const response = await fetch(`/api/marketplace/templates/${template.id}/use/`, {
        method: 'POST',
      });
      if (response.ok) {
        // Navigate to editor with template loaded
        window.location.href = `/editor?template=${template.id}`;
      }
    } catch (error) {
      console.error('Failed to use template:', error);
    }
  };

  const handlePurchaseTemplate = async (template: MarketplaceTemplate) => {
    try {
      const response = await fetch(`/api/marketplace/templates/${template.id}/purchase/`, {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        // Redirect to Stripe checkout
        window.location.href = data.checkout_url;
      }
    } catch (error) {
      console.error('Failed to purchase template:', error);
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<span key={i} className="text-yellow-400">★</span>);
      } else if (i === fullStars && hasHalfStar) {
        stars.push(<span key={i} className="text-yellow-400">☆</span>);
      } else {
        stars.push(<span key={i} className="text-gray-300">★</span>);
      }
    }
    return stars;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold mb-2">Template Marketplace</h1>
          <p className="text-purple-100 mb-6">
            Discover thousands of professional templates created by our community
          </p>

          {/* Search Bar */}
          <div className="max-w-2xl">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search templates..."
                className="w-full px-4 py-3 pl-12 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-300"
              />
              <svg
                className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-64 flex-shrink-0">
            {/* Categories */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Categories</h3>
              <div className="space-y-1">
                {CATEGORIES.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-left transition-colors ${
                      selectedCategory === category.id
                        ? 'bg-purple-100 text-purple-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <span>{category.icon}</span>
                    <span className="text-sm">{category.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Price Filter */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Price</h3>
              <div className="space-y-2">
                {[
                  { value: 'all', label: 'All' },
                  { value: 'free', label: 'Free' },
                  { value: 'premium', label: 'Premium' },
                ].map((option) => (
                  <label
                    key={option.value}
                    className="flex items-center gap-2 cursor-pointer"
                  >
                    <input
                      type="radio"
                      name="price"
                      value={option.value}
                      checked={priceFilter === option.value}
                      onChange={(e) => setPriceFilter(e.target.value as typeof priceFilter)}
                      className="text-purple-600 focus:ring-purple-500"
                    />
                    <span className="text-sm text-gray-600">{option.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Become a Creator CTA */}
            <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg p-4 text-white">
              <h3 className="font-semibold mb-2">Become a Creator</h3>
              <p className="text-sm text-purple-100 mb-3">
                Earn money by selling your templates on our marketplace.
              </p>
              <a
                href="/marketplace/creator"
                className="inline-block px-4 py-2 bg-white text-purple-600 rounded-md text-sm font-medium hover:bg-purple-50 transition-colors"
              >
                Start Selling
              </a>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Sort and Filter Bar */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                {loading ? 'Loading...' : `${templates.length} templates found`}
              </p>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {SORT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Template Grid */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow-sm overflow-hidden animate-pulse">
                    <div className="aspect-[4/3] bg-gray-200" />
                    <div className="p-4">
                      <div className="h-4 bg-gray-200 rounded mb-2" />
                      <div className="h-3 bg-gray-200 rounded w-2/3" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {templates.map((template) => (
                  <div
                    key={template.id}
                    className="bg-white rounded-lg shadow-sm overflow-hidden group hover:shadow-md transition-shadow"
                  >
                    {/* Thumbnail */}
                    <div className="relative aspect-[4/3] bg-gray-100">
                      <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>

                      {/* Overlay Actions */}
                      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        <button
                          onClick={() => {
                            setSelectedTemplate(template);
                            setShowPreview(true);
                          }}
                          className="px-3 py-2 bg-white text-gray-900 rounded-md text-sm font-medium hover:bg-gray-100"
                        >
                          Preview
                        </button>
                        <button
                          onClick={() => template.isFree ? handleUseTemplate(template) : handlePurchaseTemplate(template)}
                          className="px-3 py-2 bg-purple-600 text-white rounded-md text-sm font-medium hover:bg-purple-700"
                        >
                          {template.isFree ? 'Use' : `$${template.price}`}
                        </button>
                      </div>

                      {/* Free Badge */}
                      {template.isFree && (
                        <div className="absolute top-2 left-2 px-2 py-1 bg-green-500 text-white text-xs font-medium rounded">
                          FREE
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="p-4">
                      <h3 className="font-medium text-gray-900 mb-1 line-clamp-1">
                        {template.name}
                      </h3>
                      <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                        {template.description}
                      </p>

                      {/* Creator */}
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs">
                          {template.creator.name.charAt(0)}
                        </div>
                        <span className="text-sm text-gray-600">{template.creator.name}</span>
                        {template.creator.verified && (
                          <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>

                      {/* Stats */}
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-1">
                          {renderStars(template.stats.rating)}
                          <span className="text-gray-500 ml-1">({template.stats.reviews})</span>
                        </div>
                        <span className="text-gray-500">
                          {formatNumber(template.stats.downloads)} uses
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && selectedTemplate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h2 className="text-xl font-semibold text-gray-900">
                {selectedTemplate.name}
              </h2>
              <button
                onClick={() => setShowPreview(false)}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Preview Images */}
                <div className="space-y-4">
                  <div className="aspect-[4/3] bg-gray-100 rounded-lg flex items-center justify-center">
                    <span className="text-gray-400">Preview Image</span>
                  </div>
                  <div className="flex gap-2">
                    {[1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className="w-20 h-16 bg-gray-100 rounded border-2 border-transparent hover:border-purple-500 cursor-pointer"
                      />
                    ))}
                  </div>
                </div>

                {/* Details */}
                <div>
                  <p className="text-gray-600 mb-4">{selectedTemplate.description}</p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {selectedTemplate.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Creator Info */}
                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg mb-4">
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                      {selectedTemplate.creator.name.charAt(0)}
                    </div>
                    <div>
                      <div className="flex items-center gap-1">
                        <span className="font-medium">{selectedTemplate.creator.name}</span>
                        {selectedTemplate.creator.verified && (
                          <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <a href="#" className="text-sm text-purple-600 hover:underline">
                        View all templates
                      </a>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-xl font-bold text-gray-900">
                        {formatNumber(selectedTemplate.stats.downloads)}
                      </div>
                      <div className="text-sm text-gray-500">Downloads</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-xl font-bold text-gray-900">
                        {selectedTemplate.stats.rating}
                      </div>
                      <div className="text-sm text-gray-500">Rating</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-xl font-bold text-gray-900">
                        {selectedTemplate.stats.reviews}
                      </div>
                      <div className="text-sm text-gray-500">Reviews</div>
                    </div>
                  </div>

                  {/* Price & Action */}
                  <div className="flex items-center gap-4">
                    {selectedTemplate.isFree ? (
                      <span className="text-2xl font-bold text-green-600">Free</span>
                    ) : (
                      <span className="text-2xl font-bold text-gray-900">
                        ${selectedTemplate.price}
                      </span>
                    )}
                    <button
                      onClick={() => {
                        setShowPreview(false);
                        if (selectedTemplate.isFree) {
                          handleUseTemplate(selectedTemplate);
                        } else {
                          handlePurchaseTemplate(selectedTemplate);
                        }
                      }}
                      className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
                    >
                      {selectedTemplate.isFree ? 'Use This Template' : 'Purchase Template'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
