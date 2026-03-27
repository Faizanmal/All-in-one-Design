"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Layers,
  Plus,
  Search,
  Copy,
  Trash2,
  Edit2,
  MousePointer2,
  Hand,
  Ban,
  Check,
  AlertCircle,
  Loader2,
  Settings2,
  Grid3X3,
  LayoutGrid,
  Link2,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';

// Types
interface ComponentVariant {
  id: number;
  name: string;
  icon: React.ElementType;
  color: string;
  isDefault?: boolean;
}

interface DesignComponent {
  id: number;
  name: string;
  category: string;
  variants: ComponentVariant[];
  instances: number;
  lastModified: string;
}

// Mock Data
const mockComponents: DesignComponent[] = [
  {
    id: 1, name: 'Button', category: 'Inputs',
    variants: [
      { id: 1, name: 'Default', icon: MousePointer2, color: '#3B82F6', isDefault: true },
      { id: 2, name: 'Hover', icon: Hand, color: '#2563EB' },
      { id: 3, name: 'Pressed', icon: MousePointer2, color: '#1D4ED8' },
      { id: 4, name: 'Disabled', icon: Ban, color: '#9CA3AF' },
      { id: 5, name: 'Loading', icon: Loader2, color: '#3B82F6' },
    ],
    instances: 156, lastModified: '2 hours ago',
  },
  {
    id: 2, name: 'Input Field', category: 'Inputs',
    variants: [
      { id: 1, name: 'Empty', icon: MousePointer2, color: '#6B7280', isDefault: true },
      { id: 2, name: 'Focused', icon: Hand, color: '#3B82F6' },
      { id: 3, name: 'Filled', icon: Check, color: '#10B981' },
      { id: 4, name: 'Error', icon: AlertCircle, color: '#EF4444' },
      { id: 5, name: 'Disabled', icon: Ban, color: '#9CA3AF' },
    ],
    instances: 89, lastModified: '5 hours ago',
  },
  {
    id: 3, name: 'Card', category: 'Containers',
    variants: [
      { id: 1, name: 'Default', icon: MousePointer2, color: '#FFFFFF', isDefault: true },
      { id: 2, name: 'Hover', icon: Hand, color: '#F3F4F6' },
      { id: 3, name: 'Selected', icon: Check, color: '#EFF6FF' },
    ],
    instances: 67, lastModified: '1 day ago',
  },
  {
    id: 4, name: 'Checkbox', category: 'Inputs',
    variants: [
      { id: 1, name: 'Unchecked', icon: MousePointer2, color: '#E5E7EB', isDefault: true },
      { id: 2, name: 'Checked', icon: Check, color: '#3B82F6' },
      { id: 3, name: 'Indeterminate', icon: Loader2, color: '#3B82F6' },
      { id: 4, name: 'Disabled', icon: Ban, color: '#9CA3AF' },
    ],
    instances: 45, lastModified: '3 days ago',
  },
  {
    id: 5, name: 'Avatar', category: 'Display',
    variants: [
      { id: 1, name: 'Image', icon: MousePointer2, color: '#F3F4F6', isDefault: true },
      { id: 2, name: 'Initials', icon: MousePointer2, color: '#3B82F6' },
      { id: 3, name: 'Placeholder', icon: MousePointer2, color: '#E5E7EB' },
      { id: 4, name: 'Online', icon: Check, color: '#10B981' },
      { id: 5, name: 'Offline', icon: Ban, color: '#6B7280' },
    ],
    instances: 234, lastModified: '1 hour ago',
  },
];

const categories = ['All', 'Inputs', 'Containers', 'Display', 'Navigation', 'Feedback'];

// Variant Preview Component
function VariantPreview({ variant, isSelected, onClick }: { variant: ComponentVariant; isSelected: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick}
      className={`flex flex-col items-center p-3 rounded-lg border-2 transition-all ${
        isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300 bg-white'
      }`}>
      <div className="w-16 h-12 rounded-md mb-2 flex items-center justify-center" style={{ backgroundColor: variant.color + '20', border: `2px solid ${variant.color}` }}>
        <variant.icon className="h-5 w-5" style={{ color: variant.color }} />
      </div>
      <span className="text-xs font-medium text-gray-700">{variant.name}</span>
      {variant.isDefault && <Badge variant="outline" className="text-xs mt-1">Default</Badge>}
    </button>
  );
}

// Component Card
function ComponentCard({ component, onSelect }: { component: DesignComponent; onSelect: () => void }) {
  return (
    <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={onSelect}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base">{component.name}</CardTitle>
            <Badge variant="outline" className="mt-1">{component.category}</Badge>
          </div>
          <div className="flex gap-1">
            <Button size="sm" variant="ghost" onClick={(e) => e.stopPropagation()}><Copy className="h-4 w-4" /></Button>
            <Button size="sm" variant="ghost" onClick={(e) => e.stopPropagation()}><Edit2 className="h-4 w-4" /></Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2 mb-4">
          {component.variants.slice(0, 4).map(variant => (
            <div key={variant.id} className="w-8 h-8 rounded-md flex items-center justify-center" 
              style={{ backgroundColor: variant.color + '20', border: `1px solid ${variant.color}` }}>
              <variant.icon className="h-3 w-3" style={{ color: variant.color }} />
            </div>
          ))}
          {component.variants.length > 4 && (
            <div className="w-8 h-8 rounded-md flex items-center justify-center bg-gray-100 text-xs font-medium text-gray-500">
              +{component.variants.length - 4}
            </div>
          )}
        </div>
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>{component.variants.length} variants</span>
          <span>{component.instances} instances</span>
        </div>
      </CardContent>
    </Card>
  );
}

