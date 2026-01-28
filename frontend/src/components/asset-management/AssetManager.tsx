'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  FolderPlus, Search, Filter, Grid, List, Upload,
  Image, FileVideo, FileAudio, File, Trash2, Download,
  Copy, Tag, Star, StarOff, MoreVertical, Eye,
  ChevronRight, CloudUpload, Sparkles, Link, Clock,
  FolderOpen, Check, X, ArrowUpDown, HardDrive
} from 'lucide-react';

// Types
interface AssetFolder {
  id: string;
  name: string;
  parentId: string | null;
  isSmartFolder: boolean;
  smartCriteria: Record<string, any> | null;
  color: string;
  assetCount: number;
}

interface Asset {
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

interface CDNIntegration {
  id: string;
  provider: 'cloudinary' | 'imgix' | 'cloudflare';
  isActive: boolean;
  settings: Record<string, any>;
}

// Asset Icon Component
const AssetIcon = ({ type, size = 24 }: { type: Asset['type']; size?: number }) => {
  const iconProps = { size, className: 'text-gray-400' };
  
  switch (type) {
    case 'image':
      return <Image {...iconProps} className="text-blue-400" />;
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
  const [showMenu, setShowMenu] = useState(false);

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
            <img
              src={asset.thumbnailUrl}
              alt={asset.name}
              className="w-full h-full object-cover"
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
            <span className="px-2 py-1 bg-green-900/30 text-green-400 rounded text-sm">
              Used {asset.usageCount}×
            </span>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite();
            }}
            className="p-1.5 hover:bg-gray-700 rounded"
          >
            {asset.isFavorite ? (
              <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
            ) : (
              <StarOff className="w-5 h-5 text-gray-400" />
            )}
          </button>
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
          <img
            src={asset.thumbnailUrl}
            alt={asset.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <AssetIcon type={asset.type} size={48} />
          </div>
        )}

        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg">
            <Eye className="w-5 h-5 text-white" />
          </button>
          <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg">
            <Download className="w-5 h-5 text-white" />
          </button>
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

// Asset Manager Component
export function AssetManager({ projectId }: { projectId?: string }) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [folders, setFolders] = useState<AssetFolder[]>([]);
  const [currentFolder, setCurrentFolder] = useState<string | null>(null);
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');
  const [showSmartFolderDialog, setShowSmartFolderDialog] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadAssets();
    loadFolders();
  }, [projectId, currentFolder]);

  const loadAssets = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (currentFolder) params.set('folder', currentFolder);
      if (projectId) params.set('project', projectId);

      const response = await fetch(`/api/v1/asset-management/assets/?${params}`);
      const data = await response.json();
      setAssets(data.results || data);
    } catch (error) {
      // Load mock data
      setAssets([
        {
          id: '1',
          name: 'hero-image.jpg',
          type: 'image',
          url: '/assets/hero.jpg',
          thumbnailUrl: '/assets/hero-thumb.jpg',
          size: 524288,
          dimensions: { width: 1920, height: 1080 },
          folderId: null,
          tags: ['hero', 'marketing'],
          isFavorite: true,
          usageCount: 5,
          uploadedAt: new Date().toISOString(),
          aiAnalysis: {
            dominantColors: ['#3B82F6', '#1F2937', '#FFFFFF'],
            description: 'A modern abstract design with blue gradients',
            category: 'marketing',
          },
        },
        {
          id: '2',
          name: 'icon-set.svg',
          type: 'image',
          url: '/assets/icons.svg',
          thumbnailUrl: '/assets/icons-thumb.png',
          size: 32768,
          dimensions: { width: 512, height: 512 },
          folderId: null,
          tags: ['icons', 'ui'],
          isFavorite: false,
          usageCount: 12,
          uploadedAt: new Date().toISOString(),
          aiAnalysis: null,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFolders = async () => {
    try {
      const response = await fetch('/api/v1/asset-management/folders/');
      const data = await response.json();
      setFolders(data.results || data);
    } catch (error) {
      setFolders([
        { id: '1', name: 'Images', parentId: null, isSmartFolder: false, smartCriteria: null, color: '#3B82F6', assetCount: 24 },
        { id: '2', name: 'Icons', parentId: null, isSmartFolder: false, smartCriteria: null, color: '#10B981', assetCount: 48 },
        { id: '3', name: 'Recent', parentId: null, isSmartFolder: true, smartCriteria: { uploadedAfter: '7d' }, color: '#8B5CF6', assetCount: 12 },
      ]);
    }
  };

  const handleUpload = async (files: FileList) => {
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });
    if (currentFolder) {
      formData.append('folder_id', currentFolder);
    }

    try {
      const response = await fetch('/api/v1/asset-management/assets/bulk-upload/', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setAssets((prev) => [...data, ...prev]);
    } catch (error) {
      console.error('Upload failed', error);
    }
  };

  const handleSearch = async (query: string, type: 'text' | 'semantic') => {
    try {
      const response = await fetch('/api/v1/asset-management/assets/search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, search_type: type }),
      });
      const data = await response.json();
      setAssets(data.results || data);
    } catch (error) {
      console.error('Search failed', error);
    }
  };

  const toggleFavorite = async (assetId: string) => {
    setAssets((prev) =>
      prev.map((a) =>
        a.id === assetId ? { ...a, isFavorite: !a.isFavorite } : a
      )
    );

    try {
      await fetch(`/api/v1/asset-management/assets/${assetId}/toggle-favorite/`, {
        method: 'POST',
      });
    } catch (error) {
      console.error('Failed to toggle favorite', error);
    }
  };

  const deleteAsset = async (assetId: string) => {
    try {
      await fetch(`/api/v1/asset-management/assets/${assetId}/`, {
        method: 'DELETE',
      });
      setAssets((prev) => prev.filter((a) => a.id !== assetId));
    } catch (error) {
      console.error('Failed to delete asset', error);
    }
  };

  const createSmartFolder = async (folder: Partial<AssetFolder>) => {
    try {
      const response = await fetch('/api/v1/asset-management/folders/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(folder),
      });
      const data = await response.json();
      setFolders((prev) => [...prev, data]);
    } catch (error) {
      console.error('Failed to create folder', error);
    }
  };

  return (
    <div className="flex h-full bg-gray-900 text-white">
      {/* Sidebar */}
      <div className="w-64 border-r border-gray-700 p-4">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full flex items-center justify-center gap-2 p-3 bg-blue-600 hover:bg-blue-700 rounded-lg mb-4"
        >
          <Upload className="w-5 h-5" />
          Upload Assets
        </button>
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
              <div className="w-px h-6 bg-gray-700 mx-2" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'name' | 'size' | 'date')}
                className="p-2 bg-gray-800 border border-gray-700 rounded"
              >
                <option value="date">Date Added</option>
                <option value="name">Name</option>
                <option value="size">Size</option>
              </select>
            </div>

            {selectedAssets.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">
                  {selectedAssets.length} selected
                </span>
                <button className="p-2 hover:bg-gray-800 rounded">
                  <Download className="w-5 h-5" />
                </button>
                <button className="p-2 hover:bg-gray-800 rounded text-red-400">
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Assets Grid/List */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full" />
            </div>
          ) : viewMode === 'grid' ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {assets.map((asset) => (
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
              {assets.map((asset) => (
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
  );
}

export default AssetManager;
