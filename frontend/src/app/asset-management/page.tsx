"use client";

import React, { useState, useCallback } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import Image from 'next/image';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
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
  Database,
  Search,
  Upload,
  FolderPlus,
  Grid,
  List,
  Filter,
  SortAsc,
  MoreVertical,
  Star,
  Trash2,
  Download,
  Tag,
  Eye,
  Copy,
  Move,
  FolderOpen,
  Sparkles,
  ChevronRight,
  ChevronDown,
  Plus,
  X,
  HardDrive,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface AssetFolder {
  id: number;
  name: string;
  parent: number | null;
  children: AssetFolder[];
  assets_count: number;
}

interface AssetTag {
  id: number;
  name: string;
  color: string;
  usage_count: number;
}

interface Asset {
  id: number;
  name: string;
  thumbnail: string;
  file_type: 'image' | 'video' | 'audio' | 'document' | 'font' | '3d_model' | 'other';
  file_size: number;
  width?: number;
  height?: number;
  folder: number | null;
  tags: AssetTag[];
  ai_tags?: string[];
  ai_description?: string;
  colors?: string[];
  is_favorite: boolean;
  usage_count: number;
  created_by: { id: number; username: string };
  created_at: string;
  updated_at: string;
}

// Mock Data
const mockFolders: AssetFolder[] = [
  {
    id: 1, name: 'Brand Assets', parent: null, assets_count: 45,
    children: [
      { id: 2, name: 'Logos', parent: 1, children: [], assets_count: 12 },
      { id: 3, name: 'Icons', parent: 1, children: [], assets_count: 28 },
      { id: 4, name: 'Typography', parent: 1, children: [], assets_count: 5 },
    ],
  },
  {
    id: 5, name: 'Stock Photos', parent: null, assets_count: 156,
    children: [
      { id: 6, name: 'People', parent: 5, children: [], assets_count: 42 },
      { id: 7, name: 'Nature', parent: 5, children: [], assets_count: 38 },
      { id: 8, name: 'Business', parent: 5, children: [], assets_count: 76 },
    ],
  },
  { id: 9, name: 'Videos', parent: null, assets_count: 23, children: [] },
  { id: 10, name: 'Illustrations', parent: null, assets_count: 67, children: [] },
];

const mockTags: AssetTag[] = [
  { id: 1, name: 'Marketing', color: '#3B82F6', usage_count: 45 },
  { id: 2, name: 'Social Media', color: '#8B5CF6', usage_count: 38 },
  { id: 3, name: 'Website', color: '#10B981', usage_count: 62 },
  { id: 4, name: 'Print', color: '#F59E0B', usage_count: 21 },
  { id: 5, name: 'Presentation', color: '#EF4444', usage_count: 15 },
];

