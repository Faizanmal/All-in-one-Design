"use client";

import React, { useState, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Search, Download, ExternalLink, Image, Video, Palette, Loader2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { stockAssetsApi, type StockAsset, type StockSearchParams } from '@/lib/stock-assets-api';
import { toast } from 'sonner';

interface StockAssetBrowserProps {
  onSelectAsset?: (asset: StockAsset & { downloadUrl: string }) => void;
  className?: string;
}

export function StockAssetBrowser({ onSelectAsset, className }: StockAssetBrowserProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const [provider, setProvider] = useState<string>('all');
  const [mediaType, setMediaType] = useState<string>('photo');
  const [orientation, setOrientation] = useState<string>('');
  const [page, setPage] = useState(1);
  const [downloading, setDownloading] = useState<string | null>(null);

  const searchParams: StockSearchParams = {
    q: activeQuery,
    provider: provider as StockSearchParams['provider'],
    type: mediaType as StockSearchParams['type'],
    page,
    per_page: 20,
    ...(orientation && { orientation: orientation as StockSearchParams['orientation'] }),
  };

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['stock-assets', searchParams],
    queryFn: () => stockAssetsApi.search(searchParams),
    enabled: activeQuery.length > 0,
    staleTime: 1000 * 60 * 5,
  });

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    setActiveQuery(searchQuery);
    setPage(1);
  }, [searchQuery]);

  const handleSelectAsset = useCallback(async (asset: StockAsset) => {
    if (downloading) return;
    setDownloading(asset.id);
    try {
      const downloadUrl = await stockAssetsApi.getDownloadUrl(asset.provider, asset.id);
      onSelectAsset?.({ ...asset, downloadUrl });
      toast.success(`Added "${asset.title || 'stock asset'}" to your design`);
    } catch {
      // Fallback to preview URL
      onSelectAsset?.({ ...asset, downloadUrl: asset.download_url });
      toast.success('Asset added to your design');
    } finally {
      setDownloading(null);
    }
  }, [downloading, onSelectAsset]);

  const renderResults = () => {
    if (!activeQuery) {
      return (
        <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
          <Image className="w-12 h-12 mb-4 opacity-50" />
          <p className="text-lg font-medium">Search Stock Assets</p>
          <p className="text-sm mt-1">Search millions of free photos, videos &amp; illustrations</p>
          <div className="flex gap-2 mt-4 flex-wrap justify-center">
            {['Nature', 'Business', 'Technology', 'Food', 'Travel', 'Abstract'].map((tag) => (
              <Badge
                key={tag}
                variant="secondary"
                className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                onClick={() => { setSearchQuery(tag); setActiveQuery(tag); }}
              >
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      );
    }

    if (isLoading) {
      return (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 p-2">
          {Array.from({ length: 9 }).map((_, i) => (
            <Skeleton key={i} className="aspect-[4/3] rounded-lg" />
          ))}
        </div>
      );
    }

    if (!data?.results?.length) {
      return (
        <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
          <Search className="w-10 h-10 mb-3 opacity-50" />
          <p>No results found for &ldquo;{activeQuery}&rdquo;</p>
          <p className="text-sm mt-1">Try different keywords or change the provider</p>
        </div>
      );
    }

    return (
      <>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 p-2">
          {data.results.map((asset) => (
            <Card
              key={`${asset.provider}-${asset.id}`}
              className="group relative overflow-hidden cursor-pointer hover:ring-2 hover:ring-primary transition-all"
              onClick={() => handleSelectAsset(asset)}
            >
              <CardContent className="p-0">
                <div className="relative aspect-[4/3]">
                  <img
                    src={asset.thumbnail || asset.preview}
                    alt={asset.title || 'Stock asset'}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                      {downloading === asset.id ? (
                        <Loader2 className="w-6 h-6 text-white animate-spin" />
                      ) : (
                        <Download className="w-6 h-6 text-white" />
                      )}
                    </div>
                  </div>
                  {/* Provider badge */}
                  <Badge
                    variant="secondary"
                    className="absolute top-2 left-2 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    {asset.provider}
                  </Badge>
                  {/* Type badge */}
                  {asset.type === 'video' && (
                    <Badge className="absolute top-2 right-2 text-xs">
                      <Video className="w-3 h-3 mr-1" />
                      Video
                    </Badge>
                  )}
                </div>
                {/* Info */}
                <div className="p-2">
                  <p className="text-xs text-muted-foreground truncate">
                    by {asset.author || 'Unknown'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {asset.width}×{asset.height}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Pagination */}
        {data.total > 20 && (
          <div className="flex justify-center gap-2 py-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1 || isFetching}
            >
              Previous
            </Button>
            <span className="flex items-center text-sm text-muted-foreground px-3">
              Page {page} of {Math.ceil(data.total / 20)}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={page >= Math.ceil(data.total / 20) || isFetching}
            >
              Next
            </Button>
          </div>
        )}
      </>
    );
  };

  return (
    <div className={className}>
      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-2 p-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search stock photos, videos..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button type="submit" disabled={!searchQuery.trim()}>
          Search
        </Button>
      </form>

      {/* Filters */}
      <div className="flex gap-2 px-3 pb-2">
        <Select value={provider} onValueChange={setProvider}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Provider" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Sources</SelectItem>
            <SelectItem value="unsplash">Unsplash</SelectItem>
            <SelectItem value="pexels">Pexels</SelectItem>
            <SelectItem value="pixabay">Pixabay</SelectItem>
          </SelectContent>
        </Select>

        <Tabs value={mediaType} onValueChange={setMediaType} className="flex-1">
          <TabsList className="h-9">
            <TabsTrigger value="photo" className="text-xs px-3">
              <Image className="w-3 h-3 mr-1" /> Photos
            </TabsTrigger>
            <TabsTrigger value="video" className="text-xs px-3">
              <Video className="w-3 h-3 mr-1" /> Videos
            </TabsTrigger>
            <TabsTrigger value="illustration" className="text-xs px-3">
              <Palette className="w-3 h-3 mr-1" /> Illustrations
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <Select value={orientation} onValueChange={setOrientation}>
          <SelectTrigger className="w-[120px]">
            <SelectValue placeholder="Orientation" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Any</SelectItem>
            <SelectItem value="landscape">Landscape</SelectItem>
            <SelectItem value="portrait">Portrait</SelectItem>
            <SelectItem value="squarish">Square</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Results */}
      <ScrollArea className="h-[500px]">
        {renderResults()}
      </ScrollArea>
    </div>
  );
}
