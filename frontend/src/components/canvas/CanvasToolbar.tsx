"use client";

import React from 'react';
import { Button } from '@/components/ui/button';
import {
  Type,
  Square,
  Circle,
  Image as ImageIcon,
  Trash2,
  Copy,
  ArrowUp,
  ArrowDown,
  Download,
  Save,
  Sparkles,
} from 'lucide-react';
import { Separator } from '@/components/ui/separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface CanvasToolbarProps {
  onAddText: () => void;
  onAddRectangle: () => void;
  onAddCircle: () => void;
  onAddImage: () => void;
  onDelete: () => void;
  onClone: () => void;
  onBringToFront: () => void;
  onSendToBack: () => void;
  onExportPNG: () => void;
  onExportSVG: () => void;
  onSave: () => void;
  onAIGenerate: () => void;
  hasSelection: boolean;
}

export const CanvasToolbar: React.FC<CanvasToolbarProps> = ({
  onAddText,
  onAddRectangle,
  onAddCircle,
  onAddImage,
  onDelete,
  onClone,
  onBringToFront,
  onSendToBack,
  onExportPNG,
  onExportSVG,
  onSave,
  onAIGenerate,
  hasSelection,
}) => {
  return (
    <TooltipProvider>
      <div className="flex items-center gap-2 p-2 bg-white border-b">
        {/* Add Elements */}
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onAddText}>
                <Type className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Add Text</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onAddRectangle}>
                <Square className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Add Rectangle</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onAddCircle}>
                <Circle className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Add Circle</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onAddImage} aria-label="Add Image">
                <ImageIcon className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Add Image</TooltipContent>
          </Tooltip>
        </div>

        <Separator orientation="vertical" className="h-6" />

        {/* Object Actions */}
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClone}
                disabled={!hasSelection}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Duplicate</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={onDelete}
                disabled={!hasSelection}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Delete</TooltipContent>
          </Tooltip>
        </div>

        <Separator orientation="vertical" className="h-6" />

        {/* Layering */}
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={onBringToFront}
                disabled={!hasSelection}
              >
                <ArrowUp className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Bring to Front</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={onSendToBack}
                disabled={!hasSelection}
              >
                <ArrowDown className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Send to Back</TooltipContent>
          </Tooltip>
        </div>

        <Separator orientation="vertical" className="h-6" />

        {/* AI */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline" size="sm" onClick={onAIGenerate}>
              <Sparkles className="h-4 w-4 mr-2" />
              AI Generate
            </Button>
          </TooltipTrigger>
          <TooltipContent>Generate with AI</TooltipContent>
        </Tooltip>

        <div className="ml-auto flex items-center gap-2">
          {/* Export */}
          <Button variant="outline" size="sm" onClick={onExportPNG}>
            <Download className="h-4 w-4 mr-2" />
            PNG
          </Button>

          <Button variant="outline" size="sm" onClick={onExportSVG}>
            <Download className="h-4 w-4 mr-2" />
            SVG
          </Button>

          {/* Save */}
          <Button variant="default" size="sm" onClick={onSave}>
            <Save className="h-4 w-4 mr-2" />
            Save
          </Button>
        </div>
      </div>
    </TooltipProvider>
  );
};

export default CanvasToolbar;