const mockAssets: Asset[] = [
  {
    id: 1, name: 'hero-banner.png', thumbnail: 'https://picsum.photos/seed/1/300/200',
    file_type: 'image', file_size: 2456000, width: 1920, height: 1080, folder: 1,
    tags: [mockTags[0], mockTags[2]], ai_tags: ['banner', 'hero', 'gradient', 'modern'],
    ai_description: 'A modern hero banner with gradient background',
    colors: ['#3B82F6', '#8B5CF6', '#FFFFFF'], is_favorite: true, usage_count: 12,
    created_by: { id: 1, username: 'john_doe' },
    created_at: '2024-02-15T10:30:00Z', updated_at: '2024-02-20T14:45:00Z',
  },
  {
    id: 2, name: 'company-logo.svg', thumbnail: 'https://picsum.photos/seed/2/300/200',
    file_type: 'image', file_size: 45000, width: 512, height: 512, folder: 2,
    tags: [mockTags[0]], ai_tags: ['logo', 'brand', 'vector'],
    is_favorite: true, usage_count: 45, created_by: { id: 1, username: 'john_doe' },
    created_at: '2024-01-10T09:00:00Z', updated_at: '2024-02-18T11:20:00Z',
  },
  {
    id: 3, name: 'team-meeting.jpg', thumbnail: 'https://picsum.photos/seed/3/300/200',
    file_type: 'image', file_size: 1890000, width: 2400, height: 1600, folder: 6,
    tags: [mockTags[2], mockTags[4]], ai_tags: ['people', 'meeting', 'business', 'office'],
    ai_description: 'Business team in a collaborative meeting setting',
    colors: ['#1E40AF', '#F3F4F6', '#374151'], is_favorite: false, usage_count: 8,
    created_by: { id: 2, username: 'jane_smith' },
    created_at: '2024-02-01T15:20:00Z', updated_at: '2024-02-01T15:20:00Z',
  },
  {
    id: 4, name: 'product-demo.mp4', thumbnail: 'https://picsum.photos/seed/4/300/200',
    file_type: 'video', file_size: 45600000, folder: 9,
    tags: [mockTags[0], mockTags[1]], is_favorite: false, usage_count: 3,
    created_by: { id: 1, username: 'john_doe' },
    created_at: '2024-02-10T12:00:00Z', updated_at: '2024-02-10T12:00:00Z',
  },
  {
    id: 5, name: 'icon-set.svg', thumbnail: 'https://picsum.photos/seed/5/300/200',
    file_type: 'image', file_size: 156000, folder: 3,
    tags: [mockTags[2]], ai_tags: ['icons', 'ui', 'interface', 'set'],
    is_favorite: true, usage_count: 67, created_by: { id: 1, username: 'john_doe' },
    created_at: '2024-01-20T08:30:00Z', updated_at: '2024-02-15T09:45:00Z',
  },
  {
    id: 6, name: 'nature-landscape.jpg', thumbnail: 'https://picsum.photos/seed/6/300/200',
    file_type: 'image', file_size: 3200000, width: 3840, height: 2160, folder: 7,
    tags: [mockTags[1]], ai_tags: ['nature', 'landscape', 'mountains', 'sunset'],
    ai_description: 'Beautiful mountain landscape during golden hour',
    colors: ['#F59E0B', '#7C3AED', '#1E3A8A'], is_favorite: false, usage_count: 5,
    created_by: { id: 2, username: 'jane_smith' },
    created_at: '2024-02-05T16:40:00Z', updated_at: '2024-02-05T16:40:00Z',
  },
];

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Folder Tree Component
function FolderTree({ folders, selectedFolder, onSelectFolder, expandedFolders, onToggleExpand }: {
  folders: AssetFolder[];
  selectedFolder: number | null;
  onSelectFolder: (id: number | null) => void;
  expandedFolders: Set<number>;
  onToggleExpand: (id: number) => void;
}) {
  const renderFolder = (folder: AssetFolder, level: number = 0) => {
    const isExpanded = expandedFolders.has(folder.id);
    const isSelected = selectedFolder === folder.id;
    const hasChildren = folder.children && folder.children.length > 0;

    return (
      <div key={folder.id}>
        <div
          className={`flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer transition-colors ${
            isSelected ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100 text-gray-700'
          }`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => onSelectFolder(folder.id)}
        >
          {hasChildren && (
            <button onClick={(e) => { e.stopPropagation(); onToggleExpand(folder.id); }} className="p-0.5 hover:bg-gray-200 rounded">
              {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </button>
          )}
          {!hasChildren && <div className="w-5" />}
          <FolderOpen className={`h-4 w-4 ${isSelected ? 'text-blue-600' : 'text-amber-500'}`} />
          <span className="flex-1 text-sm truncate">{folder.name}</span>
          <span className="text-xs text-gray-400">{folder.assets_count}</span>
        </div>
        {hasChildren && isExpanded && folder.children.map((child) => renderFolder(child, level + 1))}
      </div>
    );
  };

  return <div className="space-y-0.5">{folders.map((f) => renderFolder(f))}</div>;
}

// Asset Grid Item Component
function AssetGridItem({ asset, isSelected, onSelect, onToggleFavorite, onView }: {
  asset: Asset;
  isSelected: boolean;
  onSelect: (id: number, checked: boolean) => void;
  onToggleFavorite: (id: number) => void;
  onView: (asset: Asset) => void;
}) {
  return (
    <div className={`group relative bg-white rounded-lg border overflow-hidden transition-all hover:shadow-lg ${
      isSelected ? 'ring-2 ring-blue-500 border-blue-500' : 'border-gray-200'
    }`}>
      <div className="relative aspect-video bg-gray-100 overflow-hidden">
        <Image src={asset.thumbnail} alt={asset.name} className="w-full h-full object-cover transition-transform group-hover:scale-105" width={320} height={180} />
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <Button size="sm" variant="secondary" className="h-8" onClick={() => onView(asset)}>
            <Eye className="h-4 w-4 mr-1" />View
          </Button>
          <Button size="sm" variant="secondary" className="h-8"><Download className="h-4 w-4" /></Button>
        </div>
        <div className="absolute top-2 left-2">
          <Checkbox checked={isSelected} onCheckedChange={(checked) => onSelect(asset.id, !!checked)} className="bg-white border-white" />
        </div>
        <button onClick={() => onToggleFavorite(asset.id)} className="absolute top-2 right-2 p-1.5 rounded-full bg-white/90 hover:bg-white transition-colors">
          <Star className={`h-4 w-4 ${asset.is_favorite ? 'fill-yellow-400 text-yellow-400' : 'text-gray-400'}`} />
        </button>
        <div className="absolute bottom-2 left-2">
          <Badge variant="secondary" className="bg-white/90 text-xs">{asset.file_type.toUpperCase()}</Badge>
        </div>
      </div>
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{asset.name}</p>
            <p className="text-xs text-gray-500">{formatFileSize(asset.file_size)}{asset.width && asset.height && ` • ${asset.width}×${asset.height}`}</p>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild><Button variant="ghost" size="sm" className="h-8 w-8 p-0"><MoreVertical className="h-4 w-4" /></Button></DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem><Eye className="h-4 w-4 mr-2" />Preview</DropdownMenuItem>
              <DropdownMenuItem><Download className="h-4 w-4 mr-2" />Download</DropdownMenuItem>
              <DropdownMenuItem><Copy className="h-4 w-4 mr-2" />Duplicate</DropdownMenuItem>
              <DropdownMenuItem><Move className="h-4 w-4 mr-2" />Move to...</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem><Tag className="h-4 w-4 mr-2" />Edit Tags</DropdownMenuItem>
              <DropdownMenuItem><Sparkles className="h-4 w-4 mr-2" />AI Analyze</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-red-600"><Trash2 className="h-4 w-4 mr-2" />Delete</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        {asset.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {asset.tags.slice(0, 2).map((tag) => (
              <Badge key={tag.id} variant="outline" className="text-xs" style={{ borderColor: tag.color, color: tag.color }}>{tag.name}</Badge>
            ))}
            {asset.tags.length > 2 && <Badge variant="outline" className="text-xs text-gray-500">+{asset.tags.length - 2}</Badge>}
          </div>
        )}
        {asset.ai_tags && asset.ai_tags.length > 0 && (
          <div className="flex items-center gap-1 mt-2">
            <Sparkles className="h-3 w-3 text-purple-500" />
            <span className="text-xs text-gray-400 truncate">{asset.ai_tags.slice(0, 3).join(', ')}</span>
          </div>
        )}
      </div>
    </div>
  );
}

