"use client";

import React, { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import {
  Play, Pause, SkipBack, SkipForward, Scissors, Plus, Trash2,
  Volume2, VolumeX, Eye, EyeOff, Lock, Unlock, Type,
  Film, Music, Image, Sparkles, Layers, ChevronRight,
  ZoomIn, ZoomOut, Maximize2, Download, Check,
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { videoTimelineApi, type Timeline, type TimelineTrack, type TimelineClip } from '@/lib/video-timeline-api';
import { toast } from 'sonner';

interface VideoTimelineEditorProps {
  projectId: number;
  className?: string;
}

const TRACK_HEIGHT = 48;
const PIXELS_PER_SECOND_DEFAULT = 60;

const trackTypeIcons: Record<string, React.ReactNode> = {
  video: <Film className="w-4 h-4" />,
  audio: <Music className="w-4 h-4" />,
  text: <Type className="w-4 h-4" />,
  image: <Image className="w-4 h-4" />,
  effect: <Sparkles className="w-4 h-4" />,
};

const trackTypeColors: Record<string, string> = {
  video: 'bg-blue-500/30 border-blue-500/50',
  audio: 'bg-green-500/30 border-green-500/50',
  text: 'bg-purple-500/30 border-purple-500/50',
  image: 'bg-amber-500/30 border-amber-500/50',
  effect: 'bg-pink-500/30 border-pink-500/50',
};

export function VideoTimelineEditor({ projectId, className }: VideoTimelineEditorProps) {
  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [playhead, setPlayhead] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [zoom, setZoom] = useState(PIXELS_PER_SECOND_DEFAULT);
  const [selectedClip, setSelectedClip] = useState<string | null>(null);
  const [selectedTrack, setSelectedTrack] = useState<string | null>(null);
  const timelineRef = useRef<HTMLDivElement>(null);
  const playIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch transitions
  const { data: transitions } = useQuery({
    queryKey: ['video-transitions'],
    queryFn: () => videoTimelineApi.getTransitions(),
  });

  // Fetch export presets
  const { data: exportPresets } = useQuery({
    queryKey: ['video-export-presets'],
    queryFn: () => videoTimelineApi.getExportPresets(),
  });

  // Initialize timeline
  useEffect(() => {
    if (!timeline) {
      const newTimeline: Timeline = {
        id: crypto.randomUUID(),
        project_id: projectId,
        user_id: 0,
        settings: { width: 1920, height: 1080, fps: 30, duration: 0, background_color: '#000000' },
        tracks: [
          {
            id: crypto.randomUUID(), type: 'video', name: 'Video 1',
            clips: [], muted: false, locked: false, visible: true,
            volume: 1.0, opacity: 1.0, order: 0,
          },
          {
            id: crypto.randomUUID(), type: 'audio', name: 'Audio 1',
            clips: [], muted: false, locked: false, visible: true,
            volume: 1.0, opacity: 1.0, order: 1,
          },
        ],
        markers: [],
        audio_tracks: [],
        playhead_position: 0,
      };
      setTimeline(newTimeline);
    }
  }, [timeline, projectId]);

  const totalDuration = useMemo(() => {
    if (!timeline) return 30;
    let max = 30;
    for (const track of timeline.tracks) {
      for (const clip of track.clips) {
        max = Math.max(max, clip.end_time);
      }
    }
    return max + 5;
  }, [timeline]);

  // Playback control
  const togglePlayback = useCallback(() => {
    if (isPlaying) {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
      setIsPlaying(false);
    } else {
      setIsPlaying(true);
      playIntervalRef.current = setInterval(() => {
        setPlayhead(prev => {
          if (prev >= totalDuration) {
            clearInterval(playIntervalRef.current!);
            setIsPlaying(false);
            return 0;
          }
          return prev + 1 / 30;
        });
      }, 1000 / 30);
    }
  }, [isPlaying, totalDuration]);

  const skipToStart = () => { setPlayhead(0); };
  const skipToEnd = () => { setPlayhead(totalDuration - 5); };

  const addTrack = useCallback((type: string) => {
    if (!timeline) return;
    const count = timeline.tracks.filter(t => t.type === type).length;
    const newTrack: TimelineTrack = {
      id: crypto.randomUUID(),
      type: type as TimelineTrack['type'],
      name: `${type.charAt(0).toUpperCase() + type.slice(1)} ${count + 1}`,
      clips: [],
      muted: false,
      locked: false,
      visible: true,
      volume: 1.0,
      opacity: 1.0,
      order: timeline.tracks.length,
    };
    setTimeline({ ...timeline, tracks: [...timeline.tracks, newTrack] });
    toast.success(`Added ${type} track`);
  }, [timeline]);

  const removeTrack = useCallback((trackId: string) => {
    if (!timeline) return;
    setTimeline({
      ...timeline,
      tracks: timeline.tracks.filter(t => t.id !== trackId),
    });
  }, [timeline]);

  const toggleTrackProp = useCallback((trackId: string, prop: 'muted' | 'locked' | 'visible') => {
    if (!timeline) return;
    setTimeline({
      ...timeline,
      tracks: timeline.tracks.map(t =>
        t.id === trackId ? { ...t, [prop]: !t[prop] } : t
      ),
    });
  }, [timeline]);

  const addClipToTrack = useCallback((trackId: string) => {
    if (!timeline) return;
    const track = timeline.tracks.find(t => t.id === trackId);
    if (!track || track.locked) return;

    const lastEnd = track.clips.length > 0
      ? Math.max(...track.clips.map(c => c.end_time))
      : 0;

    const newClip: TimelineClip = {
      id: crypto.randomUUID(),
      type: track.type,
      source_url: '',
      start_time: lastEnd,
      end_time: lastEnd + 5,
      in_point: 0,
      out_point: null,
      duration: 5,
      name: `Clip ${track.clips.length + 1}`,
      volume: 1.0,
      opacity: 1.0,
      speed: 1.0,
      filters: [],
      transform: { x: 0, y: 0, scale_x: 1, scale_y: 1, rotation: 0, anchor_x: 0.5, anchor_y: 0.5 },
      transition_in: null,
      transition_out: null,
      keyframes: [],
    };

    setTimeline({
      ...timeline,
      tracks: timeline.tracks.map(t =>
        t.id === trackId ? { ...t, clips: [...t.clips, newClip] } : t
      ),
    });
    setSelectedClip(newClip.id);
    toast.success('Clip added');
  }, [timeline]);

  const deleteClip = useCallback((trackId: string, clipId: string) => {
    if (!timeline) return;
    setTimeline({
      ...timeline,
      tracks: timeline.tracks.map(t =>
        t.id === trackId
          ? { ...t, clips: t.clips.filter(c => c.id !== clipId) }
          : t
      ),
    });
    if (selectedClip === clipId) setSelectedClip(null);
    toast.success('Clip removed');
  }, [timeline, selectedClip]);

  const splitClipAtPlayhead = useCallback((trackId: string, clipId: string) => {
    if (!timeline) return;
    const track = timeline.tracks.find(t => t.id === trackId);
    const clip = track?.clips.find(c => c.id === clipId);
    if (!clip) return;
    if (playhead <= clip.start_time || playhead >= clip.end_time) {
      toast.error('Playhead must be within clip to split');
      return;
    }

    const clipB: TimelineClip = {
      ...clip,
      id: crypto.randomUUID(),
      name: `${clip.name} (B)`,
      start_time: playhead,
      in_point: playhead - clip.start_time + clip.in_point,
      duration: clip.end_time - playhead,
    };

    const updatedClip = {
      ...clip,
      end_time: playhead,
      duration: playhead - clip.start_time,
    };

    setTimeline({
      ...timeline,
      tracks: timeline.tracks.map(t =>
        t.id === trackId
          ? { ...t, clips: t.clips.flatMap(c => c.id === clipId ? [updatedClip, clipB] : [c]) }
          : t
      ),
    });
    toast.success('Clip split at playhead');
  }, [timeline, playhead]);

  // Format time as MM:SS.ms
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
  };

  // Render time ruler ticks
  const renderRuler = () => {
    const ticks = [];
    const step = zoom >= 100 ? 1 : zoom >= 50 ? 2 : 5;
    for (let t = 0; t <= totalDuration; t += step) {
      ticks.push(
        <div
          key={t}
          className="absolute top-0 h-full flex flex-col items-center"
          style={{ left: `${t * zoom}px`, width: '1px' }}
        >
          <div className="w-px h-3 bg-muted-foreground/40" />
          <span className="text-[9px] text-muted-foreground mt-0.5">{formatTime(t)}</span>
        </div>
      );
    }
    return ticks;
  };

  if (!timeline) return null;

  return (
    <div className={`flex flex-col h-full ${className || ''}`}>
      {/* Transport Controls */}
      <div className="flex items-center gap-3 px-4 py-2 border-b bg-card">
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" onClick={skipToStart}>
            <SkipBack className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={togglePlayback}>
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>
          <Button variant="ghost" size="icon" onClick={skipToEnd}>
            <SkipForward className="w-4 h-4" />
          </Button>
        </div>

        <div className="text-sm font-mono bg-muted px-2 py-1 rounded min-w-[100px] text-center">
          {formatTime(playhead)}
        </div>

        <div className="h-6 w-px bg-border" />

        {/* Zoom */}
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={() => setZoom(z => Math.max(20, z - 10))}>
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Slider
            value={[zoom]}
            onValueChange={([v]) => setZoom(v)}
            min={20}
            max={200}
            step={10}
            className="w-24"
          />
          <Button variant="ghost" size="icon" onClick={() => setZoom(z => Math.min(200, z + 10))}>
            <ZoomIn className="w-4 h-4" />
          </Button>
        </div>

        <div className="h-6 w-px bg-border" />

        {/* Add Track */}
        <Select onValueChange={(v) => addTrack(v)}>
          <SelectTrigger className="w-[140px] h-8">
            <Plus className="w-3 h-3 mr-1" />
            <SelectValue placeholder="Add Track" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="video">Video Track</SelectItem>
            <SelectItem value="audio">Audio Track</SelectItem>
            <SelectItem value="text">Text Track</SelectItem>
            <SelectItem value="image">Image Track</SelectItem>
            <SelectItem value="effect">Effect Track</SelectItem>
          </SelectContent>
        </Select>

        <div className="flex-1" />

        <Badge variant="outline">{timeline.tracks.length} tracks</Badge>
        <Badge variant="outline">{formatTime(totalDuration - 5)}</Badge>
      </div>

      {/* Timeline Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Track Labels */}
        <div className="w-48 flex-shrink-0 border-r bg-card">
          {/* Ruler spacer */}
          <div className="h-8 border-b" />

          {timeline.tracks.map((track) => (
            <div
              key={track.id}
              className={`flex items-center gap-1.5 px-2 border-b cursor-pointer transition-colors ${
                selectedTrack === track.id ? 'bg-accent' : 'hover:bg-muted/50'
              }`}
              style={{ height: TRACK_HEIGHT }}
              onClick={() => setSelectedTrack(track.id)}
            >
              <span className="text-muted-foreground">{trackTypeIcons[track.type]}</span>
              <span className="text-xs font-medium truncate flex-1">{track.name}</span>
              <div className="flex gap-0.5">
                <button
                  className="p-0.5 rounded hover:bg-muted"
                  onClick={(e) => { e.stopPropagation(); toggleTrackProp(track.id, 'muted'); }}
                >
                  {track.muted ? <VolumeX className="w-3 h-3 text-red-400" /> : <Volume2 className="w-3 h-3" />}
                </button>
                <button
                  className="p-0.5 rounded hover:bg-muted"
                  onClick={(e) => { e.stopPropagation(); toggleTrackProp(track.id, 'visible'); }}
                >
                  {track.visible ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3 text-red-400" />}
                </button>
                <button
                  className="p-0.5 rounded hover:bg-muted"
                  onClick={(e) => { e.stopPropagation(); toggleTrackProp(track.id, 'locked'); }}
                >
                  {track.locked ? <Lock className="w-3 h-3 text-amber-400" /> : <Unlock className="w-3 h-3" />}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Timeline Canvas */}
        <ScrollArea className="flex-1">
          <div ref={timelineRef} className="relative" style={{ width: `${totalDuration * zoom}px` }}>
            {/* Time Ruler */}
            <div className="h-8 border-b relative bg-muted/30 sticky top-0 z-10">
              {renderRuler()}
            </div>

            {/* Tracks */}
            {timeline.tracks.map((track) => (
              <div
                key={track.id}
                className="relative border-b"
                style={{ height: TRACK_HEIGHT }}
                onDoubleClick={() => !track.locked && addClipToTrack(track.id)}
              >
                {/* Clips */}
                {track.clips.map((clip) => (
                  <div
                    key={clip.id}
                    className={`absolute top-1 bottom-1 rounded cursor-pointer border transition-all ${
                      trackTypeColors[track.type]
                    } ${selectedClip === clip.id ? 'ring-2 ring-primary shadow-lg' : 'hover:brightness-110'}`}
                    style={{
                      left: `${clip.start_time * zoom}px`,
                      width: `${(clip.end_time - clip.start_time) * zoom}px`,
                    }}
                    onClick={(e) => { e.stopPropagation(); setSelectedClip(clip.id); setSelectedTrack(track.id); }}
                  >
                    <div className="px-2 py-1 text-xs truncate font-medium h-full flex items-center">
                      {clip.name}
                      {clip.transition_in && (
                        <Badge variant="secondary" className="ml-1 text-[8px] h-4 px-1">
                          {clip.transition_in.name}
                        </Badge>
                      )}
                    </div>

                    {/* Trim handles */}
                    <div className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-primary/50 rounded-l" />
                    <div className="absolute right-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-primary/50 rounded-r" />
                  </div>
                ))}

                {/* Empty track hint */}
                {track.clips.length === 0 && (
                  <div className="absolute inset-0 flex items-center justify-center text-xs text-muted-foreground opacity-50">
                    Double-click to add clip
                  </div>
                )}
              </div>
            ))}

            {/* Playhead */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-20 pointer-events-none"
              style={{ left: `${playhead * zoom}px` }}
            >
              <div className="w-3 h-3 bg-red-500 -ml-[5px] rounded-b-sm" />
            </div>

            {/* Click to set playhead */}
            <div
              className="absolute inset-0 z-5"
              onClick={(e) => {
                const rect = timelineRef.current?.getBoundingClientRect();
                if (rect) {
                  const x = e.clientX - rect.left + (timelineRef.current?.parentElement?.scrollLeft || 0);
                  setPlayhead(Math.max(0, x / zoom));
                }
              }}
              style={{ pointerEvents: 'auto', zIndex: 5 }}
            />
          </div>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>
      </div>

      {/* Clip Properties Panel */}
      {selectedClip && selectedTrack && (
        <div className="border-t bg-card px-4 py-3">
          {(() => {
            const track = timeline.tracks.find(t => t.id === selectedTrack);
            const clip = track?.clips.find(c => c.id === selectedClip);
            if (!clip || !track) return null;

            return (
              <div className="flex items-center gap-4 flex-wrap">
                <div className="space-y-1">
                  <Label className="text-xs">Name</Label>
                  <Input
                    value={clip.name}
                    onChange={(e) => {
                      setTimeline({
                        ...timeline,
                        tracks: timeline.tracks.map(t =>
                          t.id === selectedTrack
                            ? { ...t, clips: t.clips.map(c => c.id === selectedClip ? { ...c, name: e.target.value } : c) }
                            : t
                        ),
                      });
                    }}
                    className="h-7 w-32 text-xs"
                  />
                </div>

                <div className="space-y-1">
                  <Label className="text-xs">Speed</Label>
                  <Select
                    value={String(clip.speed)}
                    onValueChange={(v) => {
                      setTimeline({
                        ...timeline,
                        tracks: timeline.tracks.map(t =>
                          t.id === selectedTrack
                            ? { ...t, clips: t.clips.map(c => c.id === selectedClip ? { ...c, speed: parseFloat(v) } : c) }
                            : t
                        ),
                      });
                    }}
                  >
                    <SelectTrigger className="h-7 w-20 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0.25">0.25x</SelectItem>
                      <SelectItem value="0.5">0.5x</SelectItem>
                      <SelectItem value="1">1x</SelectItem>
                      <SelectItem value="1.5">1.5x</SelectItem>
                      <SelectItem value="2">2x</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-1">
                  <Label className="text-xs">Opacity</Label>
                  <Slider
                    value={[clip.opacity * 100]}
                    onValueChange={([v]) => {
                      setTimeline({
                        ...timeline,
                        tracks: timeline.tracks.map(t =>
                          t.id === selectedTrack
                            ? { ...t, clips: t.clips.map(c => c.id === selectedClip ? { ...c, opacity: v / 100 } : c) }
                            : t
                        ),
                      });
                    }}
                    min={0} max={100} step={1}
                    className="w-20"
                  />
                </div>

                <div className="space-y-1">
                  <Label className="text-xs">Transition In</Label>
                  <Select
                    value={clip.transition_in?.name || 'none'}
                    onValueChange={(v) => {
                      const trans = transitions?.[v] || null;
                      setTimeline({
                        ...timeline,
                        tracks: timeline.tracks.map(t =>
                          t.id === selectedTrack
                            ? { ...t, clips: t.clips.map(c => c.id === selectedClip ? { ...c, transition_in: trans } : c) }
                            : t
                        ),
                      });
                    }}
                  >
                    <SelectTrigger className="h-7 w-28 text-xs">
                      <SelectValue placeholder="None" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      {transitions && Object.entries(transitions).map(([key, trans]) => (
                        <SelectItem key={key} value={key}>{trans.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex gap-1 ml-auto">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => splitClipAtPlayhead(selectedTrack, selectedClip)}
                  >
                    <Scissors className="w-3 h-3 mr-1" /> Split
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => deleteClip(selectedTrack, selectedClip)}
                  >
                    <Trash2 className="w-3 h-3 mr-1" /> Delete
                  </Button>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}
