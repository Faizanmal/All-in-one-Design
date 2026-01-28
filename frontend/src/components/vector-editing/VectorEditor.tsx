'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { 
  PenTool, 
  Circle, 
  Square, 
  Triangle, 
  Star, 
  Minus, 
  Plus, 
  RotateCcw,
  RotateCw,
  Move,
  Scissors,
  Copy,
  Layers
} from 'lucide-react';

interface Point {
  x: number;
  y: number;
  handleIn?: { x: number; y: number };
  handleOut?: { x: number; y: number };
  cornerRadius?: number;
}

interface VectorPath {
  id: string;
  points: Point[];
  closed: boolean;
  stroke: string;
  strokeWidth: number;
  fill: string;
}

interface VectorEditorProps {
  width?: number;
  height?: number;
  onPathChange?: (paths: VectorPath[]) => void;
}

type Tool = 'pen' | 'select' | 'move' | 'rectangle' | 'ellipse' | 'polygon' | 'line';
type BooleanOp = 'union' | 'subtract' | 'intersect' | 'exclude';

export function VectorEditor({ width = 800, height = 600, onPathChange }: VectorEditorProps) {
  const [paths, setPaths] = useState<VectorPath[]>([]);
  const [activeTool, setActiveTool] = useState<Tool>('pen');
  const [selectedPaths, setSelectedPaths] = useState<string[]>([]);
  const [currentPath, setCurrentPath] = useState<VectorPath | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const canvasRef = useRef<SVGSVGElement>(null);

  const tools = [
    { id: 'pen', icon: PenTool, label: 'Pen Tool (P)' },
    { id: 'select', icon: Move, label: 'Select (V)' },
    { id: 'rectangle', icon: Square, label: 'Rectangle (R)' },
    { id: 'ellipse', icon: Circle, label: 'Ellipse (O)' },
    { id: 'polygon', icon: Triangle, label: 'Polygon' },
    { id: 'line', icon: Minus, label: 'Line (L)' },
  ];

  const booleanOperations: { op: BooleanOp; label: string; icon: React.ElementType }[] = [
    { op: 'union', label: 'Union', icon: Plus },
    { op: 'subtract', label: 'Subtract', icon: Minus },
    { op: 'intersect', label: 'Intersect', icon: Layers },
    { op: 'exclude', label: 'Exclude', icon: Scissors },
  ];

  const handleCanvasClick = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (activeTool !== 'pen') return;

    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (!currentPath) {
      // Start new path
      const newPath: VectorPath = {
        id: `path_${Date.now()}`,
        points: [{ x, y }],
        closed: false,
        stroke: '#000000',
        strokeWidth: 2,
        fill: 'none',
      };
      setCurrentPath(newPath);
      setIsDrawing(true);
    } else {
      // Add point to current path
      const firstPoint = currentPath.points[0];
      const distance = Math.sqrt(Math.pow(x - firstPoint.x, 2) + Math.pow(y - firstPoint.y, 2));

      if (distance < 10 && currentPath.points.length > 2) {
        // Close path
        const closedPath = { ...currentPath, closed: true };
        setPaths([...paths, closedPath]);
        setCurrentPath(null);
        setIsDrawing(false);
        onPathChange?.([...paths, closedPath]);
      } else {
        // Add new point
        setCurrentPath({
          ...currentPath,
          points: [...currentPath.points, { x, y }],
        });
      }
    }
  }, [activeTool, currentPath, paths, onPathChange]);

  const handleDoubleClick = useCallback(() => {
    if (currentPath && currentPath.points.length > 1) {
      setPaths([...paths, currentPath]);
      setCurrentPath(null);
      setIsDrawing(false);
      onPathChange?.([...paths, currentPath]);
    }
  }, [currentPath, paths, onPathChange]);

  const handleBooleanOperation = useCallback((op: BooleanOp) => {
    if (selectedPaths.length < 2) {
      alert('Select at least 2 paths for boolean operations');
      return;
    }
    // In production, send to API
    console.log(`Boolean ${op} operation on:`, selectedPaths);
  }, [selectedPaths]);

  const pathToSvg = (path: VectorPath): string => {
    if (path.points.length === 0) return '';

    let d = `M ${path.points[0].x} ${path.points[0].y}`;

    for (let i = 1; i < path.points.length; i++) {
      const point = path.points[i];
      const prevPoint = path.points[i - 1];

      if (point.handleIn && prevPoint.handleOut) {
        // Cubic bezier
        d += ` C ${prevPoint.handleOut.x} ${prevPoint.handleOut.y} ${point.handleIn.x} ${point.handleIn.y} ${point.x} ${point.y}`;
      } else {
        // Line
        d += ` L ${point.x} ${point.y}`;
      }
    }

    if (path.closed) {
      d += ' Z';
    }

    return d;
  };

  const handlePathSelect = (pathId: string, e: React.MouseEvent) => {
    if (e.shiftKey) {
      setSelectedPaths(prev => 
        prev.includes(pathId) 
          ? prev.filter(id => id !== pathId)
          : [...prev, pathId]
      );
    } else {
      setSelectedPaths([pathId]);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Toolbar */}
      <div className="flex items-center gap-2 p-2 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        {/* Tools */}
        <div className="flex items-center gap-1 border-r border-gray-200 dark:border-gray-700 pr-2">
          {tools.map(tool => (
            <button
              key={tool.id}
              onClick={() => setActiveTool(tool.id as Tool)}
              className={`p-2 rounded-md transition-colors ${
                activeTool === tool.id
                  ? 'bg-blue-500 text-white'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
              }`}
              title={tool.label}
            >
              <tool.icon className="w-5 h-5" />
            </button>
          ))}
        </div>

        {/* Boolean Operations */}
        <div className="flex items-center gap-1 border-r border-gray-200 dark:border-gray-700 pr-2">
          {booleanOperations.map(({ op, label, icon: Icon }) => (
            <button
              key={op}
              onClick={() => handleBooleanOperation(op)}
              disabled={selectedPaths.length < 2}
              className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              title={label}
            >
              <Icon className="w-5 h-5" />
            </button>
          ))}
        </div>

        {/* Path Actions */}
        <div className="flex items-center gap-1">
          <button
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300"
            title="Undo"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
          <button
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300"
            title="Redo"
          >
            <RotateCw className="w-5 h-5" />
          </button>
        </div>

        {/* Corner Radius */}
        <div className="flex items-center gap-2 ml-auto">
          <label className="text-sm text-gray-600 dark:text-gray-300">Corner Radius:</label>
          <input
            type="range"
            min="0"
            max="50"
            defaultValue="0"
            className="w-24"
          />
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 overflow-hidden p-4">
        <svg
          ref={canvasRef}
          width={width}
          height={height}
          className="bg-white dark:bg-gray-950 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 cursor-crosshair"
          onClick={handleCanvasClick}
          onDoubleClick={handleDoubleClick}
        >
          {/* Grid */}
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Existing paths */}
          {paths.map(path => (
            <g key={path.id} onClick={(e) => { e.stopPropagation(); handlePathSelect(path.id, e); }}>
              <path
                d={pathToSvg(path)}
                fill={path.fill}
                stroke={selectedPaths.includes(path.id) ? '#3b82f6' : path.stroke}
                strokeWidth={selectedPaths.includes(path.id) ? path.strokeWidth + 1 : path.strokeWidth}
                className="cursor-pointer"
              />
              {/* Control points for selected paths */}
              {selectedPaths.includes(path.id) && path.points.map((point, i) => (
                <circle
                  key={i}
                  cx={point.x}
                  cy={point.y}
                  r={5}
                  fill="#3b82f6"
                  stroke="white"
                  strokeWidth={2}
                  className="cursor-move"
                />
              ))}
            </g>
          ))}

          {/* Current path being drawn */}
          {currentPath && (
            <g>
              <path
                d={pathToSvg(currentPath)}
                fill="none"
                stroke="#3b82f6"
                strokeWidth={2}
                strokeDasharray="5,5"
              />
              {currentPath.points.map((point, i) => (
                <circle
                  key={i}
                  cx={point.x}
                  cy={point.y}
                  r={i === 0 ? 8 : 5}
                  fill={i === 0 ? '#22c55e' : '#3b82f6'}
                  stroke="white"
                  strokeWidth={2}
                />
              ))}
            </g>
          )}
        </svg>
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400">
        <span>
          {isDrawing ? `Drawing path (${currentPath?.points.length || 0} points)` : 'Ready'}
        </span>
        <span>{paths.length} paths • {selectedPaths.length} selected</span>
      </div>
    </div>
  );
}

export default VectorEditor;
