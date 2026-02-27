"use client";

import React from 'react';
import { Button } from '@/components/ui/button';
import {
  Type,
  Square,
  Circle,
  Triangle,
  Minus,
  Image as ImageIcon,
  Trash2,
  Copy,
  ArrowUp,
  ArrowDown,
  Save,
  Sparkles,
  Undo2,
  Redo2,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignStartVertical,
  AlignCenterVertical,
  AlignEndVertical,
  ChevronDown,
  FileImage,
  Lock,
  Unlock,
  FlipHorizontal,
  FlipVertical,
  Group,
  Ungroup,
  SlidersHorizontal,
} from 'lucide-react';
import { Separator } from '@/components/ui/separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

interface CanvasToolbarProps {
  onAddText: (text?: string, position?: { x: number; y: number }) => void;
  onAddRectangle: (position?: { x: number; y: number }) => void;
  onAddCircle: (position?: { x: number; y: number }) => void;
  onAddTriangle?: (position?: { x: number; y: number }) => void;
  onAddLine?: (position?: { x: number; y: number }) => void;
  onAddImage: (url?: string, position?: { x: number; y: number }) => void;
  onDelete: () => void;
  onClone: () => void;
  onBringToFront: () => void;
  onSendToBack: () => void;
  onExportPNG: () => void;
  onExportSVG: () => void;
  onExportJSON?: () => void;
  onSave: () => void;
  onAIGenerate: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  onAlignLeft?: () => void;
  onAlignCenter?: () => void;
  onAlignRight?: () => void;
  onAlignTop?: () => void;
  onAlignMiddle?: () => void;
  onAlignBottom?: () => void;
  onFlipHorizontal?: () => void;
  onFlipVertical?: () => void;
  onGroup?: () => void;
  onUngroup?: () => void;
  onLock?: () => void;
  hasSelection: boolean;
  isLocked?: boolean;
  canUndo?: boolean;
  canRedo?: boolean;
}

