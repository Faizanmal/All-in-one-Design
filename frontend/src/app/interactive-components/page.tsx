"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

import {
  Package,
  Plus,
  Search,
  Play,
  MousePointer2,
  Pointer,
  ArrowRight,
  MoveHorizontal,
  Sparkles,
  Settings2,
  Zap,
  Trash2,
  Timer,
  Smartphone,
  Monitor,
  Tablet,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';

// Types
interface Interaction {
  id: number;
  trigger: string;
  triggerIcon: React.ElementType;
  action: string;
  target: string;
  animation: string;
  duration: number;
}

interface InteractiveComponent {
  id: number;
  name: string;
  type: string;
  screen: string;
  interactions: Interaction[];
  preview: string;
}

// Mock Data
const triggers = [
  { id: 'click', name: 'On Click', icon: MousePointer2 },
  { id: 'hover', name: 'On Hover', icon: Pointer },
  { id: 'drag', name: 'On Drag', icon: MoveHorizontal },
  { id: 'keypress', name: 'On Keypress', icon: Package },
  { id: 'timer', name: 'After Delay', icon: Timer },
];

const actions = ['Navigate To', 'Open Overlay', 'Close Overlay', 'Swap With', 'Change Property', 'Play Animation', 'Open URL'];
const animations = ['Instant', 'Dissolve', 'Smart Animate', 'Move In', 'Move Out', 'Push', 'Slide In', 'Slide Out'];

const mockComponents: InteractiveComponent[] = [
  {
    id: 1, name: 'Primary Button', type: 'Button', screen: 'Home Screen',
    preview: 'bg-blue-600',
    interactions: [
      { id: 1, trigger: 'On Click', triggerIcon: MousePointer2, action: 'Navigate To', target: 'Dashboard', animation: 'Smart Animate', duration: 300 },
      { id: 2, trigger: 'On Hover', triggerIcon: Pointer, action: 'Change Property', target: 'Self', animation: 'Dissolve', duration: 150 },
    ],
  },
  {
    id: 2, name: 'Navigation Menu', type: 'Nav', screen: 'All Screens',
    preview: 'bg-gray-800',
    interactions: [
      { id: 1, trigger: 'On Click', triggerIcon: MousePointer2, action: 'Navigate To', target: 'Selected Page', animation: 'Push', duration: 300 },
    ],
  },
  {
    id: 3, name: 'Modal Dialog', type: 'Overlay', screen: 'Settings',
    preview: 'bg-white border-2',
    interactions: [
      { id: 1, trigger: 'On Click', triggerIcon: MousePointer2, action: 'Close Overlay', target: 'Self', animation: 'Dissolve', duration: 200 },
    ],
  },
  {
    id: 4, name: 'Card Hover', type: 'Card', screen: 'Products',
    preview: 'bg-white border shadow-sm',
    interactions: [
      { id: 1, trigger: 'On Hover', triggerIcon: Pointer, action: 'Change Property', target: 'Shadow', animation: 'Smart Animate', duration: 200 },
      { id: 2, trigger: 'On Click', triggerIcon: MousePointer2, action: 'Navigate To', target: 'Product Details', animation: 'Slide In', duration: 300 },
    ],
  },
  {
    id: 5, name: 'Dropdown Menu', type: 'Dropdown', screen: 'Header',
    preview: 'bg-white border',
    interactions: [
      { id: 1, trigger: 'On Click', triggerIcon: MousePointer2, action: 'Open Overlay', target: 'Menu Items', animation: 'Move In', duration: 200 },
    ],
  },
];

// Interaction Row Component
function InteractionRow({ interaction, onEdit, onDelete }: { interaction: Interaction; onEdit: () => void; onDelete: () => void }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg group">
      <div className="p-2 bg-blue-100 rounded-lg">
        <interaction.triggerIcon className="h-4 w-4 text-blue-600" />
      </div>
      <div className="flex-1 flex items-center gap-2">
        <span className="text-sm font-medium text-gray-700">{interaction.trigger}</span>
        <ArrowRight className="h-4 w-4 text-gray-400" />
        <span className="text-sm text-gray-600">{interaction.action}</span>
        <ArrowRight className="h-4 w-4 text-gray-400" />
        <span className="text-sm text-blue-600 font-medium">{interaction.target}</span>
      </div>
      <Badge variant="outline" className="text-xs">{interaction.animation}</Badge>
      <span className="text-xs text-gray-500">{interaction.duration}ms</span>
      <div className="opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity">
        <Button size="sm" variant="ghost" onClick={onEdit}><Settings2 className="h-3 w-3" /></Button>
        <Button size="sm" variant="ghost" className="text-red-600" onClick={onDelete}><Trash2 className="h-3 w-3" /></Button>
      </div>
    </div>
  );
}

