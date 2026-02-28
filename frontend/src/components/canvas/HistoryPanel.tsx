'use client';

import type { FabricCanvas } from '@/types/fabric';
/**
 * History Panel Component
 * Version history and time-travel debugging like Figma
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Clock, RotateCcw, RotateCw, History, Eye } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

interface HistoryEntry {
  id: string;
  action: string;
  timestamp: Date;
  state: unknown;
  thumbnail?: string;
  user?: {
    name: string;
    avatar?: string;
  };
}

interface HistoryPanelProps {
  canvas: FabricCanvas | null;
  maxHistory?: number;
  onRestore?: (entry: HistoryEntry) => void;
}

export function HistoryPanel({ 
  canvas, 
  maxHistory = 50,
  onRestore 
}: HistoryPanelProps) {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const isInitialized = useRef(false);

  // Capture canvas state
  const captureState = useCallback((action: string) => {
    if (!canvas) return;

    const state = canvas.toJSON();
    
    // Generate thumbnail
    const thumbnail = canvas.toDataURL({
      format: 'png',
      quality: 0.3,
      multiplier: 0.1,
    });

    const entry: HistoryEntry = {
      id: `history-${Date.now()}`,
      action,
      timestamp: new Date(),
      state,
      thumbnail,
      user: {
        name: 'You',
      },
    };

    setHistory(prev => {
      // Remove any entries after current index if we're not at the end
      const newHistory = currentIndex < prev.length - 1 
        ? prev.slice(0, currentIndex + 1)
        : prev;

      // Add new entry and limit history size
      const updated = [...newHistory, entry].slice(-maxHistory);
      return updated;
    });

    setCurrentIndex(() => {
      // Use the same logic as setHistory
      const newHistoryLength = currentIndex < history.length - 1 
        ? currentIndex + 1 + 1 // +1 for the new entry
        : history.length + 1;
      return Math.min(newHistoryLength - 1, maxHistory - 1);
    });
  }, [canvas, currentIndex, history.length, maxHistory]);

  // Initial capture
  useEffect(() => {
    if (canvas && !isInitialized.current) {
      isInitialized.current = true;
      // Defer state capture to avoid synchronous setState in effect
      setTimeout(() => captureState('Initial state'), 0);
    }
  }, [canvas, captureState]);

  // Undo
  const undo = useCallback(() => {
    if (currentIndex <= 0 || !canvas) return;

    const prevIndex = currentIndex - 1;
    const entry = history[prevIndex];

    canvas.loadFromJSON(entry.state as Record<string, any>).then(() => { // eslint-disable-line @typescript-eslint/no-explicit-any
      canvas.renderAll();
      setCurrentIndex(prevIndex);
      onRestore?.(entry);
    });
  }, [canvas, currentIndex, history, onRestore]);

  // Redo
  const redo = useCallback(() => {
    if (currentIndex >= history.length - 1 || !canvas) return;

    const nextIndex = currentIndex + 1;
    const entry = history[nextIndex];

    canvas.loadFromJSON(entry.state as Record<string, any>).then(() => { // eslint-disable-line @typescript-eslint/no-explicit-any
      canvas.renderAll();
      setCurrentIndex(nextIndex);
      onRestore?.(entry);
    });
  }, [canvas, currentIndex, history, onRestore]);

  // Restore to specific point
  const restoreToPoint = useCallback((index: number) => {
    if (index < 0 || index >= history.length || !canvas) return;

    const entry = history[index];

    canvas.loadFromJSON(entry.state as Record<string, any>).then(() => { // eslint-disable-line @typescript-eslint/no-explicit-any
      canvas.renderAll();
      setCurrentIndex(index);
      onRestore?.(entry);
    });
  }, [canvas, history, onRestore]);

  // Setup canvas event listeners
  useEffect(() => {
    if (!canvas) return;

    const handleObjectAdded = () => captureState('Object added');
    const handleObjectRemoved = () => captureState('Object removed');
    const handleObjectModified = (e: unknown) => {
      const obj = (e as { target: Record<string, unknown> }).target;
      captureState(`${(obj as { type?: string }).type || 'Object'} modified`);
    };

    canvas.on('object:added', handleObjectAdded);
    canvas.on('object:removed', handleObjectRemoved);
    canvas.on('object:modified', handleObjectModified);

    return () => {
      canvas.off('object:added', handleObjectAdded);
      canvas.off('object:removed', handleObjectRemoved);
      canvas.off('object:modified', handleObjectModified);
    };
  }, [canvas, captureState]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        undo();
      } else if ((e.metaKey || e.ctrlKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault();
        redo();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [undo, redo]);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <History className="w-4 h-4" />
          History
          <Badge variant="secondary" className="ml-auto text-xs">
            {currentIndex + 1}/{history.length}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 p-0 overflow-hidden flex flex-col">
        {/* Undo/Redo controls */}
        <div className="flex gap-2 p-2 border-b">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={undo}
            disabled={currentIndex <= 0}
          >
            <RotateCcw className="w-3.5 h-3.5 mr-1" />
            Undo
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={redo}
            disabled={currentIndex >= history.length - 1}
          >
            <RotateCw className="w-3.5 h-3.5 mr-1" />
            Redo
          </Button>
        </div>

        {/* History timeline */}
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {history.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground text-sm">
                No history yet
              </div>
            ) : (
              history.map((entry, index) => (
                <div
                  key={entry.id}
                  onClick={() => restoreToPoint(index)}
                  className={cn(
                    'group flex items-start gap-2 p-2 rounded cursor-pointer transition-colors',
                    index === currentIndex 
                      ? 'bg-primary/10 border border-primary/20' 
                      : 'hover:bg-accent',
                    index > currentIndex && 'opacity-40'
                  )}
                >
                  {/* Thumbnail */}
                  {entry.thumbnail && (
                    <div className="w-12 h-12 rounded overflow-hidden bg-muted flex-shrink-0">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img 
                        src={entry.thumbnail} 
                        alt={entry.action}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium truncate">
                        {entry.action}
                      </span>
                      {index === currentIndex && (
                        <Badge variant="default" className="text-xs">Current</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-muted-foreground">
                        {formatDistanceToNow(entry.timestamp, { addSuffix: true })}
                      </span>
                      {entry.user && (
                        <>
                          <span className="text-xs text-muted-foreground">•</span>
                          <span className="text-xs text-muted-foreground">
                            {entry.user.name}
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Preview button */}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100"
                    onClick={(e) => {
                      e.stopPropagation();
                      restoreToPoint(index);
                    }}
                  >
                    <Eye className="w-3.5 h-3.5" />
                  </Button>
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        {/* Stats */}
        <div className="border-t p-2 text-xs text-muted-foreground text-center">
          {history.length > 0 && (
            <div className="flex items-center justify-center gap-2">
              <Clock className="w-3 h-3" />
              <span>
                {history.length} {history.length === 1 ? 'change' : 'changes'} tracked
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
