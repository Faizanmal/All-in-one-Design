"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';

import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Repeat,
  ChevronRight,
  ChevronDown,
  Plus,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  Square,
  Circle,
  Type,
  Image as ImageIcon,
  Minus,
  ZoomIn,
  ZoomOut,
  Download,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface Keyframe {
  id: number;
  time: number;
  properties: { [key: string]: number | string };
}

interface AnimationTrack {
  id: number;
  name: string;
  type: 'layer' | 'property';
  icon: React.ElementType;
  color: string;
  visible: boolean;
  locked: boolean;
  expanded: boolean;
  keyframes: Keyframe[];
  children?: AnimationTrack[];
}

// Mock Data
const mockTracks: AnimationTrack[] = [
  {
    id: 1, name: 'Hero Text', type: 'layer', icon: Type, color: '#3B82F6', visible: true, locked: false, expanded: true,
    keyframes: [
      { id: 1, time: 0, properties: { opacity: 0, y: 50 } },
      { id: 2, time: 500, properties: { opacity: 1, y: 0 } },
    ],
    children: [
      { id: 11, name: 'Opacity', type: 'property', icon: Eye, color: '#3B82F6', visible: true, locked: false, expanded: false, keyframes: [{ id: 1, time: 0, properties: { value: 0 } }, { id: 2, time: 500, properties: { value: 1 } }] },
      { id: 12, name: 'Position Y', type: 'property', icon: Minus, color: '#3B82F6', visible: true, locked: false, expanded: false, keyframes: [{ id: 1, time: 0, properties: { value: 50 } }, { id: 2, time: 500, properties: { value: 0 } }] },
    ],
  },
  {
    id: 2, name: 'Logo', type: 'layer', icon: ImageIcon, color: '#10B981', visible: true, locked: false, expanded: false,
    keyframes: [
      { id: 1, time: 200, properties: { scale: 0, rotation: -45 } },
      { id: 2, time: 700, properties: { scale: 1, rotation: 0 } },
    ],
  },
  {
    id: 3, name: 'Background', type: 'layer', icon: Square, color: '#8B5CF6', visible: true, locked: true, expanded: false,
    keyframes: [
      { id: 1, time: 0, properties: { opacity: 0 } },
      { id: 2, time: 300, properties: { opacity: 1 } },
    ],
  },
  {
    id: 4, name: 'Circle Decoration', type: 'layer', icon: Circle, color: '#F59E0B', visible: true, locked: false, expanded: false,
    keyframes: [
      { id: 1, time: 400, properties: { scale: 0 } },
      { id: 2, time: 800, properties: { scale: 1 } },
      { id: 3, time: 1200, properties: { scale: 1.1 } },
      { id: 4, time: 1500, properties: { scale: 1 } },
    ],
  },
];

const easingOptions = ['Linear', 'Ease In', 'Ease Out', 'Ease In Out', 'Bounce', 'Elastic', 'Back'];

