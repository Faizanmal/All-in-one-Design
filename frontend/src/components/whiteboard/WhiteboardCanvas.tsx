'use client';

import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import {
  MousePointer2,
  Hand,
  Square,
  Circle,
  Triangle,
  Minus,
  Type,
  StickyNote,
  Image,
  Pencil,
  Eraser,
  ArrowRight,
  Users,
  MessageSquare,
  Timer,
  Vote,
  Undo2,
  Redo2,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Grid,
  Layers,
  Lock,
  Unlock,
  MoreHorizontal,
  Palette,
  Bold,
  Italic,
  AlignLeft,
  AlignCenter,
  AlignRight,
  ChevronDown,
  Download,
  Share2,
  Plus,
  Trash2,
  Copy,
  Group,
  Ungroup,
  Minimize2,
  Fullscreen,
} from 'lucide-react';
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
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';

// Types
interface Point {
  x: number;
  y: number;
}

interface Size {
  width: number;
  height: number;
}

interface WhiteboardElement {
  id: string;
  type: 'sticky' | 'shape' | 'text' | 'image' | 'connector' | 'drawing';
  position: Point;
  size: Size;
  rotation: number;
  zIndex: number;
  isLocked: boolean;
  groupId?: string;
  data: StickyNoteData | ShapeData | TextData | ImageData | ConnectorData | DrawingData;
}

interface StickyNoteData {
  type: 'sticky';
  content: string;
  color: string;
  author?: string;
  votes: number;
  votedBy: string[];
}

interface ShapeData {
  type: 'shape';
  shape: 'rectangle' | 'circle' | 'triangle' | 'diamond' | 'star';
  fill: string;
  stroke: string;
  strokeWidth: number;
}

interface TextData {
  type: 'text';
  content: string;
  fontSize: number;
  fontWeight: 'normal' | 'bold';
  fontStyle: 'normal' | 'italic';
  textAlign: 'left' | 'center' | 'right';
  color: string;
}

interface ImageData {
  type: 'image';
  src: string;
  alt: string;
}

interface ConnectorData {
  type: 'connector';
  startElementId?: string;
  endElementId?: string;
  startPoint: Point;
  endPoint: Point;
  lineStyle: 'solid' | 'dashed' | 'dotted';
  arrowStart: boolean;
  arrowEnd: boolean;
  color: string;
  strokeWidth: number;
}

interface DrawingData {
  type: 'drawing';
  points: Point[];
  color: string;
  strokeWidth: number;
}

interface Cursor {
  id: string;
  userId: string;
  userName: string;
  color: string;
  position: Point;
}

interface Comment {
  id: string;
  elementId?: string;
  position: Point;
  content: string;
  author: string;
  createdAt: string;
  resolved: boolean;
}

interface CanvasState {
  zoom: number;
  pan: Point;
  selectedIds: string[];
  tool: Tool;
  isDrawing: boolean;
}

type Tool = 'select' | 'pan' | 'sticky' | 'rectangle' | 'circle' | 'triangle' | 'line' | 'arrow' | 'text' | 'draw' | 'eraser' | 'comment';

// Constants
const STICKY_COLORS = ['#FEF08A', '#FCA5A5', '#86EFAC', '#93C5FD', '#C4B5FD', '#FDBA74'];
const SHAPE_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
const MIN_ZOOM = 0.1;
const MAX_ZOOM = 5;
const GRID_SIZE = 20;

