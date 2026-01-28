/**
 * Stock Assets Browser Component
 * Search and import assets from Unsplash, Pexels, and other providers
 */
'use client';

import React, { useState, useCallback, useEffect } from 'react';
import Image from 'next/image';
import { Search, Download, Heart, ExternalLink, Loader2 } from 'lucide-react';
import { useDebounce } from '@/hooks/useDebounce';

interface StockAsset {
  id: string;
  provider: string;
  title: string;
  description?: string;
  previewUrl: string;
  downloadUrl: string;
  author: {
    name: string;
    profileUrl: string;
  };
  dimensions: {
    width: number;
    height: number;
  };
  tags?: string[];
}

interface StockAssetBrowserProps {
  onSelectAsset: (asset: StockAsset) => void;
  assetType?: 'image' | 'video' | 'all';
}

const PROVIDERS = [
  { id: 'all', name: 'All Sources', icon: '🌐' },
  { id: 'unsplash', name: 'Unsplash', icon: '📷' },
  { id: 'pexels', name: 'Pexels', icon: '🎬' },
];

export const StockAssetBrowser: React.FC<StockAssetBrowserProps> = ({
  onSelectAsset,
  assetType = 'all',
}) => {
  const [query, setQuery] = useState('');
  const [provider, setProvider] = useState('all');
  const [assets, setAssets] = useState<StockAsset[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

  const debouncedQuery = useDebounce(query, 500);

  const searchAssets = useCallback(async (searchQuery: string, pageNum: number = 1, append: boolean = false) => {
    if (!searchQuery.trim()) {
      setAssets([]);
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams({
        query: searchQuery,
        provider: provider,
        page: pageNum.toString(),
        per_page: '20',
        ...(assetType !== 'all' && { type: assetType }),
      });

      const response = await fetch(`/api/v1/integrations/stock-assets/search/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        const newAssets = data.results || [];
        
        if (append) {
          setAssets(prev => [...prev, ...newAssets]);
        } else {
          setAssets(newAssets);
        }
        
        setHasMore(newAssets.length === 20);
      }
    } catch (err) {
      console.error('Failed to search assets:', err);
    } finally {
      setLoading(false);
    }
  }, [provider, assetType]);

  useEffect(() => {
    setPage(1);
    searchAssets(debouncedQuery);
  }, [debouncedQuery, provider, searchAssets]);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    searchAssets(debouncedQuery, nextPage, true);
  };

  const toggleFavorite = (assetId: string) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(assetId)) {
        newFavorites.delete(assetId);
      } else {
        newFavorites.add(assetId);
      }
      return newFavorites;
    });
  };

  const handleDownload = async (asset: StockAsset) => {
    try {
      // Track download and get actual download URL
      const response = await fetch('/api/v1/integrations/stock-assets/download/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          asset_id: asset.id,
          provider: asset.provider,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        onSelectAsset({ ...asset, downloadUrl: data.download_url });
      }
    } catch (err) {
      console.error('Failed to download asset:', err);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Stock Assets
        </h3>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for images, photos, illustrations..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        {/* Provider Tabs */}
        <div className="flex gap-2">
          {PROVIDERS.map((p) => (
            <button
              key={p.id}
              onClick={() => setProvider(p.id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                provider === p.id
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
              }`}
            >
              <span>{p.icon}</span>
              <span>{p.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Results Grid */}
      <div className="p-4">
        {loading && assets.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : assets.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            {query ? 'No results found' : 'Start searching to find assets'}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {assets.map((asset) => (
                <div
                  key={asset.id}
                  className="group relative rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 aspect-square"
                >
                  <Image
                    src={asset.previewUrl}
                    alt={asset.title}
                    fill
                    className="object-cover"
                    loading="lazy"
                  />

                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-3">
                    {/* Top Actions */}
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => toggleFavorite(asset.id)}
                        className={`p-2 rounded-full ${
                          favorites.has(asset.id)
                            ? 'bg-red-500 text-white'
                            : 'bg-white/20 text-white hover:bg-white/30'
                        }`}
                      >
                        <Heart
                          className={`w-4 h-4 ${
                            favorites.has(asset.id) ? 'fill-current' : ''
                          }`}
                        />
                      </button>
                      <a
                        href={asset.author.profileUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 rounded-full bg-white/20 text-white hover:bg-white/30"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>

                    {/* Bottom Info & Actions */}
                    <div>
                      <p className="text-white text-sm truncate mb-2">
                        by {asset.author.name}
                      </p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleDownload(asset)}
                          className="flex-1 flex items-center justify-center gap-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                        >
                          <Download className="w-4 h-4" />
                          Use
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Provider Badge */}
                  <div className="absolute top-2 left-2 px-2 py-1 bg-black/50 rounded text-white text-xs">
                    {asset.provider}
                  </div>
                </div>
              ))}
            </div>

            {/* Load More */}
            {hasMore && (
              <div className="mt-6 text-center">
                <button
                  onClick={loadMore}
                  disabled={loading}
                  className="px-6 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium disabled:opacity-50"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin mx-auto" />
                  ) : (
                    'Load More'
                  )}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default StockAssetBrowser;
