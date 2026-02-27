'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Maximize,
  Minimize,
  Monitor,
  Tablet,
  Smartphone,
  Code,
  Copy,
  Check,
  Download,
  Settings,
  Eye,
  Ruler,
  Palette,
  Type,
  Box,
  Layers,
  ChevronLeft,
  ChevronRight,
  Grid,
  Zap,
  Share2,
  MessageSquare,
  Clock,
  Users,
  ExternalLink,
  FileCode,
  Layout,
  ArrowUpRight,
  Moon,
  Sun,
  Repeat,
  Timer,
  StickyNote,
  Keyboard,
  HelpCircle,
  X,
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

// Types
interface Slide {
  id: string;
  name: string;
  thumbnail: string;
  notes?: string;
  duration?: number;
}

interface Presentation {
  id: string;
  name: string;
  slides: Slide[];
  currentSlideIndex: number;
  isPlaying: boolean;
  autoAdvance: boolean;
  autoAdvanceInterval: number;
}

interface DevModeNode {
  id: string;
  name: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  opacity: number;
  styles: {
    fills: { type: string; color: string; opacity: number }[];
    strokes: { color: string; weight: number; style: string }[];
    effects: { type: string; color: string; offset: { x: number; y: number }; blur: number }[];
    cornerRadius: number | number[];
  };
  typography?: {
    fontFamily: string;
    fontWeight: number;
    fontSize: number;
    lineHeight: number | string;
    letterSpacing: number;
    textAlign: string;
  };
  constraints?: {
    horizontal: string;
    vertical: string;
  };
}

interface CodeExport {
  format: 'css' | 'tailwind' | 'scss' | 'styled-components' | 'react' | 'swift' | 'flutter';
  code: string;
}

// Default empty data — real data should be passed via props or fetched from the API
const defaultSlides: Slide[] = [];

const defaultSelectedNode: DevModeNode = {
  id: 'btn-primary',
  name: 'Primary Button',
  type: 'COMPONENT',
  x: 120,
  y: 456,
  width: 180,
  height: 48,
  rotation: 0,
  opacity: 1,
  styles: {
    fills: [{ type: 'SOLID', color: '#3B82F6', opacity: 1 }],
    strokes: [],
    effects: [
      { type: 'DROP_SHADOW', color: 'rgba(59, 130, 246, 0.3)', offset: { x: 0, y: 4 }, blur: 12 },
    ],
    cornerRadius: 8,
  },
  typography: {
    fontFamily: 'Inter',
    fontWeight: 600,
    fontSize: 16,
    lineHeight: 1.5,
    letterSpacing: 0,
    textAlign: 'center',
  },
};

const generateCode = (node: DevModeNode, format: CodeExport['format']): string => {
  switch (format) {
    case 'css':
      return `.${node.name.toLowerCase().replace(/\s+/g, '-')} {
  width: ${node.width}px;
  height: ${node.height}px;
  background-color: ${node.styles.fills[0]?.color || 'transparent'};
  border-radius: ${typeof node.styles.cornerRadius === 'number' ? node.styles.cornerRadius : node.styles.cornerRadius[0]}px;
  ${node.styles.effects.length > 0 ? `box-shadow: ${node.styles.effects.map(e => `${e.offset.x}px ${e.offset.y}px ${e.blur}px ${e.color}`).join(', ')};` : ''}
  ${node.typography ? `
  font-family: '${node.typography.fontFamily}', sans-serif;
  font-weight: ${node.typography.fontWeight};
  font-size: ${node.typography.fontSize}px;
  line-height: ${node.typography.lineHeight};
  text-align: ${node.typography.textAlign};` : ''}
}`;
    case 'tailwind':
      return `<button className="w-[${node.width}px] h-[${node.height}px] bg-blue-500 rounded-lg shadow-lg font-semibold text-base text-center hover:bg-blue-600 transition-colors">
  Button Text
</button>`;
    case 'react':
      return `import React from 'react';

interface ${node.name.replace(/\s+/g, '')}Props {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export const ${node.name.replace(/\s+/g, '')}: React.FC<${node.name.replace(/\s+/g, '')}Props> = ({
  children,
  onClick,
  disabled = false,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="px-6 py-3 bg-blue-500 text-white rounded-lg font-semibold shadow-lg hover:bg-blue-600 disabled:opacity-50 transition-all"
    >
      {children}
    </button>
  );
};`;
    case 'swift':
      return `import SwiftUI

struct ${node.name.replace(/\s+/g, '')}: View {
    var title: String
    var action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: ${node.typography?.fontSize || 16}, weight: .semibold))
                .foregroundColor(.white)
                .frame(width: ${node.width}, height: ${node.height})
                .background(Color.blue)
                .cornerRadius(${typeof node.styles.cornerRadius === 'number' ? node.styles.cornerRadius : 8})
                .shadow(color: Color.blue.opacity(0.3), radius: 6, x: 0, y: 4)
        }
    }
}`;
    default:
      return '// Code generation not available for this format';
  }
};

