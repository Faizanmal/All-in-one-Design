'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Search, Star, Heart, Download,
  Grid, List, Eye, X, Check,
  Sparkles, Zap, TrendingUp,
} from 'lucide-react';
import Image from 'next/image';

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

// Toast Component with progress bar
function ToastContainer({ toasts, removeToast }: { toasts: { id: string, message: string, type: 'success' | 'info' }[], removeToast: (id: string) => void }) {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="pointer-events-auto animate-in slide-in-from-right-8 fade-in duration-300 relative overflow-hidden flex items-center gap-3 px-5 py-3.5 bg-[#13141c]/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl"
        >
          {toast.type === 'success' ? (
            <div className="w-8 h-8 rounded-full bg-emerald-500/15 flex items-center justify-center shrink-0">
              <Check className="w-4 h-4 text-emerald-400" />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-rose-500/15 flex items-center justify-center shrink-0">
              <Heart className="w-4 h-4 text-rose-400" />
            </div>
          )}
          <span className="text-sm font-medium text-white">{toast.message}</span>
          <button onClick={() => removeToast(toast.id)} className="ml-3 text-gray-500 hover:text-white transition-colors shrink-0">
            <X className="w-4 h-4" />
          </button>
          {/* Auto-dismiss progress bar */}
          <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-white/5">
            <div
              className={`h-full ${toast.type === 'success' ? 'bg-emerald-500/60' : 'bg-rose-500/60'}`}
              style={{ animation: 'toast-progress 4s linear forwards' }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// Skeleton Component with shimmer
function TemplateSkeleton() {
  return (
    <div className="bg-[#12131a] rounded-2xl overflow-hidden border border-white/[0.05] flex flex-col h-full relative">
      {/* Shimmer overlay */}
      <div className="absolute inset-0 animate-shimmer z-10 pointer-events-none" />
      <div className="aspect-[4/3] bg-gray-800/30 shrink-0" />
      <div className="p-5 flex flex-col flex-1">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gray-800/30" />
            <div className="h-4 w-24 bg-gray-800/30 rounded-md" />
          </div>
          <div className="h-4 w-10 bg-gray-800/30 rounded-md" />
        </div>
        <div className="h-5 w-4/5 bg-gray-800/30 rounded-md mb-2" />
        <div className="h-5 w-2/3 bg-gray-800/30 rounded-md mb-6" />
        <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
          <div className="h-4 w-16 bg-gray-800/30 rounded-md" />
          <div className="h-6 w-16 bg-gray-800/30 rounded-md" />
        </div>
      </div>
    </div>
  );
}

// Template Card Component with cursor-tracking glow
export function TemplateCard({
  template,
  onView,
  onFavorite,
  onPurchase,
  index = 0,
}: {
  template: Template;
  onView: () => void;
  onFavorite: () => void;
  onPurchase: () => void;
  index?: number;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const glowRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current || !glowRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    glowRef.current.style.opacity = '1';
    glowRef.current.style.transform = `translate(${x - 150}px, ${y - 150}px)`;
  };

  const handleMouseLeave = () => {
    if (!glowRef.current) return;
    glowRef.current.style.opacity = '0';
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="group relative bg-[#12131a] rounded-2xl overflow-hidden transition-all duration-500 hover:shadow-[0_0_40px_-10px_rgba(99,102,241,0.2)] hover:-translate-y-2 border border-white/[0.05] hover:border-indigo-500/30 flex flex-col h-full animate-in fade-in slide-in-from-bottom-8 fill-mode-both"
      style={{ animationDelay: `${index * 75}ms`, animationDuration: '500ms' }}
    >
      {/* Cursor-tracking glow */}
      <div
        ref={glowRef}
        className="absolute w-[300px] h-[300px] rounded-full pointer-events-none z-[1] transition-opacity duration-400"
        style={{
          background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.06) 40%, transparent 70%)',
          opacity: 0,
        }}
      />
      {/* Thumbnail */}
      <div className="aspect-[4/3] bg-gray-900 relative overflow-hidden shrink-0 cursor-pointer" onClick={onView}>
        <Image
          src={template.thumbnailUrl || '/placeholder.png'}
          alt={template.name}
          width={400}
          height={300}
          className="w-full h-full object-cover transform scale-100 group-hover:scale-110 transition-transform duration-700 ease-out"
        />
        
        {/* Glass Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
        
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 scale-95 group-hover:scale-100 pointer-events-none">
          <div className="flex items-center gap-2 px-6 py-3 bg-white/10 backdrop-blur-md rounded-full text-white font-medium border border-white/20 shadow-xl">
            <Eye className="w-5 h-5" />
            <span>Preview</span>
          </div>
        </div>

        {/* Top Badges */}
        <div className="absolute top-4 left-4 flex gap-2">
          {template.isFree ? (
            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 text-xs rounded-full font-bold tracking-wide backdrop-blur-md">
              FREE
            </span>
          ) : (
            <span className="px-3 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/20 text-xs rounded-full font-bold tracking-wide backdrop-blur-md">
              PRO
            </span>
          )}
        </div>

        {/* Favorite */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onFavorite();
          }}
          className="absolute top-4 right-4 p-2.5 bg-black/40 hover:bg-black/60 backdrop-blur-md rounded-full transition-all duration-300 hover:scale-110 border border-white/10 shadow-lg z-10"
        >
          <Heart
            className={`w-4 h-4 transition-colors ${
              template.isFavorite ? 'text-rose-500 fill-rose-500' : 'text-white'
            }`}
          />
        </button>
      </div>

      {/* Content */}
      <div className="p-5 flex flex-col flex-1">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full overflow-hidden border border-white/10 relative bg-gray-800">
              <Image
                src={template.creator.avatar || '/default-avatar.png'}
                alt={template.creator.name}
                fill
                className="object-cover"
              />
            </div>
            <span className="text-sm font-medium text-gray-400 hover:text-indigo-400 transition-colors cursor-pointer line-clamp-1">
              {template.creator.name}
            </span>
            {template.creator.verified && (
              <Check className="w-3.5 h-3.5 text-indigo-400 bg-indigo-400/10 rounded-full p-0.5 shrink-0" />
            )}
          </div>
          <div className="flex items-center gap-1.5 text-sm font-medium shrink-0">
            <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
            <span className="text-white">{template.rating.toFixed(1)}</span>
          </div>
        </div>

        <h3 
          className="font-semibold text-lg text-white mb-4 line-clamp-2 group-hover:text-indigo-300 transition-colors cursor-pointer"
          onClick={onView}
        >
          {template.name}
        </h3>

        <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
          <div className="flex items-center gap-2 text-sm text-gray-500 font-medium">
            <Download className="w-4 h-4" />
            <span>{template.downloadCount.toLocaleString()}</span>
          </div>
          
          <div className="font-bold text-lg">
            {template.isFree ? (
              <span className="text-emerald-400">Free</span>
            ) : (
              <span className="text-white">${template.price}</span>
            )}
          </div>
        </div>
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
  const [reviews] = useState<Review[]>([
    {
      id: '1',
      userId: '1',
      userName: 'John Doe',
      userAvatar: '/default-avatar.png',
      rating: 5,
      comment: 'Absolutely stunning! Saved me 10 hours of design work. The layer organization is phenomenal.',
      createdAt: new Date().toISOString(),
      helpful: 12,
    },
    {
      id: '2',
      userId: '2',
      userName: 'Jane Smith',
      userAvatar: '/default-avatar.png',
      rating: 4,
      comment: 'Very clean and modern aesthetics. Easily adaptable for my SaaS client.',
      createdAt: new Date().toISOString(),
      helpful: 8,
    },
  ]);

  useEffect(() => {
    if (template) {
      setActiveImage(0);
    }
  }, [template]);

  if (!isOpen || !template) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-xl flex items-center justify-center z-50 p-4 sm:p-6 overflow-y-auto">
      <div 
        className="fixed inset-0"
        onClick={onClose}
      />
      <div className="relative bg-[#0f1016] border border-white/10 rounded-3xl w-full max-w-5xl my-auto flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-300">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 sm:p-6 border-b border-white/5 bg-[#0a0b10]/50 shrink-0 rounded-t-3xl">
          <div className="flex items-center gap-3">
            <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">{template.name}</h2>
            {template.isFree && (
              <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 text-xs rounded-full font-bold">FREE</span>
            )}
          </div>
          <button 
            onClick={onClose} 
            className="p-2 bg-white/5 hover:bg-white/10 rounded-full transition-colors group"
          >
            <X className="w-5 h-5 text-gray-400 group-hover:text-white" />
          </button>
        </div>

        <div className="overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent max-h-[80vh]">
          <div className="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-8 p-6 sm:p-8">
            
            {/* Left Col: Visuals */}
            <div className="space-y-6">
              <div className="aspect-[16/10] bg-gray-900 rounded-2xl overflow-hidden border border-white/5 relative group shadow-lg">
                <Image
                  src={template.previewImages[activeImage] || template.thumbnailUrl}
                  alt={`Preview ${activeImage + 1}`}
                  fill
                  className="object-cover"
                />
              </div>
              
              <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                {(template.previewImages.length > 0 ? template.previewImages : [template.thumbnailUrl]).map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveImage(idx)}
                    className={`shrink-0 w-20 h-14 sm:w-24 sm:h-16 rounded-xl overflow-hidden border-2 transition-all duration-300 relative bg-gray-900 ${
                      activeImage === idx 
                        ? 'border-indigo-500 opacity-100 shadow-[0_0_15px_-3px_rgba(99,102,241,0.5)]' 
                        : 'border-transparent opacity-50 hover:opacity-100'
                    }`}
                  >
                    <Image src={img} alt="" fill className="object-cover" />
                  </button>
                ))}
              </div>
            </div>

            {/* Right Col: Details */}
            <div className="flex flex-col">
              <div className="flex items-center gap-4 mb-6 p-4 bg-white/[0.02] border border-white/5 rounded-2xl">
                <div className="relative w-14 h-14 rounded-full border-2 border-indigo-500/30 overflow-hidden bg-gray-800">
                  <Image
                    src={template.creator.avatar}
                    alt={template.creator.name}
                    fill
                    className="object-cover"
                  />
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-0.5">Designed by</div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white text-lg">{template.creator.name}</span>
                    {template.creator.verified && (
                      <Check className="w-4 h-4 text-indigo-400 bg-indigo-400/10 rounded-full p-0.5" />
                    )}
                  </div>
                </div>
              </div>

              <div className="prose prose-invert mb-8">
                <p className="text-gray-300 text-base leading-relaxed">{template.description}</p>
              </div>

              <div className="flex flex-wrap gap-2 mb-8">
                {template.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1.5 bg-indigo-500/10 text-indigo-300 border border-indigo-500/10 rounded-lg text-sm font-medium"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="flex flex-col items-center justify-center p-4 bg-white/[0.02] border border-white/5 rounded-2xl">
                  <div className="flex items-center gap-1.5 text-amber-400 mb-1">
                    <Star className="w-5 h-5 fill-amber-400" />
                    <span className="text-xl font-bold">{template.rating.toFixed(1)}</span>
                  </div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">{template.reviewCount} Reviews</span>
                </div>
                <div className="flex flex-col items-center justify-center p-4 bg-white/[0.02] border border-white/5 rounded-2xl">
                  <div className="flex items-center gap-1.5 text-blue-400 mb-1">
                    <Download className="w-5 h-5" />
                    <span className="text-xl font-bold">{template.downloadCount}</span>
                  </div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Downloads</span>
                </div>
                <div className="flex flex-col items-center justify-center p-4 bg-white/[0.02] border border-white/5 rounded-2xl">
                  <div className="text-xl font-bold text-white mb-1">
                    {template.isFree ? 'Free' : `$${template.price}`}
                  </div>
                  <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">License</span>
                </div>
              </div>

              <div className="mt-auto space-y-3">
                <button
                  onClick={onPurchase}
                  disabled={template.isPurchased}
                  className={`w-full py-4 rounded-2xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-2 ${
                    template.isPurchased
                      ? 'bg-white/5 text-gray-400 cursor-not-allowed border border-white/5'
                      : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-[0_0_30px_-10px_rgba(99,102,241,0.5)] hover:shadow-[0_0_40px_-5px_rgba(99,102,241,0.6)] hover:-translate-y-0.5'
                  }`}
                >
                  {template.isPurchased ? (
                    <>
                      <Check className="w-5 h-5" />
                      In Your Library
                    </>
                  ) : template.isFree ? (
                    <>
                      <Download className="w-5 h-5" />
                      Download Free
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5" />
                      Get for ${template.price}
                    </>
                  )}
                </button>
                {!template.isPurchased && !template.isFree && (
                  <p className="text-center text-xs text-gray-500">
                    Includes lifetime updates and commercial license
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Reviews Section */}
          <div className="px-6 sm:px-8 pb-8">
            <div className="h-px w-full bg-white/5 mb-8" />
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-bold text-xl text-white">User Reviews</h3>
              <button className="text-indigo-400 text-sm font-medium hover:text-indigo-300 transition-colors">
                See all {template.reviewCount} reviews
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              {reviews.map((review) => (
                <div key={review.id} className="p-5 bg-white/[0.02] border border-white/5 rounded-2xl hover:bg-white/[0.04] transition-colors">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="relative w-10 h-10 rounded-full bg-gray-800 overflow-hidden">
                        <Image
                          src={review.userAvatar}
                          alt={review.userName}
                          fill
                          className="object-cover"
                        />
                      </div>
                      <div>
                        <div className="font-semibold text-white">{review.userName}</div>
                        <div className="flex items-center gap-0.5">
                          {Array.from({ length: 5 }).map((_, i) => (
                            <Star
                              key={i}
                              className={`w-3.5 h-3.5 ${
                                i < review.rating
                                  ? 'text-amber-400 fill-amber-400'
                                  : 'text-gray-700'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500 font-medium">
                      {new Date(review.createdAt).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}
                    </div>
                  </div>
                  <p className="text-gray-300 text-sm leading-relaxed">{review.comment}</p>
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
    <div className="flex gap-2 overflow-x-auto pb-4 sm:pb-0 scrollbar-hide -mx-6 px-6 md:mx-0 md:px-0">
      <button
        onClick={() => onSelect(null)}
        className={`shrink-0 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 border ${
          selectedCategory === null
            ? 'bg-indigo-600 border-indigo-500 text-white shadow-[0_0_20px_-5px_rgba(99,102,241,0.4)]'
            : 'bg-[#13141c] border-white/10 text-gray-400 hover:text-white hover:border-white/20'
        }`}
      >
        All Magic
      </button>
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onSelect(cat.slug)}
          className={`shrink-0 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 border flex items-center gap-2.5 ${
            selectedCategory === cat.slug
              ? 'bg-indigo-600 border-indigo-500 text-white shadow-[0_0_20px_-5px_rgba(99,102,241,0.4)]'
              : 'bg-[#13141c] border-white/10 text-gray-400 hover:text-white hover:border-white/20'
          }`}
        >
          <span className="text-base">{cat.icon}</span>
          {cat.name}
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
  const [toasts, setToasts] = useState<{ id: string; message: string; type: 'success' | 'info' }[]>([]);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const addToast = (message: string, type: 'success' | 'info' = 'success') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const loadTemplates = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedCategory) params.set('category', selectedCategory);
      params.set('ordering', sortBy === 'popular' ? '-download_count' : sortBy === 'newest' ? '-created_at' : sortBy === 'rating' ? '-rating' : sortBy === 'price-low' ? 'price' : '-price');
      if (priceFilter === 'free') params.set('is_free', 'true');
      if (priceFilter === 'paid') params.set('is_free', 'false');

      const response = await fetch(`/api/v1/marketplace/templates/?${params}`);
      const data = await response.json();
      setTemplates(data.results || data || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
      // Dummy data fallback for visual testing
      setTemplates([
        {
          id: '1', name: 'Dark SaaS Dashboard', description: 'Premium Next.js admin dashboard',
          thumbnailUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800', previewImages: [],
          category: 'dashboard', tags: ['saas', 'admin', 'react'], price: 49, isFree: false,
          creator: { id: 'c1', name: 'Design Studio X', avatar: '/default-avatar.png', verified: true },
          rating: 4.9, reviewCount: 128, downloadCount: 1400, isFavorite: false, isPurchased: false,
          createdAt: new Date().toISOString(), updatedAt: new Date().toISOString()
        },
        {
          id: '2', name: 'Creative Portfolio Pro', description: 'Showcase your work beautifully',
          thumbnailUrl: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=800', previewImages: [],
          category: 'portfolio', tags: ['creative', 'minimal', 'agency'], price: 0, isFree: true,
          creator: { id: 'c2', name: 'Alex UI', avatar: '/default-avatar.png', verified: true },
          rating: 4.8, reviewCount: 85, downloadCount: 3200, isFavorite: true, isPurchased: false,
          createdAt: new Date().toISOString(), updatedAt: new Date().toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory, sortBy, priceFilter]);

  const loadCategories = async () => {
    try {
      const response = await fetch('/api/v1/marketplace/categories/');
      const data = await response.json();
      setCategories(data.results || data || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
      // Dummy data fallback
      setCategories([
        { id: '1', name: 'Dashboards', slug: 'dashboard', icon: '📊', templateCount: 124 },
        { id: '2', name: 'Landing Pages', slug: 'landing', icon: '🚀', templateCount: 342 },
        { id: '3', name: 'E-commerce', slug: 'ecommerce', icon: '🛍️', templateCount: 89 },
        { id: '4', name: 'Portfolios', slug: 'portfolio', icon: '✨', templateCount: 215 },
      ]);
    }
  };

  useEffect(() => {
    loadTemplates();
    loadCategories();
  }, [selectedCategory, sortBy, priceFilter, loadTemplates]);

  const toggleFavorite = async (templateId: string) => {
    setTemplates(prev => {
      const isFav = prev.find(t => t.id === templateId)?.isFavorite;
      if (isFav) {
        addToast('Removed from Favorites', 'info');
      } else {
        addToast('Added to Favorites', 'success');
      }
      return prev.map(t =>
        t.id === templateId ? { ...t, isFavorite: !t.isFavorite } : t
      );
    });
    try {
      await fetch(`/api/v1/marketplace/templates/${templateId}/favorite/`, { method: 'POST' });
    } catch (error) {
      console.error('Failed to toggle favorite', error);
    }
  };

  const purchaseTemplate = async (templateId: string) => {
    try {
      await fetch(`/api/v1/marketplace/templates/${templateId}/purchase/`, { method: 'POST' });
      setTemplates(prev =>
        prev.map(t =>
          t.id === templateId ? { ...t, isPurchased: true } : t
        )
      );
      if (selectedTemplate?.id === templateId) {
        setSelectedTemplate({ ...selectedTemplate, isPurchased: true });
      }
      addToast('Template unlocked successfully!', 'success');
    } catch (error) {
      console.error('Failed to purchase', error);
    }
  };

  const filteredTemplates = templates.filter(t =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white selection:bg-indigo-500/30 font-sans pb-10">
      {/* Premium Hero Section */}
      <div className="relative py-24 px-6 overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-[#0a0a0f]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/40 via-[#0a0a0f] to-[#0a0a0f]" />
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/20 blur-[120px]" />
        <div className="absolute top-[20%] right-[-5%] w-[30%] h-[30%] rounded-full bg-blue-600/20 blur-[100px]" />
        
        <div className="relative max-w-6xl mx-auto text-center z-10">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.08] mb-8 backdrop-blur-md">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span className="text-sm font-medium text-indigo-200">The Ultimate Design Library</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
            Elevate Your <br className="md:hidden" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              Creative Vision
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-400 mb-10 max-w-2xl mx-auto font-light leading-relaxed">
            Discover thousands of world-class, ready-to-use templates crafted by top-tier designers to accelerate your workflow.
          </p>
          
          <div className="max-w-2xl mx-auto relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-500"></div>
            <div className="relative flex items-center bg-[#13141c] border border-white/10 rounded-2xl overflow-hidden backdrop-blur-xl">
              <Search className="absolute left-5 w-6 h-6 text-gray-500 group-focus-within:text-indigo-400 transition-colors" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search templates, categories, or creators..."
                className="w-full pl-14 pr-24 py-5 bg-transparent text-white placeholder-gray-500 focus:outline-none text-lg"
              />
              <div className="absolute right-28 hidden sm:flex items-center gap-1 px-2 py-1 bg-white/5 border border-white/10 rounded-md pointer-events-none">
                <span className="text-xs text-gray-400 font-medium">⌘</span>
                <span className="text-xs text-gray-400 font-medium">K</span>
              </div>
              <button className="absolute right-3 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition-colors">
                Search
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Filters & Controls */}
      <div className="sticky top-0 z-40 bg-[#0a0a0f]/80 backdrop-blur-xl border-y border-white/[0.05] py-4 mb-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row gap-4 items-center justify-between">
          <CategoryFilter
            categories={categories}
            selectedCategory={selectedCategory}
            onSelect={setSelectedCategory}
          />

          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="relative">
              <select
                value={priceFilter}
                onChange={(e) => setPriceFilter(e.target.value as 'all' | 'free' | 'paid')}
                className="appearance-none bg-[#13141c] border border-white/10 text-gray-300 text-sm rounded-xl px-4 py-2.5 pr-10 hover:border-indigo-500/50 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all cursor-pointer"
              >
                <option value="all">All Prices</option>
                <option value="free">Free Templates</option>
                <option value="paid">Premium</option>
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
              </div>
            </div>
            
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'popular' | 'newest' | 'rating' | 'price-low' | 'price-high')}
                className="appearance-none bg-[#13141c] border border-white/10 text-gray-300 text-sm rounded-xl px-4 py-2.5 pr-10 hover:border-indigo-500/50 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all cursor-pointer"
              >
                <option value="popular">Trending</option>
                <option value="newest">Latest Release</option>
                <option value="rating">Top Rated</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
              </div>
            </div>

            <div className="hidden sm:flex items-center p-1 bg-[#13141c] border border-white/10 rounded-xl">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-indigo-500/20 text-indigo-400' : 'text-gray-500 hover:text-white'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-indigo-500/20 text-indigo-400' : 'text-gray-500 hover:text-white'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="max-w-6xl mx-auto px-6 pb-20">
        {isLoading ? (
          <div className={`grid gap-6 ${viewMode === 'grid' ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' : 'grid-cols-1'}`}>
            {Array.from({ length: 8 }).map((_, i) => (
              <TemplateSkeleton key={i} />
            ))}
          </div>
        ) : filteredTemplates.length > 0 ? (
          <div className={`grid gap-6 ${viewMode === 'grid' ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' : 'grid-cols-1'}`}>
            {filteredTemplates.map((template, index) => (
              <TemplateCard
                key={template.id}
                template={template}
                index={index}
                onView={() => setSelectedTemplate(template)}
                onFavorite={() => toggleFavorite(template.id)}
                onPurchase={() => purchaseTemplate(template.id)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-24 bg-white/[0.02] border border-white/5 rounded-3xl max-w-2xl mx-auto">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/5 mb-4 border border-white/10">
              <Search className="w-8 h-8 text-gray-500" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">No templates found</h3>
            <p className="text-gray-400 max-w-md mx-auto">
              We couldn't find any templates matching your current filters. Try adjusting your search or category selection.
            </p>
            <button 
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory(null);
                setPriceFilter('all');
              }}
              className="mt-6 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition-colors"
            >
              Clear Filters
            </button>
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

      <ToastContainer toasts={toasts} removeToast={(id) => setToasts(prev => prev.filter(t => t.id !== id))} />
    </div>
  );
}

export default TemplateMarketplace;