// Helper functions
const generateId = () => `el-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

// Toolbar Button Component
interface ToolButtonProps {
  icon: React.ReactNode;
  isActive?: boolean;
  onClick: () => void;
  title: string;
  disabled?: boolean;
  shortcut?: string;
}

const ToolButton: React.FC<ToolButtonProps> = ({ icon, isActive, onClick, title, disabled, shortcut }) => (
  <Tooltip>
    <TooltipTrigger asChild>
      <button
        onClick={onClick}
        disabled={disabled}
        className={`p-2 rounded-lg transition-all ${
          isActive
            ? 'bg-blue-600 text-white shadow-lg'
            : disabled
            ? 'text-gray-600 cursor-not-allowed'
            : 'text-gray-400 hover:text-white hover:bg-gray-700'
        }`}
      >
        {icon}
      </button>
    </TooltipTrigger>
    <TooltipContent side="right">
      {title}{shortcut && <kbd className="ml-1.5 text-[10px] opacity-70">{shortcut}</kbd>}
    </TooltipContent>
  </Tooltip>
);

// Sticky Note Component
interface StickyNoteElementProps {
  element: WhiteboardElement;
  isSelected: boolean;
  onSelect: (id: string, multi: boolean) => void;
  onUpdate: (id: string, data: Partial<WhiteboardElement>) => void;
  onVote: (id: string) => void;
  currentUserId: string;
}

const StickyNoteElement: React.FC<StickyNoteElementProps> = ({
  element,
  isSelected,
  onSelect,
  onUpdate,
  onVote,
  currentUserId,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const data = element.data as StickyNoteData;
  const hasVoted = data.votedBy.includes(currentUserId);

  return (
    <div
      className={`absolute cursor-move transition-shadow ${
        isSelected ? 'ring-2 ring-blue-500 shadow-xl' : 'shadow-lg hover:shadow-xl'
      }`}
      style={{
        left: element.position.x,
        top: element.position.y,
        width: element.size.width,
        height: element.size.height,
        transform: `rotate(${element.rotation}deg)`,
        zIndex: element.zIndex,
      }}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(element.id, e.shiftKey);
      }}
      onDoubleClick={() => !element.isLocked && setIsEditing(true)}
    >
      <div
        className="w-full h-full rounded-lg p-3 flex flex-col"
        style={{ backgroundColor: data.color }}
      >
        {isEditing ? (
          <textarea
            autoFocus
            defaultValue={data.content}
            onBlur={(e) => {
              setIsEditing(false);
              onUpdate(element.id, {
                data: { ...data, content: e.target.value },
              });
            }}
            className="flex-1 bg-transparent resize-none outline-none text-gray-800 text-sm"
            placeholder="Type something..."
          />
        ) : (
          <p className="flex-1 text-gray-800 text-sm whitespace-pre-wrap overflow-hidden">
            {data.content || 'Double-click to edit'}
          </p>
        )}
        
        <div className="flex items-center justify-between mt-2 pt-2 border-t border-black/10">
          <span className="text-xs text-gray-600 truncate max-w-[60%]">
            {data.author}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onVote(element.id);
            }}
            className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-xs transition-colors ${
              hasVoted
                ? 'bg-blue-500 text-white'
                : 'bg-black/10 text-gray-600 hover:bg-black/20'
            }`}
          >
            <Vote size={10} />
            {data.votes}
          </button>
        </div>
      </div>

      {/* Resize handles */}
      {isSelected && !element.isLocked && (
        <>
          <div className="absolute -right-1.5 -bottom-1.5 w-3 h-3 bg-blue-500 rounded-full cursor-se-resize" />
          <div className="absolute -left-1.5 -bottom-1.5 w-3 h-3 bg-blue-500 rounded-full cursor-sw-resize" />
          <div className="absolute -right-1.5 -top-1.5 w-3 h-3 bg-blue-500 rounded-full cursor-ne-resize" />
          <div className="absolute -left-1.5 -top-1.5 w-3 h-3 bg-blue-500 rounded-full cursor-nw-resize" />
        </>
      )}

      {element.isLocked && (
        <div className="absolute -top-2 -right-2 p-1 bg-gray-800 rounded-full">
          <Lock size={10} className="text-yellow-400" />
        </div>
      )}
    </div>
  );
};

// Shape Component
interface ShapeElementProps {
  element: WhiteboardElement;
  isSelected: boolean;
  onSelect: (id: string, multi: boolean) => void;
}