// Asset Detail Panel Component
function AssetDetailPanel({ asset, onClose }: { asset: Asset; onClose: () => void }) {
  return (
    <div className="w-80 border-l border-gray-200 bg-white flex flex-col">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Asset Details</h3>
        <Button variant="ghost" size="sm" onClick={onClose}><X className="h-4 w-4" /></Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-6">
          <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
            <Image src={asset.thumbnail} alt={asset.name} className="w-full h-full object-cover" width={320} height={180} />
          </div>
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-900">{asset.name}</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-gray-500">Type</div>
              <div className="text-gray-900 capitalize">{asset.file_type}</div>
              <div className="text-gray-500">Size</div>
              <div className="text-gray-900">{formatFileSize(asset.file_size)}</div>
              {asset.width && asset.height && (<><div className="text-gray-500">Dimensions</div><div className="text-gray-900">{asset.width} × {asset.height}</div></>)}
              <div className="text-gray-500">Created</div>
              <div className="text-gray-900">{new Date(asset.created_at).toLocaleDateString()}</div>
              <div className="text-gray-500">Used in</div>
              <div className="text-gray-900">{asset.usage_count} places</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-gray-900">Tags</h4>
              <Button variant="ghost" size="sm" className="h-7 text-xs"><Plus className="h-3 w-3 mr-1" />Add</Button>
            </div>
            <div className="flex flex-wrap gap-1">
              {asset.tags.map((tag) => (
                <Badge key={tag.id} variant="outline" className="text-xs" style={{ borderColor: tag.color, color: tag.color }}>
                  {tag.name}<button className="ml-1 hover:text-red-500"><X className="h-3 w-3" /></button>
                </Badge>
              ))}
            </div>
          </div>
          {(asset.ai_tags || asset.ai_description || asset.colors) && (
            <div className="space-y-3">
              <div className="flex items-center gap-2"><Sparkles className="h-4 w-4 text-purple-500" /><h4 className="text-sm font-medium text-gray-900">AI Analysis</h4></div>
              {asset.ai_description && <p className="text-sm text-gray-600">{asset.ai_description}</p>}
              {asset.ai_tags && <div className="flex flex-wrap gap-1">{asset.ai_tags.map((tag, i) => <Badge key={i} variant="secondary" className="text-xs">{tag}</Badge>)}</div>}
              {asset.colors && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Colors:</span>
                  <div className="flex gap-1">{asset.colors.map((color, i) => <div key={i} className="w-6 h-6 rounded-full border border-gray-200" style={{ backgroundColor: color }} title={color} />)}</div>
                </div>
              )}
            </div>
          )}
          <div className="space-y-2">
            <Button className="w-full" size="sm"><Download className="h-4 w-4 mr-2" />Download</Button>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="outline" size="sm"><Copy className="h-4 w-4 mr-2" />Copy URL</Button>
              <Button variant="outline" size="sm"><Move className="h-4 w-4 mr-2" />Move</Button>
            </div>
            <Button variant="outline" size="sm" className="w-full"><Sparkles className="h-4 w-4 mr-2" />Re-analyze with AI</Button>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}