// Component Card
function InteractiveComponentCard({ component, onSelect, isSelected }: { component: InteractiveComponent; onSelect: () => void; isSelected: boolean }) {
  return (
    <Card className={`cursor-pointer transition-all ${isSelected ? 'ring-2 ring-blue-500' : 'hover:shadow-md'}`} onClick={onSelect}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${component.preview}`}>
            <Package className="h-5 w-5 text-white" />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">{component.name}</h4>
            <p className="text-sm text-gray-500">{component.screen}</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline" className="text-xs">{component.type}</Badge>
              <span className="text-xs text-gray-400">{component.interactions.length} interactions</span>
            </div>
          </div>
          <Zap className="h-4 w-4 text-amber-500" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function InteractiveComponentsPage() {
  const { toast } = useToast();
  const [components] = useState<InteractiveComponent[]>(mockComponents);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedComponent, setSelectedComponent] = useState<InteractiveComponent | null>(mockComponents[0]);
  const [showAddInteraction, setShowAddInteraction] = useState(false);
  const [previewDevice, setPreviewDevice] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [isPlaying, setIsPlaying] = useState(false);

  const filteredComponents = components.filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()));

  const handleAddInteraction = () => {
    setShowAddInteraction(false);
    toast({ title: 'Interaction Added', description: 'New interaction has been added to the component' });
  };

  const handlePreview = () => {
    setIsPlaying(true);
    toast({ title: 'Preview Mode', description: 'Interactions are now active' });
    setTimeout(() => setIsPlaying(false), 5000);
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
                  <Package className="h-7 w-7 text-blue-600" />Interactive Components
                </h1>
                <p className="text-gray-500">Build clickable, interactive prototypes</p>
              </div>
              <div className="flex gap-3">
                <div className="flex border rounded-lg overflow-hidden bg-white">
                  <Button size="sm" variant={previewDevice === 'desktop' ? 'default' : 'ghost'} className="rounded-none" onClick={() => setPreviewDevice('desktop')}>
                    <Monitor className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant={previewDevice === 'tablet' ? 'default' : 'ghost'} className="rounded-none" onClick={() => setPreviewDevice('tablet')}>
                    <Tablet className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant={previewDevice === 'mobile' ? 'default' : 'ghost'} className="rounded-none" onClick={() => setPreviewDevice('mobile')}>
                    <Smartphone className="h-4 w-4" />
                  </Button>
                </div>
                <Button variant="outline" onClick={handlePreview}>
                  <Play className={`h-4 w-4 mr-2 ${isPlaying ? 'text-green-600' : ''}`} />Preview
                </Button>
                <Button><Plus className="h-4 w-4 mr-2" />Add Component</Button>
              </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 grid grid-cols-12 gap-6 overflow-hidden">
              {/* Component List */}
              <div className="col-span-4 flex flex-col overflow-hidden">
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input placeholder="Search components..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-10" />
                </div>
                <ScrollArea className="flex-1">
                  <div className="space-y-3 pr-4">
                    {filteredComponents.map(component => (
                      <InteractiveComponentCard key={component.id} component={component} onSelect={() => setSelectedComponent(component)} isSelected={selectedComponent?.id === component.id} />
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* Preview & Interaction Editor */}
              <div className="col-span-8 flex flex-col overflow-hidden bg-white rounded-xl border border-gray-200">
                {selectedComponent ? (
                  <>
                    {/* Preview Area */}
                    <div className="flex-1 bg-gray-100 flex items-center justify-center p-8 relative">
                      <div className={`bg-white rounded-lg shadow-xl overflow-hidden ${
                        previewDevice === 'desktop' ? 'w-full max-w-4xl h-full' :
                        previewDevice === 'tablet' ? 'w-[768px] h-[1024px] scale-50 origin-center' :
                        'w-[375px] h-[812px] scale-75 origin-center'
                      }`}>
                        <div className="bg-gray-200 h-8 flex items-center px-3 gap-2">
                          <div className="flex gap-1.5">
                            <div className="w-3 h-3 rounded-full bg-red-400" />
                            <div className="w-3 h-3 rounded-full bg-yellow-400" />
                            <div className="w-3 h-3 rounded-full bg-green-400" />
                          </div>
                        </div>
                        <div className="p-8 flex items-center justify-center h-64">
                          <div className={`px-8 py-4 rounded-lg ${selectedComponent.preview} ${isPlaying ? 'animate-pulse' : ''}`}>
                            <span className="text-white font-medium">{selectedComponent.name}</span>
                          </div>
                        </div>
                      </div>
                      {isPlaying && (
                        <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm flex items-center gap-2">
                          <span className="w-2 h-2 bg-white rounded-full animate-ping" />Preview Active
                        </div>
                      )}
                    </div>

                    {/* Interactions Panel */}
                    <div className="border-t border-gray-200 p-4">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                          <Zap className="h-4 w-4 text-amber-500" />Interactions
                        </h3>
                        <Button size="sm" onClick={() => setShowAddInteraction(true)}><Plus className="h-4 w-4 mr-1" />Add Interaction</Button>
                      </div>
                      <div className="space-y-2">
                        {selectedComponent.interactions.map(interaction => (
                          <InteractionRow key={interaction.id} interaction={interaction} onEdit={() => {}} onDelete={() => { toast({ title: 'Interaction Deleted' }); }} />
                        ))}
                        {selectedComponent.interactions.length === 0 && (
                          <div className="text-center py-8 text-gray-500">
                            <Sparkles className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                            <p>No interactions yet</p>
                            <Button size="sm" variant="link" onClick={() => setShowAddInteraction(true)}>Add your first interaction</Button>
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-gray-500">
                    <div className="text-center">
                      <Package className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>Select a component to view and edit interactions</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Add Interaction Dialog */}
      <Dialog open={showAddInteraction} onOpenChange={setShowAddInteraction}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add Interaction</DialogTitle>
            <DialogDescription>Define how users interact with this component</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Trigger</Label>
              <Select defaultValue="click">
                <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {triggers.map(t => (
                    <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Action</Label>
              <Select defaultValue="Navigate To">
                <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {actions.map(a => (
                    <SelectItem key={a} value={a}>{a}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Target</Label>
              <Input placeholder="Select target screen or element" className="mt-1" />
            </div>
            <div>
              <Label>Animation</Label>
              <Select defaultValue="Smart Animate">
                <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {animations.map(a => (
                    <SelectItem key={a} value={a}>{a}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Duration (ms)</Label>
              <div className="flex items-center gap-3 mt-1">
                <Slider defaultValue={[300]} max={1000} min={0} step={50} className="flex-1" />
                <span className="text-sm font-medium w-12">300ms</span>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddInteraction(false)}>Cancel</Button>
            <Button onClick={handleAddInteraction}>Add Interaction</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
