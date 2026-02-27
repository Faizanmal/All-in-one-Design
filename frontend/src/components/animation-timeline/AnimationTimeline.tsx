'use client';

import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Square,
  Maximize2,
  Minimize2,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  Volume2,
  VolumeX,
  Plus,
  Trash2,
  Copy,
  Scissors,
  RotateCcw,
  Layers,
  ChevronDown,
  ChevronRight,
  Settings,
  Download,
  Upload,
  Zap,
  Diamond,
  Repeat,
  Magnet,
  StepBack,
  StepForward,
  ChevronUp,
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Badge } from '@/components/ui/badge';

// Types
interface Keyframe {
  id: string;
  time: number;
  value: number | string | { [key: string]: number };
  easing: string;
  isSelected?: boolean;
}

interface AnimationTrack {
  id: string;
  name: string;
  property: string;
  keyframes: Keyframe[];
  color: string;
  isExpanded?: boolean;
}

interface AnimationLayer {
  id: string;
  name: string;
  tracks: AnimationTrack[];
  isVisible: boolean;
  isLocked: boolean;
  isMuted: boolean;
  isExpanded: boolean;
  order: number;
}

interface AnimationComposition {
  id: string;
  name: string;
  duration: number;
  frameRate: number;
  layers: AnimationLayer[];
}

interface TimelineState {
  currentTime: number;
  isPlaying: boolean;
  zoom: number;
  scrollX: number;
  selection: {
    keyframes: string[];
    layers: string[];
    tracks: string[];
  };
}

// Constants
const TIMELINE_HEIGHT = 400;
const LAYER_HEIGHT = 32;
const TRACK_HEIGHT = 24;
const HEADER_HEIGHT = 48;
const RULER_HEIGHT = 28;
const SIDEBAR_WIDTH = 240;
const KEYFRAME_SIZE = 10;
const MIN_ZOOM = 0.1;
const MAX_ZOOM = 10;

// Color palette for tracks
const TRACK_COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
  '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
];

// Easing presets
const EASING_PRESETS = [
  { id: 'linear', name: 'Linear', curve: 'linear' },
  { id: 'ease', name: 'Ease', curve: 'ease' },
  { id: 'ease-in', name: 'Ease In', curve: 'ease-in' },
  { id: 'ease-out', name: 'Ease Out', curve: 'ease-out' },
  { id: 'ease-in-out', name: 'Ease In Out', curve: 'ease-in-out' },
  { id: 'spring', name: 'Spring', curve: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)' },
  { id: 'bounce', name: 'Bounce', curve: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)' },
];