const ShapeElement: React.FC<ShapeElementProps> = ({ element, isSelected, onSelect }) => {
  const data = element.data as ShapeData;

  const renderShape = () => {
    const { width, height } = element.size;
    const commonProps = {
      fill: data.fill,
      stroke: data.stroke,
      strokeWidth: data.strokeWidth,
    };

    switch (data.shape) {
      case 'circle':
        return (
          <svg width={width} height={height}>
            <ellipse
              cx={width / 2}
              cy={height / 2}
              rx={width / 2 - data.strokeWidth}
              ry={height / 2 - data.strokeWidth}
              {...commonProps}
            />
          </svg>
        );
      case 'triangle':
        return (
          <svg width={width} height={height}>
            <polygon
              points={`${width / 2},${data.strokeWidth} ${width - data.strokeWidth},${height - data.strokeWidth} ${data.strokeWidth},${height - data.strokeWidth}`}
              {...commonProps}
            />
          </svg>
        );
      case 'diamond':
        return (
          <svg width={width} height={height}>
            <polygon
              points={`${width / 2},${data.strokeWidth} ${width - data.strokeWidth},${height / 2} ${width / 2},${height - data.strokeWidth} ${data.strokeWidth},${height / 2}`}
              {...commonProps}
            />
          </svg>
        );
      default:
        return (
          <svg width={width} height={height}>
            <rect
              x={data.strokeWidth / 2}
              y={data.strokeWidth / 2}
              width={width - data.strokeWidth}
              height={height - data.strokeWidth}
              rx={4}
              {...commonProps}
            />
          </svg>
        );
    }
  };

  return (
    <div
      className={`absolute cursor-move ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
      style={{
        left: element.position.x,
        top: element.position.y,
        width: element.size.width,
        height: element.size.height,
        transform: `rotate(${element.rotation}deg)`,
        zIndex: element.zIndex,
      }}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(element.id, e.shiftKey);
      }}
    >
      {renderShape()}

      {isSelected && !element.isLocked && (
        <>
          <div className="absolute -right-1.5 -bottom-1.5 w-3 h-3 bg-blue-500 rounded-full cursor-se-resize" />
          <div className="absolute -left-1.5 -bottom-1.5 w-3 h-3 bg-blue-500 rounded-full cursor-sw-resize" />
          <div className="absolute -right-1.5 -top-1.5 w-3 h-3 bg-blue-500 rounded-full cursor-ne-resize" />
          <div className="absolute -left-1.5 -top-1.5 w-3 h-3 bg-blue-500 rounded-full cursor-nw-resize" />
        </>
      )}
    </div>
  );
};

// Text Element Component
interface TextElementProps {
  element: WhiteboardElement;
  isSelected: boolean;
  onSelect: (id: string, multi: boolean) => void;
  onUpdate: (id: string, data: Partial<WhiteboardElement>) => void;
}

const TextElement: React.FC<TextElementProps> = ({ element, isSelected, onSelect, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const data = element.data as TextData;

  return (
    <div
      className={`absolute cursor-move ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
      style={{
        left: element.position.x,
        top: element.position.y,
        minWidth: element.size.width,
        minHeight: element.size.height,
        transform: `rotate(${element.rotation}deg)`,
        zIndex: element.zIndex,
      }}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(element.id, e.shiftKey);
      }}
      onDoubleClick={() => !element.isLocked && setIsEditing(true)}
    >
      {isEditing ? (
        <textarea
          autoFocus
          defaultValue={data.content}
          onBlur={(e) => {
            setIsEditing(false);
            onUpdate(element.id, {
              data: { ...data, content: e.target.value },
            });
          }}
          style={{
            fontSize: data.fontSize,
            fontWeight: data.fontWeight,
            fontStyle: data.fontStyle,
            textAlign: data.textAlign,
            color: data.color,
          }}
          className="min-w-[100px] min-h-[24px] bg-transparent resize-none outline-none border-2 border-blue-500 rounded p-1"
        />
      ) : (
        <p
          style={{
            fontSize: data.fontSize,
            fontWeight: data.fontWeight,
            fontStyle: data.fontStyle,
            textAlign: data.textAlign,
            color: data.color,
          }}
          className="whitespace-pre-wrap"
        >
          {data.content || 'Double-click to edit'}
        </p>
      )}
    </div>
  );
};

// Connector Component
interface ConnectorElementProps {
  element: WhiteboardElement;
  isSelected: boolean;
  onSelect: (id: string, multi: boolean) => void;
}

const ConnectorElement: React.FC<ConnectorElementProps> = ({ element, isSelected, onSelect }) => {
  const data = element.data as ConnectorData;
  const { startPoint, endPoint } = data;

  const minX = Math.min(startPoint.x, endPoint.x);
  const minY = Math.min(startPoint.y, endPoint.y);
  const width = Math.abs(endPoint.x - startPoint.x) + 20;
  const height = Math.abs(endPoint.y - startPoint.y) + 20;

  const localStart = { x: startPoint.x - minX + 10, y: startPoint.y - minY + 10 };
  const localEnd = { x: endPoint.x - minX + 10, y: endPoint.y - minY + 10 };

  return (
    <svg
      className={`absolute pointer-events-none ${isSelected ? 'filter drop-shadow-lg' : ''}`}
      style={{
        left: minX - 10,
        top: minY - 10,
        width,
        height,
        zIndex: element.zIndex,
      }}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(element.id, e.shiftKey);
      }}
    >
      <defs>
        <marker
          id={`arrow-${element.id}`}
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill={data.color} />
        </marker>
      </defs>
      <line
        x1={localStart.x}
        y1={localStart.y}
        x2={localEnd.x}
        y2={localEnd.y}
        stroke={data.color}
        strokeWidth={data.strokeWidth}
        strokeDasharray={data.lineStyle === 'dashed' ? '8,4' : data.lineStyle === 'dotted' ? '2,2' : 'none'}
        markerEnd={data.arrowEnd ? `url(#arrow-${element.id})` : undefined}
        className="pointer-events-auto cursor-move"
      />
      {isSelected && (
        <>
          <circle cx={localStart.x} cy={localStart.y} r={5} fill="#3B82F6" className="cursor-move" />
          <circle cx={localEnd.x} cy={localEnd.y} r={5} fill="#3B82F6" className="cursor-move" />
        </>
      )}
    </svg>
  );
};

// Cursor Component
interface CursorOverlayProps {
  cursors: Cursor[];
  currentUserId: string;
}

const CursorOverlay: React.FC<CursorOverlayProps> = ({ cursors, currentUserId }) => {
  return (
    <>
      {cursors
        .filter((c) => c.userId !== currentUserId)
        .map((cursor) => (
          <div
            key={cursor.id}
            className="absolute pointer-events-none z-50 transition-all duration-75"
            style={{
              left: cursor.position.x,
              top: cursor.position.y,
            }}
          >
            <MousePointer2
              size={16}
              style={{ color: cursor.color }}
              className="drop-shadow-md"
            />
            <span
              className="ml-3 px-1.5 py-0.5 text-xs text-white rounded whitespace-nowrap"
              style={{ backgroundColor: cursor.color }}
            >
              {cursor.userName}
            </span>
          </div>
        ))}
    </>
  );
};

