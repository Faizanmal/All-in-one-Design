'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  PenTool,
  Circle,
  Square,
  Triangle,
  Minus,
  Plus,
  RotateCcw,
  RotateCw,
  Move,
  Scissors,
  Layers,
  Trash2,
  Copy,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  ChevronUp,
  ChevronDown,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface Point {
  x: number;
  y: number;
  handleIn?: { x: number; y: number };
  handleOut?: { x: number; y: number };
  cornerRadius?: number;
}

interface VectorPath {
  id: string;
  name: string;
  points: Point[];
  closed: boolean;
  stroke: string;
  strokeWidth: number;
  fill: string;
  visible: boolean;
  locked: boolean;
}

interface VectorEditorProps {
  width?: number;
  height?: number;
  onPathChange?: (paths: VectorPath[]) => void;
}

type Tool = 'pen' | 'select' | 'move' | 'rectangle' | 'ellipse' | 'polygon' | 'line';
type BooleanOp = 'union' | 'subtract' | 'intersect' | 'exclude';

interface DragState {
  startX: number;
  startY: number;
  currentX: number;
  currentY: number;
}

export function VectorEditor({ width = 800, height = 600, onPathChange }: VectorEditorProps) {
  const [paths, setPaths] = useState<VectorPath[]>([]);
  const [activeTool, setActiveTool] = useState<Tool>('pen');
  const [selectedPaths, setSelectedPaths] = useState<string[]>([]);
  const [currentPath, setCurrentPath] = useState<VectorPath | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [dragState, setDragState] = useState<DragState | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const [strokeColor, setStrokeColor] = useState('#000000');
  const [fillColor, setFillColor] = useState('#3b82f6');
  const [strokeWidth, setStrokeWidth] = useState(2);
  const [cornerRadius, setCornerRadius] = useState(0);
  const [fillEnabled, setFillEnabled] = useState(false);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);

  const historyRef = useRef<VectorPath[][]>([[]]);
  const historyIndexRef = useRef<number>(0);
  const canvasRef = useRef<SVGSVGElement>(null);

  const pushHistory = useCallback((newPaths: VectorPath[]) => {
    historyRef.current = historyRef.current.slice(0, historyIndexRef.current + 1);
    historyRef.current.push(JSON.parse(JSON.stringify(newPaths)));
    historyIndexRef.current = historyRef.current.length - 1;
    setCanUndo(historyIndexRef.current > 0);
    setCanRedo(false);
  }, []);

  const undo = useCallback(() => {
    if (historyIndexRef.current <= 0) return;
    historyIndexRef.current -= 1;
    const restored: VectorPath[] = JSON.parse(JSON.stringify(historyRef.current[historyIndexRef.current]));
    setPaths(restored);
    setCurrentPath(null);
    setIsDrawing(false);
    onPathChange?.(restored);
    setCanUndo(historyIndexRef.current > 0);
    setCanRedo(historyIndexRef.current < historyRef.current.length - 1);
  }, [onPathChange]);

  const redo = useCallback(() => {
    if (historyIndexRef.current >= historyRef.current.length - 1) return;
    historyIndexRef.current += 1;
    const restored: VectorPath[] = JSON.parse(JSON.stringify(historyRef.current[historyIndexRef.current]));
    setPaths(restored);
    onPathChange?.(restored);
    setCanUndo(historyIndexRef.current > 0);
    setCanRedo(historyIndexRef.current < historyRef.current.length - 1);
  }, [onPathChange]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement).tagName;
      if (tag === 'INPUT') return;
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) { e.preventDefault(); undo(); }
      if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) { e.preventDefault(); redo(); }
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedPaths.length > 0) {
          setPaths(prev => {
            const next = prev.filter(p => !selectedPaths.includes(p.id));
            pushHistory(next);
            onPathChange?.(next);
            return next;
          });
          setSelectedPaths([]);
        }
      }
      if (e.key === 'Escape') { setCurrentPath(null); setIsDrawing(false); }
      if (e.key === 'p') setActiveTool('pen');
      if (e.key === 'v') setActiveTool('select');
      if (e.key === 'r') setActiveTool('rectangle');
      if (e.key === 'o') setActiveTool('ellipse');
      if (e.key === 'l') setActiveTool('line');
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [undo, redo, selectedPaths, pushHistory, onPathChange]);

  const getPos = (e: React.MouseEvent<SVGSVGElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return { x: 0, y: 0 };
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };

  const tools: { id: Tool; icon: React.ElementType; label: string; shortcut: string }[] = [
    { id: 'pen', icon: PenTool, label: 'Pen Tool', shortcut: 'P' },
    { id: 'select', icon: Move, label: 'Select', shortcut: 'V' },
    { id: 'rectangle', icon: Square, label: 'Rectangle', shortcut: 'R' },
    { id: 'ellipse', icon: Circle, label: 'Ellipse', shortcut: 'O' },
    { id: 'polygon', icon: Triangle, label: 'Polygon', shortcut: '' },
    { id: 'line', icon: Minus, label: 'Line', shortcut: 'L' },
  ];

  const booleanOperations: { op: BooleanOp; label: string; icon: React.ElementType }[] = [
    { op: 'union', label: 'Union', icon: Plus },
    { op: 'subtract', label: 'Subtract', icon: Minus },
    { op: 'intersect', label: 'Intersect', icon: Layers },
    { op: 'exclude', label: 'Exclude', icon: Scissors },
  ];

  const handleMouseDown = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (activeTool === 'pen' || activeTool === 'select') return;
    const { x, y } = getPos(e);
    setDragState({ startX: x, startY: y, currentX: x, currentY: y });
  }, [activeTool]);

  const handleMouseMove = useCallback((_e: React.MouseEvent<SVGSVGElement>) => {
    const { x, y } = getPos(_e);
    setMousePos({ x: Math.round(x), y: Math.round(y) });
    if (dragState) setDragState(prev => prev ? { ...prev, currentX: x, currentY: y } : null);
  }, [dragState]);

  const handleMouseUp = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (!dragState) return;
    const { startX, startY, currentX, currentY } = dragState;
    if (Math.abs(currentX - startX) < 2 && Math.abs(currentY - startY) < 2) { setDragState(null); return; }

    const id = `path_${Date.now()}`;
    const baseName = activeTool.charAt(0).toUpperCase() + activeTool.slice(1);
    const name = `${baseName} ${paths.length + 1}`;
    const base = { id, name, closed: true, stroke: strokeColor, strokeWidth, fill: fillEnabled ? fillColor : 'none', visible: true, locked: false };
    let newPath: VectorPath | null = null;

    if (activeTool === 'rectangle') {
      const [x1, y1] = [Math.min(startX, currentX), Math.min(startY, currentY)];
      const [x2, y2] = [Math.max(startX, currentX), Math.max(startY, currentY)];
      newPath = { ...base, points: [{ x: x1, y: y1 }, { x: x2, y: y1 }, { x: x2, y: y2 }, { x: x1, y: y2 }] };
    } else if (activeTool === 'ellipse') {
      const cx = (startX + currentX) / 2, cy = (startY + currentY) / 2;
      const rx = Math.abs(currentX - startX) / 2, ry = Math.abs(currentY - startY) / 2;
      const k = 0.5523;
      newPath = { ...base, points: [
        { x: cx, y: cy - ry, handleOut: { x: cx + rx * k, y: cy - ry }, handleIn: { x: cx - rx * k, y: cy - ry } },
        { x: cx + rx, y: cy, handleOut: { x: cx + rx, y: cy + ry * k }, handleIn: { x: cx + rx, y: cy - ry * k } },
        { x: cx, y: cy + ry, handleOut: { x: cx - rx * k, y: cy + ry }, handleIn: { x: cx + rx * k, y: cy + ry } },
        { x: cx - rx, y: cy, handleOut: { x: cx - rx, y: cy - ry * k }, handleIn: { x: cx - rx, y: cy + ry * k } },
      ]};
    } else if (activeTool === 'line') {
      newPath = { ...base, closed: false, points: [{ x: startX, y: startY }, { x: currentX, y: currentY }] };
    }

    if (newPath) {
      const next = [...paths, newPath];
      setPaths(next); pushHistory(next); setSelectedPaths([newPath.id]); onPathChange?.(next);
    }
    setDragState(null);
  }, [dragState, activeTool, paths, strokeColor, strokeWidth, fillColor, fillEnabled, pushHistory, onPathChange]);

  const handleCanvasClick = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (activeTool !== 'pen') return;
    const { x, y } = getPos(e);
    if (!currentPath) {
      setCurrentPath({ id: `path_${Date.now()}`, name: `Path ${paths.length + 1}`, points: [{ x, y }], closed: false, stroke: strokeColor, strokeWidth, fill: fillEnabled ? fillColor : 'none', visible: true, locked: false });
      setIsDrawing(true);
    } else {
      const fp = currentPath.points[0];
      const dist = Math.sqrt((x - fp.x) ** 2 + (y - fp.y) ** 2);
      if (dist < 10 && currentPath.points.length > 2) {
        const closed = { ...currentPath, closed: true };
        const next = [...paths, closed];
        setPaths(next); pushHistory(next); setCurrentPath(null); setIsDrawing(false); onPathChange?.(next);
      } else {
        setCurrentPath({ ...currentPath, points: [...currentPath.points, { x, y }] });
      }
    }
  }, [activeTool, currentPath, paths, strokeColor, strokeWidth, fillColor, fillEnabled, pushHistory, onPathChange]);

  const handleDoubleClick = useCallback(() => {
    if (currentPath && currentPath.points.length > 1) {
      const next = [...paths, currentPath];
      setPaths(next); pushHistory(next); setCurrentPath(null); setIsDrawing(false); onPathChange?.(next);
    }
  }, [currentPath, paths, pushHistory, onPathChange]);

  const handleBooleanOperation = useCallback((op: BooleanOp) => {
    if (selectedPaths.length < 2) return;
    console.log(`Boolean ${op} on:`, selectedPaths);
  }, [selectedPaths]);

  const pathToSvg = (path: VectorPath): string => {
    if (!path.points.length) return '';
    let d = `M ${path.points[0].x} ${path.points[0].y}`;
    for (let i = 1; i < path.points.length; i++) {
      const pt = path.points[i], prev = path.points[i - 1];
      if (pt.handleIn && prev.handleOut) d += ` C ${prev.handleOut.x} ${prev.handleOut.y} ${pt.handleIn.x} ${pt.handleIn.y} ${pt.x} ${pt.y}`;
      else d += ` L ${pt.x} ${pt.y}`;
    }
    if (path.closed) d += ' Z';
    return d;
  };

  const renderDragPreview = () => {
    if (!dragState) return null;
    const { startX, startY, currentX, currentY } = dragState;
    const style: React.SVGProps<SVGRectElement> = { fill: fillEnabled ? fillColor : 'none', stroke: strokeColor, strokeWidth, strokeDasharray: '5,3', opacity: 0.7 };
    if (activeTool === 'rectangle') return <rect x={Math.min(startX, currentX)} y={Math.min(startY, currentY)} width={Math.abs(currentX - startX)} height={Math.abs(currentY - startY)} {...(style as React.SVGProps<SVGRectElement>)} />;
    if (activeTool === 'ellipse') return <ellipse cx={(startX + currentX) / 2} cy={(startY + currentY) / 2} rx={Math.abs(currentX - startX) / 2} ry={Math.abs(currentY - startY) / 2} {...(style as React.SVGProps<SVGEllipseElement>)} />;
    if (activeTool === 'line') return <line x1={startX} y1={startY} x2={currentX} y2={currentY} stroke={strokeColor} strokeWidth={strokeWidth} strokeDasharray="5,3" />;
    return null;
  };

  const handlePathSelect = (pathId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (activeTool !== 'select') return;
    if (e.shiftKey) setSelectedPaths(prev => prev.includes(pathId) ? prev.filter(id => id !== pathId) : [...prev, pathId]);
    else setSelectedPaths([pathId]);
  };

  const toggleVisibility = (pathId: string) => setPaths(prev => prev.map(p => p.id === pathId ? { ...p, visible: !p.visible } : p));
  const toggleLock = (pathId: string) => setPaths(prev => prev.map(p => p.id === pathId ? { ...p, locked: !p.locked } : p));
  const deletePath = (pathId: string) => {
    setPaths(prev => { const next = prev.filter(p => p.id !== pathId); pushHistory(next); onPathChange?.(next); return next; });
    setSelectedPaths(prev => prev.filter(id => id !== pathId));
  };
  const duplicatePath = (pathId: string) => {
    const found = paths.find(p => p.id === pathId);
    if (!found) return;
    const cloned: VectorPath = { ...JSON.parse(JSON.stringify(found)), id: `path_${Date.now()}`, name: found.name + ' Copy' };
    cloned.points = cloned.points.map((pt: Point) => ({ ...pt, x: pt.x + 10, y: pt.y + 10 }));
    const next = [...paths, cloned];
    setPaths(next); pushHistory(next); onPathChange?.(next);
  };
  const movePath = (pathId: string, dir: 'up' | 'down') => {
    const idx = paths.findIndex(p => p.id === pathId);
    if (idx < 0) return;
    const next = [...paths];
    const swapIdx = dir === 'up' ? idx - 1 : idx + 1;
    if (swapIdx < 0 || swapIdx >= next.length) return;
    [next[idx], next[swapIdx]] = [next[swapIdx], next[idx]];
    setPaths(next); pushHistory(next); onPathChange?.(next);
  };
  const applyStylesToSelected = () => {
    if (!selectedPaths.length) return;
    setPaths(prev => {
      const next = prev.map(p => selectedPaths.includes(p.id) ? { ...p, stroke: strokeColor, strokeWidth, fill: fillEnabled ? fillColor : 'none' } : p);
      pushHistory(next); onPathChange?.(next); return next;
    });
  };

  return (
    <TooltipProvider>
      <div className="flex flex-col h-full bg-background">
        {/* Toolbar */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-card border-b shadow-sm flex-wrap">
          {/* Tools */}
          <div className="flex items-center gap-0.5 border rounded-md p-0.5 bg-muted">
            {tools.map(tool => (
              <Tooltip key={tool.id}>
                <TooltipTrigger asChild>
                  <Button
                    size="icon" variant={activeTool === tool.id ? 'default' : 'ghost'} className="h-7 w-7"
                    onClick={() => { setActiveTool(tool.id); setCurrentPath(null); setIsDrawing(false); }}
                  >
                    <tool.icon className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  {tool.label}{tool.shortcut && <kbd className="ml-1.5 text-[10px] opacity-60">{tool.shortcut}</kbd>}
                </TooltipContent>
              </Tooltip>
            ))}
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* Boolean Operations */}
          <div className="flex items-center gap-0.5">
            {booleanOperations.map(({ op, label, icon: Icon }) => (
              <Tooltip key={op}>
                <TooltipTrigger asChild>
                  <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => handleBooleanOperation(op)} disabled={selectedPaths.length < 2}>
                    <Icon className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">{label} <span className="text-muted-foreground text-xs">(2+ paths)</span></TooltipContent>
              </Tooltip>
            ))}
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* Undo / Redo */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={undo} disabled={!canUndo}><RotateCcw className="w-4 h-4" /></Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Undo <kbd className="ml-1 text-[10px] opacity-60">Ctrl+Z</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={redo} disabled={!canRedo}><RotateCw className="w-4 h-4" /></Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Redo <kbd className="ml-1 text-[10px] opacity-60">Ctrl+Y</kbd></TooltipContent>
          </Tooltip>

          <Separator orientation="vertical" className="h-6" />

          {/* Stroke */}
          <div className="flex items-center gap-1.5">
            <Label className="text-xs text-muted-foreground">Stroke</Label>
            <div className="relative">
              <div className="w-6 h-6 rounded border-2 border-border shadow-sm cursor-pointer" style={{ backgroundColor: strokeColor }} />
              <input type="color" value={strokeColor} onChange={e => setStrokeColor(e.target.value)} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
            </div>
            <Input value={strokeColor} onChange={e => setStrokeColor(e.target.value)} className="h-7 w-20 text-xs font-mono" maxLength={7} />
          </div>

          {/* Fill */}
          <div className="flex items-center gap-1.5">
            <Label className="text-xs text-muted-foreground">Fill</Label>
            <button
              onClick={() => setFillEnabled(!fillEnabled)}
              className={`text-[10px] px-1.5 py-0.5 rounded border transition-colors ${fillEnabled ? 'bg-primary text-primary-foreground border-primary' : 'border-border text-muted-foreground'}`}
            >
              {fillEnabled ? 'ON' : 'OFF'}
            </button>
            {fillEnabled && (
              <>
                <div className="relative">
                  <div className="w-6 h-6 rounded border-2 border-border shadow-sm cursor-pointer" style={{ backgroundColor: fillColor }} />
                  <input type="color" value={fillColor} onChange={e => setFillColor(e.target.value)} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
                </div>
                <Input value={fillColor} onChange={e => setFillColor(e.target.value)} className="h-7 w-20 text-xs font-mono" maxLength={7} />
              </>
            )}
          </div>

          {/* Stroke width */}
          <div className="flex items-center gap-1.5">
            <Label className="text-xs text-muted-foreground whitespace-nowrap">Width</Label>
            <Slider value={[strokeWidth]} onValueChange={([v]) => setStrokeWidth(v)} min={0.5} max={20} step={0.5} className="w-20" />
            <span className="text-xs text-muted-foreground w-5">{strokeWidth}</span>
          </div>

          {/* Corner radius (rectangle only) */}
          {activeTool === 'rectangle' && (
            <div className="flex items-center gap-1.5">
              <Label className="text-xs text-muted-foreground whitespace-nowrap">Radius</Label>
              <Slider value={[cornerRadius]} onValueChange={([v]) => setCornerRadius(v)} min={0} max={50} step={1} className="w-20" />
              <span className="text-xs text-muted-foreground w-5">{cornerRadius}</span>
            </div>
          )}

          {selectedPaths.length > 0 && (
            <Button size="sm" variant="outline" className="h-7 text-xs ml-auto" onClick={applyStylesToSelected}>Apply Style</Button>
          )}
        </div>

        {/* Main */}
        <div className="flex flex-1 overflow-hidden">
          {/* SVG Canvas */}
          <div className="flex-1 overflow-auto p-4 bg-muted/30">
            <svg
              ref={canvasRef}
              width={width}
              height={height}
              className="bg-white dark:bg-gray-950 rounded-lg shadow-lg border border-border block"
              style={{ cursor: activeTool === 'select' ? 'default' : 'crosshair' }}
              onClick={handleCanvasClick}
              onDoubleClick={handleDoubleClick}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
            >
              <defs>
                <pattern id="vgrid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" strokeWidth="0.5" />
                </pattern>
                <pattern id="vgrid-major" width="100" height="100" patternUnits="userSpaceOnUse">
                  <rect width="100" height="100" fill="url(#vgrid)" />
                  <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#d1d5db" strokeWidth="1" />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#vgrid-major)" />

              {paths.map(path => path.visible && (
                <g key={path.id} onClick={(e) => handlePathSelect(path.id, e)} style={{ opacity: path.locked ? 0.5 : 1 }}>
                  <path
                    d={pathToSvg(path)}
                    fill={path.fill}
                    stroke={selectedPaths.includes(path.id) ? '#3b82f6' : path.stroke}
                    strokeWidth={selectedPaths.includes(path.id) ? path.strokeWidth + 1 : path.strokeWidth}
                    className={activeTool === 'select' && !path.locked ? 'cursor-pointer' : ''}
                  />
                  {selectedPaths.includes(path.id) && path.points.map((pt, i) => (
                    <circle key={i} cx={pt.x} cy={pt.y} r={5} fill="#3b82f6" stroke="white" strokeWidth={2} className="cursor-move" />
                  ))}
                </g>
              ))}

              {currentPath && (
                <g>
                  <path d={pathToSvg(currentPath)} fill="none" stroke="#3b82f6" strokeWidth={2} strokeDasharray="5,5" />
                  {currentPath.points.length > 0 && (
                    <line x1={currentPath.points[currentPath.points.length - 1].x} y1={currentPath.points[currentPath.points.length - 1].y}
                      x2={mousePos.x} y2={mousePos.y} stroke="#3b82f6" strokeWidth={1} strokeDasharray="3,3" opacity={0.5} />
                  )}
                  {currentPath.points.map((pt, i) => (
                    <circle key={i} cx={pt.x} cy={pt.y} r={i === 0 ? 8 : 5} fill={i === 0 ? '#22c55e' : '#3b82f6'} stroke="white" strokeWidth={2} />
                  ))}
                </g>
              )}

              {renderDragPreview()}
            </svg>
          </div>

          {/* Path List Panel */}
          <div className="w-52 border-l bg-card flex flex-col">
            <div className="px-3 py-2 border-b flex items-center justify-between">
              <span className="text-sm font-medium">Paths</span>
              <Badge variant="secondary" className="text-xs">{paths.length}</Badge>
            </div>
            <ScrollArea className="flex-1">
              <div className="p-1 space-y-0.5">
                {paths.length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-6 px-2">No paths yet.<br />Start drawing.</p>
                )}
                {[...paths].reverse().map((path) => (
                  <div
                    key={path.id}
                    onClick={() => setSelectedPaths([path.id])}
                    className={`flex items-center gap-1 px-2 py-1.5 rounded-md group text-xs transition-colors cursor-pointer ${
                      selectedPaths.includes(path.id) ? 'bg-primary/10 text-primary' : 'hover:bg-muted'
                    }`}
                  >
                    <div className="w-3 h-3 rounded-sm border flex-shrink-0" style={{ backgroundColor: path.fill === 'none' ? 'transparent' : path.fill, borderColor: path.stroke }} />
                    <span className="flex-1 truncate">{path.name}</span>
                    <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="p-0.5 rounded hover:bg-muted-foreground/20" onClick={e => { e.stopPropagation(); movePath(path.id, 'up'); }}><ChevronUp className="w-3 h-3" /></button>
                        </TooltipTrigger>
                        <TooltipContent side="left">Move up</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="p-0.5 rounded hover:bg-muted-foreground/20" onClick={e => { e.stopPropagation(); movePath(path.id, 'down'); }}><ChevronDown className="w-3 h-3" /></button>
                        </TooltipTrigger>
                        <TooltipContent side="left">Move down</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="p-0.5 rounded hover:bg-muted-foreground/20" onClick={e => { e.stopPropagation(); toggleVisibility(path.id); }}>
                            {path.visible ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3 opacity-40" />}
                          </button>
                        </TooltipTrigger>
                        <TooltipContent side="left">Visibility</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="p-0.5 rounded hover:bg-muted-foreground/20" onClick={e => { e.stopPropagation(); toggleLock(path.id); }}>
                            {path.locked ? <Lock className="w-3 h-3 text-amber-500" /> : <Unlock className="w-3 h-3" />}
                          </button>
                        </TooltipTrigger>
                        <TooltipContent side="left">Lock</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="p-0.5 rounded hover:bg-muted-foreground/20" onClick={e => { e.stopPropagation(); duplicatePath(path.id); }}><Copy className="w-3 h-3" /></button>
                        </TooltipTrigger>
                        <TooltipContent side="left">Duplicate</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button className="p-0.5 rounded hover:bg-red-500/20 text-red-500" onClick={e => { e.stopPropagation(); deletePath(path.id); }}><Trash2 className="w-3 h-3" /></button>
                        </TooltipTrigger>
                        <TooltipContent side="left">Delete</TooltipContent>
                      </Tooltip>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            {/* Selected path properties */}
            {selectedPaths.length === 1 && (() => {
              const sel = paths.find(p => p.id === selectedPaths[0]);
              if (!sel) return null;
              return (
                <div className="border-t p-3 space-y-1.5">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Properties</p>
                  <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-xs">
                    <span className="text-muted-foreground">Points</span><span>{sel.points.length}</span>
                    <span className="text-muted-foreground">Closed</span><span>{sel.closed ? 'Yes' : 'No'}</span>
                    <span className="text-muted-foreground">Stroke</span>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-sm border" style={{ backgroundColor: sel.stroke }} /><span className="font-mono">{sel.stroke}</span></div>
                    <span className="text-muted-foreground">Fill</span>
                    {sel.fill !== 'none'
                      ? <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-sm border" style={{ backgroundColor: sel.fill }} /><span className="font-mono">{sel.fill}</span></div>
                      : <span className="text-muted-foreground italic">none</span>
                    }
                  </div>
                </div>
              );
            })()}
          </div>
        </div>

        {/* Status bar */}
        <div className="flex items-center justify-between px-3 py-1 bg-card border-t text-xs text-muted-foreground">
          <div className="flex items-center gap-3">
            <span className="capitalize font-medium">{activeTool} tool</span>
            {isDrawing && <span className="text-blue-500">{currentPath?.points.length || 0} pts — dbl-click to finish, Esc to cancel</span>}
            {dragState && <span className="text-blue-500">Drawing…</span>}
          </div>
          <div className="flex items-center gap-3">
            <span>X: {mousePos.x}  Y: {mousePos.y}</span>
            <span>{paths.length} paths</span>
            {selectedPaths.length > 0 && <span className="text-primary">{selectedPaths.length} selected</span>}
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}

export default VectorEditor;
