'use client';

import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import Image from 'next/image';
import apiClient from '@/lib/design-api';
import {
  Search, Grid, List, Upload, CloudUpload, Sparkles,
  Image as ImageIcon, FileVideo, FileAudio, File, Trash2, Download,
  Copy, Tag, Star, StarOff, MoreVertical, Eye,
  FolderOpen, Check, X, HardDrive,
  SortAsc,
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';

// Types
export interface AssetFolder {
  id: string;
  name: string;
  parentId: string | null;
  isSmartFolder: boolean;
  smartCriteria: Record<string, unknown> | null;
  color: string;
  assetCount: number;
}

export interface Asset {
  id: string;
  name: string;
  type: 'image' | 'video' | 'audio' | 'font' | 'document' | 'other';
  url: string;
  thumbnailUrl: string;
  size: number;
  dimensions: { width: number; height: number } | null;
  folderId: string | null;
  tags: string[];
  isFavorite: boolean;
  usageCount: number;
  uploadedAt: string;
  aiAnalysis: {
    dominantColors: string[];
    description: string;
    category: string;
  } | null;
}

// Asset Icon Component
const AssetIcon = ({ type, size = 24 }: { type: Asset['type']; size?: number }) => {
  const iconProps = { size, className: 'text-gray-400' };
  
  switch (type) {
    case 'image':
      return <ImageIcon {...iconProps} className="text-blue-400" />;
    case 'video':
      return <FileVideo {...iconProps} className="text-purple-400" />;
    case 'audio':
      return <FileAudio {...iconProps} className="text-green-400" />;
    default:
      return <File {...iconProps} />;
  }
};

// Smart Folder Setup
export function SmartFolderDialog({
  isOpen,
  onClose,
  onSave,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSave: (folder: Partial<AssetFolder>) => void;
}) {
  const [name, setName] = useState('');
  const [criteria, setCriteria] = useState({
    type: [] as string[],
    tags: [] as string[],
    uploadedAfter: '',
    minUsageCount: 0,
    favorites: false,
  });

  const handleSave = () => {
    onSave({
      name,
      isSmartFolder: true,
      smartCriteria: criteria,
    });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-xl w-full max-w-md p-6 text-white">
        <h3 className="font-semibold text-lg mb-4">Create Smart Folder</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Folder Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
              placeholder="e.g., Recent Images"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Asset Type
            </label>
            <div className="flex flex-wrap gap-2">
              {['image', 'video', 'audio', 'document'].map((type) => (
                <button
                  key={type}
                  onClick={() =>
                    setCriteria((prev) => ({
                      ...prev,
                      type: prev.type.includes(type)
                        ? prev.type.filter((t) => t !== type)
                        : [...prev.type, type],
                    }))
                  }
                  className={`px-3 py-1.5 rounded capitalize ${
                    criteria.type.includes(type)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-400'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Uploaded After
            </label>
            <input
              type="date"
              value={criteria.uploadedAfter}
              onChange={(e) =>
                setCriteria((prev) => ({ ...prev, uploadedAfter: e.target.value }))
              }
              className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
            />
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={criteria.favorites}
              onChange={(e) =>
                setCriteria((prev) => ({ ...prev, favorites: e.target.checked }))
              }
              className="w-4 h-4 rounded bg-gray-800 border-gray-700"
            />
            <span>Favorites only</span>
          </label>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!name}
            className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
          >
            Create
          </button>
        </div>
      </div>
    </div>
  );
}

// AI Search Component
export function AIAssetSearch({
  onSearch,
}: {
  onSearch: (query: string, type: 'text' | 'semantic') => void;
}) {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'text' | 'semantic'>('text');
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async () => {
    setIsSearching(true);
    await onSearch(query, searchType);
    setIsSearching(false);
  };

  return (
    <div className="flex gap-2">
      <div className="flex-1 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder={
            searchType === 'semantic'
              ? 'Describe what you\'re looking for...'
              : 'Search assets...'
          }
          className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white"
        />
      </div>
      <button
        onClick={() => setSearchType(searchType === 'text' ? 'semantic' : 'text')}
        className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
          searchType === 'semantic'
            ? 'bg-purple-600 text-white'
            : 'bg-gray-800 text-gray-400'
        }`}
        title="Toggle AI Search"
      >
        <Sparkles className="w-5 h-5" />
        AI
      </button>
      <button
        onClick={handleSearch}
        disabled={isSearching}
        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white"
      >
        Search
      </button>
    </div>
  );
}

// Asset Card Component
export function AssetCard({
  asset,
  onSelect,
  onToggleFavorite,
  onDelete,
  isSelected,
  viewMode,
}: {
  asset: Asset;
  onSelect: () => void;
  onToggleFavorite: () => void;
  onDelete: () => void;
  isSelected: boolean;
  viewMode: 'grid' | 'list';
}) {
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (viewMode === 'list') {
    return (
      <div
        className={`flex items-center gap-4 p-3 bg-gray-800 rounded-lg cursor-pointer transition-colors ${
          isSelected ? 'ring-2 ring-blue-500' : 'hover:bg-gray-750'
        }`}
        onClick={onSelect}
      >
        <div className="w-12 h-12 bg-gray-700 rounded-lg overflow-hidden flex-shrink-0">
          {asset.type === 'image' ? (
            <Image
              unoptimized
              src={asset.thumbnailUrl}
              alt={asset.name}
              fill
              className="object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <AssetIcon type={asset.type} />
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-white truncate">{asset.name}</div>
          <div className="text-sm text-gray-400">
            {formatSize(asset.size)}
            {asset.dimensions &&
              ` • ${asset.dimensions.width}×${asset.dimensions.height}`}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {asset.usageCount > 0 && (
            <Badge className="bg-green-900/30 text-green-400 border-green-700/30 text-xs">
              {asset.usageCount}×
            </Badge>
          )}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={(e) => { e.stopPropagation(); onToggleFavorite(); }}
                className="p-1.5 hover:bg-gray-700 rounded transition-colors"
              >
                {asset.isFavorite ? (
                  <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                ) : (
                  <StarOff className="w-5 h-5 text-gray-400" />
                )}
              </button>
            </TooltipTrigger>
            <TooltipContent>{asset.isFavorite ? 'Remove from favorites' : 'Add to favorites'}</TooltipContent>
          </Tooltip>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                onClick={(e) => e.stopPropagation()}
                className="p-1.5 hover:bg-gray-700 rounded transition-colors"
              >
                <MoreVertical className="w-4 h-4 text-gray-400" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem className="gap-2"><Download size={14} />Download</DropdownMenuItem>
              <DropdownMenuItem className="gap-2"><Copy size={14} />Copy Link</DropdownMenuItem>
              <DropdownMenuItem className="gap-2"><Tag size={14} />Edit Tags</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={(e) => { e.stopPropagation(); onDelete(); }}
                className="gap-2 text-red-400 focus:text-red-400"
              >
                <Trash2 size={14} />Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`group relative bg-gray-800 rounded-xl overflow-hidden cursor-pointer transition-all ${
        isSelected ? 'ring-2 ring-blue-500' : 'hover:ring-1 hover:ring-gray-600'
      }`}
      onClick={onSelect}
    >
      <div className="aspect-square bg-gray-700 relative">
        {asset.type === 'image' ? (
          <Image
            unoptimized
            src={asset.thumbnailUrl}
            alt={asset.name}
            fill
            className="object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <AssetIcon type={asset.type} size={48} />
          </div>
        )}

        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors">
                <Eye className="w-5 h-5 text-white" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Preview</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors">
                <Download className="w-5 h-5 text-white" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Download</TooltipContent>
          </Tooltip>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors" onClick={(e) => e.stopPropagation()}>
                <MoreVertical className="w-5 h-5 text-white" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem className="gap-2"><Copy size={14} />Copy Link</DropdownMenuItem>
              <DropdownMenuItem className="gap-2"><Tag size={14} />Edit Tags</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={(e) => { e.stopPropagation(); onDelete(); }}
                className="gap-2 text-red-400 focus:text-red-400"
              >
                <Trash2 size={14} />Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Favorite button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite();
          }}
          className="absolute top-2 right-2 p-1.5 bg-black/50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
        >
          {asset.isFavorite ? (
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
          ) : (
            <StarOff className="w-4 h-4 text-white" />
          )}
        </button>

        {/* Usage indicator */}
        {asset.usageCount > 0 && (
          <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/50 rounded text-xs text-white">
            {asset.usageCount}×
          </div>
        )}
      </div>

      <div className="p-3">
        <div className="font-medium text-white text-sm truncate">{asset.name}</div>
        <div className="text-xs text-gray-400 mt-1">{formatSize(asset.size)}</div>
        {asset.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {asset.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="px-1.5 py-0.5 bg-gray-700 text-gray-300 rounded text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface ApiAsset {
  id: number; name: string; asset_type: string; file_url: string; thumbnail_url: string;
  file_size: number; width: number | null; height: number | null; folder: number | null;
  tag_names: string[]; is_favorite: boolean; usage_count: number; created_at: string;
  ai_colors: string[]; ai_description: string;
}
interface ApiFolder {
  id: number; name: string; parent: number | null; is_smart: boolean;
  smart_rules: Record<string, unknown>; color: string; asset_count: number;
}
function toAsset(data: ApiAsset): Asset {
  const type = ['video', 'audio', 'font', 'document'].includes(data.asset_type) ? data.asset_type as Asset['type'] : ['image', 'icon', 'illustration', 'photo', 'logo', 'svg'].includes(data.asset_type) ? 'image' : 'other';
  return { id: String(data.id), name: data.name, type, url: data.file_url, thumbnailUrl: data.thumbnail_url || data.file_url, size: data.file_size, dimensions: data.width && data.height ? { width: data.width, height: data.height } : null, folderId: data.folder === null ? null : String(data.folder), tags: data.tag_names || [], isFavorite: data.is_favorite, usageCount: data.usage_count, uploadedAt: data.created_at, aiAnalysis: data.ai_description ? { dominantColors: data.ai_colors || [], description: data.ai_description, category: data.asset_type } : null };
}
function toFolder(data: ApiFolder): AssetFolder {
  return { id: String(data.id), name: data.name, parentId: data.parent === null ? null : String(data.parent), isSmartFolder: data.is_smart, smartCriteria: data.smart_rules, color: data.color, assetCount: data.asset_count };
}

// Asset Manager Component
export function AssetManager({ projectId: _projectId }: { projectId?: string }) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [folders, setFolders] = useState<AssetFolder[]>([]);
  const [currentFolder, setCurrentFolder] = useState<string | null>(null);
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');
  const [showSmartFolderDialog, setShowSmartFolderDialog] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDraggingOver, setIsDraggingOver] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const sortedAssets = useMemo(() => [...assets].sort((a, b) => sortBy === 'name' ? a.name.localeCompare(b.name) : sortBy === 'size' ? b.size - a.size : new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime()), [assets, sortBy]);

  const downloadSelected = async () => {
    try {
      for (const asset of assets.filter(item => selectedAssets.includes(item.id))) {
        const response = await fetch(asset.url);
        if (!response.ok) throw new Error('Download failed');
        const url = URL.createObjectURL(await response.blob());
        const link = document.createElement('a');
        link.href = url;
        link.download = asset.name;
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      }
    } catch { setError('Unable to download selected assets. Please retry.'); }
  };

  const loadAssets = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { data } = await apiClient.get<ApiAsset[] | { results: ApiAsset[] }>('/v1/asset-management/items/', {
        params: currentFolder ? { folder: currentFolder } : {},
      });
      setAssets((Array.isArray(data) ? data : data.results).map(toAsset));
    } catch {
      setAssets([]);
      setError('Unable to load assets. Please retry.');
    } finally {
      setIsLoading(false);
    }
  }, [currentFolder]);

  const loadFolders = useCallback(async () => {
    try {
      const { data } = await apiClient.get<ApiFolder[] | { results: ApiFolder[] }>('/v1/asset-management/folders/');
      setFolders((Array.isArray(data) ? data : data.results).map(toFolder));
    } catch {
      setFolders([]);
      setError('Unable to load folders. Please retry.');
    }
  }, []);

  useEffect(() => { void loadAssets(); void loadFolders(); }, [loadAssets, loadFolders]);

  const handleUpload = async (files: FileList) => {
    setError(null);
    for (const file of Array.from(files)) {
      const form = new FormData();
      form.append('file', file);
      const kind = file.type.startsWith('image/') ? 'image' : file.type.startsWith('video/') ? 'video' : file.type.startsWith('audio/') ? 'audio' : /\.(woff2?|ttf|otf)$/i.test(file.name) ? 'font' : 'document';
      form.append('asset_type', kind);
      if (currentFolder) form.append('folder', currentFolder);
      try {
        const { data } = await apiClient.post<ApiAsset>('/v1/asset-management/items/upload/', form, { headers: { 'Content-Type': 'multipart/form-data' } });
        setAssets(previous => [toAsset(data), ...previous]);
      } catch {
        setError(`Could not upload ${file.name}. Files must be 50 MB or smaller. Please retry.`);
        break;
      }
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
    void loadFolders();
  };

  const handleSearch = async (query: string, type: 'text' | 'semantic') => {
    setError(null);
    try {
      const { data } = await apiClient.post<ApiAsset[] | { results: ApiAsset[] }>('/v1/asset-management/items/search/', { query, ai_search: type === 'semantic', ...(currentFolder ? { folder_id: Number(currentFolder) } : {}) });
      setAssets((Array.isArray(data) ? data : data.results).map(toAsset));
    } catch {
      setError('Unable to search assets. Please retry.');
    }
  };

  const toggleFavorite = async (assetId: string) => {
    try {
      const { data } = await apiClient.post<{ is_favorite: boolean }>(`/v1/asset-management/items/${assetId}/favorite/`);
      setAssets(previous => previous.map(asset => asset.id === assetId ? { ...asset, isFavorite: data.is_favorite } : asset));
    } catch { setError('Unable to update favorite. Please retry.'); }
  };

  const deleteAsset = async (assetId: string) => {
    try {
      await apiClient.delete(`/v1/asset-management/items/${assetId}/`);
      setAssets(previous => previous.filter(asset => asset.id !== assetId));
      setSelectedAssets(previous => previous.filter(id => id !== assetId));
    } catch { setError('Unable to delete asset. Please retry.'); }
  };

  const createSmartFolder = async (folder: Partial<AssetFolder>) => {
    try {
      const { data } = await apiClient.post<ApiFolder>('/v1/asset-management/folders/', { name: folder.name, parent: folder.parentId, is_smart: true, smart_rules: folder.smartCriteria ?? {}, color: folder.color });
      setFolders(previous => [...previous, toFolder(data)]);
      setShowSmartFolderDialog(false);
    } catch { setError('Unable to create folder. Please retry.'); }
  };

  return (
    <TooltipProvider>
    <div
      className="flex h-full bg-gray-900 text-white"
      onDragOver={(e) => { e.preventDefault(); setIsDraggingOver(true); }}
      onDragLeave={() => setIsDraggingOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDraggingOver(false);
        if (e.dataTransfer.files.length > 0) handleUpload(e.dataTransfer.files);
      }}
    >
      {isDraggingOver && (
        <div className="absolute inset-0 bg-blue-600/20 border-4 border-dashed border-blue-500 rounded-xl z-50 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <CloudUpload className="w-16 h-16 mx-auto text-blue-400 mb-3" />
            <p className="text-xl font-semibold text-blue-300">Drop files to upload</p>
          </div>
        </div>
      )}
      {/* Sidebar */}
      <div className="w-64 border-r border-gray-700 p-4">
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full flex items-center justify-center gap-2 p-3 bg-blue-600 hover:bg-blue-700 rounded-lg mb-4 transition-colors"
            >
              <Upload className="w-5 h-5" />
              Upload Assets
            </button>
          </TooltipTrigger>
          <TooltipContent>Click or drag & drop files</TooltipContent>
        </Tooltip>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => e.target.files && handleUpload(e.target.files)}
        />

        <div className="mb-4">
          <button
            onClick={() => setShowSmartFolderDialog(true)}
            className="w-full flex items-center gap-2 p-2 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg"
          >
            <Sparkles className="w-4 h-4" />
            Create Smart Folder
          </button>
        </div>

        <div className="space-y-1">
          <button
            onClick={() => setCurrentFolder(null)}
            className={`w-full flex items-center gap-2 p-2 rounded-lg ${
              !currentFolder ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800'
            }`}
          >
            <HardDrive className="w-4 h-4" />
            All Assets
          </button>

          {folders.map((folder) => (
            <button
              key={folder.id}
              onClick={() => setCurrentFolder(folder.id)}
              className={`w-full flex items-center justify-between p-2 rounded-lg ${
                currentFolder === folder.id
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center gap-2">
                {folder.isSmartFolder ? (
                  <Sparkles className="w-4 h-4" style={{ color: folder.color }} />
                ) : (
                  <FolderOpen className="w-4 h-4" style={{ color: folder.color }} />
                )}
                <span>{folder.name}</span>
              </div>
              <span className="text-xs text-gray-500">{folder.assetCount}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Toolbar */}
        <div className="p-4 border-b border-gray-700 space-y-4">
          <AIAssetSearch onSearch={handleSearch} />

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex items-center bg-gray-800 rounded-lg p-0.5">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`p-1.5 rounded transition-colors ${
                        viewMode === 'grid' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      <Grid className="w-4 h-4" />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>Grid view</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`p-1.5 rounded transition-colors ${
                        viewMode === 'list' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      <List className="w-4 h-4" />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>List view</TooltipContent>
                </Tooltip>
              </div>
              <div className="w-px h-6 bg-gray-700 mx-1" />
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-1.5 px-2.5 py-1.5 text-sm text-gray-400 hover:text-white bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
                    <SortAsc className="w-4 h-4" />
                    {sortBy === 'date' ? 'Date' : sortBy === 'name' ? 'Name' : 'Size'}
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  <DropdownMenuItem onClick={() => setSortBy('date')}>Date Added {sortBy === 'date' && <Check className="w-3 h-3 ml-auto" />}</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy('name')}>Name {sortBy === 'name' && <Check className="w-3 h-3 ml-auto" />}</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy('size')}>Size {sortBy === 'size' && <Check className="w-3 h-3 ml-auto" />}</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {selectedAssets.length > 0 && (
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs">
                  {selectedAssets.length} selected
                </Badge>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button onClick={() => void downloadSelected()} className="p-1.5 hover:bg-gray-800 rounded transition-colors text-gray-400 hover:text-white">
                      <Download className="w-4 h-4" />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>Download selected</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      onClick={() => { void Promise.all(selectedAssets.map(deleteAsset)); }}
                      className="p-1.5 hover:bg-gray-800 rounded transition-colors text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>Delete selected</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      onClick={() => setSelectedAssets([])}
                      className="p-1.5 hover:bg-gray-800 rounded transition-colors text-gray-400 hover:text-white"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>Clear selection</TooltipContent>
                </Tooltip>
              </div>
            )}
          </div>
        </div>

        {error && <div role="alert" className="p-4 text-red-300"><p>{error}</p><button className="underline" onClick={() => { void loadAssets(); void loadFolders(); }}>Retry</button></div>}
        {/* Assets Grid/List */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full" />
            </div>
          ) : assets.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-20">
              <div className="w-24 h-24 bg-gray-800 rounded-2xl flex items-center justify-center mb-6">
                <CloudUpload className="w-12 h-12 text-gray-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-300 mb-2">No assets yet</h3>
              <p className="text-sm text-gray-500 max-w-xs mb-6">
                Upload images, videos, fonts and documents to use in your designs
              </p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-medium transition-colors"
              >
                <Upload className="w-4 h-4" />
                Upload First Asset
              </button>
            </div>
          ) : viewMode === 'grid' ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {sortedAssets.map((asset) => (
                <AssetCard
                  key={asset.id}
                  asset={asset}
                  isSelected={selectedAssets.includes(asset.id)}
                  onSelect={() =>
                    setSelectedAssets((prev) =>
                      prev.includes(asset.id)
                        ? prev.filter((id) => id !== asset.id)
                        : [...prev, asset.id]
                    )
                  }
                  onToggleFavorite={() => toggleFavorite(asset.id)}
                  onDelete={() => deleteAsset(asset.id)}
                  viewMode={viewMode}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {sortedAssets.map((asset) => (
                <AssetCard
                  key={asset.id}
                  asset={asset}
                  isSelected={selectedAssets.includes(asset.id)}
                  onSelect={() =>
                    setSelectedAssets((prev) =>
                      prev.includes(asset.id)
                        ? prev.filter((id) => id !== asset.id)
                        : [...prev, asset.id]
                    )
                  }
                  onToggleFavorite={() => toggleFavorite(asset.id)}
                  onDelete={() => deleteAsset(asset.id)}
                  viewMode={viewMode}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      <SmartFolderDialog
        isOpen={showSmartFolderDialog}
        onClose={() => setShowSmartFolderDialog(false)}
        onSave={createSmartFolder}
      />
    </div>
    </TooltipProvider>
  );
}

export default AssetManager;