export const CanvasToolbar: React.FC<CanvasToolbarProps> = ({
  onAddText,
  onAddRectangle,
  onAddCircle,
  onAddTriangle,
  onAddLine,
  onAddImage,
  onDelete,
  onClone,
  onBringToFront,
  onSendToBack,
  onExportPNG,
  onExportSVG,
  onExportJSON,
  onSave,
  onAIGenerate,
  onUndo,
  onRedo,
  onAlignLeft,
  onAlignCenter,
  onAlignRight,
  onAlignTop,
  onAlignMiddle,
  onAlignBottom,
  onFlipHorizontal,
  onFlipVertical,
  onGroup,
  onUngroup,
  onLock,
  hasSelection,
  isLocked = false,
  canUndo = false,
  canRedo = false,
}) => {
  return (
    <TooltipProvider delayDuration={300}>
      <div className="flex items-center gap-1 px-3 py-1.5 bg-card border-b shadow-sm overflow-x-auto">

        {/* Undo / Redo */}
        <div className="flex items-center gap-0.5">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onUndo} disabled={!canUndo} className="h-8 w-8">
                <Undo2 className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Undo <kbd className="ml-1 text-xs bg-muted px-1 rounded">Ctrl+Z</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onRedo} disabled={!canRedo} className="h-8 w-8">
                <Redo2 className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Redo <kbd className="ml-1 text-xs bg-muted px-1 rounded">Ctrl+Y</kbd></TooltipContent>
          </Tooltip>
        </div>

        <Separator orientation="vertical" className="h-6 mx-1" />

        {/* Add Elements */}
        <div className="flex items-center gap-0.5">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={() => onAddText()} className="h-8 w-8">
                <Type className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Add Text <kbd className="ml-1 text-xs bg-muted px-1 rounded">T</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={() => onAddRectangle()} className="h-8 w-8">
                <Square className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Rectangle <kbd className="ml-1 text-xs bg-muted px-1 rounded">R</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={() => onAddCircle()} className="h-8 w-8">
                <Circle className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Circle <kbd className="ml-1 text-xs bg-muted px-1 rounded">O</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={() => onAddTriangle?.()} className="h-8 w-8">
                <Triangle className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Triangle</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={() => onAddLine?.()} className="h-8 w-8">
                <Minus className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Line <kbd className="ml-1 text-xs bg-muted px-1 rounded">L</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={() => onAddImage()} className="h-8 w-8" aria-label="Add Image">
                <ImageIcon className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Add Image</TooltipContent>
          </Tooltip>
        </div>

        <Separator orientation="vertical" className="h-6 mx-1" />

        {/* Object Actions */}
        <div className="flex items-center gap-0.5">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onClone} disabled={!hasSelection} className="h-8 w-8">
                <Copy className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Duplicate <kbd className="ml-1 text-xs bg-muted px-1 rounded">Ctrl+D</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onDelete} disabled={!hasSelection} className="h-8 w-8 hover:text-destructive">
                <Trash2 className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Delete <kbd className="ml-1 text-xs bg-muted px-1 rounded">Del</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onLock} disabled={!hasSelection} className="h-8 w-8">
                {isLocked ? <Lock className="h-4 w-4" /> : <Unlock className="h-4 w-4" />}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">{isLocked ? 'Unlock' : 'Lock'} Layer</TooltipContent>
          </Tooltip>
        </div>

        <Separator orientation="vertical" className="h-6 mx-1" />

        {/* Layering */}
        <div className="flex items-center gap-0.5">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onBringToFront} disabled={!hasSelection} className="h-8 w-8">
                <ArrowUp className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Bring to Front <kbd className="ml-1 text-xs bg-muted px-1 rounded">]</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onSendToBack} disabled={!hasSelection} className="h-8 w-8">
                <ArrowDown className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Send to Back <kbd className="ml-1 text-xs bg-muted px-1 rounded">[</kbd></TooltipContent>
          </Tooltip>
        </div>

        <Separator orientation="vertical" className="h-6 mx-1" />

        {/* Alignment Tools */}
        <Popover>
          <Tooltip>
            <TooltipTrigger asChild>
              <PopoverTrigger asChild>
                <Button variant="ghost" size="sm" disabled={!hasSelection} className="h-8 gap-1 px-2">
                  <AlignLeft className="h-4 w-4" />
                  <ChevronDown className="h-3 w-3 opacity-60" />
                </Button>
              </PopoverTrigger>
            </TooltipTrigger>
            <TooltipContent side="bottom">Align & Distribute</TooltipContent>
          </Tooltip>
          <PopoverContent className="w-auto p-2" side="bottom" align="start">
            <div className="text-xs font-medium text-muted-foreground mb-2 px-1">Align Horizontal</div>
            <div className="flex gap-1 mb-3">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onAlignLeft}><AlignLeft className="h-4 w-4" /></Button>
                </TooltipTrigger>
                <TooltipContent>Align Left</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onAlignCenter}><AlignCenter className="h-4 w-4" /></Button>
                </TooltipTrigger>
                <TooltipContent>Align Center</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onAlignRight}><AlignRight className="h-4 w-4" /></Button>
                </TooltipTrigger>
                <TooltipContent>Align Right</TooltipContent>
              </Tooltip>
            </div>
            <div className="text-xs font-medium text-muted-foreground mb-2 px-1">Align Vertical</div>
            <div className="flex gap-1 mb-3">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onAlignTop}><AlignStartVertical className="h-4 w-4" /></Button>
                </TooltipTrigger>
                <TooltipContent>Align Top</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onAlignMiddle}><AlignCenterVertical className="h-4 w-4" /></Button>
                </TooltipTrigger>
                <TooltipContent>Align Middle</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onAlignBottom}><AlignEndVertical className="h-4 w-4" /></Button>
                </TooltipTrigger>
                <TooltipContent>Align Bottom</TooltipContent>
              </Tooltip>
            </div>
            <div className="text-xs font-medium text-muted-foreground mb-2 px-1">Flip</div>
            <div className="flex gap-1">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onFlipHorizontal}><FlipHorizontal className="h-4 w-4" /></Button>
                </TooltipTrigger>
                <TooltipContent>Flip Horizontal</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onFlipVertical}><FlipVertical className="h-4 w-4" /></Button>
                </TooltipTrigger>
                <TooltipContent>Flip Vertical</TooltipContent>
              </Tooltip>
            </div>
          </PopoverContent>
        </Popover>

        {/* Group / Ungroup */}
        <div className="flex items-center gap-0.5">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" disabled={!hasSelection} className="h-8 w-8" onClick={onGroup}>
                <Group className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Group <kbd className="ml-1 text-xs bg-muted px-1 rounded">Ctrl+G</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" disabled={!hasSelection} className="h-8 w-8" onClick={onUngroup}>
                <Ungroup className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Ungroup <kbd className="ml-1 text-xs bg-muted px-1 rounded">Ctrl+Shift+G</kbd></TooltipContent>
          </Tooltip>
        </div>

        <Separator orientation="vertical" className="h-6 mx-1" />

        {/* AI Generate */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline" size="sm" onClick={onAIGenerate} className="h-8 gap-1.5 px-3 border-primary/40 text-primary hover:bg-primary/10">
              <Sparkles className="h-4 w-4" />
              AI Generate
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom">Generate design with AI</TooltipContent>
        </Tooltip>

        <div className="ml-auto flex items-center gap-1.5">
          {/* Export Dropdown */}
          <DropdownMenu>
            <Tooltip>
              <TooltipTrigger asChild>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="h-8 gap-1 px-2.5">
                    <SlidersHorizontal className="h-4 w-4" />
                    Export
                    <ChevronDown className="h-3 w-3 opacity-60" />
                  </Button>
                </DropdownMenuTrigger>
              </TooltipTrigger>
              <TooltipContent side="bottom">Export canvas</TooltipContent>
            </Tooltip>
            <DropdownMenuContent align="end" className="w-44">
              <DropdownMenuLabel className="text-xs">Export As</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onExportPNG} className="gap-2">
                <FileImage className="h-4 w-4" />
                PNG Image (2x)
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onExportSVG} className="gap-2">
                <FileImage className="h-4 w-4" />
                SVG Vector
              </DropdownMenuItem>
              {onExportJSON && (
                <DropdownMenuItem onClick={onExportJSON} className="gap-2">
                  <FileImage className="h-4 w-4" />
                  JSON Data
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Save */}
          <Button variant="default" size="sm" onClick={onSave} className="h-8 gap-1.5 px-3">
            <Save className="h-4 w-4" />
            Save
          </Button>
        </div>
      </div>
    </TooltipProvider>
  );
};