// Color Picker Component
interface ColorPickerProps {
  colors: string[];
  selected: string;
  onSelect: (color: string) => void;
}

const ColorPicker: React.FC<ColorPickerProps> = ({ colors, selected, onSelect }) => (
  <div className="flex gap-1 p-1">
    {colors.map((color) => (
      <button
        key={color}
        onClick={() => onSelect(color)}
        className={`w-6 h-6 rounded-full transition-transform ${
          selected === color ? 'ring-2 ring-white scale-110' : 'hover:scale-105'
        }`}
        style={{ backgroundColor: color }}
      />
    ))}
  </div>
);

// Main Whiteboard Component
interface WhiteboardCanvasProps {
  whiteboardId?: string;
  onSave?: (elements: WhiteboardElement[]) => void;
  onShare?: () => void;
  collaborators?: { id: string; name: string; color: string }[];
}

export const WhiteboardCanvas: React.FC<WhiteboardCanvasProps> = ({
  whiteboardId,
  onSave,
  onShare,
  collaborators = [],
}) => {
  // Demo data
  const demoElements: WhiteboardElement[] = useMemo(() => [
    {
      id: 'sticky-1',
      type: 'sticky',
      position: { x: 100, y: 100 },
      size: { width: 200, height: 200 },
      rotation: -2,
      zIndex: 1,
      isLocked: false,
      data: {
        type: 'sticky',
        content: 'Brainstorm ideas for the new feature',
        color: STICKY_COLORS[0],
        author: 'John Doe',
        votes: 5,
        votedBy: ['user-2', 'user-3'],
      } as StickyNoteData,
    },
    {
      id: 'sticky-2',
      type: 'sticky',
      position: { x: 350, y: 120 },
      size: { width: 200, height: 200 },
      rotation: 1,
      zIndex: 2,
      isLocked: false,
      data: {
        type: 'sticky',
        content: 'User research findings:\n- Users want faster load times\n- Mobile-first approach needed',
        color: STICKY_COLORS[2],
        author: 'Jane Smith',
        votes: 8,
        votedBy: ['user-1', 'user-3', 'user-4'],
      } as StickyNoteData,
    },
    {
      id: 'shape-1',
      type: 'shape',
      position: { x: 600, y: 150 },
      size: { width: 150, height: 100 },
      rotation: 0,
      zIndex: 3,
      isLocked: false,
      data: {
        type: 'shape',
        shape: 'rectangle',
        fill: '#3B82F620',
        stroke: '#3B82F6',
        strokeWidth: 2,
      } as ShapeData,
    },
    {
      id: 'text-1',
      type: 'text',
      position: { x: 100, y: 350 },
      size: { width: 300, height: 40 },
      rotation: 0,
      zIndex: 4,
      isLocked: false,
      data: {
        type: 'text',
        content: 'Project Timeline',
        fontSize: 24,
        fontWeight: 'bold',
        fontStyle: 'normal',
        textAlign: 'left',
        color: '#ffffff',
      } as TextData,
    },
  ], []);

  const [elements, setElements] = useState<WhiteboardElement[]>(demoElements);
  const [state, setState] = useState<CanvasState>({
    zoom: 1,
    pan: { x: 0, y: 0 },
    selectedIds: [],
    tool: 'select',
    isDrawing: false,
  });
  const [cursors, setCursors] = useState<Cursor[]>([]);
  const [showGrid, setShowGrid] = useState(true);
  const [stickyColor, setStickyColor] = useState(STICKY_COLORS[0]);
  const [shapeColor, setShapeColor] = useState(SHAPE_COLORS[0]);
  const [history, setHistory] = useState<WhiteboardElement[][]>([demoElements]);
  const [historyIndex, setHistoryIndex] = useState(0);

  const canvasRef = useRef<HTMLDivElement>(null);
  const currentUserId = 'current-user';

  // History management
  const pushHistory = useCallback((newElements: WhiteboardElement[]) => {
    setHistory((prev) => [...prev.slice(0, historyIndex + 1), newElements]);
    setHistoryIndex((prev) => prev + 1);
  }, [historyIndex]);

  const undo = useCallback(() => {
    if (historyIndex > 0) {
      setHistoryIndex((prev) => prev - 1);
      setElements(history[historyIndex - 1]);
    }
  }, [historyIndex, history]);

  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex((prev) => prev + 1);
      setElements(history[historyIndex + 1]);
    }
  }, [historyIndex, history]);

  // Element operations
  const handleSelect = useCallback((id: string, multi: boolean) => {
    setState((prev) => ({
      ...prev,
      selectedIds: multi
        ? prev.selectedIds.includes(id)
          ? prev.selectedIds.filter((i) => i !== id)
          : [...prev.selectedIds, id]
        : [id],
    }));
  }, []);

  const handleUpdateElement = useCallback((id: string, updates: Partial<WhiteboardElement>) => {
    setElements((prev) => {
      const newElements = prev.map((el) =>
        el.id === id ? { ...el, ...updates } : el
      );
      pushHistory(newElements);
      return newElements;
    });
  }, [pushHistory]);

  const handleVote = useCallback((id: string) => {
    setElements((prev) =>
      prev.map((el) => {
        if (el.id === id && el.data.type === 'sticky') {
          const data = el.data as StickyNoteData;
          const hasVoted = data.votedBy.includes(currentUserId);
          return {
            ...el,
            data: {
              ...data,
              votes: hasVoted ? data.votes - 1 : data.votes + 1,
              votedBy: hasVoted
                ? data.votedBy.filter((u) => u !== currentUserId)
                : [...data.votedBy, currentUserId],
            },
          };
        }
        return el;
      })
    );
  }, []);

  const handleDeleteSelected = useCallback(() => {
    if (state.selectedIds.length === 0) return;
    setElements((prev) => {
      const newElements = prev.filter((el) => !state.selectedIds.includes(el.id));
      pushHistory(newElements);
      return newElements;
    });
    setState((prev) => ({ ...prev, selectedIds: [] }));
  }, [state.selectedIds, pushHistory]);

  const handleDuplicateSelected = useCallback(() => {
    if (state.selectedIds.length === 0) return;
    const selected = elements.filter((el) => state.selectedIds.includes(el.id));
    const duplicates = selected.map((el) => ({
      ...el,
      id: generateId(),
      position: { x: el.position.x + 20, y: el.position.y + 20 },
      zIndex: Math.max(...elements.map((e) => e.zIndex)) + 1,
    }));
    setElements((prev) => {
      const newElements = [...prev, ...duplicates];
      pushHistory(newElements);
      return newElements;
    });
    setState((prev) => ({ ...prev, selectedIds: duplicates.map((d) => d.id) }));
  }, [state.selectedIds, elements, pushHistory]);

  // Canvas click handler
  const handleCanvasClick = useCallback((e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      setState((prev) => ({ ...prev, selectedIds: [] }));
    }

    if (!canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - state.pan.x) / state.zoom;
    const y = (e.clientY - rect.top - state.pan.y) / state.zoom;

    if (state.tool === 'sticky') {
      const newSticky: WhiteboardElement = {
        id: generateId(),
        type: 'sticky',
        position: { x: x - 100, y: y - 100 },
        size: { width: 200, height: 200 },
        rotation: Math.random() * 6 - 3,
        zIndex: Math.max(...elements.map((e) => e.zIndex), 0) + 1,
        isLocked: false,
        data: {
          type: 'sticky',
          content: '',
          color: stickyColor,
          author: 'Current User',
          votes: 0,
          votedBy: [],
        },
      };
      setElements((prev) => {
        const newElements = [...prev, newSticky];
        pushHistory(newElements);
        return newElements;
      });
      setState((prev) => ({ ...prev, selectedIds: [newSticky.id] }));
    }

    if (state.tool === 'rectangle' || state.tool === 'circle' || state.tool === 'triangle') {
      const shape = state.tool === 'rectangle' ? 'rectangle' : state.tool === 'circle' ? 'circle' : 'triangle';
      const newShape: WhiteboardElement = {
        id: generateId(),
        type: 'shape',
        position: { x: x - 50, y: y - 50 },
        size: { width: 100, height: 100 },
        rotation: 0,
        zIndex: Math.max(...elements.map((e) => e.zIndex), 0) + 1,
        isLocked: false,
        data: {
          type: 'shape',
          shape,
          fill: `${shapeColor}20`,
          stroke: shapeColor,
          strokeWidth: 2,
        },
      };
      setElements((prev) => {
        const newElements = [...prev, newShape];
        pushHistory(newElements);
        return newElements;
      });
      setState((prev) => ({ ...prev, selectedIds: [newShape.id] }));
    }

    if (state.tool === 'text') {
      const newText: WhiteboardElement = {
        id: generateId(),
        type: 'text',
        position: { x, y },
        size: { width: 200, height: 30 },
        rotation: 0,
        zIndex: Math.max(...elements.map((e) => e.zIndex), 0) + 1,
        isLocked: false,
        data: {
          type: 'text',
          content: '',
          fontSize: 16,
          fontWeight: 'normal',
          fontStyle: 'normal',
          textAlign: 'left',
          color: '#ffffff',
        },
      };
      setElements((prev) => {
        const newElements = [...prev, newText];
        pushHistory(newElements);
        return newElements;
      });
      setState((prev) => ({ ...prev, selectedIds: [newText.id] }));
    }
  }, [state.tool, state.pan, state.zoom, stickyColor, shapeColor, elements, pushHistory]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      if (e.key === 'Delete' || e.key === 'Backspace') {
        handleDeleteSelected();
      }
      if (e.key === 'd' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        handleDuplicateSelected();
      }
      if (e.key === 'z' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        if (e.shiftKey) {
          redo();
        } else {
          undo();
        }
      }
      if (e.key === 'v') setState((prev) => ({ ...prev, tool: 'select' }));
      if (e.key === 'h') setState((prev) => ({ ...prev, tool: 'pan' }));
      if (e.key === 's') setState((prev) => ({ ...prev, tool: 'sticky' }));
      if (e.key === 'r') setState((prev) => ({ ...prev, tool: 'rectangle' }));
      if (e.key === 'o') setState((prev) => ({ ...prev, tool: 'circle' }));
      if (e.key === 't') setState((prev) => ({ ...prev, tool: 'text' }));
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleDeleteSelected, handleDuplicateSelected, undo, redo]);

  // Zoom handlers
  const handleZoomIn = () => setState((prev) => ({ ...prev, zoom: Math.min(MAX_ZOOM, prev.zoom * 1.25) }));
  const handleZoomOut = () => setState((prev) => ({ ...prev, zoom: Math.max(MIN_ZOOM, prev.zoom / 1.25) }));
  const handleZoomReset = () => setState((prev) => ({ ...prev, zoom: 1, pan: { x: 0, y: 0 } }));

  // Lock/unlock selected
  const handleToggleLock = useCallback(() => {
    if (state.selectedIds.length === 0) return;
    setElements((prev) =>
      prev.map((el) =>
        state.selectedIds.includes(el.id)
          ? { ...el, isLocked: !el.isLocked }
          : el
      )
    );
  }, [state.selectedIds]);

  const selectedElements = elements.filter((el) => state.selectedIds.includes(el.id));
  const isAnyLocked = selectedElements.some((el) => el.isLocked);

  return (
    <TooltipProvider>
    <div className="flex flex-col h-full bg-gray-950">
      {/* Top Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-white">Whiteboard</h3>
          {elements.length > 0 && (
            <Badge variant="secondary" className="text-[10px] bg-gray-700 text-gray-300">
              {elements.length} elements
            </Badge>
          )}
          <span className="text-xs text-gray-600">•</span>
          <div className="flex items-center gap-1">
            {collaborators.slice(0, 4).map((c) => (
              <Tooltip key={c.id}>
                <TooltipTrigger asChild>
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-medium text-white cursor-default ring-2 ring-gray-900"
                    style={{ backgroundColor: c.color }}
                  >
                    {c.name.charAt(0)}
                  </div>
                </TooltipTrigger>
                <TooltipContent>{c.name}</TooltipContent>
              </Tooltip>
            ))}
            {collaborators.length > 4 && (
              <div className="w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center text-[10px] text-gray-300">
                +{collaborators.length - 4}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={undo}
                disabled={historyIndex === 0}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded disabled:opacity-40"
              >
                <Undo2 size={16} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Undo <kbd className="ml-1 text-[10px]">Ctrl+Z</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={redo}
                disabled={historyIndex >= history.length - 1}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded disabled:opacity-40"
              >
                <Redo2 size={16} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Redo <kbd className="ml-1 text-[10px]">Ctrl+Y</kbd></TooltipContent>
          </Tooltip>

          <div className="w-px h-4 bg-gray-700" />

          {/* Export dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-1 px-2 py-1.5 text-xs text-gray-300 hover:text-white hover:bg-gray-800 rounded">
                <Download size={13} />
                Export
                <ChevronDown size={10} className="opacity-60" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-gray-800 border-gray-700 text-white">
              <DropdownMenuItem
                className="text-xs text-gray-300 hover:bg-gray-700 cursor-pointer"
                onClick={() => {
                  const data = JSON.stringify({ elements, version: '1.0' }, null, 2);
                  const blob = new Blob([data], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a'); a.href = url; a.download = 'whiteboard.json'; a.click();
                  URL.revokeObjectURL(url);
                }}
              >
                Save as JSON
              </DropdownMenuItem>
              <DropdownMenuItem className="text-xs text-gray-300 hover:bg-gray-700 cursor-pointer" onClick={() => onShare?.()}>
                Share link
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-700" />
              <DropdownMenuItem
                className="text-xs text-red-400 hover:bg-red-900/20 cursor-pointer"
                onClick={() => {
                  if (confirm('Clear all elements? This cannot be undone.')) {
                    setElements([]);
                  }
                }}
              >
                Clear board
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <button
            onClick={onShare}
            className="flex items-center gap-1 px-3 py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            <Share2 size={12} />
            Share
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Toolbar */}
        <div className="flex flex-col gap-1 p-2 bg-gray-900 border-r border-gray-800">
          <ToolButton
            icon={<MousePointer2 size={18} />}
            isActive={state.tool === 'select'}
            onClick={() => setState((prev) => ({ ...prev, tool: 'select' }))}
            title="Select" shortcut="V"
          />
          <ToolButton
            icon={<Hand size={18} />}
            isActive={state.tool === 'pan'}
            onClick={() => setState((prev) => ({ ...prev, tool: 'pan' }))}
            title="Pan" shortcut="H"
          />
          
          <div className="w-full h-px bg-gray-700 my-1" />
          
          <div className="relative group">
            <ToolButton
              icon={<StickyNote size={18} />}
              isActive={state.tool === 'sticky'}
              onClick={() => setState((prev) => ({ ...prev, tool: 'sticky' }))}
              title="Sticky Note" shortcut="S"
            />
            <div className="absolute left-full ml-2 top-0 hidden group-hover:block bg-gray-800 border border-gray-700 rounded-lg p-2 z-50">
              <ColorPicker
                colors={STICKY_COLORS}
                selected={stickyColor}
                onSelect={setStickyColor}
              />
            </div>
          </div>
          
          <ToolButton
            icon={<Square size={18} />}
            isActive={state.tool === 'rectangle'}
            onClick={() => setState((prev) => ({ ...prev, tool: 'rectangle' }))}
            title="Rectangle" shortcut="R"
          />
          
          <ToolButton
            icon={<Circle size={18} />}
            isActive={state.tool === 'circle'}
            onClick={() => setState((prev) => ({ ...prev, tool: 'circle' }))}
            title="Circle" shortcut="O"
          />
          
          <ToolButton
            icon={<Triangle size={18} />}
            isActive={state.tool === 'triangle'}
            onClick={() => setState((prev) => ({ ...prev, tool: 'triangle' }))}
            title="Triangle"
          />
          
          <ToolButton
            icon={<ArrowRight size={18} />}
            isActive={state.tool === 'arrow'}
            onClick={() => setState((prev) => ({ ...prev, tool: 'arrow' }))}
            title="Connector"
          />
          
          <ToolButton
            icon={<Type size={18} />}
            isActive={state.tool === 'text'}
            onClick={() => setState((prev) => ({ ...prev, tool: 'text' }))}
            title="Text" shortcut="T"
          />
          
          <ToolButton
            icon={<Pencil size={18} />}
            isActive={state.tool === 'draw'}
            onClick={() => setState((prev) => ({ ...prev, tool: 'draw' }))}
            title="Draw" shortcut="D"
          />
          
          <div className="w-full h-px bg-gray-700 my-1" />
          
          <ToolButton
            icon={<MessageSquare size={18} />}
            isActive={state.tool === 'comment'}
            onClick={() => setState((prev) => ({ ...prev, tool: 'comment' }))}
            title="Comment"
          />
          
          <ToolButton
            icon={<Timer size={18} />}
            isActive={false}
            onClick={() => {}}
            title="Timer"
          />

          <div className="w-full h-px bg-gray-700 my-1" />

          {/* Eraser */}
          <ToolButton
            icon={<Eraser size={18} />}
            isActive={state.tool === 'eraser'}
            onClick={() => setState(prev => ({ ...prev, tool: 'eraser' }))}
            title="Eraser" shortcut="E"
          />
        </div>

        {/* Canvas */}
        <div className="flex-1 relative overflow-hidden">
          {/* Grid Background */}
          {showGrid && (
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                backgroundImage: `
                  linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px),
                  linear-gradient(to bottom, rgba(255,255,255,0.02) 1px, transparent 1px)
                `,
                backgroundSize: `${GRID_SIZE * state.zoom}px ${GRID_SIZE * state.zoom}px`,
                backgroundPosition: `${state.pan.x}px ${state.pan.y}px`,
              }}
            />
          )}

          {/* Canvas Content */}
          <div
            ref={canvasRef}
            className="absolute inset-0 cursor-crosshair"
            onClick={handleCanvasClick}
            style={{
              transform: `translate(${state.pan.x}px, ${state.pan.y}px) scale(${state.zoom})`,
              transformOrigin: '0 0',
            }}
          >
            {elements.map((element) => {
              switch (element.type) {
                case 'sticky':
                  return (
                    <StickyNoteElement
                      key={element.id}
                      element={element}
                      isSelected={state.selectedIds.includes(element.id)}
                      onSelect={handleSelect}
                      onUpdate={handleUpdateElement}
                      onVote={handleVote}
                      currentUserId={currentUserId}
                    />
                  );
                case 'shape':
                  return (
                    <ShapeElement
                      key={element.id}
                      element={element}
                      isSelected={state.selectedIds.includes(element.id)}
                      onSelect={handleSelect}
                    />
                  );
                case 'text':
                  return (
                    <TextElement
                      key={element.id}
                      element={element}
                      isSelected={state.selectedIds.includes(element.id)}
                      onSelect={handleSelect}
                      onUpdate={handleUpdateElement}
                    />
                  );
                case 'connector':
                  return (
                    <ConnectorElement
                      key={element.id}
                      element={element}
                      isSelected={state.selectedIds.includes(element.id)}
                      onSelect={handleSelect}
                    />
                  );
                default:
                  return null;
              }
            })}

            <CursorOverlay cursors={cursors} currentUserId={currentUserId} />
          </div>

          {/* Zoom Controls */}
          <div className="absolute bottom-4 left-4 flex items-center gap-1 bg-gray-800/90 backdrop-blur-sm rounded-lg p-1">
            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={handleZoomOut} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                  <ZoomOut size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Zoom out</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={handleZoomReset}
                  className="px-2 py-1 text-xs text-gray-300 hover:text-white hover:bg-gray-700 rounded min-w-[50px]"
                >
                  {Math.round(state.zoom * 100)}%
                </button>
              </TooltipTrigger>
              <TooltipContent>Reset zoom (click)</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={handleZoomIn} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                  <ZoomIn size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Zoom in</TooltipContent>
            </Tooltip>
            <div className="w-px h-4 bg-gray-600 mx-1" />
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={() => setShowGrid(!showGrid)}
                  className={`p-1.5 rounded ${showGrid ? 'text-blue-400' : 'text-gray-400 hover:text-white'}`}
                >
                  <Grid size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Toggle grid</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={() => setState(prev => ({ ...prev, zoom: 1, pan: { x: 0, y: 0 } }))}
                  className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                >
                  <Maximize2 size={16} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Fit to screen</TooltipContent>
            </Tooltip>
          </div>
        </div>

        {/* Right Panel (Selection Properties) */}
        {state.selectedIds.length > 0 && (
          <div className="w-64 bg-gray-900 border-l border-gray-800 p-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-medium text-white">
                {state.selectedIds.length === 1 ? 'Properties' : `${state.selectedIds.length} selected`}
              </h4>
              <div className="flex items-center gap-1">
                <button
                  onClick={handleToggleLock}
                  className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                  title={isAnyLocked ? 'Unlock' : 'Lock'}
                >
                  {isAnyLocked ? <Unlock size={14} /> : <Lock size={14} />}
                </button>
                <button
                  onClick={handleDuplicateSelected}
                  className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                  title="Duplicate"
                >
                  <Copy size={14} />
                </button>
                <button
                  onClick={handleDeleteSelected}
                  className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-900/20 rounded"
                  title="Delete"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>

            {selectedElements.length === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Position</label>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex items-center bg-gray-800 rounded px-2">
                      <span className="text-xs text-gray-500">X</span>
                      <input
                        type="number"
                        value={Math.round(selectedElements[0].position.x)}
                        onChange={(e) =>
                          handleUpdateElement(selectedElements[0].id, {
                            position: { ...selectedElements[0].position, x: Number(e.target.value) },
                          })
                        }
                        className="w-full bg-transparent py-1 px-2 text-sm text-white outline-none"
                      />
                    </div>
                    <div className="flex items-center bg-gray-800 rounded px-2">
                      <span className="text-xs text-gray-500">Y</span>
                      <input
                        type="number"
                        value={Math.round(selectedElements[0].position.y)}
                        onChange={(e) =>
                          handleUpdateElement(selectedElements[0].id, {
                            position: { ...selectedElements[0].position, y: Number(e.target.value) },
                          })
                        }
                        className="w-full bg-transparent py-1 px-2 text-sm text-white outline-none"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-400 block mb-1">Size</label>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex items-center bg-gray-800 rounded px-2">
                      <span className="text-xs text-gray-500">W</span>
                      <input
                        type="number"
                        value={Math.round(selectedElements[0].size.width)}
                        onChange={(e) =>
                          handleUpdateElement(selectedElements[0].id, {
                            size: { ...selectedElements[0].size, width: Number(e.target.value) },
                          })
                        }
                        className="w-full bg-transparent py-1 px-2 text-sm text-white outline-none"
                      />
                    </div>
                    <div className="flex items-center bg-gray-800 rounded px-2">
                      <span className="text-xs text-gray-500">H</span>
                      <input
                        type="number"
                        value={Math.round(selectedElements[0].size.height)}
                        onChange={(e) =>
                          handleUpdateElement(selectedElements[0].id, {
                            size: { ...selectedElements[0].size, height: Number(e.target.value) },
                          })
                        }
                        className="w-full bg-transparent py-1 px-2 text-sm text-white outline-none"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-400 block mb-1">Rotation</label>
                  <div className="flex items-center bg-gray-800 rounded px-2">
                    <input
                      type="number"
                      value={Math.round(selectedElements[0].rotation)}
                      onChange={(e) =>
                        handleUpdateElement(selectedElements[0].id, {
                          rotation: Number(e.target.value),
                        })
                      }
                      className="w-full bg-transparent py-1 px-2 text-sm text-white outline-none"
                    />
                    <span className="text-xs text-gray-500">°</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
    </TooltipProvider>
  );
};

export default WhiteboardCanvas;
