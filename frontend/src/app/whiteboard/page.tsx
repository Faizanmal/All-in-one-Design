"use client";

import React, { useState, useRef } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Pencil,
  MousePointer2,
  Hand,
  Square,
  Circle,
  Type,
  Image as ImageIcon,
  Minus,
  ArrowRight,
  StickyNote,
  Eraser,
  Undo2,
  Redo2,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Download,
  Share2,
  Users,
  MoreVertical,
  Layers,
  Lock,
  Unlock,
  Grid3X3,
  Sparkles,
  MessageSquare,
  Video,
  Highlighter,
  Move,
  RotateCcw,
  Trash2,
  Copy,
  Scissors,
  ClipboardPaste,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface WhiteboardTool {
  id: string;
  name: string;
  icon: React.ElementType;
  shortcut?: string;
}

interface User {
  id: number;
  name: string;
  avatar?: string;
  color: string;
  cursor?: { x: number; y: number };
}

interface WhiteboardElement {
  id: string;
  type: 'shape' | 'text' | 'sticky' | 'image' | 'drawing' | 'line' | 'arrow';
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  content?: string;
}

// Data
const tools: WhiteboardTool[] = [
  { id: 'select', name: 'Select', icon: MousePointer2, shortcut: 'V' },
  { id: 'pan', name: 'Pan', icon: Hand, shortcut: 'H' },
  { id: 'pen', name: 'Pen', icon: Pencil, shortcut: 'P' },
  { id: 'highlighter', name: 'Highlighter', icon: Highlighter, shortcut: 'M' },
  { id: 'eraser', name: 'Eraser', icon: Eraser, shortcut: 'E' },
  { id: 'line', name: 'Line', icon: Minus, shortcut: 'L' },
  { id: 'arrow', name: 'Arrow', icon: ArrowRight, shortcut: 'A' },
  { id: 'rectangle', name: 'Rectangle', icon: Square, shortcut: 'R' },
  { id: 'ellipse', name: 'Ellipse', icon: Circle, shortcut: 'O' },
  { id: 'text', name: 'Text', icon: Type, shortcut: 'T' },
  { id: 'sticky', name: 'Sticky Note', icon: StickyNote, shortcut: 'S' },
  { id: 'image', name: 'Image', icon: ImageIcon, shortcut: 'I' },
];

const colors = [
  '#1F2937', '#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#FFFFFF',
];

