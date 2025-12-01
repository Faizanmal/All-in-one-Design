'use client';

import React, { useState, useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Layers,
  Move,
  Trash2,
  Copy,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignStartVertical,
  AlignCenterVertical,
  AlignEndVertical,
  FlipHorizontal,
  FlipVertical,
  Maximize,
  Minimize,
  Palette,
  RotateCcw,
  History,
  ChevronDown,
  Search,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';

interface BatchOperationsToolbarProps {
  projectId: number;
  selectedComponents: number[];
  onOperationComplete?: () => void;
}

interface BatchOperation {
  id: number;
  operation_type: string;
  status: string;
  component_count: number;
  success_count: number;
  error_count: number;
  created_at: string;
}

export function BatchOperationsToolbar({
  projectId,
  selectedComponents,
  onOperationComplete,
}: BatchOperationsToolbarProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isMoveDialogOpen, setIsMoveDialogOpen] = useState(false);
  const [isStyleDialogOpen, setIsStyleDialogOpen] = useState(false);
  const [isHistoryDialogOpen, setIsHistoryDialogOpen] = useState(false);
  
  // Move values
  const [moveX, setMoveX] = useState(0);
  const [moveY, setMoveY] = useState(0);
  
  // Style values
  const [styleUpdates, setStyleUpdates] = useState<Record<string, string>>({});
  
  const hasSelection = selectedComponents.length > 0;

  // Fetch operation history
  const { data: history } = useQuery({
    queryKey: ['batch-operations-history', projectId],
    queryFn: async () => {
      const response = await fetch(
        `/api/v1/projects/batch-operations/history/?project_id=${projectId}`
      );
      if (!response.ok) throw new Error('Failed to fetch history');
      return response.json();
    },
  });

  // Generic batch operation mutation
  const batchOperationMutation = useMutation({
    mutationFn: async ({
      endpoint,
      data,
    }: {
      endpoint: string;
      data: Record<string, unknown>;
    }) => {
      const response = await fetch(`/api/v1/projects/batch-operations/${endpoint}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          component_ids: selectedComponents,
          ...data,
        }),
      });
      if (!response.ok) throw new Error('Operation failed');
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['batch-operations-history', projectId] });
      toast({
        title: 'Operation Complete',
        description: `${data.success_count} components updated successfully.`,
      });
      onOperationComplete?.();
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: 'Failed to complete operation. Please try again.',
        variant: 'destructive',
      });
    },
  });

  // Undo mutation
  const undoMutation = useMutation({
    mutationFn: async (operationId: number) => {
      const response = await fetch(
        `/api/v1/projects/batch-operations/${operationId}/undo/`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Undo failed');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch-operations-history', projectId] });
      toast({ title: 'Undone', description: 'Operation has been undone.' });
      onOperationComplete?.();
    },
  });

  const handleAlign = useCallback(
    (alignment: string) => {
      batchOperationMutation.mutate({
        endpoint: 'align',
        data: { alignment },
      });
    },
    [batchOperationMutation]
  );

  const handleDistribute = useCallback(
    (direction: string) => {
      batchOperationMutation.mutate({
        endpoint: 'distribute',
        data: { direction },
      });
    },
    [batchOperationMutation]
  );

  const handleMove = useCallback(() => {
    batchOperationMutation.mutate({
      endpoint: 'move',
      data: { delta_x: moveX, delta_y: moveY },
    });
    setIsMoveDialogOpen(false);
    setMoveX(0);
    setMoveY(0);
  }, [batchOperationMutation, moveX, moveY]);

  const handleDuplicate = useCallback(() => {
    batchOperationMutation.mutate({
      endpoint: 'duplicate',
      data: { offset_x: 20, offset_y: 20 },
    });
  }, [batchOperationMutation]);

  const handleDelete = useCallback(() => {
    batchOperationMutation.mutate({
      endpoint: 'delete',
      data: {},
    });
  }, [batchOperationMutation]);

  const handleStyle = useCallback(() => {
    batchOperationMutation.mutate({
      endpoint: 'style',
      data: { style_updates: styleUpdates },
    });
    setIsStyleDialogOpen(false);
    setStyleUpdates({});
  }, [batchOperationMutation, styleUpdates]);

  const handleChangeOrder = useCallback(
    (action: string) => {
      batchOperationMutation.mutate({
        endpoint: 'change-order',
        data: { action },
      });
    },
    [batchOperationMutation]
  );

  const isPending = batchOperationMutation.isPending;

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">Batch Operations</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={hasSelection ? 'default' : 'secondary'}>
              {selectedComponents.length} selected
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => setIsHistoryDialogOpen(true)}
            >
              <History className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Alignment Section */}
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Align
          </label>
          <div className="flex gap-1 mt-2">
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={!hasSelection || isPending}
              onClick={() => handleAlign('left')}
              title="Align Left"
            >
              <AlignLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={!hasSelection || isPending}
              onClick={() => handleAlign('center')}
              title="Align Center"
            >
              <AlignCenter className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={!hasSelection || isPending}
              onClick={() => handleAlign('right')}
              title="Align Right"
            >
              <AlignRight className="h-4 w-4" />
            </Button>
            <Separator orientation="vertical" className="h-8 mx-1" />
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={!hasSelection || isPending}
              onClick={() => handleAlign('top')}
              title="Align Top"
            >
              <AlignStartVertical className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={!hasSelection || isPending}
              onClick={() => handleAlign('middle')}
              title="Align Middle"
            >
              <AlignCenterVertical className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={!hasSelection || isPending}
              onClick={() => handleAlign('bottom')}
              title="Align Bottom"
            >
              <AlignEndVertical className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Distribute Section */}
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Distribute
          </label>
          <div className="flex gap-1 mt-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!hasSelection || selectedComponents.length < 3 || isPending}
              onClick={() => handleDistribute('horizontal')}
            >
              <FlipHorizontal className="h-4 w-4 mr-1" />
              Horizontal
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!hasSelection || selectedComponents.length < 3 || isPending}
              onClick={() => handleDistribute('vertical')}
            >
              <FlipVertical className="h-4 w-4 mr-1" />
              Vertical
            </Button>
          </div>
        </div>

        {/* Transform Section */}
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Transform
          </label>
          <div className="grid grid-cols-4 gap-1 mt-2">
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={!hasSelection || isPending}
              onClick={() => setIsMoveDialogOpen(true)}
              title="Move"
            >
              <Move className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={!hasSelection || isPending}
              onClick={handleDuplicate}
              title="Duplicate"
            >
              <Copy className="h-4 w-4" />
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  disabled={!hasSelection || isPending}
                  title="Z-Order"
                >
                  <Layers className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={() => handleChangeOrder('bring_front')}>
                  Bring to Front
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleChangeOrder('bring_forward')}>
                  Bring Forward
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleChangeOrder('send_backward')}>
                  Send Backward
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleChangeOrder('send_back')}>
                  Send to Back
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8 text-destructive hover:text-destructive"
              disabled={!hasSelection || isPending}
              onClick={handleDelete}
              title="Delete"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Style Section */}
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Style
          </label>
          <div className="flex gap-1 mt-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!hasSelection || isPending}
              onClick={() => setIsStyleDialogOpen(true)}
            >
              <Palette className="h-4 w-4 mr-1" />
              Apply Style
            </Button>
          </div>
        </div>

        {isPending && (
          <div className="flex items-center justify-center py-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
            Processing...
          </div>
        )}
      </CardContent>

      {/* Move Dialog */}
      <Dialog open={isMoveDialogOpen} onOpenChange={setIsMoveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Move Components</DialogTitle>
            <DialogDescription>
              Move {selectedComponents.length} components by offset
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">X Offset (px)</label>
              <Input
                type="number"
                value={moveX}
                onChange={(e) => setMoveX(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Y Offset (px)</label>
              <Input
                type="number"
                value={moveY}
                onChange={(e) => setMoveY(Number(e.target.value))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsMoveDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleMove}>Move</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Style Dialog */}
      <Dialog open={isStyleDialogOpen} onOpenChange={setIsStyleDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Apply Style</DialogTitle>
            <DialogDescription>
              Apply style changes to {selectedComponents.length} components
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Fill Color</label>
              <Input
                type="color"
                value={styleUpdates.fill || '#000000'}
                onChange={(e) =>
                  setStyleUpdates({ ...styleUpdates, fill: e.target.value })
                }
                className="h-10"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Opacity</label>
              <Slider
                value={[Number(styleUpdates.opacity || 100)]}
                onValueChange={([value]) =>
                  setStyleUpdates({ ...styleUpdates, opacity: String(value / 100) })
                }
                min={0}
                max={100}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Border Radius (px)</label>
              <Input
                type="number"
                value={styleUpdates['style.borderRadius'] || ''}
                onChange={(e) =>
                  setStyleUpdates({
                    ...styleUpdates,
                    'style.borderRadius': e.target.value,
                  })
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsStyleDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleStyle}>Apply</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* History Dialog */}
      <Dialog open={isHistoryDialogOpen} onOpenChange={setIsHistoryDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Operation History</DialogTitle>
            <DialogDescription>Recent batch operations</DialogDescription>
          </DialogHeader>
          <ScrollArea className="h-[300px]">
            <div className="space-y-2">
              {history?.history?.map((op: BatchOperation) => (
                <div
                  key={op.id}
                  className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                >
                  <div>
                    <div className="font-medium capitalize">
                      {op.operation_type.replace('_', ' ')}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {op.success_count} of {op.component_count} •{' '}
                      {new Date(op.created_at).toLocaleString()}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => undoMutation.mutate(op.id)}
                    disabled={undoMutation.isPending}
                  >
                    <RotateCcw className="h-4 w-4 mr-1" />
                    Undo
                  </Button>
                </div>
              ))}
              {(!history?.history || history.history.length === 0) && (
                <div className="text-center py-8 text-muted-foreground">
                  No operations yet
                </div>
              )}
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

export default BatchOperationsToolbar;
