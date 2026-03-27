"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Pen,
  Move,
  Square,
  Circle,
  Triangle,
  Star,
  Minus,
  Type,
  MousePointer,
  Scissors,
  RotateCcw,
  RotateCw,
  FlipHorizontal,
  FlipVertical,
  Copy,
  Trash2,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  Layers,
  ZoomIn,
  ZoomOut,
  Maximize,
  Grid,
  Magnet,
  Save,
  Download,
  Plus,
  GripVertical,
  Pipette,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface VectorLayer {
  id: number;
  name: string;
  type: 'path' | 'shape' | 'text' | 'group';
  visible: boolean;
  locked: boolean;
  selected: boolean;
}

// Mock Data
const mockLayers: VectorLayer[] = [
  { id: 1, name: 'Logo Shape', type: 'path', visible: true, locked: false, selected: true },
  { id: 2, name: 'Background Circle', type: 'shape', visible: true, locked: false, selected: false },
  { id: 3, name: 'Icon Path', type: 'path', visible: true, locked: true, selected: false },
  { id: 4, name: 'Text Label', type: 'text', visible: true, locked: false, selected: false },
  { id: 5, name: 'Decorative Elements', type: 'group', visible: false, locked: false, selected: false },
];

const tools = [
  { id: 'select', icon: MousePointer, label: 'Select', shortcut: 'V' },
  { id: 'move', icon: Move, label: 'Move', shortcut: 'M' },
  { id: 'pen', icon: Pen, label: 'Pen', shortcut: 'P' },
  { id: 'line', icon: Minus, label: 'Line', shortcut: 'L' },
  { id: 'rectangle', icon: Square, label: 'Rectangle', shortcut: 'R' },
  { id: 'ellipse', icon: Circle, label: 'Ellipse', shortcut: 'E' },
  { id: 'triangle', icon: Triangle, label: 'Triangle', shortcut: 'T' },
  { id: 'star', icon: Star, label: 'Star', shortcut: 'S' },
  { id: 'text', icon: Type, label: 'Text', shortcut: 'X' },
  { id: 'scissors', icon: Scissors, label: 'Scissors', shortcut: 'C' },
  { id: 'eyedropper', icon: Pipette, label: 'Eyedropper', shortcut: 'I' },
];

const presetColors = ['#000000', '#FFFFFF', '#FF5733', '#33A1FF', '#28A745', '#FFC107', '#6F42C1', '#E83E8C'];

