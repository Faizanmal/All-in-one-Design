'use client';

import React, { useState, useCallback, useRef } from 'react';
import {
  Video,
  Image,
  Film,
  Upload,
  Link,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize,
  Download,
  Settings,
  RefreshCw,
  Check,
  X,
  Youtube,
  Loader2
} from 'lucide-react';

interface MediaAsset {
  id: string;
  type: 'video' | 'gif' | 'lottie';
  name: string;
  url: string;
  thumbnail?: string;
  duration?: number;
  width?: number;
  height?: number;
}

interface ExportSettings {
  format: 'gif' | 'mp4' | 'webm' | 'lottie' | 'apng' | 'webp';
  quality: 'low' | 'medium' | 'high';
  fps: number;
  width: number;
  height: number;
  loop: boolean;
}

interface MediaAssetsProps {
  onAssetSelect?: (asset: MediaAsset) => void;
  onExport?: (settings: ExportSettings) => void;
}

export function MediaAssets({ onAssetSelect, onExport }: MediaAssetsProps) {
  const [activeTab, setActiveTab] = useState<'library' | 'embed' | 'export'>('library');
  const [assets, setAssets] = useState<MediaAsset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<MediaAsset | null>(null);
  const [embedUrl, setEmbedUrl] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportSettings, setExportSettings] = useState<ExportSettings>({
    format: 'gif',
    quality: 'medium',
    fps: 30,
    width: 800,
    height: 600,
    loop: true
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  const handleFileUpload = useCallback(async (files: FileList | null) => {
    if (!files) return;

    setIsUploading(true);
    try {
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/v1/media/upload/', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          const asset = await response.json();
          setAssets(prev => [...prev, asset]);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  }, []);

  const handleEmbedUrl = useCallback(async () => {
    if (!embedUrl) return;

    setIsUploading(true);
    try {
      const response = await fetch('/api/v1/media/videos/from_url/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: embedUrl })
      });

      if (response.ok) {
        const asset = await response.json();
        setAssets(prev => [...prev, asset]);
        setEmbedUrl('');
      }
    } catch (error) {
      console.error('Embed error:', error);
    } finally {
      setIsUploading(false);
    }
  }, [embedUrl]);

  const handleExport = useCallback(async () => {
    setIsExporting(true);
    setExportProgress(0);

    try {
      // Simulate export progress
      const interval = setInterval(() => {
        setExportProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 500);

      const response = await fetch('/api/v1/media/exports/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(exportSettings)
      });

      if (response.ok) {
        clearInterval(interval);
        setExportProgress(100);
        onExport?.(exportSettings);
      }
    } catch (error) {
      console.error('Export error:', error);
    } finally {
      setTimeout(() => {
        setIsExporting(false);
        setExportProgress(0);
      }, 1000);
    }
  }, [exportSettings, onExport]);

  const togglePlayback = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const formatTypes = [
    { format: 'gif', label: 'GIF', desc: 'Animated GIF' },
    { format: 'mp4', label: 'MP4', desc: 'Video (H.264)' },
    { format: 'webm', label: 'WebM', desc: 'Video (VP9)' },
    { format: 'lottie', label: 'Lottie', desc: 'JSON Animation' },
    { format: 'apng', label: 'APNG', desc: 'Animated PNG' },
    { format: 'webp', label: 'WebP', desc: 'Animated WebP' },
  ];

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Media Assets</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Videos, GIFs, and animated exports
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {[
          { id: 'library', label: 'Library', icon: Film },
          { id: 'embed', label: 'Embed', icon: Link },
          { id: 'export', label: 'Export', icon: Download },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as 'embed' | 'library' | 'export')}
            className={`flex items-center gap-2 px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'library' && (
          <div className="space-y-4">
            {/* Upload Area */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*,image/gif,.json"
                multiple
                onChange={(e) => handleFileUpload(e.target.files)}
                className="hidden"
              />
              {isUploading ? (
                <Loader2 className="w-12 h-12 mx-auto mb-3 text-blue-500 animate-spin" />
              ) : (
                <Upload className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              )}
              <p className="text-gray-600 dark:text-gray-300 font-medium">
                {isUploading ? 'Uploading...' : 'Click to upload or drag and drop'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                MP4, WebM, GIF, Lottie JSON
              </p>
            </div>

            {/* Asset Grid */}
            {assets.length > 0 ? (
              <div className="grid grid-cols-3 gap-4">
                {assets.map(asset => (
                  <div
                    key={asset.id}
                    onClick={() => {
                      setSelectedAsset(asset);
                      onAssetSelect?.(asset);
                    }}
                    className={`relative rounded-lg overflow-hidden border-2 cursor-pointer transition-all ${
                      selectedAsset?.id === asset.id
                        ? 'border-blue-500 ring-2 ring-blue-200'
                        : 'border-transparent hover:border-gray-300'
                    }`}
                  >
                    {asset.type === 'video' && (
                      <div className="aspect-video bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                        <Video className="w-8 h-8 text-gray-400" />
                      </div>
                    )}
                    {asset.type === 'gif' && (
                      <div className="aspect-video bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                        <Image className="w-8 h-8 text-gray-400" />
                      </div>
                    )}
                    {asset.type === 'lottie' && (
                      <div className="aspect-video bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
                        <Film className="w-8 h-8 text-gray-400" />
                      </div>
                    )}
                    <div className="p-2 bg-white dark:bg-gray-800">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {asset.name}
                      </p>
                      <p className="text-xs text-gray-500 capitalize">{asset.type}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <Film className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="font-medium">No media assets</p>
                <p className="text-sm">Upload videos, GIFs, or Lottie animations</p>
              </div>
            )}

            {/* Video Preview */}
            {selectedAsset && selectedAsset.type === 'video' && (
              <div className="mt-4 p-4 bg-gray-100 dark:bg-gray-900 rounded-lg">
                <div className="aspect-video bg-black rounded-lg overflow-hidden relative">
                  <video ref={videoRef} className="w-full h-full object-contain" />
                  <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={togglePlayback}
                        className="p-2 bg-white/20 rounded-full hover:bg-white/30"
                      >
                        {isPlaying ? <Pause className="w-5 h-5 text-white" /> : <Play className="w-5 h-5 text-white" />}
                      </button>
                      <button
                        onClick={() => setIsMuted(!isMuted)}
                        className="p-2 bg-white/20 rounded-full hover:bg-white/30"
                      >
                        {isMuted ? <VolumeX className="w-5 h-5 text-white" /> : <Volume2 className="w-5 h-5 text-white" />}
                      </button>
                      <div className="flex-1" />
                      <button className="p-2 bg-white/20 rounded-full hover:bg-white/30">
                        <Maximize className="w-5 h-5 text-white" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'embed' && (
          <div className="space-y-6">
            {/* URL Embed */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Video URL
              </label>
              <div className="flex gap-2">
                <input
                  type="url"
                  value={embedUrl}
                  onChange={(e) => setEmbedUrl(e.target.value)}
                  placeholder="https://youtube.com/watch?v=... or https://vimeo.com/..."
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
                <button
                  onClick={handleEmbedUrl}
                  disabled={!embedUrl || isUploading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Link className="w-4 h-4" />}
                  Embed
                </button>
              </div>
            </div>

            {/* Platform Icons */}
            <div className="grid grid-cols-3 gap-4">
              {[
                { name: 'YouTube', icon: Youtube, color: 'bg-red-500' },
                { name: 'Vimeo', icon: Video, color: 'bg-blue-400' },
                { name: 'Direct URL', icon: Link, color: 'bg-gray-500' },
              ].map(platform => (
                <div
                  key={platform.name}
                  className="p-6 border border-gray-200 dark:border-gray-700 rounded-lg text-center hover:border-gray-300 cursor-pointer"
                >
                  <div className={`w-12 h-12 ${platform.color} rounded-full flex items-center justify-center mx-auto mb-3`}>
                    <platform.icon className="w-6 h-6 text-white" />
                  </div>
                  <p className="font-medium text-gray-900 dark:text-white">{platform.name}</p>
                </div>
              ))}
            </div>

            {/* Embed Code */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Or paste embed code
              </label>
              <textarea
                rows={4}
                placeholder="<iframe src='...' />"
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 font-mono text-sm"
              />
            </div>
          </div>
        )}

        {activeTab === 'export' && (
          <div className="space-y-6">
            {/* Format Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Export Format
              </label>
              <div className="grid grid-cols-3 gap-3">
                {formatTypes.map(ft => (
                  <button
                    key={ft.format}
                    onClick={() => setExportSettings({ ...exportSettings, format: ft.format as 'lottie' | 'gif' | 'webp' | 'mp4' | 'webm' | 'apng' })}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      exportSettings.format === ft.format
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-semibold text-gray-900 dark:text-white">{ft.label}</div>
                    <div className="text-xs text-gray-500">{ft.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Quality */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Quality
              </label>
              <div className="flex gap-2">
                {['low', 'medium', 'high'].map(q => (
                  <button
                    key={q}
                    onClick={() => setExportSettings({ ...exportSettings, quality: q as 'high' | 'medium' | 'low' })}
                    className={`flex-1 py-2 rounded-lg border capitalize ${
                      exportSettings.quality === q
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-600'
                        : 'border-gray-200 dark:border-gray-700 text-gray-600'
                    }`}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Dimensions */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Width (px)
                </label>
                <input
                  type="number"
                  value={exportSettings.width}
                  onChange={(e) => setExportSettings({ ...exportSettings, width: Number(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Height (px)
                </label>
                <input
                  type="number"
                  value={exportSettings.height}
                  onChange={(e) => setExportSettings({ ...exportSettings, height: Number(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
            </div>

            {/* FPS */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Frame Rate: {exportSettings.fps} FPS
              </label>
              <input
                type="range"
                min={10}
                max={60}
                value={exportSettings.fps}
                onChange={(e) => setExportSettings({ ...exportSettings, fps: Number(e.target.value) })}
                className="w-full"
              />
            </div>

            {/* Loop */}
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={exportSettings.loop}
                onChange={(e) => setExportSettings({ ...exportSettings, loop: e.target.checked })}
                className="rounded"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">Loop animation</span>
            </label>

            {/* Export Button */}
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isExporting ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Exporting... {exportProgress}%
                </>
              ) : (
                <>
                  <Download className="w-5 h-5" />
                  Export as {exportSettings.format.toUpperCase()}
                </>
              )}
            </button>

            {/* Progress */}
            {isExporting && (
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${exportProgress}%` }}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default MediaAssets;