// Presentation Mode Component
interface PresentationModeProps {
  slides?: Slide[];
  onClose?: () => void;
}

export const PresentationMode: React.FC<PresentationModeProps> = ({
  slides = defaultSlides,
  onClose,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showNotes, setShowNotes] = useState(false);
  const [loopEnabled, setLoopEnabled] = useState(false);
  const [advanceInterval, setAdvanceInterval] = useState(5);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const clockRef = useRef<NodeJS.Timeout | null>(null);

  const currentSlide = slides[currentIndex];

  // Auto-advance
  useEffect(() => {
    if (isPlaying) {
      timerRef.current = setInterval(() => {
        setCurrentIndex((prev) => {
          const next = prev + 1;
          if (next >= slides.length) {
            if (loopEnabled) return 0;
            setIsPlaying(false);
            return prev;
          }
          return next;
        });
      }, advanceInterval * 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, slides.length, loopEnabled, advanceInterval]);

  // Presentation clock
  useEffect(() => {
    if (isPlaying) {
      clockRef.current = setInterval(() => setElapsedSeconds((s) => s + 1), 1000);
    } else {
      if (clockRef.current) clearInterval(clockRef.current);
    }
    return () => { if (clockRef.current) clearInterval(clockRef.current); };
  }, [isPlaying]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowRight':
        case ' ':
          setCurrentIndex((prev) => Math.min(prev + 1, slides.length - 1));
          break;
        case 'ArrowLeft':
          setCurrentIndex((prev) => Math.max(prev - 1, 0));
          break;
        case 'Home':
          setCurrentIndex(0);
          break;
        case 'End':
          setCurrentIndex(slides.length - 1);
          break;
        case 'Escape':
          if (showShortcuts) { setShowShortcuts(false); break; }
          if (isFullscreen) setIsFullscreen(false);
          else onClose?.();
          break;
        case 'f':
          setIsFullscreen(!isFullscreen);
          break;
        case 'n':
          setShowNotes((v) => !v);
          break;
        case 'l':
          setLoopEnabled((v) => !v);
          break;
        case '?':
          setShowShortcuts((v) => !v);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [slides.length, isFullscreen, onClose]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  // Fullscreen toggle
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  return (
    <TooltipProvider>
    <div
      ref={containerRef}
      className={`flex flex-col h-full bg-gray-950 ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className={`p-1.5 rounded ${showSidebar ? 'bg-gray-700 text-white' : 'text-gray-400 hover:bg-gray-800'}`}
              >
                <Layers size={16} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Toggle slide panel</TooltipContent>
          </Tooltip>
          {slides.length > 0 && (
            <>
              <h3 className="text-sm font-medium text-white truncate max-w-[200px]">{slides[currentIndex]?.name}</h3>
              <span className="text-xs text-gray-500">
                {currentIndex + 1} / {slides.length}
              </span>
            </>
          )}
          {isPlaying && (
            <span className="flex items-center gap-1 text-xs text-green-400">
              <Timer size={12} />
              {formatTime(elapsedSeconds)}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Playback controls */}
          <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-1">
            <Tooltip><TooltipTrigger asChild>
              <button onClick={() => setCurrentIndex(0)} className="p-1 text-gray-400 hover:text-white rounded">
                <SkipBack size={14} />
              </button>
            </TooltipTrigger><TooltipContent>First slide <kbd>Home</kbd></TooltipContent></Tooltip>
            <Tooltip><TooltipTrigger asChild>
              <button onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))} className="p-1 text-gray-400 hover:text-white rounded">
                <ChevronLeft size={14} />
              </button>
            </TooltipTrigger><TooltipContent>Previous <kbd>←</kbd></TooltipContent></Tooltip>
            <Tooltip><TooltipTrigger asChild>
              <button
                onClick={() => { setIsPlaying(!isPlaying); if (!isPlaying) setElapsedSeconds(0); }}
                className={`p-1.5 rounded ${isPlaying ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
              >
                {isPlaying ? <Pause size={14} /> : <Play size={14} />}
              </button>
            </TooltipTrigger><TooltipContent>{isPlaying ? 'Pause' : 'Play'} <kbd>Space</kbd></TooltipContent></Tooltip>
            <Tooltip><TooltipTrigger asChild>
              <button onClick={() => setCurrentIndex((prev) => Math.min(slides.length - 1, prev + 1))} className="p-1 text-gray-400 hover:text-white rounded">
                <ChevronRight size={14} />
              </button>
            </TooltipTrigger><TooltipContent>Next <kbd>→</kbd></TooltipContent></Tooltip>
            <Tooltip><TooltipTrigger asChild>
              <button onClick={() => setCurrentIndex(slides.length - 1)} className="p-1 text-gray-400 hover:text-white rounded">
                <SkipForward size={14} />
              </button>
            </TooltipTrigger><TooltipContent>Last slide <kbd>End</kbd></TooltipContent></Tooltip>
          </div>

          {/* Loop toggle */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setLoopEnabled(!loopEnabled)}
                className={`p-1.5 rounded ${loopEnabled ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-800'}`}
              >
                <Repeat size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Loop <kbd>L</kbd></TooltipContent>
          </Tooltip>

          {/* Interval */}
          <Tooltip>
            <TooltipTrigger asChild>
              <select
                value={advanceInterval}
                onChange={(e) => setAdvanceInterval(Number(e.target.value))}
                className="px-2 py-1 text-xs bg-gray-800 border border-gray-700 rounded text-gray-300"
              >
                {[3,5,10,15,30,60].map(s => (
                  <option key={s} value={s}>{s}s</option>
                ))}
              </select>
            </TooltipTrigger>
            <TooltipContent>Auto-advance interval</TooltipContent>
          </Tooltip>

          <div className="w-px h-4 bg-gray-700" />

          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setShowNotes(!showNotes)}
                className={`p-1.5 rounded ${showNotes ? 'bg-gray-700 text-white' : 'text-gray-400 hover:bg-gray-800'}`}
              >
                <StickyNote size={16} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Speaker notes <kbd>N</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded">
                <MessageSquare size={16} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Comments</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded">
                <Share2 size={16} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Share presentation</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setShowShortcuts(true)}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
              >
                <HelpCircle size={16} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Keyboard shortcuts <kbd>?</kbd></TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={toggleFullscreen}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
              >
                {isFullscreen ? <Minimize size={16} /> : <Maximize size={16} />}
              </button>
            </TooltipTrigger>
            <TooltipContent>Fullscreen <kbd>F</kbd></TooltipContent>
          </Tooltip>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Slide thumbnails sidebar */}
        {showSidebar && (
          <div className="w-48 bg-gray-900 border-r border-gray-800 overflow-y-auto p-2 space-y-2">
            {slides.length === 0 ? (
              <div className="text-center text-gray-600 text-xs p-4">No slides added</div>
            ) : (
              slides.map((slide, index) => (
                <button
                  key={slide.id}
                  onClick={() => setCurrentIndex(index)}
                  className={`w-full rounded-lg overflow-hidden border-2 transition-all ${
                    index === currentIndex
                      ? 'border-blue-500 ring-2 ring-blue-500/30'
                      : 'border-transparent hover:border-gray-700'
                  }`}
                >
                  <div className="aspect-[4/3] bg-gray-800 relative">
                    <div className="absolute inset-0 flex items-center justify-center text-gray-600">
                      <Layout size={24} />
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                      <p className="text-xs text-white truncate">{slide.name}</p>
                      <p className="text-[10px] text-gray-400">{index + 1}</p>
                    </div>
                    {slide.notes && (
                      <div className="absolute top-1 left-1">
                        <StickyNote size={10} className="text-yellow-400" />
                      </div>
                    )}
                  </div>
                </button>
              ))
            )}
          </div>
        )}

        {/* Main content area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Main slide view */}
          <div className="flex-1 flex items-center justify-center p-8 bg-gray-950">
            {slides.length === 0 ? (
              <div className="text-center">
                <Layout size={64} className="mx-auto text-gray-700 mb-4" />
                <p className="text-gray-400 font-medium">No slides yet</p>
                <p className="text-gray-600 text-sm mt-1">Add frames to this presentation</p>
              </div>
            ) : (
              <div className="w-full max-w-5xl aspect-[16/9] bg-gray-900 rounded-2xl shadow-2xl flex items-center justify-center relative">
                <Layout size={64} className="text-gray-700" />
                <div className="absolute bottom-4 left-4 text-sm text-gray-500">
                  {slides[currentIndex]?.name}
                </div>
              </div>
            )}
          </div>

          {/* Speaker notes panel */}
          {showNotes && slides.length > 0 && (
            <div className="h-48 border-t border-gray-800 bg-gray-900/80 flex flex-col">
              <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800">
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <StickyNote size={12} />
                  Speaker Notes
                </div>
                <button onClick={() => setShowNotes(false)} className="text-gray-500 hover:text-white">
                  <X size={14} />
                </button>
              </div>
              <div className="flex-1 p-4 overflow-y-auto">
                {slides[currentIndex]?.notes ? (
                  <p className="text-sm text-gray-300 leading-relaxed">{slides[currentIndex].notes}</p>
                ) : (
                  <p className="text-sm text-gray-600 italic">No notes for this slide</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1 bg-gray-800">
        <div
          className="h-full bg-blue-500 transition-all duration-300"
          style={{ width: slides.length > 0 ? `${((currentIndex + 1) / slides.length) * 100}%` : '0%' }}
        />
      </div>

      {/* Keyboard Shortcuts Overlay */}
      {showShortcuts && (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 w-80 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <Keyboard size={16} className="text-blue-400" /> Keyboard Shortcuts
              </h3>
              <button onClick={() => setShowShortcuts(false)} className="text-gray-400 hover:text-white">
                <X size={16} />
              </button>
            </div>
            <div className="space-y-2">
              {[
                ['← / →', 'Prev / Next slide'],
                ['Space', 'Next slide'],
                ['Home / End', 'First / Last slide'],
                ['F', 'Toggle fullscreen'],
                ['N', 'Toggle speaker notes'],
                ['L', 'Toggle loop'],
                ['Esc', 'Exit / Close'],
                ['?', 'Show this panel'],
              ].map(([key, desc]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">{desc}</span>
                  <kbd className="px-2 py-0.5 bg-gray-700 text-gray-200 rounded text-[10px] font-mono">{key}</kbd>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
    </TooltipProvider>
  );
};

// Dev Mode Component
interface DevModeProps {
  selectedNode?: DevModeNode;
  onCopyCode?: (code: string) => void;
  onExportAssets?: () => void;
}

export const DevMode: React.FC<DevModeProps> = ({
  selectedNode = defaultSelectedNode,
  onCopyCode,
  onExportAssets,
}) => {
  const [activeTab, setActiveTab] = useState<'inspect' | 'code' | 'assets'>('inspect');
  const [codeFormat, setCodeFormat] = useState<CodeExport['format']>('css');
  const [copiedCode, setCopiedCode] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [measureMode, setMeasureMode] = useState(false);
  const [unit, setUnit] = useState<'px' | 'rem' | '%'>('px');

  const generatedCode = generateCode(selectedNode, codeFormat);

  const handleCopyCode = useCallback(() => {
    navigator.clipboard.writeText(generatedCode);
    setCopiedCode(true);
    onCopyCode?.(generatedCode);
    setTimeout(() => setCopiedCode(false), 2000);
  }, [generatedCode, onCopyCode]);

  const convertValue = (value: number): string => {
    switch (unit) {
      case 'rem':
        return `${(value / 16).toFixed(3)}rem`;
      case '%':
        return `${value}%`;
      default:
        return `${value}px`;
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-850 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <Code size={18} className="text-green-400" />
          <h3 className="text-sm font-semibold text-white">Dev Mode</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`p-1.5 rounded ${showGrid ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
          >
            <Grid size={14} />
          </button>
          <button
            onClick={() => setMeasureMode(!measureMode)}
            className={`p-1.5 rounded ${measureMode ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
          >
            <Ruler size={14} />
          </button>
          <select
            value={unit}
            onChange={(e) => setUnit(e.target.value as typeof unit)}
            className="px-2 py-1 text-xs bg-gray-800 border border-gray-700 rounded text-gray-300"
          >
            <option value="px">px</option>
            <option value="rem">rem</option>
            <option value="%">%</option>
          </select>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        {(['inspect', 'code', 'assets'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'inspect' && selectedNode && (
          <div className="p-4 space-y-4">
            {/* Element info */}
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-2">
                <Box size={14} className="text-purple-400" />
                <span className="text-sm font-medium text-white">{selectedNode.name}</span>
                <span className="text-xs px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded">
                  {selectedNode.type}
                </span>
              </div>
              <p className="text-xs text-gray-500">ID: {selectedNode.id}</p>
            </div>

            {/* Position & Size */}
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-2">Layout</h4>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-gray-800/50 rounded p-2">
                  <span className="text-[10px] text-gray-500 block">X</span>
                  <span className="text-sm text-white">{convertValue(selectedNode.x)}</span>
                </div>
                <div className="bg-gray-800/50 rounded p-2">
                  <span className="text-[10px] text-gray-500 block">Y</span>
                  <span className="text-sm text-white">{convertValue(selectedNode.y)}</span>
                </div>
                <div className="bg-gray-800/50 rounded p-2">
                  <span className="text-[10px] text-gray-500 block">Width</span>
                  <span className="text-sm text-white">{convertValue(selectedNode.width)}</span>
                </div>
                <div className="bg-gray-800/50 rounded p-2">
                  <span className="text-[10px] text-gray-500 block">Height</span>
                  <span className="text-sm text-white">{convertValue(selectedNode.height)}</span>
                </div>
              </div>
            </div>

            {/* Fills */}
            {selectedNode.styles.fills.length > 0 && (
              <div>
                <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-2">Fill</h4>
                {selectedNode.styles.fills.map((fill, i) => (
                  <div key={i} className="flex items-center gap-2 bg-gray-800/50 rounded p-2">
                    <div
                      className="w-6 h-6 rounded border border-gray-600"
                      style={{ backgroundColor: fill.color }}
                    />
                    <div className="flex-1">
                      <span className="text-sm text-white font-mono">{fill.color}</span>
                      <span className="text-xs text-gray-500 ml-2">
                        {Math.round(fill.opacity * 100)}%
                      </span>
                    </div>
                    <button
                      onClick={() => navigator.clipboard.writeText(fill.color)}
                      className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                    >
                      <Copy size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Effects */}
            {selectedNode.styles.effects.length > 0 && (
              <div>
                <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-2">Effects</h4>
                {selectedNode.styles.effects.map((effect, i) => (
                  <div key={i} className="bg-gray-800/50 rounded p-2">
                    <span className="text-xs text-purple-400">{effect.type}</span>
                    <div className="text-sm text-gray-300 mt-1">
                      {effect.offset.x}px {effect.offset.y}px {effect.blur}px {effect.color}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Typography */}
            {selectedNode.typography && (
              <div>
                <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-2">Typography</h4>
                <div className="bg-gray-800/50 rounded p-3 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-500">Font</span>
                    <span className="text-sm text-white">
                      {selectedNode.typography.fontFamily} {selectedNode.typography.fontWeight}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-500">Size</span>
                    <span className="text-sm text-white">{selectedNode.typography.fontSize}px</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-500">Line Height</span>
                    <span className="text-sm text-white">{selectedNode.typography.lineHeight}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-500">Letter Spacing</span>
                    <span className="text-sm text-white">{selectedNode.typography.letterSpacing}px</span>
                  </div>
                </div>
              </div>
            )}

            {/* Corner Radius */}
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-2">Border Radius</h4>
              <div className="bg-gray-800/50 rounded p-2">
                <span className="text-sm text-white font-mono">
                  {typeof selectedNode.styles.cornerRadius === 'number'
                    ? `${selectedNode.styles.cornerRadius}px`
                    : selectedNode.styles.cornerRadius.join('px ')}
                </span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'code' && (
          <div className="p-4 space-y-4">
            {/* Format selector */}
            <div className="flex items-center gap-2 flex-wrap">
              {(['css', 'tailwind', 'react', 'swift'] as const).map((format) => (
                <button
                  key={format}
                  onClick={() => setCodeFormat(format)}
                  className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                    codeFormat === format
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {format.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Code preview */}
            <div className="relative">
              <pre className="bg-gray-950 rounded-lg p-4 text-sm font-mono text-gray-300 overflow-x-auto">
                <code>{generatedCode}</code>
              </pre>
              <button
                onClick={handleCopyCode}
                className="absolute top-2 right-2 p-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white transition-colors"
              >
                {copiedCode ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
              </button>
            </div>

            {/* Export options */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyCode}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <Copy size={12} />
                Copy Code
              </button>
              <button className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600">
                <Download size={12} />
                Download File
              </button>
            </div>
          </div>
        )}

        {activeTab === 'assets' && (
          <div className="p-4 space-y-4">
            <div className="bg-gray-800/50 rounded-lg p-4 text-center">
              <Download size={32} className="mx-auto text-gray-500 mb-2" />
              <p className="text-sm text-gray-300">Export Assets</p>
              <p className="text-xs text-gray-500 mt-1">
                Export selected elements as PNG, SVG, or PDF
              </p>
              <div className="flex items-center justify-center gap-2 mt-4">
                <button className="px-3 py-1.5 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600">
                  PNG
                </button>
                <button className="px-3 py-1.5 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600">
                  SVG
                </button>
                <button className="px-3 py-1.5 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600">
                  PDF
                </button>
              </div>
            </div>

            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-2">Export Settings</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between bg-gray-800/50 rounded p-2">
                  <span className="text-sm text-gray-300">Scale</span>
                  <select className="bg-gray-700 border-none text-sm text-white rounded px-2 py-1">
                    <option>1x</option>
                    <option>2x</option>
                    <option>3x</option>
                    <option>4x</option>
                  </select>
                </div>
                <div className="flex items-center justify-between bg-gray-800/50 rounded p-2">
                  <span className="text-sm text-gray-300">Include padding</span>
                  <input type="checkbox" className="rounded bg-gray-700 border-gray-600" />
                </div>
              </div>
            </div>

            <button
              onClick={onExportAssets}
              className="w-full py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Export Selected
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PresentationMode;