const collaborators: User[] = [
  { id: 1, name: 'John Doe', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=john', color: '#3B82F6', cursor: { x: 450, y: 280 } },
  { id: 2, name: 'Jane Smith', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=jane', color: '#10B981', cursor: { x: 720, y: 420 } },
  { id: 3, name: 'Mike Wilson', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=mike', color: '#F59E0B', cursor: { x: 280, y: 550 } },
];

const mockElements: WhiteboardElement[] = [
  { id: 'e1', type: 'sticky', x: 100, y: 150, width: 200, height: 200, color: '#FEF3C7', content: 'User Research\n\n• Interviews\n• Surveys\n• Analytics' },
  { id: 'e2', type: 'sticky', x: 350, y: 150, width: 200, height: 200, color: '#DBEAFE', content: 'Design Sprint\n\n• Wireframes\n• Prototypes\n• Testing' },
  { id: 'e3', type: 'sticky', x: 600, y: 150, width: 200, height: 200, color: '#D1FAE5', content: 'Development\n\n• Frontend\n• Backend\n• Testing' },
  { id: 'e4', type: 'shape', x: 200, y: 450, width: 150, height: 80, color: '#3B82F6', content: 'Start' },
  { id: 'e5', type: 'shape', x: 450, y: 450, width: 150, height: 80, color: '#8B5CF6', content: 'Process' },
  { id: 'e6', type: 'shape', x: 700, y: 450, width: 150, height: 80, color: '#10B981', content: 'End' },
];

export default function WhiteboardPage() {
  const { toast } = useToast();
  const canvasRef = useRef<HTMLDivElement>(null);
  const [activeTool, setActiveTool] = useState('select');
  const [activeColor, setActiveColor] = useState('#1F2937');
  const [strokeWidth, setStrokeWidth] = useState([3]);
  const [zoom, setZoom] = useState(100);
  const [showGrid, setShowGrid] = useState(true);
  const [elements] = useState<WhiteboardElement[]>(mockElements);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [isLocked, setIsLocked] = useState(false);

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 10, 200));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 10, 25));
  const handleResetZoom = () => setZoom(100);

  const handleExport = () => {
    toast({ title: 'Exporting...', description: 'Preparing whiteboard for download' });
  };

  const handleShare = () => {
    toast({ title: 'Share Link Copied', description: 'Anyone with the link can view this whiteboard' });
  };

  return (
    <TooltipProvider>
      <div className="flex h-screen bg-gray-100">
        <DashboardSidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <MainHeader />
          
          <main className="flex-1 flex flex-col overflow-hidden">
            {/* Toolbar */}
            <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                {/* Primary Tools */}
                <div className="flex items-center bg-gray-100 rounded-lg p-1">
                  {tools.slice(0, 5).map(tool => (
                    <Tooltip key={tool.id}>
                      <TooltipTrigger asChild>
                        <Button variant={activeTool === tool.id ? 'secondary' : 'ghost'} size="sm" className="h-8 w-8 p-0" onClick={() => setActiveTool(tool.id)}>
                          <tool.icon className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent><p>{tool.name} ({tool.shortcut})</p></TooltipContent>
                    </Tooltip>
                  ))}
                </div>

                <div className="w-px h-6 bg-gray-300" />

                {/* Shapes & Lines */}
                <div className="flex items-center bg-gray-100 rounded-lg p-1">
                  {tools.slice(5, 9).map(tool => (
                    <Tooltip key={tool.id}>
                      <TooltipTrigger asChild>
                        <Button variant={activeTool === tool.id ? 'secondary' : 'ghost'} size="sm" className="h-8 w-8 p-0" onClick={() => setActiveTool(tool.id)}>
                          <tool.icon className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent><p>{tool.name} ({tool.shortcut})</p></TooltipContent>
                    </Tooltip>
                  ))}
                </div>

                <div className="w-px h-6 bg-gray-300" />

                {/* Content Tools */}
                <div className="flex items-center bg-gray-100 rounded-lg p-1">
                  {tools.slice(9).map(tool => (
                    <Tooltip key={tool.id}>
                      <TooltipTrigger asChild>
                        <Button variant={activeTool === tool.id ? 'secondary' : 'ghost'} size="sm" className="h-8 w-8 p-0" onClick={() => setActiveTool(tool.id)}>
                          <tool.icon className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent><p>{tool.name} ({tool.shortcut})</p></TooltipContent>
                    </Tooltip>
                  ))}
                </div>

                <div className="w-px h-6 bg-gray-300" />

                {/* Color Picker */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-8 px-2">
                      <div className="w-5 h-5 rounded border-2 border-gray-300" style={{ backgroundColor: activeColor }} />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <div className="grid grid-cols-4 gap-1 p-2">
                      {colors.map(color => (
                        <button key={color} onClick={() => setActiveColor(color)}
                          className={`w-6 h-6 rounded border-2 ${activeColor === color ? 'border-blue-500' : 'border-gray-200'}`}
                          style={{ backgroundColor: color }} />
                      ))}
                    </div>
                  </DropdownMenuContent>
                </DropdownMenu>

                {/* Stroke Width */}
                <div className="flex items-center gap-2 px-2">
                  <span className="text-xs text-gray-500">Stroke</span>
                  <Slider value={strokeWidth} onValueChange={setStrokeWidth} min={1} max={20} step={1} className="w-20" />
                  <span className="text-xs text-gray-700 w-4">{strokeWidth[0]}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* Undo/Redo */}
                <div className="flex items-center">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Undo2 className="h-4 w-4" /></Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Redo2 className="h-4 w-4" /></Button>
                </div>

                <div className="w-px h-6 bg-gray-300" />

                {/* Toggle Grid */}
                <Button variant={showGrid ? 'secondary' : 'ghost'} size="sm" className="h-8 w-8 p-0" onClick={() => setShowGrid(!showGrid)}>
                  <Grid3X3 className="h-4 w-4" />
                </Button>

                {/* Lock */}
                <Button variant={isLocked ? 'secondary' : 'ghost'} size="sm" className="h-8 w-8 p-0" onClick={() => setIsLocked(!isLocked)}>
                  {isLocked ? <Lock className="h-4 w-4" /> : <Unlock className="h-4 w-4" />}
                </Button>

                <div className="w-px h-6 bg-gray-300" />

                {/* Collaborators */}
                <div className="flex items-center -space-x-2">
                  {collaborators.map(user => (
                    <Tooltip key={user.id}>
                      <TooltipTrigger>
                        <Avatar className="h-7 w-7 border-2 border-white" style={{ borderColor: user.color }}>
                          <AvatarImage src={user.avatar} />
                          <AvatarFallback className="text-xs">{user.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                        </Avatar>
                      </TooltipTrigger>
                      <TooltipContent><p>{user.name}</p></TooltipContent>
                    </Tooltip>
                  ))}
                </div>
                <Badge variant="secondary" className="text-xs"><Users className="h-3 w-3 mr-1" />{collaborators.length} online</Badge>

                <div className="w-px h-6 bg-gray-300" />

                {/* Actions */}
                <Button variant="outline" size="sm" onClick={handleShare}><Share2 className="h-4 w-4 mr-1" />Share</Button>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild><Button variant="ghost" size="sm" className="h-8 w-8 p-0"><MoreVertical className="h-4 w-4" /></Button></DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={handleExport}><Download className="h-4 w-4 mr-2" />Export</DropdownMenuItem>
                    <DropdownMenuItem><Video className="h-4 w-4 mr-2" />Start Video Call</DropdownMenuItem>
                    <DropdownMenuItem><MessageSquare className="h-4 w-4 mr-2" />Open Chat</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem><Layers className="h-4 w-4 mr-2" />Layers Panel</DropdownMenuItem>
                    <DropdownMenuItem><Sparkles className="h-4 w-4 mr-2" />AI Assist</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>

            {/* Canvas */}
            <div className="flex-1 relative overflow-hidden bg-gray-200" ref={canvasRef}>
              {/* Grid Background */}
              {showGrid && (
                <div className="absolute inset-0 pointer-events-none" style={{
                  backgroundImage: 'radial-gradient(circle, #00000010 1px, transparent 1px)',
                  backgroundSize: `${20 * zoom / 100}px ${20 * zoom / 100}px`,
                }} />
              )}

              {/* Canvas Content */}
              <div className="absolute inset-0" style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'center' }}>
                {/* Elements */}
                {elements.map(el => (
                  <div key={el.id} onClick={() => setSelectedElement(el.id)}
                    className={`absolute cursor-pointer transition-shadow ${selectedElement === el.id ? 'ring-2 ring-blue-500 ring-offset-2' : ''}`}
                    style={{ left: el.x, top: el.y, width: el.width, height: el.height }}>
                    {el.type === 'sticky' && (
                      <div className="w-full h-full p-3 shadow-lg" style={{ backgroundColor: el.color }}>
                        <p className="text-sm font-medium whitespace-pre-wrap">{el.content}</p>
                      </div>
                    )}
                    {el.type === 'shape' && (
                      <div className="w-full h-full rounded-lg flex items-center justify-center text-white font-medium" style={{ backgroundColor: el.color }}>
                        {el.content}
                      </div>
                    )}
                  </div>
                ))}

                {/* Collaborator Cursors */}
                {collaborators.map(user => user.cursor && (
                  <div key={user.id} className="absolute pointer-events-none transition-all duration-100" style={{ left: user.cursor.x, top: user.cursor.y }}>
                    <svg width="24" height="36" viewBox="0 0 24 36" fill="none">
                      <path d="M5.65376 12.4563L0.161133 0.0693359L19.8394 11.8568L5.65376 12.4563Z" fill={user.color} />
                    </svg>
                    <div className="px-2 py-0.5 rounded text-xs text-white mt-1 whitespace-nowrap" style={{ backgroundColor: user.color }}>
                      {user.name.split(' ')[0]}
                    </div>
                  </div>
                ))}
              </div>

              {/* Zoom Controls */}
              <div className="absolute bottom-4 left-4 flex items-center gap-2 bg-white rounded-lg shadow-lg p-2">
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={handleZoomOut}><ZoomOut className="h-4 w-4" /></Button>
                <button onClick={handleResetZoom} className="text-sm font-medium w-12 text-center hover:bg-gray-100 rounded px-1 py-0.5">
                  {zoom}%
                </button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={handleZoomIn}><ZoomIn className="h-4 w-4" /></Button>
                <div className="w-px h-4 bg-gray-200" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Maximize2 className="h-4 w-4" /></Button>
              </div>

              {/* Context Menu (Selection Tools) */}
              {selectedElement && (
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-1 bg-white rounded-lg shadow-lg p-2">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Move className="h-4 w-4" /></Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><RotateCcw className="h-4 w-4" /></Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Copy className="h-4 w-4" /></Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Scissors className="h-4 w-4" /></Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><ClipboardPaste className="h-4 w-4" /></Button>
                  <div className="w-px h-4 bg-gray-200" />
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-red-500"><Trash2 className="h-4 w-4" /></Button>
                </div>
              )}

              {/* Mini Map */}
              <div className="absolute bottom-4 right-4 w-40 h-28 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
                <div className="absolute inset-0 p-2">
                  <div className="w-full h-full bg-gray-100 rounded relative">
                    {elements.map(el => (
                      <div key={el.id} className="absolute rounded" style={{
                        left: `${(el.x / 1000) * 100}%`,
                        top: `${(el.y / 700) * 100}%`,
                        width: `${(el.width / 1000) * 100}%`,
                        height: `${(el.height / 700) * 100}%`,
                        backgroundColor: el.type === 'sticky' ? el.color : el.color,
                        opacity: 0.7,
                      }} />
                    ))}
                    <div className="absolute border-2 border-blue-500 rounded" style={{
                      left: '20%', top: '15%', width: '50%', height: '60%', opacity: 0.5
                    }} />
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </TooltipProvider>
  );
}