// Helper functions
const formatTime = (seconds: number, fps: number = 30): string => {
  const totalFrames = Math.floor(seconds * fps);
  const frames = totalFrames % fps;
  const secs = Math.floor(seconds) % 60;
  const mins = Math.floor(seconds / 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}:${frames.toString().padStart(2, '0')}`;
};

const timeToPosition = (time: number, zoom: number, pixelsPerSecond: number = 100): number => {
  return time * pixelsPerSecond * zoom;
};

const positionToTime = (position: number, zoom: number, pixelsPerSecond: number = 100): number => {
  return position / (pixelsPerSecond * zoom);
};

// Keyframe Component
interface KeyframeMarkerProps {
  keyframe: Keyframe;
  trackColor: string;
  zoom: number;
  isSelected: boolean;
  onSelect: (id: string, multi: boolean) => void;
  onDrag: (id: string, newTime: number) => void;
  onDoubleClick: (id: string) => void;
}

const KeyframeMarker: React.FC<KeyframeMarkerProps> = ({
  keyframe,
  trackColor,
  zoom,
  isSelected,
  onSelect,
  onDrag,
  onDoubleClick,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const startXRef = useRef(0);
  const startTimeRef = useRef(0);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
    startXRef.current = e.clientX;
    startTimeRef.current = keyframe.time;
    onSelect(keyframe.id, e.shiftKey || e.metaKey);
  }, [keyframe.id, keyframe.time, onSelect]);

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      const deltaX = e.clientX - startXRef.current;
      const deltaTime = positionToTime(deltaX, zoom);
      const newTime = Math.max(0, startTimeRef.current + deltaTime);
      onDrag(keyframe.id, newTime);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, keyframe.id, zoom, onDrag]);

  const position = timeToPosition(keyframe.time, zoom);

  return (
    <div
      className={`absolute cursor-pointer transition-transform duration-75 ${
        isDragging ? 'scale-125 z-50' : 'hover:scale-110'
      }`}
      style={{
        left: position - KEYFRAME_SIZE / 2,
        top: '50%',
        transform: 'translateY(-50%)',
      }}
      onMouseDown={handleMouseDown}
      onDoubleClick={() => onDoubleClick(keyframe.id)}
    >
      <Diamond
        size={KEYFRAME_SIZE}
        fill={isSelected ? '#fff' : trackColor}
        stroke={isSelected ? trackColor : 'transparent'}
        strokeWidth={2}
        className="rotate-0"
      />
    </div>
  );
};

// Track Component
interface TrackRowProps {
  track: AnimationTrack;
  zoom: number;
  selectedKeyframes: string[];
  onKeyframeSelect: (id: string, multi: boolean) => void;
  onKeyframeDrag: (id: string, newTime: number) => void;
  onKeyframeDoubleClick: (id: string) => void;
  onAddKeyframe: (trackId: string, time: number) => void;
}

const TrackRow: React.FC<TrackRowProps> = ({
  track,
  zoom,
  selectedKeyframes,
  onKeyframeSelect,
  onKeyframeDrag,
  onKeyframeDoubleClick,
  onAddKeyframe,
}) => {
  const trackRef = useRef<HTMLDivElement>(null);

  const handleDoubleClick = useCallback((e: React.MouseEvent) => {
    if (!trackRef.current) return;
    const rect = trackRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const time = positionToTime(x, zoom);
    onAddKeyframe(track.id, time);
  }, [track.id, zoom, onAddKeyframe]);

  return (
    <div
      ref={trackRef}
      className="relative h-6 bg-gray-800/50 border-b border-gray-700/50"
      onDoubleClick={handleDoubleClick}
    >
      {/* Track background with gradient */}
      <div 
        className="absolute inset-0 opacity-10"
        style={{ 
          background: `linear-gradient(90deg, ${track.color}20 0%, transparent 100%)`
        }}
      />
      
      {/* Keyframes */}
      {track.keyframes.map((keyframe) => (
        <KeyframeMarker
          key={keyframe.id}
          keyframe={keyframe}
          trackColor={track.color}
          zoom={zoom}
          isSelected={selectedKeyframes.includes(keyframe.id)}
          onSelect={onKeyframeSelect}
          onDrag={onKeyframeDrag}
          onDoubleClick={onKeyframeDoubleClick}
        />
      ))}

      {/* Connection lines between keyframes */}
      {track.keyframes.length > 1 && track.keyframes.map((kf, i) => {
        if (i === 0) return null;
        const prevKf = track.keyframes[i - 1];
        const startX = timeToPosition(prevKf.time, zoom);
        const endX = timeToPosition(kf.time, zoom);
        return (
          <div
            key={`line-${prevKf.id}-${kf.id}`}
            className="absolute h-0.5 top-1/2 -translate-y-1/2"
            style={{
              left: startX,
              width: endX - startX,
              backgroundColor: track.color,
              opacity: 0.4,
            }}
          />
        );
      })}
    </div>
  );
};

// Layer Component
interface LayerRowProps {
  layer: AnimationLayer;
  zoom: number;
  selectedKeyframes: string[];
  onToggleVisibility: (id: string) => void;
  onToggleLock: (id: string) => void;
  onToggleMute: (id: string) => void;
  onToggleExpand: (id: string) => void;
  onKeyframeSelect: (id: string, multi: boolean) => void;
  onKeyframeDrag: (id: string, newTime: number) => void;
  onKeyframeDoubleClick: (id: string) => void;
  onAddKeyframe: (trackId: string, time: number) => void;
  onDeleteLayer: (id: string) => void;
  onDuplicateLayer: (id: string) => void;
}

const LayerRow: React.FC<LayerRowProps> = ({
  layer,
  zoom,
  selectedKeyframes,
  onToggleVisibility,
  onToggleLock,
  onToggleMute,
  onToggleExpand,
  onKeyframeSelect,
  onKeyframeDrag,
  onKeyframeDoubleClick,
  onAddKeyframe,
  onDeleteLayer,
  onDuplicateLayer,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className="border-b border-gray-700"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Layer Header */}
      <div className="flex items-center h-8 bg-gray-800 hover:bg-gray-750 transition-colors">
        {/* Sidebar */}
        <div 
          className="flex items-center gap-1 px-2 border-r border-gray-700"
          style={{ width: SIDEBAR_WIDTH }}
        >
          <button
            onClick={() => onToggleExpand(layer.id)}
            className="p-0.5 hover:bg-gray-700 rounded"
          >
            {layer.isExpanded ? (
              <ChevronDown size={14} className="text-gray-400" />
            ) : (
              <ChevronRight size={14} className="text-gray-400" />
            )}
          </button>
          
          <span className="text-sm text-gray-200 truncate flex-1 font-medium">
            {layer.name}
          </span>

          <div className="flex items-center gap-0.5">
            <button
              onClick={() => onToggleVisibility(layer.id)}
              className={`p-0.5 rounded transition-colors ${
                layer.isVisible ? 'text-gray-400 hover:bg-gray-700' : 'text-gray-600'
              }`}
            >
              {layer.isVisible ? <Eye size={12} /> : <EyeOff size={12} />}
            </button>
            <button
              onClick={() => onToggleLock(layer.id)}
              className={`p-0.5 rounded transition-colors ${
                layer.isLocked ? 'text-yellow-500' : 'text-gray-400 hover:bg-gray-700'
              }`}
            >
              {layer.isLocked ? <Lock size={12} /> : <Unlock size={12} />}
            </button>
            <button
              onClick={() => onToggleMute(layer.id)}
              className={`p-0.5 rounded transition-colors ${
                layer.isMuted ? 'text-red-500' : 'text-gray-400 hover:bg-gray-700'
              }`}
            >
              {layer.isMuted ? <VolumeX size={12} /> : <Volume2 size={12} />}
            </button>
          </div>

          {isHovered && (
            <div className="flex items-center gap-0.5 ml-1">
              <button
                onClick={() => onDuplicateLayer(layer.id)}
                className="p-0.5 text-gray-400 hover:bg-gray-700 rounded"
              >
                <Copy size={12} />
              </button>
              <button
                onClick={() => onDeleteLayer(layer.id)}
                className="p-0.5 text-gray-400 hover:bg-red-600/20 hover:text-red-400 rounded"
              >
                <Trash2 size={12} />
              </button>
            </div>
          )}
        </div>

        {/* Layer timeline area */}
        <div className="flex-1 h-full bg-gray-850" />
      </div>

      {/* Tracks (when expanded) */}
      {layer.isExpanded && layer.tracks.map((track) => (
        <div key={track.id} className="flex items-center">
          {/* Track sidebar */}
          <div 
            className="flex items-center gap-2 px-6 py-1 border-r border-gray-700 bg-gray-850"
            style={{ width: SIDEBAR_WIDTH }}
          >
            <div 
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: track.color }}
            />
            <span className="text-xs text-gray-400 truncate">
              {track.name}
            </span>
          </div>

          {/* Track timeline */}
          <div className="flex-1">
            <TrackRow
              track={track}
              zoom={zoom}
              selectedKeyframes={selectedKeyframes}
              onKeyframeSelect={onKeyframeSelect}
              onKeyframeDrag={onKeyframeDrag}
              onKeyframeDoubleClick={onKeyframeDoubleClick}
              onAddKeyframe={onAddKeyframe}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

// Time Ruler Component
interface TimeRulerProps {
  duration: number;
  zoom: number;
  currentTime: number;
  frameRate: number;
  onSeek: (time: number) => void;
}

const TimeRuler: React.FC<TimeRulerProps> = ({
  duration,
  zoom,
  currentTime,
  frameRate,
  onSeek,
}) => {
  const rulerRef = useRef<HTMLDivElement>(null);

  const handleClick = useCallback((e: React.MouseEvent) => {
    if (!rulerRef.current) return;
    const rect = rulerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const time = Math.max(0, Math.min(duration, positionToTime(x, zoom)));
    onSeek(time);
  }, [duration, zoom, onSeek]);

  // Calculate tick marks
  const ticks = useMemo(() => {
    const result: { time: number; isMajor: boolean }[] = [];
    const tickInterval = zoom < 0.5 ? 5 : zoom < 1 ? 1 : 0.5;
    const majorInterval = zoom < 0.5 ? 10 : zoom < 1 ? 5 : 1;
    
    for (let t = 0; t <= duration; t += tickInterval) {
      result.push({
        time: t,
        isMajor: t % majorInterval === 0,
      });
    }
    return result;
  }, [duration, zoom]);

  return (
    <div
      ref={rulerRef}
      className="relative h-7 bg-gray-900 border-b border-gray-700 cursor-pointer"
      onClick={handleClick}
    >
      {/* Tick marks */}
      {ticks.map(({ time, isMajor }) => (
        <div
          key={time}
          className="absolute top-0 flex flex-col items-center"
          style={{ left: timeToPosition(time, zoom) }}
        >
          <div
            className={`w-px ${isMajor ? 'h-3 bg-gray-500' : 'h-2 bg-gray-600'}`}
          />
          {isMajor && (
            <span className="text-[10px] text-gray-500 mt-0.5">
              {formatTime(time, frameRate)}
            </span>
          )}
        </div>
      ))}

      {/* Playhead indicator */}
      <div
        className="absolute top-0 w-3 h-3 -ml-1.5 bg-red-500"
        style={{ 
          left: timeToPosition(currentTime, zoom),
          clipPath: 'polygon(50% 100%, 0 0, 100% 0)',
        }}
      />
    </div>
  );
};

// Playhead Component
interface PlayheadProps {
  currentTime: number;
  zoom: number;
  height: number;
}

const Playhead: React.FC<PlayheadProps> = ({ currentTime, zoom, height }) => {
  return (
    <div
      className="absolute top-0 w-px bg-red-500 pointer-events-none z-40"
      style={{
        left: timeToPosition(currentTime, zoom) + SIDEBAR_WIDTH,
        height,
      }}
    >
      <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-red-500 rounded-full" />
    </div>
  );
};

// Main Animation Timeline Component
interface AnimationTimelineProps {
  composition?: AnimationComposition;
  onCompositionChange?: (composition: AnimationComposition) => void;
  onExport?: (format: 'lottie' | 'gif' | 'video') => void;
  onImport?: (file: File) => void;
}

export const AnimationTimeline: React.FC<AnimationTimelineProps> = ({
  composition: externalComposition,
  onCompositionChange,
  onExport,
  onImport,
}) => {
  // Demo composition for standalone usage
  const defaultComposition: AnimationComposition = useMemo(() => ({
    id: 'demo',
    name: 'Demo Animation',
    duration: 10,
    frameRate: 30,
    layers: [
      {
        id: 'layer-1',
        name: 'Rectangle',
        isVisible: true,
        isLocked: false,
        isMuted: false,
        isExpanded: true,
        order: 0,
        tracks: [
          {
            id: 'track-1-1',
            name: 'Position X',
            property: 'position.x',
            color: TRACK_COLORS[0],
            keyframes: [
              { id: 'kf-1', time: 0, value: 0, easing: 'ease' },
              { id: 'kf-2', time: 2.5, value: 200, easing: 'ease-out' },
              { id: 'kf-3', time: 5, value: 400, easing: 'ease' },
            ],
          },
          {
            id: 'track-1-2',
            name: 'Opacity',
            property: 'opacity',
            color: TRACK_COLORS[1],
            keyframes: [
              { id: 'kf-4', time: 0, value: 1, easing: 'linear' },
              { id: 'kf-5', time: 3, value: 0.5, easing: 'ease-in-out' },
              { id: 'kf-6', time: 6, value: 1, easing: 'linear' },
            ],
          },
        ],
      },
      {
        id: 'layer-2',
        name: 'Circle',
        isVisible: true,
        isLocked: false,
        isMuted: false,
        isExpanded: false,
        order: 1,
        tracks: [
          {
            id: 'track-2-1',
            name: 'Scale',
            property: 'scale',
            color: TRACK_COLORS[2],
            keyframes: [
              { id: 'kf-7', time: 0, value: 1, easing: 'spring' },
              { id: 'kf-8', time: 4, value: 1.5, easing: 'bounce' },
              { id: 'kf-9', time: 8, value: 1, easing: 'spring' },
            ],
          },
        ],
      },
      {
        id: 'layer-3',
        name: 'Text Label',
        isVisible: true,
        isLocked: true,
        isMuted: false,
        isExpanded: false,
        order: 2,
        tracks: [
          {
            id: 'track-3-1',
            name: 'Rotation',
            property: 'rotation',
            color: TRACK_COLORS[3],
            keyframes: [
              { id: 'kf-10', time: 0, value: 0, easing: 'ease' },
              { id: 'kf-11', time: 5, value: 360, easing: 'ease' },
            ],
          },
        ],
      },
    ],
  }), []);

  const [composition, setComposition] = useState<AnimationComposition>(
    externalComposition || defaultComposition
  );

  const [state, setState] = useState<TimelineState>({
    currentTime: 0,
    isPlaying: false,
    zoom: 1,
    scrollX: 0,
    selection: {
      keyframes: [],
      layers: [],
      tracks: [],
    },
  });

  const [isFullscreen, setIsFullscreen] = useState(false);
  const [loopEnabled, setLoopEnabled] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [snapEnabled, setSnapEnabled] = useState(true);
  const [resizeHandleTime, setResizeHandleTime] = useState<string | null>(null);
  const importInputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number | null>(null);

  // Playback logic
  useEffect(() => {
    if (!state.isPlaying) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }

    let lastTime = performance.now();

    const animate = (currentTime: number) => {
      const deltaTime = (currentTime - lastTime) / 1000;
      lastTime = currentTime;

      setState((prev) => {
        let newTime = prev.currentTime + deltaTime * playbackSpeed;
        if (newTime >= composition.duration) {
          newTime = loopEnabled ? 0 : composition.duration;
          if (!loopEnabled) cancelAnimationFrame(animationRef.current!);
        }
        return { ...prev, currentTime: newTime, isPlaying: loopEnabled || newTime < composition.duration };
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [state.isPlaying, composition.duration]);

  const handleDeleteSelectedKeyframes = useCallback(() => {
    setComposition((prev) => ({
      ...prev,
      layers: prev.layers.map((layer) => ({
        ...layer,
        tracks: layer.tracks.map((track) => ({
          ...track,
          keyframes: track.keyframes.filter(
            (kf) => !state.selection.keyframes.includes(kf.id)
          ),
        })),
      })),
    }));
    setState((prev) => ({
      ...prev,
      selection: { ...prev.selection, keyframes: [] },
    }));
  }, [state.selection.keyframes]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return;

      switch (e.key) {
        case ' ':
          e.preventDefault();
          setState((prev) => ({ ...prev, isPlaying: !prev.isPlaying }));
          break;
        case 'Home':
          setState((prev) => ({ ...prev, currentTime: 0 }));
          break;
        case 'End':
          setState((prev) => ({ ...prev, currentTime: composition.duration }));
          break;
        case 'ArrowLeft':
          setState((prev) => ({
            ...prev,
            currentTime: Math.max(0, prev.currentTime - 1 / composition.frameRate),
          }));
          break;
        case 'ArrowRight':
          setState((prev) => ({
            ...prev,
            currentTime: Math.min(
              composition.duration,
              prev.currentTime + 1 / composition.frameRate
            ),
          }));
          break;
        case 'Delete':
        case 'Backspace':
          if (state.selection.keyframes.length > 0) {
            handleDeleteSelectedKeyframes();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [composition.duration, composition.frameRate, handleDeleteSelectedKeyframes, state.selection.keyframes]);

  // Handlers
  const handlePlay = () => setState((prev) => ({ ...prev, isPlaying: true }));
  const handlePause = () => setState((prev) => ({ ...prev, isPlaying: false }));
  const handleStop = () => setState((prev) => ({ ...prev, isPlaying: false, currentTime: 0 }));
  const handleSeek = (time: number) => setState((prev) => ({ ...prev, currentTime: time }));
  
  const handleZoomIn = () => setState((prev) => ({
    ...prev,
    zoom: Math.min(MAX_ZOOM, prev.zoom * 1.5),
  }));
  
  const handleZoomOut = () => setState((prev) => ({
    ...prev,
    zoom: Math.max(MIN_ZOOM, prev.zoom / 1.5),
  }));

  const handleToggleFullscreen = () => setIsFullscreen(!isFullscreen);
  const handleStepBackward = () => setState(prev => ({ ...prev, currentTime: Math.max(0, prev.currentTime - 1 / composition.frameRate) }));
  const handleStepForward = () => setState(prev => ({ ...prev, currentTime: Math.min(composition.duration, prev.currentTime + 1 / composition.frameRate) }));
  const handleImportClick = () => importInputRef.current?.click();
  const handleImportFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onImport?.(file);
    e.target.value = '';
  };

  const handleKeyframeSelect = useCallback((id: string, multi: boolean) => {
    setState((prev) => ({
      ...prev,
      selection: {
        ...prev.selection,
        keyframes: multi
          ? prev.selection.keyframes.includes(id)
            ? prev.selection.keyframes.filter((k) => k !== id)
            : [...prev.selection.keyframes, id]
          : [id],
      },
    }));
  }, []);

  const handleKeyframeDrag = useCallback((id: string, newTime: number) => {
    setComposition((prev) => ({
      ...prev,
      layers: prev.layers.map((layer) => ({
        ...layer,
        tracks: layer.tracks.map((track) => ({
          ...track,
          keyframes: track.keyframes.map((kf) =>
            kf.id === id ? { ...kf, time: newTime } : kf
          ),
        })),
      })),
    }));
  }, []);

  const handleKeyframeDoubleClick = useCallback((id: string) => {
    // Open keyframe editor modal (placeholder)
    console.log('Edit keyframe:', id);
  }, []);

  const handleAddKeyframe = useCallback((trackId: string, time: number) => {
    const newKeyframe: Keyframe = {
      id: `kf-${Date.now()}`,
      time,
      value: 0,
      easing: 'ease',
    };

    setComposition((prev) => ({
      ...prev,
      layers: prev.layers.map((layer) => ({
        ...layer,
        tracks: layer.tracks.map((track) =>
          track.id === trackId
            ? {
                ...track,
                keyframes: [...track.keyframes, newKeyframe].sort(
                  (a, b) => a.time - b.time
                ),
              }
            : track
        ),
      })),
    }));
  }, []);

  const handleToggleLayerVisibility = useCallback((id: string) => {
    setComposition((prev) => ({
      ...prev,
      layers: prev.layers.map((layer) =>
        layer.id === id ? { ...layer, isVisible: !layer.isVisible } : layer
      ),
    }));
  }, []);

  const handleToggleLayerLock = useCallback((id: string) => {
    setComposition((prev) => ({
      ...prev,
      layers: prev.layers.map((layer) =>
        layer.id === id ? { ...layer, isLocked: !layer.isLocked } : layer
      ),
    }));
  }, []);

  const handleToggleLayerMute = useCallback((id: string) => {
    setComposition((prev) => ({
      ...prev,
      layers: prev.layers.map((layer) =>
        layer.id === id ? { ...layer, isMuted: !layer.isMuted } : layer
      ),
    }));
  }, []);

  const handleToggleLayerExpand = useCallback((id: string) => {
    setComposition((prev) => ({
      ...prev,
      layers: prev.layers.map((layer) =>
        layer.id === id ? { ...layer, isExpanded: !layer.isExpanded } : layer
      ),
    }));
  }, []);

  const handleDeleteLayer = useCallback((id: string) => {
    setComposition((prev) => ({
      ...prev,
      layers: prev.layers.filter((layer) => layer.id !== id),
    }));
  }, []);

  const handleDuplicateLayer = useCallback((id: string) => {
    setComposition((prev) => {
      const layerToDuplicate = prev.layers.find((l) => l.id === id);
      if (!layerToDuplicate) return prev;

      const newLayer: AnimationLayer = {
        ...layerToDuplicate,
        id: `layer-${Date.now()}`,
        name: `${layerToDuplicate.name} Copy`,
        tracks: layerToDuplicate.tracks.map((track) => ({
          ...track,
          id: `track-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          keyframes: track.keyframes.map((kf) => ({
            ...kf,
            id: `kf-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          })),
        })),
      };

      return {
        ...prev,
        layers: [...prev.layers, newLayer],
      };
    });
  }, []);

  const handleAddLayer = useCallback(() => {
    const newLayer: AnimationLayer = {
      id: `layer-${Date.now()}`,
      name: `Layer ${composition.layers.length + 1}`,
      isVisible: true,
      isLocked: false,
      isMuted: false,
      isExpanded: true,
      order: composition.layers.length,
      tracks: [
        {
          id: `track-${Date.now()}`,
          name: 'Position X',
          property: 'position.x',
          color: TRACK_COLORS[composition.layers.length % TRACK_COLORS.length],
          keyframes: [],
        },
      ],
    };

    setComposition((prev) => ({
      ...prev,
      layers: [...prev.layers, newLayer],
    }));
  }, [composition.layers.length]);

  // Calculate total height
  const totalHeight = useMemo(() => {
    return composition.layers.reduce((total, layer) => {
      return total + LAYER_HEIGHT + (layer.isExpanded ? layer.tracks.length * TRACK_HEIGHT : 0);
    }, 0);
  }, [composition.layers]);

  return (
    <TooltipProvider>
    <div
      ref={containerRef}
      className={`flex flex-col bg-gray-900 border border-gray-700 rounded-lg overflow-hidden ${
        isFullscreen ? 'fixed inset-0 z-50 rounded-none' : ''
      }`}
      style={{ height: isFullscreen ? '100vh' : TIMELINE_HEIGHT }}
    >
      {/* Hidden import input */}
      <input ref={importInputRef} type="file" accept=".json,.lottie" className="hidden" onChange={handleImportFile} />

      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-gray-850 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-white">{composition.name}</h3>
          <span className="text-xs text-gray-500">{composition.duration}s @ {composition.frameRate}fps</span>
          {/* Selection badge */}
          {state.selection.keyframes.length > 0 && (
            <Badge variant="secondary" className="text-xs bg-blue-600/30 text-blue-300 border-blue-600/50">
              {state.selection.keyframes.length} kf
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-1">
          {/* Playback controls */}
          <div className="flex items-center gap-0.5 bg-gray-800 rounded-lg p-0.5">
            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={() => setState(prev => ({ ...prev, currentTime: 0 }))} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                  <SkipBack size={13} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Go to start <kbd className="ml-1 text-[10px]">Home</kbd></TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={handleStepBackward} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                  <StepBack size={13} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Prev frame <kbd className="ml-1 text-[10px]">←</kbd></TooltipContent>
            </Tooltip>

            {state.isPlaying ? (
              <Tooltip>
                <TooltipTrigger asChild>
                  <button onClick={handlePause} className="p-1.5 text-white bg-blue-600 hover:bg-blue-700 rounded">
                    <Pause size={13} />
                  </button>
                </TooltipTrigger>
                <TooltipContent>Pause <kbd className="ml-1 text-[10px]">Space</kbd></TooltipContent>
              </Tooltip>
            ) : (
              <Tooltip>
                <TooltipTrigger asChild>
                  <button onClick={handlePlay} className="p-1.5 text-white bg-blue-600 hover:bg-blue-700 rounded">
                    <Play size={13} />
                  </button>
                </TooltipTrigger>
                <TooltipContent>Play <kbd className="ml-1 text-[10px]">Space</kbd></TooltipContent>
              </Tooltip>
            )}

            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={handleStop} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                  <Square size={13} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Stop</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={handleStepForward} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                  <StepForward size={13} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Next frame <kbd className="ml-1 text-[10px]">→</kbd></TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={() => setState(prev => ({ ...prev, currentTime: composition.duration }))} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                  <SkipForward size={13} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Go to end <kbd className="ml-1 text-[10px]">End</kbd></TooltipContent>
            </Tooltip>
          </div>

          {/* Loop toggle */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setLoopEnabled(!loopEnabled)}
                className={`p-1.5 rounded transition-colors ${loopEnabled ? 'text-blue-400 bg-blue-600/20 hover:bg-blue-600/30' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}
              >
                <Repeat size={13} />
              </button>
            </TooltipTrigger>
            <TooltipContent>{loopEnabled ? 'Loop: ON' : 'Loop: OFF'}</TooltipContent>
          </Tooltip>

          {/* Playback speed */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="px-2 py-1 text-xs font-mono text-gray-300 bg-gray-800 hover:bg-gray-700 rounded flex items-center gap-1">
                {playbackSpeed}x
                <ChevronDown size={10} />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-gray-800 border-gray-700 text-white min-w-[80px]">
              {[0.25, 0.5, 1, 1.5, 2].map(speed => (
                <DropdownMenuItem key={speed} onClick={() => setPlaybackSpeed(speed)} className={`text-xs ${playbackSpeed === speed ? 'text-blue-400' : 'text-gray-300'} hover:bg-gray-700`}>
                  {speed}x{playbackSpeed === speed && ' ✓'}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Time display */}
          <div className="px-2.5 py-1 bg-gray-800 rounded text-xs font-mono text-white border border-gray-700">
            {formatTime(state.currentTime, composition.frameRate)}
            <span className="text-gray-600 mx-1">/</span>
            <span className="text-gray-500">{formatTime(composition.duration, composition.frameRate)}</span>
          </div>

          <div className="w-px h-4 bg-gray-700 mx-1" />

          {/* Snap toggle */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setSnapEnabled(!snapEnabled)}
                className={`p-1.5 rounded transition-colors ${snapEnabled ? 'text-amber-400 bg-amber-600/20 hover:bg-amber-600/30' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}
              >
                <Magnet size={13} />
              </button>
            </TooltipTrigger>
            <TooltipContent>{snapEnabled ? 'Snap: ON' : 'Snap: OFF'}</TooltipContent>
          </Tooltip>

          {/* Zoom controls */}
          <div className="flex items-center gap-1">
            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={handleZoomOut} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                  <Minimize2 size={13} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Zoom out</TooltipContent>
            </Tooltip>
            <button
              className="text-xs text-gray-400 w-10 text-center bg-gray-800 rounded py-1 hover:bg-gray-700"
              onClick={() => setState(prev => ({ ...prev, zoom: 1 }))}
              title="Reset zoom"
            >
              {Math.round(state.zoom * 100)}%
            </button>
            <Tooltip>
              <TooltipTrigger asChild>
                <button onClick={handleZoomIn} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                  <Maximize2 size={13} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Zoom in</TooltipContent>
            </Tooltip>
          </div>

          <div className="w-px h-4 bg-gray-700 mx-1" />

          {/* Add Layer */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={handleAddLayer}
                className="flex items-center gap-1 px-2 py-1 text-xs text-gray-300 hover:text-white hover:bg-gray-700 rounded"
              >
                <Plus size={12} />
                Layer
              </button>
            </TooltipTrigger>
            <TooltipContent>Add new layer</TooltipContent>
          </Tooltip>

          <div className="w-px h-4 bg-gray-700 mx-1" />

          {/* Import */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button onClick={handleImportClick} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                <Upload size={13} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Import animation (JSON / Lottie)</TooltipContent>
          </Tooltip>

          {/* Export dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-1 px-2 py-1 text-xs text-gray-300 hover:text-white hover:bg-gray-700 rounded">
                <Download size={12} />
                Export
                <ChevronDown size={10} />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-gray-800 border-gray-700 text-white">
              <DropdownMenuItem onClick={() => onExport?.('lottie')} className="text-xs text-gray-300 hover:bg-gray-700 cursor-pointer">
                Lottie JSON
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onExport?.('gif')} className="text-xs text-gray-300 hover:bg-gray-700 cursor-pointer">
                GIF
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onExport?.('video')} className="text-xs text-gray-300 hover:bg-gray-700 cursor-pointer">
                Video (MP4)
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-700" />
              <DropdownMenuItem
                onClick={() => {
                  const json = JSON.stringify(composition, null, 2);
                  const blob = new Blob([json], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url; a.download = `${composition.name}.json`; a.click();
                  URL.revokeObjectURL(url);
                }}
                className="text-xs text-gray-300 hover:bg-gray-700 cursor-pointer"
              >
                Save as JSON
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Fullscreen */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button onClick={handleToggleFullscreen} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                {isFullscreen ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
              </button>
            </TooltipTrigger>
            <TooltipContent>{isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {/* Timeline Header with Ruler */}
      <div className="flex border-b border-gray-700">
        <div 
          className="bg-gray-850 border-r border-gray-700 flex items-center justify-center"
          style={{ width: SIDEBAR_WIDTH, height: RULER_HEIGHT }}
        >
          <Layers size={14} className="text-gray-500" />
        </div>
        <div className="flex-1 overflow-hidden">
          <TimeRuler
            duration={composition.duration}
            zoom={state.zoom}
            currentTime={state.currentTime}
            frameRate={composition.frameRate}
            onSeek={handleSeek}
          />
        </div>
      </div>

      {/* Layers */}
      <div className="flex-1 overflow-auto relative">
        <Playhead
          currentTime={state.currentTime}
          zoom={state.zoom}
          height={totalHeight}
        />
        
        {composition.layers.map((layer) => (
          <LayerRow
            key={layer.id}
            layer={layer}
            zoom={state.zoom}
            selectedKeyframes={state.selection.keyframes}
            onToggleVisibility={handleToggleLayerVisibility}
            onToggleLock={handleToggleLayerLock}
            onToggleMute={handleToggleLayerMute}
            onToggleExpand={handleToggleLayerExpand}
            onKeyframeSelect={handleKeyframeSelect}
            onKeyframeDrag={handleKeyframeDrag}
            onKeyframeDoubleClick={handleKeyframeDoubleClick}
            onAddKeyframe={handleAddKeyframe}
            onDeleteLayer={handleDeleteLayer}
            onDuplicateLayer={handleDuplicateLayer}
          />
        ))}

        {composition.layers.length === 0 && (
          <div className="flex flex-col items-center justify-center h-32 text-gray-500">
            <Layers size={32} className="mb-2 opacity-50" />
            <p className="text-sm">No layers yet</p>
            <button
              onClick={handleAddLayer}
              className="mt-2 px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Add Layer
            </button>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="flex items-center justify-between px-4 py-1 bg-gray-850 border-t border-gray-700 text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>{composition.layers.length} layers</span>
          <span>
            {composition.layers.reduce((t, l) => t + l.tracks.length, 0)} tracks
          </span>
          <span>
            {composition.layers.reduce(
              (t, l) => t + l.tracks.reduce((tt, tr) => tt + tr.keyframes.length, 0),
              0
            )}{' '}
            keyframes
          </span>
        </div>
        <div className="flex items-center gap-2">
          {state.selection.keyframes.length > 0 && (
            <span className="text-blue-400">
              {state.selection.keyframes.length} selected
            </span>
          )}
        </div>
      </div>
    </div>
    </TooltipProvider>
  );
};

export default AnimationTimeline;