// Timeline Track Component
function TimelineTrack({ track, depth = 0, duration, onToggle: _onToggle }: { track: AnimationTrack; depth?: number; duration: number; onToggle: () => void }) {
  const [isExpanded, setIsExpanded] = useState(track.expanded);

  return (
    <>
      <div className="flex items-center border-b border-gray-200 h-10 hover:bg-gray-50" style={{ paddingLeft: `${depth * 20 + 8}px` }}>
        {/* Track Label */}
        <div className="flex items-center gap-2 w-48 shrink-0 border-r border-gray-200 h-full">
          {track.children && track.children.length > 0 && (
            <button onClick={() => setIsExpanded(!isExpanded)} className="p-0.5">
              {isExpanded ? <ChevronDown className="h-3 w-3 text-gray-400" /> : <ChevronRight className="h-3 w-3 text-gray-400" />}
            </button>
          )}
          <div className="w-5 h-5 rounded flex items-center justify-center" style={{ backgroundColor: track.color + '20' }}>
            <track.icon className="h-3 w-3" style={{ color: track.color }} />
          </div>
          <span className="text-sm text-gray-700 truncate flex-1">{track.name}</span>
          <button className="p-1 opacity-50 hover:opacity-100">
            {track.visible ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
          </button>
          <button className="p-1 opacity-50 hover:opacity-100">
            {track.locked ? <Lock className="h-3 w-3" /> : <Unlock className="h-3 w-3" />}
          </button>
        </div>

        {/* Keyframe Track */}
        <div className="flex-1 relative h-full bg-gray-50/50">
          {track.keyframes.map((kf) => (
            <div key={kf.id} className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-sm cursor-pointer hover:scale-125 transition-transform"
              style={{ left: `${(kf.time / duration) * 100}%`, backgroundColor: track.color }}>
            </div>
          ))}
        </div>
      </div>

      {/* Nested Tracks */}
      {isExpanded && track.children?.map(child => (
        <TimelineTrack key={child.id} track={child} depth={depth + 1} duration={duration} onToggle={() => {}} />
      ))}
    </>
  );
}

export default function AnimationTimelinePage() {
  const { toast } = useToast();
  const [tracks] = useState<AnimationTrack[]>(mockTracks);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration] = useState(2000);
  const [zoom, setZoom] = useState(100);
  const [isLooping, setIsLooping] = useState(true);
  const [selectedEasing, setSelectedEasing] = useState('Ease Out');

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const frames = Math.floor((ms % 1000) / (1000 / 30));
    return `${seconds}:${frames.toString().padStart(2, '0')}`;
  };

  const handlePlay = () => {
    setIsPlaying(!isPlaying);
    if (!isPlaying) {
      toast({ title: 'Playing Animation' });
    }
  };

  const handleExport = () => {
    toast({ title: 'Exporting Animation', description: 'Preparing GIF/Video export...' });
  };

  // Time markers
  const timeMarkers = [];
  const markerInterval = duration / 10;
  for (let i = 0; i <= 10; i++) {
    timeMarkers.push(i * markerInterval);
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Preview Area */}
          <div className="flex-1 bg-gray-200 flex items-center justify-center p-8 relative" style={{ background: 'repeating-conic-gradient(#d1d5db 0% 25%, #e5e7eb 0% 50%) 50% / 20px 20px' }}>
            <div className="bg-white rounded-xl shadow-2xl w-[640px] h-[360px] flex items-center justify-center relative overflow-hidden">
              {/* Animated Preview Elements */}
              <div className="absolute inset-0 bg-linear-to-br from-blue-100 to-purple-100" style={{ opacity: currentTime > 150 ? 1 : currentTime / 150 }} />
              <div className="absolute w-24 h-24 rounded-full bg-amber-400/30 right-10 top-10" style={{ transform: `scale(${currentTime > 400 ? Math.min((currentTime - 400) / 400, 1) : 0})` }} />
              <div className="text-center relative z-10">
                <div className="w-16 h-16 rounded-xl bg-blue-600 mx-auto mb-4 flex items-center justify-center" style={{ transform: `scale(${currentTime > 200 ? Math.min((currentTime - 200) / 500, 1) : 0}) rotate(${currentTime > 200 ? Math.max(0, 45 - ((currentTime - 200) / 500) * 45) : 45}deg)` }}>
                  <ImageIcon className="h-8 w-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900" style={{ opacity: currentTime > 250 ? 1 : currentTime / 250, transform: `translateY(${Math.max(0, 50 - (currentTime / 500) * 50)}px)` }}>
                  Welcome to Our App
                </h2>
              </div>
            </div>
            {/* Playback indicator */}
            <div className="absolute top-4 right-4 bg-black/80 text-white px-3 py-1 rounded-full text-sm font-mono">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
          </div>

          {/* Timeline Panel */}
          <div className="h-80 bg-white border-t border-gray-200 flex flex-col">
            {/* Timeline Controls */}
            <div className="h-12 border-b border-gray-200 flex items-center justify-between px-4">
              <div className="flex items-center gap-2">
                <Button size="sm" variant="ghost" onClick={() => setCurrentTime(0)}><SkipBack className="h-4 w-4" /></Button>
                <Button size="sm" variant={isPlaying ? 'default' : 'outline'} onClick={handlePlay}>
                  {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setCurrentTime(duration)}><SkipForward className="h-4 w-4" /></Button>
                <Button size="sm" variant={isLooping ? 'default' : 'ghost'} onClick={() => setIsLooping(!isLooping)}><Repeat className="h-4 w-4" /></Button>
                <div className="h-6 w-px bg-gray-200 mx-2" />
                <span className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">{formatTime(currentTime)}</span>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">Easing:</span>
                  <Select value={selectedEasing} onValueChange={setSelectedEasing}>
                    <SelectTrigger className="w-32 h-8"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {easingOptions.map(e => <SelectItem key={e} value={e}>{e}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2">
                  <ZoomOut className="h-4 w-4 text-gray-400" />
                  <Slider value={[zoom]} onValueChange={(v) => setZoom(v[0])} min={50} max={200} className="w-24" />
                  <ZoomIn className="h-4 w-4 text-gray-400" />
                </div>
                <Button size="sm" variant="outline" onClick={handleExport}><Download className="h-4 w-4 mr-1" />Export</Button>
              </div>
            </div>

            {/* Time Ruler */}
            <div className="h-6 border-b border-gray-200 flex">
              <div className="w-48 shrink-0 border-r border-gray-200 bg-gray-50" />
              <div className="flex-1 relative bg-gray-50">
                {timeMarkers.map((time, i) => (
                  <div key={i} className="absolute top-0 h-full flex flex-col items-center" style={{ left: `${(time / duration) * 100}%` }}>
                    <span className="text-xs text-gray-400">{formatTime(time)}</span>
                    <div className="flex-1 w-px bg-gray-300" />
                  </div>
                ))}
                {/* Playhead */}
                <div className="absolute top-0 h-full w-0.5 bg-red-500 z-10" style={{ left: `${(currentTime / duration) * 100}%` }}>
                  <div className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-red-500 rotate-45" />
                </div>
              </div>
            </div>

            {/* Timeline Scrubber */}
            <div className="h-8 border-b border-gray-200 flex items-center bg-gray-50">
              <div className="w-48 shrink-0 border-r border-gray-200 px-2">
                <Button size="sm" variant="ghost" className="h-6"><Plus className="h-3 w-3 mr-1" />Add Track</Button>
              </div>
              <div className="flex-1 relative px-2">
                <Slider value={[currentTime]} onValueChange={(v) => setCurrentTime(v[0])} max={duration} className="cursor-pointer" />
              </div>
            </div>

            {/* Tracks */}
            <ScrollArea className="flex-1">
              {tracks.map(track => (
                <TimelineTrack key={track.id} track={track} duration={duration} onToggle={() => {}} />
              ))}
            </ScrollArea>
          </div>
        </div>
      </div>
    </div>
  );
}