export default function VectorEditingPage() {
  const { toast } = useToast();
  const [activeTool, setActiveTool] = useState('select');
  const [layers, setLayers] = useState<VectorLayer[]>(mockLayers);
  const [zoom, setZoom] = useState(100);
  const [showGrid, setShowGrid] = useState(true);
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [fillColor, setFillColor] = useState('#3B82F6');
  const [strokeColor, setStrokeColor] = useState('#1F2937');
  const [strokeWidth, setStrokeWidth] = useState([2]);
  const [opacity, setOpacity] = useState([100]);

  const toggleLayerVisibility = (id: number) => {
    setLayers(layers.map(l => l.id === id ? { ...l, visible: !l.visible } : l));
  };

  const toggleLayerLock = (id: number) => {
    setLayers(layers.map(l => l.id === id ? { ...l, locked: !l.locked } : l));
  };

  const selectLayer = (id: number) => {
    setLayers(layers.map(l => ({ ...l, selected: l.id === id })));
  };

  const handleSave = () => {
    toast({ title: 'Saved', description: 'Vector file saved successfully' });
  };

  const handleExport = () => {
    toast({ title: 'Export', description: 'Exporting as SVG...' });
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <div className="flex-1 flex overflow-hidden">
          {/* Left Toolbar */}
          <div className="w-14 bg-gray-900 flex flex-col items-center py-3 gap-1">
            {tools.map(tool => (
              <button key={tool.id} onClick={() => setActiveTool(tool.id)} title={`${tool.label} (${tool.shortcut})`}
                className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors ${
                  activeTool === tool.id ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}>
                <tool.icon className="h-5 w-5" />
              </button>
            ))}
            <Separator className="my-2 w-8 bg-gray-700" />
            <button onClick={() => setShowGrid(!showGrid)} title="Toggle Grid (G)"
              className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors ${showGrid ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}>
              <Grid className="h-5 w-5" />
            </button>
            <button onClick={() => setSnapToGrid(!snapToGrid)} title="Snap to Grid"
              className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors ${snapToGrid ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}>
              <Magnet className="h-5 w-5" />
            </button>
          </div>

          {/* Canvas Area */}
          <div className="flex-1 flex flex-col overflow-hidden bg-gray-200">
            {/* Top Bar */}
            <div className="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-4">
              <div className="flex items-center gap-2">
                <Button size="sm" variant="ghost"><RotateCcw className="h-4 w-4" /></Button>
                <Button size="sm" variant="ghost"><RotateCw className="h-4 w-4" /></Button>
                <Separator orientation="vertical" className="h-6" />
                <Button size="sm" variant="ghost"><FlipHorizontal className="h-4 w-4" /></Button>
                <Button size="sm" variant="ghost"><FlipVertical className="h-4 w-4" /></Button>
                <Separator orientation="vertical" className="h-6" />
                <Button size="sm" variant="ghost"><Copy className="h-4 w-4" /></Button>
                <Button size="sm" variant="ghost"><Trash2 className="h-4 w-4" /></Button>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Button size="sm" variant="ghost" onClick={() => setZoom(Math.max(25, zoom - 25))}><ZoomOut className="h-4 w-4" /></Button>
                  <span className="text-sm font-medium w-14 text-center">{zoom}%</span>
                  <Button size="sm" variant="ghost" onClick={() => setZoom(Math.min(400, zoom + 25))}><ZoomIn className="h-4 w-4" /></Button>
                  <Button size="sm" variant="ghost" onClick={() => setZoom(100)}><Maximize className="h-4 w-4" /></Button>
                </div>
                <Separator orientation="vertical" className="h-6" />
                <Button size="sm" variant="outline" onClick={handleSave}><Save className="h-4 w-4 mr-2" />Save</Button>
                <Button size="sm" onClick={handleExport}><Download className="h-4 w-4 mr-2" />Export</Button>
              </div>
            </div>

            {/* Canvas */}
            <div className="flex-1 overflow-hidden flex items-center justify-center p-8" style={{ background: 'repeating-conic-gradient(#e5e7eb 0% 25%, #f3f4f6 0% 50%) 50% / 20px 20px' }}>
              <div className="bg-white shadow-2xl rounded-lg" style={{ width: `${800 * (zoom / 100)}px`, height: `${600 * (zoom / 100)}px`, transform: `scale(${zoom / 100})`, transformOrigin: 'center' }}>
                {showGrid && (
                  <svg className="w-full h-full opacity-20">
                    <defs>
                      <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#94a3b8" strokeWidth="0.5" />
                      </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                  </svg>
                )}
                {/* Demo shapes for visual */}
                <svg className="absolute inset-0 w-full h-full">
                  <circle cx="400" cy="300" r="120" fill="#3B82F6" fillOpacity="0.3" stroke="#3B82F6" strokeWidth="2" />
                  <rect x="280" y="180" width="240" height="240" fill="none" stroke="#10B981" strokeWidth="2" strokeDasharray="5,5" />
                </svg>
              </div>
            </div>
          </div>

          {/* Right Panel */}
          <div className="w-72 bg-white border-l border-gray-200 flex flex-col">
            <Tabs defaultValue="properties" className="flex-1 flex flex-col">
              <TabsList className="grid grid-cols-2 m-2">
                <TabsTrigger value="properties">Properties</TabsTrigger>
                <TabsTrigger value="layers">Layers</TabsTrigger>
              </TabsList>

              <TabsContent value="properties" className="flex-1 overflow-auto p-4 space-y-6 mt-0">
                {/* Fill */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Fill</h3>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-10 h-10 rounded-lg border-2 border-gray-200 cursor-pointer" style={{ backgroundColor: fillColor }} />
                    <input type="text" value={fillColor} onChange={(e) => setFillColor(e.target.value)} className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg" />
                  </div>
                  <div className="flex gap-1 flex-wrap">
                    {presetColors.map(color => (
                      <button key={color} onClick={() => setFillColor(color)} className="w-7 h-7 rounded-md border border-gray-200" style={{ backgroundColor: color }} />
                    ))}
                  </div>
                </div>

                {/* Stroke */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Stroke</h3>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-10 h-10 rounded-lg border-2 border-gray-200 cursor-pointer flex items-center justify-center" style={{ backgroundColor: 'transparent' }}>
                      <div className="w-full h-1 rounded-full" style={{ backgroundColor: strokeColor }} />
                    </div>
                    <input type="text" value={strokeColor} onChange={(e) => setStrokeColor(e.target.value)} className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg" />
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-500 w-16">Width</span>
                    <Slider value={strokeWidth} onValueChange={setStrokeWidth} max={20} min={0} step={0.5} className="flex-1" />
                    <span className="text-sm font-medium w-10">{strokeWidth[0]}px</span>
                  </div>
                </div>

                {/* Opacity */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Opacity</h3>
                  <div className="flex items-center gap-3">
                    <Slider value={opacity} onValueChange={setOpacity} max={100} min={0} step={1} className="flex-1" />
                    <span className="text-sm font-medium w-10">{opacity[0]}%</span>
                  </div>
                </div>

                {/* Transform */}
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Transform</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-xs text-gray-500">X</label>
                      <input type="number" defaultValue={280} className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">Y</label>
                      <input type="number" defaultValue={180} className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">W</label>
                      <input type="number" defaultValue={240} className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">H</label>
                      <input type="number" defaultValue={240} className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg" />
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="layers" className="flex-1 overflow-hidden flex flex-col mt-0">
                <div className="p-2 border-b border-gray-200 flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Layers</span>
                  <Button size="sm" variant="ghost"><Plus className="h-4 w-4" /></Button>
                </div>
                <ScrollArea className="flex-1">
                  <div className="p-2 space-y-1">
                    {layers.map(layer => (
                      <div key={layer.id} onClick={() => selectLayer(layer.id)}
                        className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                          layer.selected ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50 border border-transparent'
                        }`}>
                        <GripVertical className="h-4 w-4 text-gray-400 cursor-grab" />
                        <div className={`w-4 h-4 rounded flex items-center justify-center ${
                          layer.type === 'path' ? 'bg-purple-100' : layer.type === 'shape' ? 'bg-blue-100' : layer.type === 'text' ? 'bg-green-100' : 'bg-gray-100'
                        }`}>
                          {layer.type === 'path' && <Pen className="h-2.5 w-2.5 text-purple-600" />}
                          {layer.type === 'shape' && <Square className="h-2.5 w-2.5 text-blue-600" />}
                          {layer.type === 'text' && <Type className="h-2.5 w-2.5 text-green-600" />}
                          {layer.type === 'group' && <Layers className="h-2.5 w-2.5 text-gray-600" />}
                        </div>
                        <span className={`flex-1 text-sm truncate ${layer.visible ? 'text-gray-900' : 'text-gray-400'}`}>{layer.name}</span>
                        <button onClick={(e) => { e.stopPropagation(); toggleLayerLock(layer.id); }} className="p-1 hover:bg-gray-200 rounded">
                          {layer.locked ? <Lock className="h-3 w-3 text-gray-500" /> : <Unlock className="h-3 w-3 text-gray-300" />}
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); toggleLayerVisibility(layer.id); }} className="p-1 hover:bg-gray-200 rounded">
                          {layer.visible ? <Eye className="h-3 w-3 text-gray-500" /> : <EyeOff className="h-3 w-3 text-gray-300" />}
                        </button>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
}
