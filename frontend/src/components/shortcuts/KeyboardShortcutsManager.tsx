/**
 * Keyboard Shortcuts Manager
 * Figma-style keyboard shortcuts with visual guide
 */
'use client';

import React, { useEffect, useState, useCallback } from 'react';
import type { FabricCanvas } from '@/types/fabric';
import { Command, Keyboard } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';

interface Shortcut {
  id: string;
  keys: string[];
  description: string;
  category: string;
  action?: () => void;
}

interface KeyboardShortcutsManagerProps {
  canvas?: FabricCanvas | null;
  onShortcut?: (shortcutId: string) => void;
}

const defaultShortcuts: Shortcut[] = [
  // Tools
  { id: 'tool-select', keys: ['V'], description: 'Select tool', category: 'Tools' },
  { id: 'tool-text', keys: ['T'], description: 'Text tool', category: 'Tools' },
  { id: 'tool-rectangle', keys: ['R'], description: 'Rectangle tool', category: 'Tools' },
  { id: 'tool-circle', keys: ['O'], description: 'Circle/Oval tool', category: 'Tools' },
  { id: 'tool-line', keys: ['L'], description: 'Line tool', category: 'Tools' },
  { id: 'tool-pen', keys: ['P'], description: 'Pen tool', category: 'Tools' },
  
  // Edit
  { id: 'undo', keys: ['Ctrl', 'Z'], description: 'Undo', category: 'Edit' },
  { id: 'redo', keys: ['Ctrl', 'Shift', 'Z'], description: 'Redo', category: 'Edit' },
  { id: 'cut', keys: ['Ctrl', 'X'], description: 'Cut', category: 'Edit' },
  { id: 'copy', keys: ['Ctrl', 'C'], description: 'Copy', category: 'Edit' },
  { id: 'paste', keys: ['Ctrl', 'V'], description: 'Paste', category: 'Edit' },
  { id: 'duplicate', keys: ['Ctrl', 'D'], description: 'Duplicate', category: 'Edit' },
  { id: 'delete', keys: ['Delete'], description: 'Delete selection', category: 'Edit' },
  
  // Selection
  { id: 'select-all', keys: ['Ctrl', 'A'], description: 'Select all', category: 'Selection' },
  { id: 'deselect', keys: ['Escape'], description: 'Deselect', category: 'Selection' },
  
  // Arrange
  { id: 'bring-front', keys: ['Ctrl', ']'], description: 'Bring forward', category: 'Arrange' },
  { id: 'send-back', keys: ['Ctrl', '['], description: 'Send backward', category: 'Arrange' },
  { id: 'bring-to-front', keys: ['Ctrl', 'Shift', ']'], description: 'Bring to front', category: 'Arrange' },
  { id: 'send-to-back', keys: ['Ctrl', 'Shift', '['], description: 'Send to back', category: 'Arrange' },
  { id: 'group', keys: ['Ctrl', 'G'], description: 'Group selection', category: 'Arrange' },
  { id: 'ungroup', keys: ['Ctrl', 'Shift', 'G'], description: 'Ungroup', category: 'Arrange' },
  
  // View
  { id: 'zoom-in', keys: ['Ctrl', '+'], description: 'Zoom in', category: 'View' },
  { id: 'zoom-out', keys: ['Ctrl', '-'], description: 'Zoom out', category: 'View' },
  { id: 'zoom-fit', keys: ['Ctrl', '0'], description: 'Zoom to fit', category: 'View' },
  { id: 'zoom-100', keys: ['Ctrl', '1'], description: 'Zoom to 100%', category: 'View' },
  { id: 'toggle-rulers', keys: ['Ctrl', 'R'], description: 'Toggle rulers', category: 'View' },
  { id: 'toggle-grid', keys: ['Ctrl', "'"], description: 'Toggle grid', category: 'View' },
  
  // File
  { id: 'save', keys: ['Ctrl', 'S'], description: 'Save', category: 'File' },
  { id: 'export', keys: ['Ctrl', 'E'], description: 'Export', category: 'File' },
  { id: 'new', keys: ['Ctrl', 'N'], description: 'New project', category: 'File' },
  
  // AI & Features
  { id: 'ai-generate', keys: ['Ctrl', 'K'], description: 'AI Generate', category: 'AI' },
  { id: 'search', keys: ['Ctrl', 'F'], description: 'Search', category: 'General' },
  { id: 'shortcuts', keys: ['Ctrl', '/'], description: 'Show shortcuts', category: 'General' },
];