export default function ComponentVariantsPage() {
  const { toast } = useToast();
  const [components] = useState<DesignComponent[]>(mockComponents);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [selectedComponent, setSelectedComponent] = useState<DesignComponent | null>(null);
  const [selectedVariant, setSelectedVariant] = useState<ComponentVariant | null>(null);
  const [showNewVariantDialog, setShowNewVariantDialog] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const filteredComponents = components.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeCategory === 'All' || c.category === activeCategory;
    return matchesSearch && matchesCategory;
  });

  const handleCreateVariant = () => {
    setShowNewVariantDialog(false);
    toast({ title: 'Variant Created', description: 'New variant has been added to the component' });
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-hidden p-6">
          <div className="max-w-7xl mx-auto h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                  <Layers className="h-7 w-7 text-blue-600" />Component Variants
                </h1>
                <p className="text-gray-500">Manage component states and variations</p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline"><Link2 className="h-4 w-4 mr-2" />Link to Design System</Button>
                <Button><Plus className="h-4 w-4 mr-2" />New Component</Button>
              </div>
            </div>

            {/* Search and Filters */}
            <div className="flex items-center gap-4 mb-6">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input placeholder="Search components..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-10" />
              </div>
              <div className="flex gap-2">
                {categories.map(cat => (
                  <Button key={cat} variant={activeCategory === cat ? 'default' : 'outline'} size="sm" onClick={() => setActiveCategory(cat)}>
                    {cat}
                  </Button>
                ))}
              </div>
              <div className="flex border rounded-lg overflow-hidden">
                <Button size="sm" variant={viewMode === 'grid' ? 'default' : 'ghost'} className="rounded-none" onClick={() => setViewMode('grid')}>
                  <Grid3X3 className="h-4 w-4" />
                </Button>
                <Button size="sm" variant={viewMode === 'list' ? 'default' : 'ghost'} className="rounded-none" onClick={() => setViewMode('list')}>
                  <LayoutGrid className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex gap-6 overflow-hidden">
              {/* Component Grid */}
              <ScrollArea className="flex-1">
                <div className={`pr-4 ${viewMode === 'grid' ? 'grid grid-cols-3 gap-4' : 'space-y-3'}`}>
                  {filteredComponents.map(component => (
                    <ComponentCard key={component.id} component={component} onSelect={() => { setSelectedComponent(component); setSelectedVariant(component.variants[0]); }} />
                  ))}
                </div>
              </ScrollArea>

              {/* Component Detail Panel */}
              {selectedComponent && (
                <div className="w-96 bg-white rounded-xl border border-gray-200 flex flex-col overflow-hidden">
                  <div className="p-4 border-b border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-lg">{selectedComponent.name}</h3>
                      <Button size="sm" variant="ghost" onClick={() => setSelectedComponent(null)}>&times;</Button>
                    </div>
                    <Badge variant="outline">{selectedComponent.category}</Badge>
                    <p className="text-sm text-gray-500 mt-2">Modified {selectedComponent.lastModified}</p>
                  </div>

                  <div className="p-4 border-b border-gray-200">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-sm">Variants ({selectedComponent.variants.length})</h4>
                      <Button size="sm" variant="outline" onClick={() => setShowNewVariantDialog(true)}><Plus className="h-3 w-3 mr-1" />Add</Button>
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      {selectedComponent.variants.map(variant => (
                        <VariantPreview key={variant.id} variant={variant} isSelected={selectedVariant?.id === variant.id} onClick={() => setSelectedVariant(variant)} />
                      ))}
                    </div>
                  </div>

                  {selectedVariant && (
                    <div className="flex-1 p-4 overflow-auto">
                      <h4 className="font-medium text-sm mb-3">Variant Properties</h4>
                      <div className="space-y-3">
                        <div>
                          <Label className="text-xs text-gray-500">Name</Label>
                          <Input defaultValue={selectedVariant.name} className="mt-1" />
                        </div>
                        <div>
                          <Label className="text-xs text-gray-500">Color</Label>
                          <div className="flex items-center gap-2 mt-1">
                            <div className="w-8 h-8 rounded-md border" style={{ backgroundColor: selectedVariant.color }} />
                            <Input defaultValue={selectedVariant.color} className="flex-1" />
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <Label className="text-sm">Set as default</Label>
                          <input type="checkbox" checked={selectedVariant.isDefault} onChange={() => {}} className="h-4 w-4" />
                        </div>
                      </div>

                      <div className="mt-6">
                        <h4 className="font-medium text-sm mb-3">Preview</h4>
                        <div className="bg-gray-50 rounded-lg p-6 flex items-center justify-center">
                          <div className="px-6 py-3 rounded-lg text-white font-medium" style={{ backgroundColor: selectedVariant.color }}>
                            {selectedComponent.name}
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 flex gap-2">
                        <Button className="flex-1"><Settings2 className="h-4 w-4 mr-2" />Edit in Editor</Button>
                        <Button variant="outline"><Copy className="h-4 w-4" /></Button>
                        <Button variant="outline" className="text-red-600 hover:text-red-700"><Trash2 className="h-4 w-4" /></Button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>

      {/* New Variant Dialog */}
      <Dialog open={showNewVariantDialog} onOpenChange={setShowNewVariantDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Variant</DialogTitle>
            <DialogDescription>Add a new variant to {selectedComponent?.name}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Variant Name</Label>
              <Input placeholder="e.g., Hover, Active, Disabled" className="mt-1" />
            </div>
            <div>
              <Label>Base Color</Label>
              <Input type="color" defaultValue="#3B82F6" className="mt-1 h-10" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewVariantDialog(false)}>Cancel</Button>
            <Button onClick={handleCreateVariant}>Create Variant</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