export default function AssetManagementPage() {
  const { toast } = useToast();
  const [assets, setAssets] = useState<Asset[]>(mockAssets);
  const [folders] = useState<AssetFolder[]>(mockFolders);
  const [tags] = useState<AssetTag[]>(mockTags);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<Set<number>>(new Set([1, 5]));
  const [selectedAssets, setSelectedAssets] = useState<Set<number>>(new Set());
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('updated_at');
  const [filterType, setFilterType] = useState<string | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showNewFolderDialog, setShowNewFolderDialog] = useState(false);

  const toggleFolderExpand = useCallback((id: number) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const toggleAssetSelect = useCallback((id: number, checked: boolean) => {
    setSelectedAssets((prev) => {
      const next = new Set(prev);
      if (checked) next.add(id);
      else next.delete(id);
      return next;
    });
  }, []);

  const toggleFavorite = useCallback((id: number) => {
    setAssets((prev) => prev.map((a) => a.id === id ? { ...a, is_favorite: !a.is_favorite } : a));
    toast({ title: 'Updated', description: 'Favorite status updated successfully.' });
  }, [toast]);

  const filteredAssets = assets.filter((asset) => {
    if (searchTerm && !asset.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    if (selectedFolder && asset.folder !== selectedFolder) return false;
    if (filterType && asset.file_type !== filterType) return false;
    return true;
  });

  const stats = {
    totalAssets: assets.length,
    totalSize: assets.reduce((acc, a) => acc + a.file_size, 0),
    favorites: assets.filter((a) => a.is_favorite).length,
    images: assets.filter((a) => a.file_type === 'image').length,
    videos: assets.filter((a) => a.file_type === 'video').length,
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 flex overflow-hidden">
          {/* Left Sidebar - Folders & Tags */}
          <div className="w-64 border-r border-gray-200 bg-white flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="flex items-center gap-2 text-blue-600"><HardDrive className="h-4 w-4" /><span className="text-xs font-medium">Storage</span></div>
                  <p className="text-lg font-bold text-blue-700 mt-1">{formatFileSize(stats.totalSize)}</p>
                </div>
                <div className="bg-purple-50 p-3 rounded-lg">
                  <div className="flex items-center gap-2 text-purple-600"><Database className="h-4 w-4" /><span className="text-xs font-medium">Assets</span></div>
                  <p className="text-lg font-bold text-purple-700 mt-1">{stats.totalAssets}</p>
                </div>
              </div>
            </div>
            <div className="flex-1 overflow-hidden flex flex-col">
              <div className="p-3 border-b border-gray-200 flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Folders</span>
                <Button variant="ghost" size="sm" className="h-7" onClick={() => setShowNewFolderDialog(true)}><FolderPlus className="h-4 w-4" /></Button>
              </div>
              <ScrollArea className="flex-1 p-2">
                <div className={`flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer mb-1 ${selectedFolder === null ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`} onClick={() => setSelectedFolder(null)}>
                  <FolderOpen className="h-4 w-4 text-gray-400" /><span className="text-sm">All Assets</span><span className="text-xs text-gray-400 ml-auto">{stats.totalAssets}</span>
                </div>
                <FolderTree folders={folders} selectedFolder={selectedFolder} onSelectFolder={setSelectedFolder} expandedFolders={expandedFolders} onToggleExpand={toggleFolderExpand} />
              </ScrollArea>
            </div>
            <div className="border-t border-gray-200 p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Tags</span>
                <Button variant="ghost" size="sm" className="h-7"><Plus className="h-4 w-4" /></Button>
              </div>
              <div className="flex flex-wrap gap-1">
                {tags.map((tag) => (
                  <Badge key={tag.id} variant="outline" className="text-xs cursor-pointer hover:bg-gray-100" style={{ borderColor: tag.color, color: tag.color }}>
                    {tag.name}<span className="ml-1 text-gray-400">{tag.usage_count}</span>
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="bg-white border-b border-gray-200 p-4">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 flex-1">
                  <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input placeholder="Search assets..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-9" />
                  </div>
                  <Button variant="outline" size="sm"><Sparkles className="h-4 w-4 mr-2 text-purple-500" />AI Search</Button>
                  <Select value={filterType || ''} onValueChange={(v) => setFilterType(v || null)}>
                    <SelectTrigger className="w-[140px]"><Filter className="h-4 w-4 mr-2" /><SelectValue placeholder="All Types" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All Types</SelectItem>
                      <SelectItem value="image">Images</SelectItem>
                      <SelectItem value="video">Videos</SelectItem>
                      <SelectItem value="audio">Audio</SelectItem>
                      <SelectItem value="document">Documents</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={sortBy} onValueChange={setSortBy}>
                    <SelectTrigger className="w-[140px]"><SortAsc className="h-4 w-4 mr-2" /><SelectValue placeholder="Sort by" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="updated_at">Last Modified</SelectItem>
                      <SelectItem value="created_at">Date Created</SelectItem>
                      <SelectItem value="name">Name</SelectItem>
                      <SelectItem value="file_size">Size</SelectItem>
                      <SelectItem value="usage_count">Most Used</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center border border-gray-200 rounded-lg p-0.5">
                    <Button variant={viewMode === 'grid' ? 'secondary' : 'ghost'} size="sm" className="h-8 px-2" onClick={() => setViewMode('grid')}><Grid className="h-4 w-4" /></Button>
                    <Button variant={viewMode === 'list' ? 'secondary' : 'ghost'} size="sm" className="h-8 px-2" onClick={() => setViewMode('list')}><List className="h-4 w-4" /></Button>
                  </div>
                  <Button onClick={() => setShowUploadDialog(true)}><Upload className="h-4 w-4 mr-2" />Upload</Button>
                </div>
              </div>
              {selectedAssets.size > 0 && (
                <div className="flex items-center gap-3 mt-3 p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm text-blue-700 font-medium">{selectedAssets.size} selected</span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-1" />Download</Button>
                    <Button variant="outline" size="sm"><Move className="h-4 w-4 mr-1" />Move</Button>
                    <Button variant="outline" size="sm"><Tag className="h-4 w-4 mr-1" />Tag</Button>
                    <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700"><Trash2 className="h-4 w-4 mr-1" />Delete</Button>
                  </div>
                  <Button variant="ghost" size="sm" className="ml-auto" onClick={() => setSelectedAssets(new Set())}>Clear selection</Button>
                </div>
              )}
            </div>
            <ScrollArea className="flex-1 p-4">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                {filteredAssets.map((asset) => (
                  <AssetGridItem key={asset.id} asset={asset} isSelected={selectedAssets.has(asset.id)} onSelect={toggleAssetSelect} onToggleFavorite={toggleFavorite} onView={setSelectedAsset} />
                ))}
              </div>
              {filteredAssets.length === 0 && (
                <div className="text-center py-16">
                  <Database className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-1">No assets found</h3>
                  <p className="text-gray-500 mb-4">{searchTerm ? 'Try adjusting your search or filters' : 'Upload your first asset to get started'}</p>
                  <Button onClick={() => setShowUploadDialog(true)}><Upload className="h-4 w-4 mr-2" />Upload Assets</Button>
                </div>
              )}
            </ScrollArea>
          </div>

          {selectedAsset && <AssetDetailPanel asset={selectedAsset} onClose={() => setSelectedAsset(null)} />}
        </main>
      </div>

      <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Upload Assets</DialogTitle>
            <DialogDescription>Drag and drop files or click to browse</DialogDescription>
          </DialogHeader>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors cursor-pointer">
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-sm text-gray-600 mb-1">Drop files here or click to browse</p>
            <p className="text-xs text-gray-400">Supports images, videos, audio, documents up to 100MB</p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUploadDialog(false)}>Cancel</Button>
            <Button>Upload</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showNewFolderDialog} onOpenChange={setShowNewFolderDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Folder</DialogTitle>
            <DialogDescription>Enter a name for your new folder</DialogDescription>
          </DialogHeader>
          <div className="py-4"><Input placeholder="Folder name" /></div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewFolderDialog(false)}>Cancel</Button>
            <Button onClick={() => { setShowNewFolderDialog(false); toast({ title: 'Created', description: 'Folder created successfully' }); }}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
