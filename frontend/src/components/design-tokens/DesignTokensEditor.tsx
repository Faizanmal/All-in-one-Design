'use client';

import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Palette,
  Plus,
  Download,
  Upload,
  Copy,
  Trash2,
  Edit2,
  Check,
  X,
  Sun,
  Moon,
  Folder,
  Search,
  ChevronRight,
  MoreVertical,
  RefreshCw,
  Code,
  FileJson,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';

interface DesignToken {
  id: number;
  name: string;
  category: string;
  token_type: string;
  value: string;
  resolved_value: string;
  css_variable: string;
  description: string;
  deprecated: boolean;
}

interface TokenLibrary {
  id: number;
  name: string;
  description: string;
  version: string;
  token_count: number;
  theme_count: number;
  is_default: boolean;
  is_public: boolean;
}

interface Theme {
  id: number;
  name: string;
  slug: string;
  theme_type: string;
  is_default: boolean;
  override_count: number;
}

const TOKEN_TYPES = [
  { value: 'color', label: 'Color', icon: '🎨' },
  { value: 'spacing', label: 'Spacing', icon: '📏' },
  { value: 'typography', label: 'Typography', icon: '🔤' },
  { value: 'shadow', label: 'Shadow', icon: '🌑' },
  { value: 'border', label: 'Border', icon: '▢' },
  { value: 'radius', label: 'Radius', icon: '⬭' },
  { value: 'opacity', label: 'Opacity', icon: '◐' },
  { value: 'z-index', label: 'Z-Index', icon: '📚' },
];

const EXPORT_FORMATS = [
  { value: 'css', label: 'CSS Variables' },
  { value: 'scss', label: 'SCSS Variables' },
  { value: 'json', label: 'JSON' },
  { value: 'js', label: 'JavaScript' },
  { value: 'ts', label: 'TypeScript' },
  { value: 'tailwind', label: 'Tailwind Config' },
];

