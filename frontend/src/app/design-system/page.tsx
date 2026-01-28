"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import {
  Palette, Type, Box, Layers, FileText, Code, Download, RefreshCw,
  Plus, Trash2, Copy, Edit, Eye, Search, Grid, List,
  ChevronRight, ExternalLink, Settings, BookOpen, Component, Paintbrush
} from 'lucide-react';

// Types
interface DesignToken {
  id: string;
  name: string;
  category: string;
  value: string | Record<string, unknown>;
  description?: string;
}

interface ComponentDef {
  id: string;
  name: string;
  category: string;
  status: 'draft' | 'review' | 'approved' | 'deprecated';
  variants: string[];
  description?: string;
}

interface DesignSystem {
  id: string;
  name: string;
  version: string;
  tokens: DesignToken[];
  components: ComponentDef[];
}

const TOKEN_CATEGORIES = [
  { id: 'colors', name: 'Colors', icon: Palette },
  { id: 'typography', name: 'Typography', icon: Type },
  { id: 'spacing', name: 'Spacing', icon: Box },
  { id: 'shadows', name: 'Shadows', icon: Layers },
  { id: 'borders', name: 'Borders', icon: Box },
  { id: 'breakpoints', name: 'Breakpoints', icon: Grid },
];

const COMPONENT_CATEGORIES = [
  'Buttons', 'Forms', 'Navigation', 'Cards', 'Modals', 'Tables', 'Lists', 'Feedback'
];

const DEFAULT_COLORS: DesignToken[] = [
  { id: '1', name: 'primary-50', category: 'colors', value: '#eef2ff', description: 'Lightest primary' },
  { id: '2', name: 'primary-100', category: 'colors', value: '#e0e7ff', description: 'Very light primary' },
  { id: '3', name: 'primary-500', category: 'colors', value: '#6366f1', description: 'Main primary color' },
  { id: '4', name: 'primary-600', category: 'colors', value: '#4f46e5', description: 'Primary hover' },
  { id: '5', name: 'primary-900', category: 'colors', value: '#312e81', description: 'Darkest primary' },
  { id: '6', name: 'gray-50', category: 'colors', value: '#f9fafb', description: 'Background light' },
  { id: '7', name: 'gray-100', category: 'colors', value: '#f3f4f6', description: 'Background' },
  { id: '8', name: 'gray-500', category: 'colors', value: '#6b7280', description: 'Text muted' },
  { id: '9', name: 'gray-900', category: 'colors', value: '#111827', description: 'Text primary' },
  { id: '10', name: 'success', category: 'colors', value: '#10b981', description: 'Success state' },
  { id: '11', name: 'warning', category: 'colors', value: '#f59e0b', description: 'Warning state' },
  { id: '12', name: 'error', category: 'colors', value: '#ef4444', description: 'Error state' },
];

const DEFAULT_SPACING: DesignToken[] = [
  { id: 's1', name: 'spacing-1', category: 'spacing', value: '4px' },
  { id: 's2', name: 'spacing-2', category: 'spacing', value: '8px' },
  { id: 's3', name: 'spacing-3', category: 'spacing', value: '12px' },
  { id: 's4', name: 'spacing-4', category: 'spacing', value: '16px' },
  { id: 's5', name: 'spacing-6', category: 'spacing', value: '24px' },
  { id: 's6', name: 'spacing-8', category: 'spacing', value: '32px' },
  { id: 's7', name: 'spacing-12', category: 'spacing', value: '48px' },
  { id: 's8', name: 'spacing-16', category: 'spacing', value: '64px' },
];

const DEFAULT_TYPOGRAPHY: DesignToken[] = [
  { id: 't1', name: 'font-family-sans', category: 'typography', value: 'Inter, system-ui, sans-serif' },
  { id: 't2', name: 'font-family-mono', category: 'typography', value: 'JetBrains Mono, monospace' },
  { id: 't3', name: 'font-size-xs', category: 'typography', value: '12px' },
  { id: 't4', name: 'font-size-sm', category: 'typography', value: '14px' },
  { id: 't5', name: 'font-size-base', category: 'typography', value: '16px' },
  { id: 't6', name: 'font-size-lg', category: 'typography', value: '18px' },
  { id: 't7', name: 'font-size-xl', category: 'typography', value: '20px' },
  { id: 't8', name: 'font-size-2xl', category: 'typography', value: '24px' },
  { id: 't9', name: 'font-size-3xl', category: 'typography', value: '30px' },
];

