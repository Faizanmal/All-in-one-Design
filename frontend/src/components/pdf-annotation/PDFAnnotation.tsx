'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  FileText,
  Upload,
  Download,
  ZoomIn,
  ZoomOut,
  RotateCw,
  ChevronLeft,
  ChevronRight,
  Highlighter,
  Type,
  Square,
  Circle,
  Pencil,
  Trash2,
  Move,
  Check,
  X,
  Layers,
  Settings,
  Loader2,
  RefreshCw
} from 'lucide-react';

interface PDFPage {
  id: string;
  pageNumber: number;
  width: number;
  height: number;
  imageUrl?: string;
}

interface PDFAnnotation {
  id: string;
  pageNumber: number;
  type: 'highlight' | 'underline' | 'strikeout' | 'text' | 'freetext' | 'line' | 'arrow' | 'rectangle' | 'circle' | 'polygon' | 'ink' | 'stamp';
  bounds: { x: number; y: number; width: number; height: number };
  color: string;
  content?: string;
  points?: { x: number; y: number }[];
}

interface PDFDocument {
  id: string;
  name: string;
  file_size: number;
  page_count: number;
  pages: PDFPage[];
  annotations: PDFAnnotation[];
  status: 'uploading' | 'processing' | 'ready' | 'error';
}

interface PDFAnnotationProps {
  onAnnotationCreate?: (annotation: PDFAnnotation) => void;
  onAnnotationImport?: (annotations: PDFAnnotation[]) => void;
}

const ANNOTATION_TOOLS = [
  { type: 'highlight', icon: Highlighter, label: 'Highlight', color: '#fef08a' },
  { type: 'text', icon: Type, label: 'Add Text', color: '#000000' },
  { type: 'rectangle', icon: Square, label: 'Rectangle', color: '#3b82f6' },
  { type: 'circle', icon: Circle, label: 'Circle', color: '#3b82f6' },
  { type: 'ink', icon: Pencil, label: 'Draw', color: '#ef4444' },
  { type: 'arrow', icon: Move, label: 'Arrow', color: '#000000' },
];