export function DesignTokensEditor() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedLibrary, setSelectedLibrary] = useState<number | null>(null);
  const [selectedTheme, setSelectedTheme] = useState<string>('default');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingToken, setEditingToken] = useState<DesignToken | null>(null);
  const [newToken, setNewToken] = useState({
    name: '',
    category: '',
    token_type: 'color',
    value: '',
    description: '',
  });

  // Fetch libraries
  const { data: libraries, isLoading: loadingLibraries } = useQuery({
    queryKey: ['design-token-libraries'],
    queryFn: async () => {
      const response = await fetch('/api/v1/projects/design-token-libraries/');
      if (!response.ok) throw new Error('Failed to fetch libraries');
      return response.json();
    },
  });

  // Fetch tokens for selected library
  const { data: libraryData, isLoading: loadingTokens } = useQuery({
    queryKey: ['design-tokens', selectedLibrary],
    queryFn: async () => {
      const response = await fetch(`/api/v1/projects/design-token-libraries/${selectedLibrary}/`);
      if (!response.ok) throw new Error('Failed to fetch tokens');
      return response.json();
    },
    enabled: !!selectedLibrary,
  });

  // Create token mutation
  const createTokenMutation = useMutation({
    mutationFn: async (tokenData: typeof newToken) => {
      const response = await fetch(`/api/v1/projects/design-tokens/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          library_id: selectedLibrary,
          ...tokenData,
        }),
      });
      if (!response.ok) throw new Error('Failed to create token');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['design-tokens', selectedLibrary] });
      setIsCreateDialogOpen(false);
      setNewToken({ name: '', category: '', token_type: 'color', value: '', description: '' });
      toast({ title: 'Token Created', description: 'Design token has been created.' });
    },
  });

  // Update token mutation
  const updateTokenMutation = useMutation({
    mutationFn: async (token: DesignToken) => {
      const response = await fetch(`/api/v1/projects/design-tokens/${token.id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(token),
      });
      if (!response.ok) throw new Error('Failed to update token');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['design-tokens', selectedLibrary] });
      setEditingToken(null);
      toast({ title: 'Token Updated', description: 'Design token has been updated.' });
    },
  });

  // Delete token mutation
  const deleteTokenMutation = useMutation({
    mutationFn: async (tokenId: number) => {
      const response = await fetch(`/api/v1/projects/design-tokens/${tokenId}/`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete token');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['design-tokens', selectedLibrary] });
      toast({ title: 'Token Deleted', description: 'Design token has been deleted.' });
    },
  });

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: async (format: string) => {
      const response = await fetch(
        `/api/v1/projects/design-token-libraries/${selectedLibrary}/export/?format=${format}&download=true`
      );
      if (!response.ok) throw new Error('Failed to export');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tokens.${format}`;
      a.click();
    },
    onSuccess: () => {
      toast({ title: 'Exported', description: 'Tokens exported successfully.' });
    },
  });

  // Filter tokens
  const filteredTokens = libraryData?.tokens?.filter((token: DesignToken) => {
    const matchesSearch = token.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      token.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || token.token_type === filterType;
    return matchesSearch && matchesType;
  }) || [];

  // Group tokens by category
  const groupedTokens = filteredTokens.reduce((acc: Record<string, DesignToken[]>, token: DesignToken) => {
    const category = token.category || 'Uncategorized';
    if (!acc[category]) acc[category] = [];
    acc[category].push(token);
    return acc;
  }, {});

  const renderTokenValue = (token: DesignToken) => {
    if (token.token_type === 'color') {
      return (
        <div className="flex items-center gap-2">
          <div
            className="w-6 h-6 rounded border"
            style={{ backgroundColor: token.resolved_value }}
          />
          <span className="font-mono text-sm">{token.value}</span>
        </div>
      );
    }
    return <span className="font-mono text-sm">{token.value}</span>;
  };

  return (
    <div className="flex h-full">
      {/* Library Sidebar */}
      <div className="w-64 border-r bg-muted/30">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Token Libraries
            </h3>
            <Button size="icon" variant="ghost" className="h-6 w-6">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        <ScrollArea className="h-[calc(100vh-200px)]">
          <div className="p-2 space-y-1">
            {libraries?.libraries?.map((library: TokenLibrary) => (
              <button
                key={library.id}
                onClick={() => setSelectedLibrary(library.id)}
                className={`w-full p-2 rounded-lg text-left transition-colors ${
                  selectedLibrary === library.id
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium truncate">{library.name}</span>
                  {library.is_default && (
                    <Badge variant="secondary" className="text-xs">Default</Badge>
                  )}
                </div>
                <div className="flex items-center gap-2 text-xs opacity-70 mt-1">
                  <span>{library.token_count} tokens</span>
                  <span>•</span>
                  <span>v{library.version}</span>
                </div>
              </button>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {selectedLibrary ? (
          <>
            {/* Toolbar */}
            <div className="p-4 border-b flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search tokens..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 w-64"
                  />
                </div>
                
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {TOKEN_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.icon} {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={selectedTheme} onValueChange={setSelectedTheme}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Theme" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">
                      <div className="flex items-center gap-2">
                        <Sun className="h-4 w-4" />
                        Default
                      </div>
                    </SelectItem>
                    {libraryData?.themes?.map((theme: Theme) => (
                      <SelectItem key={theme.slug} value={theme.slug}>
                        <div className="flex items-center gap-2">
                          {theme.theme_type === 'dark' ? (
                            <Moon className="h-4 w-4" />
                          ) : (
                            <Sun className="h-4 w-4" />
                          )}
                          {theme.name}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center gap-2">
                <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Token
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create Design Token</DialogTitle>
                      <DialogDescription>
                        Add a new token to your library
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium">Name</label>
                        <Input
                          value={newToken.name}
                          onChange={(e) => setNewToken({ ...newToken, name: e.target.value })}
                          placeholder="e.g., primary-500"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium">Category</label>
                        <Input
                          value={newToken.category}
                          onChange={(e) => setNewToken({ ...newToken, category: e.target.value })}
                          placeholder="e.g., colors"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium">Type</label>
                        <Select
                          value={newToken.token_type}
                          onValueChange={(value) => setNewToken({ ...newToken, token_type: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {TOKEN_TYPES.map((type) => (
                              <SelectItem key={type.value} value={type.value}>
                                {type.icon} {type.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Value</label>
                        <Input
                          value={newToken.value}
                          onChange={(e) => setNewToken({ ...newToken, value: e.target.value })}
                          placeholder={newToken.token_type === 'color' ? '#3B82F6' : '16px'}
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={() => createTokenMutation.mutate(newToken)}>
                        Create Token
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline">
                      <Download className="h-4 w-4 mr-2" />
                      Export
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    {EXPORT_FORMATS.map((format) => (
                      <DropdownMenuItem
                        key={format.value}
                        onClick={() => exportMutation.mutate(format.value)}
                      >
                        <Code className="h-4 w-4 mr-2" />
                        {format.label}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>

            {/* Token List */}
            <ScrollArea className="flex-1">
              <div className="p-4 space-y-6">
                {Object.entries(groupedTokens).map(([category, tokens]) => (
                  <div key={category}>
                    <h4 className="font-medium text-sm text-muted-foreground mb-2 flex items-center gap-2">
                      <Folder className="h-4 w-4" />
                      {category}
                      <Badge variant="secondary" className="text-xs">
                        {(tokens as DesignToken[]).length}
                      </Badge>
                    </h4>
                    <div className="space-y-2">
                      {(tokens as DesignToken[]).map((token) => (
                        <div
                          key={token.id}
                          className="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                        >
                          <div className="flex items-center gap-4">
                            {renderTokenValue(token)}
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-medium">{token.name}</span>
                                {token.deprecated && (
                                  <Badge variant="destructive" className="text-xs">
                                    Deprecated
                                  </Badge>
                                )}
                              </div>
                              <code className="text-xs text-muted-foreground">
                                {token.css_variable}
                              </code>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() => {
                                navigator.clipboard.writeText(token.css_variable);
                                toast({ title: 'Copied', description: 'CSS variable copied to clipboard' });
                              }}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent>
                                <DropdownMenuItem onClick={() => setEditingToken(token)}>
                                  <Edit2 className="h-4 w-4 mr-2" />
                                  Edit
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={() => {
                                    navigator.clipboard.writeText(token.value);
                                    toast({ title: 'Copied', description: 'Value copied' });
                                  }}
                                >
                                  <Copy className="h-4 w-4 mr-2" />
                                  Copy Value
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                  className="text-destructive"
                                  onClick={() => deleteTokenMutation.mutate(token.id)}
                                >
                                  <Trash2 className="h-4 w-4 mr-2" />
                                  Delete
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                {Object.keys(groupedTokens).length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    <Palette className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No tokens found</p>
                    <Button
                      variant="outline"
                      className="mt-4"
                      onClick={() => setIsCreateDialogOpen(true)}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Your First Token
                    </Button>
                  </div>
                )}
              </div>
            </ScrollArea>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <Palette className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Select a library to manage tokens</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DesignTokensEditor;