const DEFAULT_COMPONENTS: ComponentDef[] = [
  { id: 'c1', name: 'Button', category: 'Buttons', status: 'approved', variants: ['Primary', 'Secondary', 'Ghost', 'Destructive'], description: 'Interactive button component' },
  { id: 'c2', name: 'Input', category: 'Forms', status: 'approved', variants: ['Default', 'With Icon', 'With Error'], description: 'Text input field' },
  { id: 'c3', name: 'Card', category: 'Cards', status: 'approved', variants: ['Default', 'Interactive', 'With Image'], description: 'Content container' },
  { id: 'c4', name: 'Modal', category: 'Modals', status: 'review', variants: ['Default', 'Confirmation', 'Form'], description: 'Dialog overlay' },
  { id: 'c5', name: 'Navigation', category: 'Navigation', status: 'draft', variants: ['Horizontal', 'Vertical', 'Mobile'], description: 'Navigation menu' },
];

export default function DesignSystemPage() {
  const { toast } = useToast();
  const [activeCategory, setActiveCategory] = useState('colors');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddTokenDialog, setShowAddTokenDialog] = useState(false);
  const [showAddComponentDialog, setShowAddComponentDialog] = useState(false);

  const [designSystem, setDesignSystem] = useState<DesignSystem>({
    id: '1',
    name: 'My Design System',
    version: '1.0.0',
    tokens: [...DEFAULT_COLORS, ...DEFAULT_SPACING, ...DEFAULT_TYPOGRAPHY],
    components: DEFAULT_COMPONENTS,
  });

  const [newToken, setNewToken] = useState<Partial<DesignToken>>({
    name: '',
    category: 'colors',
    value: '#000000',
    description: '',
  });

  const [newComponent, setNewComponent] = useState<Partial<ComponentDef>>({
    name: '',
    category: 'Buttons',
    status: 'draft',
    variants: [],
    description: '',
  });

  const filteredTokens = designSystem.tokens.filter(token => {
    const matchesCategory = token.category === activeCategory;
    const matchesSearch = searchQuery === '' || 
      token.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (token.description?.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const addToken = () => {
    if (!newToken.name) {
      toast({ title: 'Error', description: 'Token name is required', variant: 'destructive' });
      return;
    }

    const token: DesignToken = {
      id: Date.now().toString(),
      name: newToken.name,
      category: newToken.category || 'colors',
      value: newToken.value || '',
      description: newToken.description,
    };

    setDesignSystem(prev => ({
      ...prev,
      tokens: [...prev.tokens, token]
    }));

    setNewToken({ name: '', category: activeCategory, value: '#000000', description: '' });
    setShowAddTokenDialog(false);
    toast({ title: 'Token added successfully' });
  };

  const deleteToken = (id: string) => {
    setDesignSystem(prev => ({
      ...prev,
      tokens: prev.tokens.filter(t => t.id !== id)
    }));
    toast({ title: 'Token deleted' });
  };

  const addComponent = () => {
    if (!newComponent.name) {
      toast({ title: 'Error', description: 'Component name is required', variant: 'destructive' });
      return;
    }

    const component: ComponentDef = {
      id: Date.now().toString(),
      name: newComponent.name,
      category: newComponent.category || 'Buttons',
      status: 'draft',
      variants: newComponent.variants || [],
      description: newComponent.description,
    };

    setDesignSystem(prev => ({
      ...prev,
      components: [...prev.components, component]
    }));

    setNewComponent({ name: '', category: 'Buttons', status: 'draft', variants: [], description: '' });
    setShowAddComponentDialog(false);
    toast({ title: 'Component added successfully' });
  };

  const exportTokensCSS = () => {
    let css = ':root {\n';
    designSystem.tokens.forEach(token => {
      const value = typeof token.value === 'string' ? token.value : JSON.stringify(token.value);
      css += `  --${token.name}: ${value};\n`;
    });
    css += '}';
    
    navigator.clipboard.writeText(css);
    toast({ title: 'CSS Variables copied to clipboard!' });
  };

  const exportTokensJSON = () => {
    const grouped: Record<string, Record<string, unknown>> = {};
    designSystem.tokens.forEach(token => {
      if (!grouped[token.category]) grouped[token.category] = {};
      grouped[token.category][token.name] = token.value;
    });
    
    navigator.clipboard.writeText(JSON.stringify(grouped, null, 2));
    toast({ title: 'JSON tokens copied to clipboard!' });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <Paintbrush className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">{designSystem.name}</h1>
                <p className="text-sm text-muted-foreground">Version {designSystem.version}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Sync with Figma
              </Button>
              <Select defaultValue="css" onValueChange={(v) => v === 'css' ? exportTokensCSS() : exportTokensJSON()}>
                <SelectTrigger className="w-[140px]">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="css">CSS Variables</SelectItem>
                  <SelectItem value="scss">SCSS Variables</SelectItem>
                  <SelectItem value="json">JSON Tokens</SelectItem>
                  <SelectItem value="js">JavaScript</SelectItem>
                  <SelectItem value="pdf">PDF Style Guide</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-6">
        <Tabs defaultValue="tokens" className="space-y-6">
          <TabsList className="grid w-full max-w-lg grid-cols-4">
            <TabsTrigger value="tokens" className="flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Tokens
            </TabsTrigger>
            <TabsTrigger value="components" className="flex items-center gap-2">
              <Component className="h-4 w-4" />
              Components
            </TabsTrigger>
            <TabsTrigger value="documentation" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Docs
            </TabsTrigger>
            <TabsTrigger value="styleguide" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Style Guide
            </TabsTrigger>
          </TabsList>

          {/* Tokens Tab */}
          <TabsContent value="tokens" className="space-y-6">
            <div className="flex gap-6">
              {/* Sidebar - Token Categories */}
              <div className="w-64 space-y-2">
                <Card>
                  <CardHeader className="py-3">
                    <CardTitle className="text-sm">Categories</CardTitle>
                  </CardHeader>
                  <CardContent className="p-2">
                    {TOKEN_CATEGORIES.map(category => {
                      const Icon = category.icon;
                      const count = designSystem.tokens.filter(t => t.category === category.id).length;
                      return (
                        <button
                          key={category.id}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors ${
                            activeCategory === category.id ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
                          }`}
                          onClick={() => setActiveCategory(category.id)}
                        >
                          <div className="flex items-center gap-2">
                            <Icon className="h-4 w-4" />
                            <span className="text-sm">{category.name}</span>
                          </div>
                          <Badge variant={activeCategory === category.id ? 'secondary' : 'outline'} className="text-xs">
                            {count}
                          </Badge>
                        </button>
                      );
                    })}
                  </CardContent>
                </Card>
              </div>

              {/* Main Content - Tokens */}
              <div className="flex-1 space-y-4">
                {/* Toolbar */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search tokens..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9 w-64"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="flex items-center border rounded-lg">
                      <Button
                        variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
                        size="icon"
                        className="h-8 w-8"
                        onClick={() => setViewMode('grid')}
                      >
                        <Grid className="h-4 w-4" />
                      </Button>
                      <Button
                        variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                        size="icon"
                        className="h-8 w-8"
                        onClick={() => setViewMode('list')}
                      >
                        <List className="h-4 w-4" />
                      </Button>
                    </div>

                    <Dialog open={showAddTokenDialog} onOpenChange={setShowAddTokenDialog}>
                      <DialogTrigger asChild>
                        <Button>
                          <Plus className="h-4 w-4 mr-2" />
                          Add Token
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Add New Token</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4 py-4">
                          <div className="space-y-2">
                            <Label>Token Name</Label>
                            <Input
                              placeholder="e.g., primary-500"
                              value={newToken.name}
                              onChange={(e) => setNewToken({ ...newToken, name: e.target.value })}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Category</Label>
                            <Select 
                              value={newToken.category} 
                              onValueChange={(v) => setNewToken({ ...newToken, category: v })}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {TOKEN_CATEGORIES.map(cat => (
                                  <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label>Value</Label>
                            {newToken.category === 'colors' ? (
                              <div className="flex gap-2">
                                <input
                                  type="color"
                                  value={typeof newToken.value === 'string' ? newToken.value : '#000000'}
                                  onChange={(e) => setNewToken({ ...newToken, value: e.target.value })}
                                  className="h-10 w-20 rounded cursor-pointer"
                                />
                                <Input
                                  value={typeof newToken.value === 'string' ? newToken.value : ''}
                                  onChange={(e) => setNewToken({ ...newToken, value: e.target.value })}
                                />
                              </div>
                            ) : (
                              <Input
                                placeholder="e.g., 16px"
                                value={typeof newToken.value === 'string' ? newToken.value : ''}
                                onChange={(e) => setNewToken({ ...newToken, value: e.target.value })}
                              />
                            )}
                          </div>
                          <div className="space-y-2">
                            <Label>Description</Label>
                            <Textarea
                              placeholder="Describe when to use this token..."
                              value={newToken.description}
                              onChange={(e) => setNewToken({ ...newToken, description: e.target.value })}
                            />
                          </div>
                        </div>
                        <DialogFooter>
                          <Button variant="outline" onClick={() => setShowAddTokenDialog(false)}>Cancel</Button>
                          <Button onClick={addToken}>Add Token</Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>

                {/* Token Grid/List */}
                {viewMode === 'grid' ? (
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {filteredTokens.map(token => (
                      <Card key={token.id} className="group relative overflow-hidden">
                        {token.category === 'colors' && (
                          <div 
                            className="h-24 w-full"
                            style={{ backgroundColor: typeof token.value === 'string' ? token.value : '#ccc' }}
                          />
                        )}
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-mono text-sm font-medium">{token.name}</p>
                              <p className="text-xs text-muted-foreground mt-1">
                                {typeof token.value === 'string' ? token.value : JSON.stringify(token.value)}
                              </p>
                              {token.description && (
                                <p className="text-xs text-muted-foreground mt-2">{token.description}</p>
                              )}
                            </div>
                            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Button variant="ghost" size="icon" className="h-6 w-6">
                                <Copy className="h-3 w-3" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-6 w-6 text-destructive"
                                onClick={() => deleteToken(token.id)}
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Card>
                    <div className="divide-y">
                      {filteredTokens.map(token => (
                        <div key={token.id} className="flex items-center justify-between p-4 hover:bg-muted/50">
                          <div className="flex items-center gap-4">
                            {token.category === 'colors' && (
                              <div 
                                className="h-10 w-10 rounded-lg border"
                                style={{ backgroundColor: typeof token.value === 'string' ? token.value : '#ccc' }}
                              />
                            )}
                            <div>
                              <p className="font-mono text-sm font-medium">{token.name}</p>
                              <p className="text-xs text-muted-foreground">{token.description}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <code className="text-sm bg-muted px-2 py-1 rounded">
                              {typeof token.value === 'string' ? token.value : JSON.stringify(token.value)}
                            </code>
                            <div className="flex gap-1">
                              <Button variant="ghost" size="icon" className="h-8 w-8">
                                <Copy className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="icon" className="h-8 w-8">
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-8 w-8 text-destructive"
                                onClick={() => deleteToken(token.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Components Tab */}
          <TabsContent value="components" className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Input placeholder="Search components..." className="w-64" />
                <Select defaultValue="all">
                  <SelectTrigger className="w-[140px]">
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {COMPONENT_CATEGORIES.map(cat => (
                      <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select defaultValue="all">
                  <SelectTrigger className="w-[120px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="review">In Review</SelectItem>
                    <SelectItem value="approved">Approved</SelectItem>
                    <SelectItem value="deprecated">Deprecated</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Dialog open={showAddComponentDialog} onOpenChange={setShowAddComponentDialog}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Component
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add New Component</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label>Component Name</Label>
                      <Input
                        placeholder="e.g., Button"
                        value={newComponent.name}
                        onChange={(e) => setNewComponent({ ...newComponent, name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Category</Label>
                      <Select 
                        value={newComponent.category} 
                        onValueChange={(v) => setNewComponent({ ...newComponent, category: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {COMPONENT_CATEGORIES.map(cat => (
                            <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Description</Label>
                      <Textarea
                        placeholder="Describe the component..."
                        value={newComponent.description}
                        onChange={(e) => setNewComponent({ ...newComponent, description: e.target.value })}
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setShowAddComponentDialog(false)}>Cancel</Button>
                    <Button onClick={addComponent}>Add Component</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {designSystem.components.map(component => (
                <Card key={component.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-lg">{component.name}</CardTitle>
                        <CardDescription>{component.category}</CardDescription>
                      </div>
                      <Badge variant={
                        component.status === 'approved' ? 'default' :
                        component.status === 'review' ? 'secondary' :
                        component.status === 'deprecated' ? 'destructive' : 'outline'
                      }>
                        {component.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {component.description && (
                      <p className="text-sm text-muted-foreground mb-4">{component.description}</p>
                    )}
                    <div className="flex flex-wrap gap-1 mb-4">
                      {component.variants.map(variant => (
                        <Badge key={variant} variant="outline" className="text-xs">
                          {variant}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Eye className="h-4 w-4 mr-2" />
                        Preview
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1">
                        <Code className="h-4 w-4 mr-2" />
                        Code
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Documentation Tab */}
          <TabsContent value="documentation" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <Card className="lg:col-span-1">
                <CardHeader>
                  <CardTitle className="text-sm">Documentation</CardTitle>
                </CardHeader>
                <CardContent className="p-2">
                  <div className="space-y-1">
                    {['Getting Started', 'Installation', 'Tokens', 'Components', 'Patterns', 'Accessibility', 'Changelog'].map(item => (
                      <button
                        key={item}
                        className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-left hover:bg-muted text-sm"
                      >
                        <span>{item}</span>
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="lg:col-span-3">
                <CardHeader>
                  <CardTitle>Getting Started</CardTitle>
                  <CardDescription>Learn how to use this design system in your projects</CardDescription>
                </CardHeader>
                <CardContent className="prose prose-sm dark:prose-invert max-w-none">
                  <h3>Installation</h3>
                  <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
{`npm install @your-org/design-system

# or with yarn
yarn add @your-org/design-system`}
                  </pre>
                  
                  <h3>Usage</h3>
                  <p>Import the CSS variables in your main stylesheet:</p>
                  <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
{`@import '@your-org/design-system/tokens.css';`}
                  </pre>
                  
                  <h3>Components</h3>
                  <p>Import and use components in your React application:</p>
                  <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
{`import { Button, Card, Input } from '@your-org/design-system';

function MyComponent() {
  return (
    <Card>
      <Input placeholder="Enter text..." />
      <Button variant="primary">Submit</Button>
    </Card>
  );
}`}
                  </pre>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Style Guide Tab */}
          <TabsContent value="styleguide" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Brand Overview</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="aspect-video bg-gradient-to-br from-primary to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-4xl font-bold text-white">Logo</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Our brand represents innovation, simplicity, and accessibility. 
                    The primary color palette reflects trust and professionalism.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Color Palette</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-5 gap-2">
                    {DEFAULT_COLORS.filter(c => c.name.includes('primary')).map(color => (
                      <div key={color.id} className="text-center">
                        <div 
                          className="aspect-square rounded-lg mb-2"
                          style={{ backgroundColor: typeof color.value === 'string' ? color.value : '#ccc' }}
                        />
                        <p className="text-xs font-mono">{color.name.split('-')[1]}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Typography</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-4xl font-bold">Heading 1</p>
                    <p className="text-xs text-muted-foreground">font-size-3xl / font-weight-bold</p>
                  </div>
                  <div>
                    <p className="text-2xl font-semibold">Heading 2</p>
                    <p className="text-xs text-muted-foreground">font-size-2xl / font-weight-semibold</p>
                  </div>
                  <div>
                    <p className="text-xl font-medium">Heading 3</p>
                    <p className="text-xs text-muted-foreground">font-size-xl / font-weight-medium</p>
                  </div>
                  <div>
                    <p className="text-base">Body Text</p>
                    <p className="text-xs text-muted-foreground">font-size-base / font-weight-normal</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Small Text</p>
                    <p className="text-xs text-muted-foreground">font-size-sm / text-muted</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Spacing Scale</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {DEFAULT_SPACING.map(space => (
                      <div key={space.id} className="flex items-center gap-4">
                        <div className="w-20 text-xs font-mono">{space.name}</div>
                        <div 
                          className="h-4 bg-primary rounded"
                          style={{ width: typeof space.value === 'string' ? space.value : '0' }}
                        />
                        <div className="text-xs text-muted-foreground">
                          {typeof space.value === 'string' ? space.value : ''}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Export Style Guide</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4">
                  <Button variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Export as PDF
                  </Button>
                  <Button variant="outline">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Generate Website
                  </Button>
                  <Button variant="outline">
                    <Code className="h-4 w-4 mr-2" />
                    Export to Storybook
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
