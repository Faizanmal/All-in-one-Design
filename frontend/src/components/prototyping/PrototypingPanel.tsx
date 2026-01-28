/**
 * Interactive Prototyping Panel
 * Add interactions, animations, and transitions to designs
 */
'use client';

import React, { useState } from 'react';
import { Play, Plus, Trash2, MousePointer, Eye, ZapIcon } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';

interface Interaction {
  id: string;
  elementId?: string;
  trigger: 'click' | 'hover' | 'scroll' | 'load';
  action: 'navigate' | 'animate' | 'toggle' | 'overlay';
  target?: string;
  animation?: {
    type: 'fade' | 'slide' | 'scale' | 'rotate';
    duration: number;
    easing: string;
  };
}

interface PrototypingPanelProps {
  canvas?: unknown;
  selectedElement?: unknown;
  onAddInteraction?: (interaction: Interaction) => void;
}

export function PrototypingPanel({ canvas, selectedElement, onAddInteraction }: PrototypingPanelProps) {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  
  const [newInteraction, setNewInteraction] = useState<Partial<Interaction>>({
    trigger: 'click',
    action: 'navigate',
    animation: {
      type: 'fade',
      duration: 300,
      easing: 'ease-in-out',
    },
  });

  const addInteraction = () => {
    if (!selectedElement) return;

    const interaction: Interaction = {
      id: `interaction-${Date.now()}`,
      elementId: (selectedElement as any).id || (selectedElement as any).name,
      trigger: newInteraction.trigger || 'click',
      action: newInteraction.action || 'navigate',
      animation: newInteraction.animation,
    };

    setInteractions([...interactions, interaction]);
    onAddInteraction?.(interaction);

    // Reset form
    setNewInteraction({
      trigger: 'click',
      action: 'navigate',
      animation: {
        type: 'fade',
        duration: 300,
        easing: 'ease-in-out',
      },
    });
  };

  const deleteInteraction = (id: string) => {
    setInteractions(interactions.filter(i => i.id !== id));
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'navigate': return '→';
      case 'animate': return '✨';
      case 'toggle': return '⇄';
      case 'overlay': return '📋';
      default: return '•';
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center justify-between">
          <span className="flex items-center gap-2">
            <ZapIcon className="w-4 h-4" />
            Prototyping
          </span>
          <Button
            variant={isPreviewMode ? 'default' : 'outline'}
            size="sm"
            className="h-7 px-2"
            onClick={() => setIsPreviewMode(!isPreviewMode)}
          >
            {isPreviewMode ? (
              <><Eye className="w-3.5 h-3.5 mr-1" /> Preview</>
            ) : (
              <><Play className="w-3.5 h-3.5 mr-1" /> Preview</>
            )}
          </Button>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 p-0 overflow-hidden flex flex-col">
        {!selectedElement ? (
          <div className="flex-1 flex items-center justify-center p-6 text-center text-muted-foreground text-sm">
            <div>
              <MousePointer className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Select an element to add interactions</p>
            </div>
          </div>
        ) : (
          <>
            {/* Add interaction form */}
            <div className="p-4 border-b space-y-3">
              <div className="space-y-2">
                <Label className="text-xs">Trigger</Label>
                <Select
                  value={newInteraction.trigger}
                  onValueChange={(value: unknown) => setNewInteraction({ ...newInteraction, trigger: value as 'click' | 'load' | 'scroll' | 'hover' | undefined })}
                >
                  <SelectTrigger className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="click">On Click</SelectItem>
                    <SelectItem value="hover">On Hover</SelectItem>
                    <SelectItem value="scroll">On Scroll</SelectItem>
                    <SelectItem value="load">On Load</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label className="text-xs">Action</Label>
                <Select
                  value={newInteraction.action}
                  onValueChange={(value: unknown) => setNewInteraction({ ...newInteraction, action: value as 'navigate' | 'animate' | 'toggle' | 'overlay' | undefined })}
                >
                  <SelectTrigger className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="navigate">Navigate to...</SelectItem>
                    <SelectItem value="animate">Play Animation</SelectItem>
                    <SelectItem value="toggle">Toggle Visibility</SelectItem>
                    <SelectItem value="overlay">Show Overlay</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {newInteraction.action === 'animate' && (
                <>
                  <div className="space-y-2">
                    <Label className="text-xs">Animation Type</Label>
                    <Select
                      value={newInteraction.animation?.type}
                      onValueChange={(value: unknown) => 
                        setNewInteraction({ 
                          ...newInteraction, 
                          animation: { ...newInteraction.animation!, type: value as 'rotate' | 'scale' | 'fade' | 'slide' }
                        })
                      }
                    >
                      <SelectTrigger className="h-8">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="fade">Fade</SelectItem>
                        <SelectItem value="slide">Slide</SelectItem>
                        <SelectItem value="scale">Scale</SelectItem>
                        <SelectItem value="rotate">Rotate</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-xs">Duration: {newInteraction.animation?.duration}ms</Label>
                    <Slider
                      value={[newInteraction.animation?.duration || 300]}
                      onValueChange={([value]) => 
                        setNewInteraction({
                          ...newInteraction,
                          animation: { ...newInteraction.animation!, duration: value }
                        })
                      }
                      min={100}
                      max={2000}
                      step={100}
                    />
                  </div>
                </>
              )}

              <Button size="sm" className="w-full" onClick={addInteraction}>
                <Plus className="w-3.5 h-3.5 mr-1" />
                Add Interaction
              </Button>
            </div>

            {/* Interactions list */}
            <ScrollArea className="flex-1">
              <div className="p-4 space-y-2">
                {interactions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    No interactions yet
                  </div>
                ) : (
                  interactions.map((interaction) => (
                    <Card key={interaction.id} className="p-3">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-xs">
                              {interaction.trigger}
                            </Badge>
                            <span className="text-xs">→</span>
                            <Badge variant="secondary" className="text-xs">
                              {getActionIcon(interaction.action)} {interaction.action}
                            </Badge>
                          </div>
                          {interaction.elementId && (
                            <div className="text-xs text-muted-foreground">
                              Element: {interaction.elementId}
                            </div>
                          )}
                          {interaction.animation && (
                            <div className="text-xs text-muted-foreground mt-1">
                              {interaction.animation.type} • {interaction.animation.duration}ms
                            </div>
                          )}
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0 text-destructive"
                          onClick={() => deleteInteraction(interaction.id)}
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </Card>
                  ))
                )}
              </div>
            </ScrollArea>

            {/* Quick actions */}
            <div className="p-4 border-t space-y-2">
              <Label className="text-xs font-semibold">Quick Actions</Label>
              <div className="grid grid-cols-2 gap-2">
                <Button variant="outline" size="sm" className="text-xs h-8">
                  Add Hover Effect
                </Button>
                <Button variant="outline" size="sm" className="text-xs h-8">
                  Link to Page
                </Button>
                <Button variant="outline" size="sm" className="text-xs h-8">
                  Show Tooltip
                </Button>
                <Button variant="outline" size="sm" className="text-xs h-8">
                  Scroll To
                </Button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