export function KeyboardShortcutsManager({ canvas, onShortcut }: KeyboardShortcutsManagerProps) {
  const [open, setOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [shortcuts] = useState<Shortcut[]>(defaultShortcuts);

  // Handle keyboard events
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const ctrlKey = isMac ? e.metaKey : e.ctrlKey;
    const key = e.key.toUpperCase();

    // Find matching shortcut
    for (const shortcut of shortcuts) {
      const keysMatch = shortcut.keys.every((k) => {
        if (k === 'Ctrl') return ctrlKey;
        if (k === 'Shift') return e.shiftKey;
        if (k === 'Alt') return e.altKey;
        return k.toUpperCase() === key;
      });

      if (keysMatch) {
        e.preventDefault();
        
        // Handle built-in shortcuts
        switch (shortcut.id) {
          case 'shortcuts':
            setOpen(true);
            break;
          case 'delete':
            if (canvas) {
              const activeObjects = canvas.getActiveObjects();
              canvas.remove(...activeObjects);
              canvas.discardActiveObject();
              canvas.renderAll();
            }
            break;
          case 'duplicate':
            if (canvas) {
              const activeObject = canvas.getActiveObject();
              if (activeObject) {
                activeObject.clone().then((cloned: unknown) => {
                  (cloned as any).set({
                    left: ((cloned as any).left || 0) + 20,
                    top: ((cloned as any).top || 0) + 20,
                  });
                  canvas.add(cloned as any);
                  canvas.setActiveObject(cloned as any);
                  canvas.renderAll();
                });
              }
            }
            break;
          case 'select-all':
            if (canvas) {
              canvas.discardActiveObject();
              const selection = new (window as any).fabric.ActiveSelection(
                canvas.getObjects(),
                { canvas }
              );
              canvas.setActiveObject(selection);
              canvas.renderAll();
            }
            break;
          case 'deselect':
            if (canvas) {
              canvas.discardActiveObject();
              canvas.renderAll();
            }
            break;
          case 'bring-to-front':
            if (canvas) {
              const activeObject = canvas.getActiveObject();
              if (activeObject) {
                canvas.bringObjectToFront(activeObject);
                canvas.renderAll();
              }
            }
            break;
          case 'send-to-back':
            if (canvas) {
              const activeObject = canvas.getActiveObject();
              if (activeObject) {
                canvas.sendObjectToBack(activeObject);
                canvas.renderAll();
              }
            }
            break;
          case 'group':
            if (canvas) {
              const activeObjects = canvas.getActiveObjects();
              if (activeObjects.length > 1) {
                const group = new (window as any).fabric.Group(activeObjects);
                canvas.remove(...activeObjects);
                canvas.add(group);
                canvas.setActiveObject(group);
                canvas.renderAll();
              }
            }
            break;
          default:
            // Call custom handler
            onShortcut?.(shortcut.id);
            shortcut.action?.();
        }
        break;
      }
    }
  }, [shortcuts, canvas, onShortcut]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Filter shortcuts by search
  const filteredShortcuts = shortcuts.filter(s => 
    s.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.keys.some(k => k.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Group by category
  const groupedShortcuts = filteredShortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {} as Record<string, Shortcut[]>);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Keyboard className="w-4 h-4 mr-2" />
          Shortcuts
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Keyboard className="w-5 h-5" />
            Keyboard Shortcuts
          </DialogTitle>
          <DialogDescription>
            Press <Badge variant="secondary" className="mx-1">Ctrl /</Badge> to toggle this panel
          </DialogDescription>
        </DialogHeader>

        <Input
          placeholder="Search shortcuts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="mb-4"
        />

        <ScrollArea className="h-[500px] pr-4">
          <div className="space-y-6">
            {Object.entries(groupedShortcuts).map(([category, shortcuts]) => (
              <div key={category}>
                <h3 className="font-semibold text-sm text-muted-foreground mb-2 sticky top-0 bg-background py-1">
                  {category}
                </h3>
                <div className="space-y-2">
                  {shortcuts.map((shortcut) => (
                    <div
                      key={shortcut.id}
                      className="flex items-center justify-between py-2 px-3 rounded hover:bg-accent transition-colors"
                    >
                      <span className="text-sm">{shortcut.description}</span>
                      <div className="flex items-center gap-1">
                        {shortcut.keys.map((key, index) => (
                          <React.Fragment key={index}>
                            {index > 0 && <span className="text-xs text-muted-foreground">+</span>}
                            <Badge variant="outline" className="font-mono text-xs">
                              {key === 'Ctrl' ? (navigator.platform.toUpperCase().indexOf('MAC') >= 0 ? '⌘' : 'Ctrl') : key}
                            </Badge>
                          </React.Fragment>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