export function PDFAnnotation({ onAnnotationCreate, onAnnotationImport }: PDFAnnotationProps) {
  const [document, setDocument] = useState<PDFDocument | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [zoom, setZoom] = useState(100);
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const [annotations, setAnnotations] = useState<PDFAnnotation[]>([]);
  const [selectedAnnotation, setSelectedAnnotation] = useState<PDFAnnotation | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importOptions, setImportOptions] = useState({
    convertToShapes: true,
    preserveColors: true,
    scaleToCanvas: true,
    createGroups: true
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawPath, setDrawPath] = useState<{ x: number; y: number }[]>([]);

  const handleFileUpload = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', files[0]);

      const response = await fetch('/api/v1/pdf/documents/', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const doc = await response.json();
        setDocument(doc);
        // Fetch pages
        const pagesResponse = await fetch(`/api/v1/pdf/documents/${doc.id}/pages/`);
        if (pagesResponse.ok) {
          const pages = await pagesResponse.json();
          setDocument({ ...doc, pages, status: 'ready' });
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!activeTool) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (canvas.width / rect.width);
    const y = (e.clientY - rect.top) * (canvas.height / rect.height);

    setIsDrawing(true);
    setDrawPath([{ x, y }]);
  }, [activeTool]);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !activeTool) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (canvas.width / rect.width);
    const y = (e.clientY - rect.top) * (canvas.height / rect.height);

    setDrawPath(prev => [...prev, { x, y }]);
  }, [isDrawing, activeTool]);

  const handleMouseUp = useCallback(() => {
    if (!isDrawing || drawPath.length < 2 || !activeTool) return;

    const startPoint = drawPath[0];
    const endPoint = drawPath[drawPath.length - 1];

    const newAnnotation: PDFAnnotation = {
      id: `annotation_${Date.now()}`,
      pageNumber: currentPage,
      type: activeTool as 'text' | 'circle' | 'line' | 'polygon' | 'highlight' | 'underline' | 'strikeout' | 'freetext' | 'arrow' | 'rectangle' | 'ink' | 'stamp',
      bounds: {
        x: Math.min(startPoint.x, endPoint.x),
        y: Math.min(startPoint.y, endPoint.y),
        width: Math.abs(endPoint.x - startPoint.x),
        height: Math.abs(endPoint.y - startPoint.y)
      },
      color: ANNOTATION_TOOLS.find(t => t.type === activeTool)?.color || '#000000',
      points: activeTool === 'ink' ? drawPath : undefined
    };

    setAnnotations([...annotations, newAnnotation]);
    onAnnotationCreate?.(newAnnotation);
    setIsDrawing(false);
    setDrawPath([]);
  }, [isDrawing, drawPath, activeTool, currentPage, annotations, onAnnotationCreate]);

  const handleImportToDesign = useCallback(async () => {
    if (!document || annotations.length === 0) return;

    setIsImporting(true);
    try {
      const response = await fetch('/api/v1/pdf/import-annotations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: document.id,
          annotation_ids: annotations.map(a => a.id),
          options: importOptions
        })
      });

      if (response.ok) {
        const result = await response.json();
        onAnnotationImport?.(annotations);
        setShowImportModal(false);
      }
    } catch (error) {
      console.error('Import error:', error);
    } finally {
      setIsImporting(false);
    }
  }, [document, annotations, importOptions, onAnnotationImport]);

  const handleDeleteAnnotation = useCallback((annotationId: string) => {
    setAnnotations(annotations.filter(a => a.id !== annotationId));
    if (selectedAnnotation?.id === annotationId) {
      setSelectedAnnotation(null);
    }
  }, [annotations, selectedAnnotation]);

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Toolbar */}
      <div className="flex items-center gap-2 p-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        {/* File actions */}
        <div className="flex items-center gap-1 border-r border-gray-200 dark:border-gray-700 pr-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Upload className="w-4 h-4" />
            Upload PDF
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={(e) => handleFileUpload(e.target.files)}
            className="hidden"
          />
        </div>

        {/* Annotation tools */}
        <div className="flex items-center gap-1 border-r border-gray-200 dark:border-gray-700 pr-2">
          {ANNOTATION_TOOLS.map(tool => (
            <button
              key={tool.type}
              onClick={() => setActiveTool(activeTool === tool.type ? null : tool.type)}
              className={`p-2 rounded-lg transition-colors ${
                activeTool === tool.type
                  ? 'bg-blue-500 text-white'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
              }`}
              title={tool.label}
            >
              <tool.icon className="w-5 h-5" />
            </button>
          ))}
        </div>

        {/* Zoom controls */}
        <div className="flex items-center gap-1 border-r border-gray-200 dark:border-gray-700 pr-2">
          <button
            onClick={() => setZoom(Math.max(25, zoom - 25))}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            <ZoomOut className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
          <span className="text-sm text-gray-600 dark:text-gray-300 w-12 text-center">
            {zoom}%
          </span>
          <button
            onClick={() => setZoom(Math.min(400, zoom + 25))}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            <ZoomIn className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
        </div>

        {/* Import action */}
        <button
          onClick={() => setShowImportModal(true)}
          disabled={annotations.length === 0}
          className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 ml-auto"
        >
          <Download className="w-4 h-4" />
          Import to Design
        </button>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* PDF Viewer */}
        <div className="flex-1 overflow-auto p-4">
          {isUploading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="w-12 h-12 mx-auto mb-4 text-blue-500 animate-spin" />
                <p className="text-gray-600 dark:text-gray-300">Processing PDF...</p>
              </div>
            </div>
          ) : document ? (
            <div className="flex flex-col items-center">
              {/* Page navigation */}
              <div className="flex items-center gap-4 mb-4">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage <= 1}
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg disabled:opacity-50"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  Page {currentPage} of {document.page_count}
                </span>
                <button
                  onClick={() => setCurrentPage(Math.min(document.page_count, currentPage + 1))}
                  disabled={currentPage >= document.page_count}
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg disabled:opacity-50"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>

              {/* Canvas */}
              <div 
                className="relative bg-white shadow-xl"
                style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}
              >
                <canvas
                  ref={canvasRef}
                  width={612}
                  height={792}
                  className="border border-gray-200"
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={() => setIsDrawing(false)}
                />
                
                {/* Rendered annotations */}
                <svg className="absolute inset-0 pointer-events-none" width="612" height="792">
                  {annotations
                    .filter(a => a.pageNumber === currentPage)
                    .map(annotation => (
                      <g key={annotation.id}>
                        {annotation.type === 'highlight' && (
                          <rect
                            x={annotation.bounds.x}
                            y={annotation.bounds.y}
                            width={annotation.bounds.width}
                            height={annotation.bounds.height}
                            fill={annotation.color}
                            opacity={0.5}
                          />
                        )}
                        {annotation.type === 'rectangle' && (
                          <rect
                            x={annotation.bounds.x}
                            y={annotation.bounds.y}
                            width={annotation.bounds.width}
                            height={annotation.bounds.height}
                            fill="none"
                            stroke={annotation.color}
                            strokeWidth={2}
                          />
                        )}
                        {annotation.type === 'circle' && (
                          <ellipse
                            cx={annotation.bounds.x + annotation.bounds.width / 2}
                            cy={annotation.bounds.y + annotation.bounds.height / 2}
                            rx={annotation.bounds.width / 2}
                            ry={annotation.bounds.height / 2}
                            fill="none"
                            stroke={annotation.color}
                            strokeWidth={2}
                          />
                        )}
                        {annotation.type === 'ink' && annotation.points && (
                          <path
                            d={`M ${annotation.points.map(p => `${p.x} ${p.y}`).join(' L ')}`}
                            fill="none"
                            stroke={annotation.color}
                            strokeWidth={2}
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        )}
                      </g>
                    ))}
                  
                  {/* Current drawing */}
                  {isDrawing && drawPath.length > 1 && (
                    <path
                      d={`M ${drawPath.map(p => `${p.x} ${p.y}`).join(' L ')}`}
                      fill="none"
                      stroke={ANNOTATION_TOOLS.find(t => t.type === activeTool)?.color || '#000'}
                      strokeWidth={2}
                      strokeDasharray={activeTool === 'ink' ? 'none' : '5,5'}
                    />
                  )}
                </svg>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center">
                  <FileText className="w-12 h-12 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Upload a PDF Document
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  Import PDF files to annotate and convert to design elements
                </p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Select PDF File
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Annotations Panel */}
        {document && (
          <div className="w-72 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white">Annotations</h3>
              <p className="text-xs text-gray-500">{annotations.length} total</p>
            </div>
            <div className="flex-1 overflow-auto p-2">
              {annotations.length > 0 ? (
                <div className="space-y-2">
                  {annotations.map(annotation => {
                    const tool = ANNOTATION_TOOLS.find(t => t.type === annotation.type);
                    return (
                      <div
                        key={annotation.id}
                        onClick={() => setSelectedAnnotation(annotation)}
                        className={`p-3 rounded-lg border cursor-pointer ${
                          selectedAnnotation?.id === annotation.id
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {tool && <tool.icon className="w-4 h-4" style={{ color: annotation.color }} />}
                            <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                              {annotation.type}
                            </span>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteAnnotation(annotation.id);
                            }}
                            className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          Page {annotation.pageNumber}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Layers className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No annotations yet</p>
                  <p className="text-xs">Select a tool and draw on the PDF</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Import Annotations to Design
            </h3>
            
            <div className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {annotations.length} annotations will be imported
              </p>

              <div className="space-y-3">
                {[
                  { key: 'convertToShapes', label: 'Convert to vector shapes' },
                  { key: 'preserveColors', label: 'Preserve colors' },
                  { key: 'scaleToCanvas', label: 'Scale to fit canvas' },
                  { key: 'createGroups', label: 'Group by page' },
                ].map(option => (
                  <label key={option.key} className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={importOptions[option.key as keyof typeof importOptions]}
                      onChange={(e) => setImportOptions({
                        ...importOptions,
                        [option.key]: e.target.checked
                      })}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{option.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowImportModal(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleImportToDesign}
                disabled={isImporting}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
              >
                {isImporting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                Import
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PDFAnnotation;
