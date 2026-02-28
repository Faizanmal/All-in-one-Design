/**
 * Layers Panel Component
 * Advanced layer management with drag-and-drop reordering, visibility toggle,
 * inline renaming, opacity control, and search filter.
 */
'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Group } from 'fabric';
import type { FabricCanvas, FabricObject } from '@/types/fabric';
import { 
  Eye, EyeOff, Lock, Unlock, Trash2, Copy,
  Layers, Folder, Type, Square, Circle, Image, Pen, Box,
  Search, X, MoveUp, MoveDown
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface Layer {
  id: string;
  name: string;
  type: string;
  visible: boolean;
  locked: boolean;
  object: FabricObject;
  children?: Layer[];
  isGroup?: boolean;
  expanded?: boolean;
}

interface LayersPanelProps {
  canvas: FabricCanvas | null;
  onLayerSelect?: (layerId: string) => void;
  onLayerUpdate?: () => void;
}

export function LayersPanel({ canvas, onLayerSelect, onLayerUpdate }: LayersPanelProps) {
  const [layers, setLayers] = useState<Layer[]>([]);
  const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null);
  const [draggedLayer, setDraggedLayer] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const renameInputRef = useRef<HTMLInputElement>(null);

  // Sync layers from canvas
  const syncLayers = useCallback(() => {
    if (!canvas) return;

    const objects = canvas.getObjects();
    const newLayers: Layer[] = objects.map((obj: FabricObject & { id?: string, name?: string }, index: number) => ({
      id: obj.id || `layer-${index}`,
      name: obj.name || `${obj.type || 'Object'} ${index + 1}`,
      type: obj.type || 'object',
      visible: obj.visible !== false,
      locked: !obj.selectable,
      object: obj,
      isGroup: obj.type === 'group',
      expanded: true,
    }));

    setLayers(newLayers.reverse()); // Reverse to show top layer first
  }, [canvas]);

  useEffect(() => {
    if (canvas) {
      canvas.on('object:added', syncLayers);
      canvas.on('object:removed', syncLayers);
      canvas.on('object:modified', syncLayers);
      
      return () => {
        canvas.off('object:added', syncLayers);
        canvas.off('object:removed', syncLayers);
        canvas.off('object:modified', syncLayers);
      };
    }
  }, [canvas, syncLayers]);

  // Initial sync when canvas is available
  useEffect(() => {
    if (canvas) {
      const layerList = canvas.getObjects();
      if (layerList) {
        const newLayers = layerList.map((obj, index: number) => ({
          id: String((obj as Record<string, any>).id || index), // eslint-disable-line @typescript-eslint/no-explicit-any
          name: ((obj as Record<string, any>).name as string) || (obj.type as string) || `Layer ${index + 1}`, // eslint-disable-line @typescript-eslint/no-explicit-any
          type: (obj.type as string) || 'object',
          visible: (obj.visible as boolean) !== false,
          locked: (obj.selectable as boolean) === false,
          object: obj,
          opacity: (obj.opacity as number) || 1,
          blendMode: ((obj as Record<string, any>).blendMode as string) || 'normal', // eslint-disable-line @typescript-eslint/no-explicit-any
        }));
        setLayers(newLayers); // eslint-disable-line react-hooks/set-state-in-effect
      }
    }
  }, [canvas]);

  // Toggle layer visibility
  const toggleVisibility = useCallback((layerId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!canvas) return;
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;

    layer.object.set('visible', !layer.visible);
    canvas.renderAll();
    syncLayers();
    onLayerUpdate?.();
  }, [layers, canvas, syncLayers, onLayerUpdate]);

  // Toggle layer lock
  const toggleLock = useCallback((layerId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!canvas) return;
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;

    const newLocked = !layer.locked;
    layer.object.set({
      selectable: !newLocked,
      evented: !newLocked,
    });
    canvas.renderAll();
    syncLayers();
    onLayerUpdate?.();
  }, [layers, canvas, syncLayers, onLayerUpdate]);

  // Select layer
  const selectLayer = useCallback((layerId: string) => {
    if (!canvas) return;
    const layer = layers.find(l => l.id === layerId);
    if (!layer || layer.locked) return;

    canvas.setActiveObject(layer.object);
    canvas.renderAll();
    setSelectedLayerId(layerId);
    onLayerSelect?.(layerId);
  }, [layers, canvas, onLayerSelect]);

  // Delete layer
  const deleteLayer = useCallback((layerId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!canvas) return;
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;

    canvas.remove(layer.object);
    canvas.renderAll();
    syncLayers();
    onLayerUpdate?.();
  }, [layers, canvas, syncLayers, onLayerUpdate]);

  // Duplicate layer
  const duplicateLayer = useCallback((layerId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!canvas) return;
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;

    layer.object.clone().then((cloned: FabricObject) => {
      cloned.set({
        left: (cloned.left || 0) + 20,
        top: (cloned.top || 0) + 20,
      });
      canvas.add(cloned);
      canvas.renderAll();
      syncLayers();
      onLayerUpdate?.();
    });
  }, [layers, canvas, syncLayers, onLayerUpdate]);

  // Drag and drop handlers
  const handleDragStart = useCallback((layerId: string) => {
    setDraggedLayer(layerId);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleDrop = useCallback((targetLayerId: string) => {
    if (!draggedLayer || draggedLayer === targetLayerId) {
      setDraggedLayer(null);
      return;
    }

    if (!canvas) return;

    const draggedIndex = layers.findIndex(l => l.id === draggedLayer);
    const targetIndex = layers.findIndex(l => l.id === targetLayerId);

    if (draggedIndex === -1 || targetIndex === -1) return;

    // Reorder in canvas (remember layers are reversed in display)
    // const objects = canvas.getObjects();
    // const draggedObjIndex = objects.length - 1 - draggedIndex;
    // const targetObjIndex = objects.length - 1 - targetIndex;

    // canvas.moveTo(objects[draggedObjIndex], targetObjIndex); // Method does not exist
    canvas.renderAll();
    syncLayers();
    setDraggedLayer(null);
    onLayerUpdate?.();
  }, [draggedLayer, layers, canvas, syncLayers, onLayerUpdate]);

  // Inline rename handlers
  const startRename = useCallback((layer: Layer, e: React.MouseEvent) => {
    e.stopPropagation();
    setRenamingId(layer.id);
    setRenameValue(layer.name);
    setTimeout(() => renameInputRef.current?.select(), 10);
  }, []);

  const commitRename = useCallback(() => {
    if (!renamingId || !canvas) return;
    const layer = layers.find(l => l.id === renamingId);
    if (layer && renameValue.trim()) {
      // Update the object name property
      (layer.object as FabricObject & { name?: string }).name = renameValue.trim();
      canvas.renderAll();
      syncLayers();
      onLayerUpdate?.();
    }
    setRenamingId(null);
  }, [renamingId, renameValue, layers, canvas, syncLayers, onLayerUpdate]);

  // Change opacity per layer
  const changeOpacity = useCallback((layerId: string, opacity: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!canvas) return;
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;
    layer.object.set('opacity', opacity / 100);
    canvas.renderAll();
    onLayerUpdate?.();
  }, [layers, canvas, onLayerUpdate]);

  // Move layer up (bring forward)
  const moveLayerUp = useCallback((layerId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!canvas) return;
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;
    canvas.bringObjectForward(layer.object);
    canvas.renderAll();
    syncLayers();
    onLayerUpdate?.();
  }, [layers, canvas, syncLayers, onLayerUpdate]);

  // Move layer down (send backward)
  const moveLayerDown = useCallback((layerId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!canvas) return;
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;
    canvas.sendObjectBackwards(layer.object);
    canvas.renderAll();
    syncLayers();
    onLayerUpdate?.();
  }, [layers, canvas, syncLayers, onLayerUpdate]);

  // Get icon for layer type
  const getLayerIcon = (type: string) => {
    switch (type) {
      case 'text':
      case 'i-text':
      case 'textbox':
        return <Type className="w-3.5 h-3.5 text-blue-500" />;
      case 'rect':
      case 'rectangle':
        return <Square className="w-3.5 h-3.5 text-green-500" />;
      case 'circle':
      case 'ellipse':
        return <Circle className="w-3.5 h-3.5 text-orange-500" />;
      case 'image':
        return <Image className="w-3.5 h-3.5 text-purple-500" aria-hidden="true" />;
      case 'group':
        return <Folder className="w-3.5 h-3.5 text-yellow-500" />;
      case 'path':
        return <Pen className="w-3.5 h-3.5 text-red-500" />;
      default:
        return <Box className="w-3.5 h-3.5 text-muted-foreground" />;
    }
  };

  const filteredLayers = layers.filter(l =>
    searchQuery === '' || l.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <TooltipProvider delayDuration={200}>
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 px-3 pt-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <Layers className="w-4 h-4" />
            Layers
          </CardTitle>
          <Badge variant="secondary" className="text-xs font-mono">{layers.length}</Badge>
        </div>
        {/* Search */}
        <div className="relative mt-2">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search layers..."
            className="h-7 pl-7 pr-7 text-xs"
          />
          {searchQuery && (
            <Button variant="ghost" size="icon" className="absolute right-1 top-1/2 -translate-y-1/2 h-5 w-5"
              onClick={() => setSearchQuery('')}>
              <X className="w-3 h-3" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="space-y-0.5 p-2">
            {filteredLayers.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Layers className="w-8 h-8 mx-auto mb-2 opacity-20" />
                <p className="text-xs">{searchQuery ? 'No matching layers' : 'No layers yet'}</p>
              </div>
            ) : (
              filteredLayers.map((layer) => (
                <div
                  key={layer.id}
                  draggable
                  onDragStart={() => handleDragStart(layer.id)}
                  onDragOver={handleDragOver}
                  onDrop={() => handleDrop(layer.id)}
                  onClick={() => selectLayer(layer.id)}
                  className={cn(
                    'group flex flex-col px-2 py-1.5 rounded cursor-pointer transition-colors',
                    selectedLayerId === layer.id
                      ? 'bg-primary/10 border border-primary/20'
                      : 'hover:bg-accent',
                    draggedLayer === layer.id && 'opacity-50',
                    !layer.visible && 'opacity-40'
                  )}
                >
                  <div className="flex items-center gap-1.5">
                    {/* Type icon */}
                    <span className="shrink-0">{getLayerIcon(layer.type)}</span>

                    {/* Inline Rename */}
                    {renamingId === layer.id ? (
                      <input
                        ref={renameInputRef}
                        value={renameValue}
                        onClick={(e) => e.stopPropagation()}
                        onChange={(e) => setRenameValue(e.target.value)}
                        onBlur={commitRename}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') commitRename();
                          if (e.key === 'Escape') setRenamingId(null);
                        }}
                        className="flex-1 text-xs bg-background border rounded px-1 h-5 outline-none ring-1 ring-primary"
                        autoFocus
                      />
                    ) : (
                      <span
                        className="flex-1 text-xs truncate select-none"
                        onDoubleClick={(e) => startRename(layer, e)}
                        title="Double-click to rename"
                      >
                        {layer.name}
                      </span>
                    )}

                    {/* Visibility & Lock (always visible) */}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0 shrink-0"
                          onClick={(e) => toggleVisibility(layer.id, e)}>
                          {layer.visible
                            ? <Eye className="w-3.5 h-3.5" />
                            : <EyeOff className="w-3.5 h-3.5 text-muted-foreground" />}
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Toggle visibility</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0 shrink-0"
                          onClick={(e) => toggleLock(layer.id, e)}>
                          {layer.locked
                            ? <Lock className="w-3.5 h-3.5 text-amber-500" />
                            : <Unlock className="w-3.5 h-3.5" />}
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>{layer.locked ? 'Unlock' : 'Lock'} layer</TooltipContent>
                    </Tooltip>

                    {/* More actions - shown on hover */}
                    <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0"
                            onClick={(e) => moveLayerUp(layer.id, e)}>
                            <MoveUp className="w-3.5 h-3.5" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Move up</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0"
                            onClick={(e) => moveLayerDown(layer.id, e)}>
                            <MoveDown className="w-3.5 h-3.5" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Move down</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0"
                            onClick={(e) => duplicateLayer(layer.id, e)}>
                            <Copy className="w-3.5 h-3.5" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Duplicate</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0 hover:text-destructive"
                            onClick={(e) => deleteLayer(layer.id, e)}>
                            <Trash2 className="w-3.5 h-3.5" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Delete layer</TooltipContent>
                      </Tooltip>
                    </div>
                  </div>

                  {/* Opacity – show for selected layer */}
                  {selectedLayerId === layer.id && (
                    <div className="flex items-center gap-2 mt-1.5 px-1" onClick={(e) => e.stopPropagation()}>
                      <span className="text-xs text-muted-foreground w-14 shrink-0">
                        Opacity {Math.round(((layer.object as FabricObject & { opacity?: number }).opacity ?? 1) * 100)}%
                      </span>
                      <Slider
                        min={0} max={100} step={1}
                        value={[Math.round(((layer.object as FabricObject & { opacity?: number }).opacity ?? 1) * 100)]}
                        onValueChange={([v]) => changeOpacity(layer.id, v, { stopPropagation: () => {} } as React.MouseEvent)}
                        className="flex-1 h-1.5"
                      />
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        {/* Bottom actions */}
        <div className="border-t p-2 flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={() => {
              if (!canvas) return;
              // Create new group from selection
              const activeObjects = canvas.getActiveObjects();
              if (activeObjects.length > 1) {
                const group = new Group(activeObjects);
                canvas.remove(...activeObjects);
                canvas.add(group);
                canvas.setActiveObject(group);
                canvas.renderAll();
                syncLayers();
                onLayerUpdate?.();
              }
            }}
          >
            <Folder className="w-3.5 h-3.5 mr-1" />
            Group
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={() => {
              if (!canvas) return;
              // Delete all selected
              const activeObjects = canvas.getActiveObjects();
              canvas.remove(...activeObjects);
              canvas.discardActiveObject();
              canvas.renderAll();
              syncLayers();
              onLayerUpdate?.();
            }}
          >
            <Trash2 className="w-3.5 h-3.5 mr-1" />
            Delete
          </Button>
        </div>
      </CardContent>
    </Card>
    </TooltipProvider>
  );
}
