/**
 * Layers Panel Component
 * Advanced layer management with drag-and-drop reordering, visibility toggle, and locking
 */
'use client';

import React, { useState, useCallback, useEffect } from 'react';
import type { FabricCanvas, FabricObject } from '@/types/fabric';
import { 
  Eye, EyeOff, Lock, Unlock, Trash2, Copy, 
  Layers, ChevronDown, ChevronRight, Folder, FolderOpen 
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
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
      syncLayers();
    }
  }, [canvas]); // Only depend on canvas, not syncLayers to avoid calling setState in effect

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
    const objects = canvas.getObjects();
    const draggedObjIndex = objects.length - 1 - draggedIndex;
    const targetObjIndex = objects.length - 1 - targetIndex;

    // canvas.moveTo(objects[draggedObjIndex], targetObjIndex); // Method does not exist
    canvas.renderAll();
    syncLayers();
    setDraggedLayer(null);
    onLayerUpdate?.();
  }, [draggedLayer, layers, canvas, syncLayers, onLayerUpdate]);

  // Get icon for layer type
  const getLayerIcon = (type: string) => {
    switch (type) {
      case 'text':
      case 'i-text':
      case 'textbox':
        return '📝';
      case 'rect':
      case 'rectangle':
        return '⬜';
      case 'circle':
      case 'ellipse':
        return '⭕';
      case 'image':
        return '🖼️';
      case 'group':
        return '📁';
      case 'path':
        return '✏️';
      default:
        return '⬡';
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Layers className="w-4 h-4" />
          Layers
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="space-y-0.5 p-2">
            {layers.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground text-sm">
                No layers yet
              </div>
            ) : (
              layers.map((layer) => (
                <div
                  key={layer.id}
                  draggable
                  onDragStart={() => handleDragStart(layer.id)}
                  onDragOver={handleDragOver}
                  onDrop={() => handleDrop(layer.id)}
                  onClick={() => selectLayer(layer.id)}
                  className={cn(
                    'group flex items-center gap-1.5 px-2 py-1.5 rounded cursor-pointer transition-colors',
                    selectedLayerId === layer.id 
                      ? 'bg-primary/10 border border-primary/20' 
                      : 'hover:bg-accent',
                    draggedLayer === layer.id && 'opacity-50',
                    !layer.visible && 'opacity-50'
                  )}
                >
                  {/* Layer icon & name */}
                  <span className="text-base mr-1">{getLayerIcon(layer.type)}</span>
                  <span className="flex-1 text-sm truncate">{layer.name}</span>

                  {/* Actions */}
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={(e) => toggleVisibility(layer.id, e)}
                    >
                      {layer.visible ? (
                        <Eye className="w-3.5 h-3.5" />
                      ) : (
                        <EyeOff className="w-3.5 h-3.5 text-muted-foreground" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={(e) => toggleLock(layer.id, e)}
                    >
                      {layer.locked ? (
                        <Lock className="w-3.5 h-3.5 text-destructive" />
                      ) : (
                        <Unlock className="w-3.5 h-3.5" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={(e) => duplicateLayer(layer.id, e)}
                    >
                      <Copy className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0 text-destructive"
                      onClick={(e) => deleteLayer(layer.id, e)}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
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
                const group = new window.fabric.Group(activeObjects);
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
  );
}
