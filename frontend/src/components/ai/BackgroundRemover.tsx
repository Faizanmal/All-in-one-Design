"use client";

import React, { useState, useCallback, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Upload, Wand2, Loader2, Download, Undo2, Palette,
  ImageIcon, Eraser, Sparkles, Check, X, Eye,
} from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from 'sonner';

interface BackgroundRemoverProps {
  onImageProcessed?: (imageData: string, format: string) => void;
  className?: string;
}

interface ProcessedResult {
  image_base64: string;
  format: string;
  width: number;
  height: number;
  method_used: string;
  file_size: number;
}

const BACKGROUND_COLORS = [
  { name: 'Transparent', value: '', icon: '🏁' },
  { name: 'White', value: '#FFFFFF', icon: '⬜' },
  { name: 'Black', value: '#000000', icon: '⬛' },
  { name: 'Red', value: '#EF4444', icon: '🟥' },
  { name: 'Blue', value: '#3B82F6', icon: '🟦' },
  { name: 'Green', value: '#22C55E', icon: '🟩' },
  { name: 'Yellow', value: '#EAB308', icon: '🟨' },
  { name: 'Purple', value: '#A855F7', icon: '🟪' },
];

export function BackgroundRemover({ onImageProcessed, className }: BackgroundRemoverProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<ProcessedResult | null>(null);
  const [method, setMethod] = useState('auto');
  const [outputFormat, setOutputFormat] = useState('png');
  const [refineEdges, setRefineEdges] = useState(true);
  const [backgroundColor, setBackgroundColor] = useState('');
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonPosition, setComparisonPosition] = useState(50);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 25 * 1024 * 1024) {
      toast.error('File too large. Maximum size is 25MB.');
      return;
    }

    const validTypes = ['image/png', 'image/jpeg', 'image/webp', 'image/bmp', 'image/tiff'];
    if (!validTypes.includes(file.type)) {
      toast.error('Unsupported format. Use PNG, JPG, WebP, BMP, or TIFF.');
      return;
    }

    setSelectedFile(file);
    setResult(null);
    const reader = new FileReader();
    reader.onload = () => setPreviewUrl(reader.result as string);
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      const fakeEvent = { target: { files: [file] } } as unknown as React.ChangeEvent<HTMLInputElement>;
      handleFileSelect(fakeEvent);
    }
  }, [handleFileSelect]);

  const removeBgMutation = useMutation({
    mutationFn: async () => {
      if (!selectedFile) throw new Error('No file selected');
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('method', method);
      formData.append('output_format', outputFormat);
      formData.append('refine_edges', String(refineEdges));
      if (backgroundColor) formData.append('background_color', backgroundColor);

      const response = await apiClient.post('/v1/ai/background-remover/remove/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data as ProcessedResult;
    },
    onSuccess: (data) => {
      setResult(data);
      toast.success(`Background removed using ${data.method_used}`);
      onImageProcessed?.(`data:image/${data.format};base64,${data.image_base64}`, data.format);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Background removal failed');
    },
  });

  const replaceBgMutation = useMutation({
    mutationFn: async () => {
      if (!selectedFile) throw new Error('No file selected');
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('background_color', backgroundColor || '#FFFFFF');

      const response = await apiClient.post('/v1/ai/background-remover/replace/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data as ProcessedResult;
    },
    onSuccess: (data) => {
      setResult(data);
      toast.success('Background replaced successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Background replacement failed');
    },
  });

  const handleDownload = useCallback(() => {
    if (!result) return;
    const link = document.createElement('a');
    link.href = `data:image/${result.format};base64,${result.image_base64}`;
    link.download = `bg-removed.${result.format}`;
    link.click();
    toast.success('Image downloaded');
  }, [result]);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const isProcessing = removeBgMutation.isPending || replaceBgMutation.isPending;

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eraser className="w-5 h-5 text-primary" />
            AI Background Remover
          </CardTitle>
          <CardDescription>
            Remove or replace image backgrounds instantly using AI
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Upload Area */}
          {!previewUrl ? (
            <div
              className="border-2 border-dashed border-muted-foreground/25 rounded-xl p-8 text-center cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
            >
              <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium">Drop an image here or click to upload</p>
              <p className="text-sm text-muted-foreground mt-1">
                PNG, JPG, WebP, BMP, TIFF — up to 25MB
              </p>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept="image/png,image/jpeg,image/webp,image/bmp,image/tiff"
                onChange={handleFileSelect}
              />
            </div>
          ) : (
            <div className="space-y-4">
              {/* Image Preview with Comparison Slider */}
              <div className="relative rounded-lg overflow-hidden bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+PHJlY3Qgd2lkdGg9IjEwIiBoZWlnaHQ9IjEwIiBmaWxsPSIjZjBmMGYwIi8+PHJlY3QgeD0iMTAiIHk9IjEwIiB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIGZpbGw9IiNmMGYwZjAiLz48L3N2Zz4=')]">
                {showComparison && result ? (
                  <div className="relative" style={{ maxHeight: '400px' }}>
                    <img
                      src={previewUrl}
                      alt="Original"
                      className="w-full object-contain"
                      style={{ maxHeight: '400px' }}
                    />
                    <div
                      className="absolute top-0 left-0 h-full overflow-hidden"
                      style={{ width: `${comparisonPosition}%` }}
                    >
                      <img
                        src={`data:image/${result.format};base64,${result.image_base64}`}
                        alt="Processed"
                        className="w-full object-contain"
                        style={{ maxHeight: '400px', width: `${10000 / comparisonPosition}%` }}
                      />
                    </div>
                    <div
                      className="absolute top-0 h-full w-0.5 bg-white shadow-lg cursor-ew-resize"
                      style={{ left: `${comparisonPosition}%` }}
                    />
                  </div>
                ) : (
                  <img
                    src={result ? `data:image/${result.format};base64,${result.image_base64}` : previewUrl}
                    alt={result ? 'Processed' : 'Original'}
                    className="w-full object-contain"
                    style={{ maxHeight: '400px' }}
                  />
                )}
              </div>

              {/* Controls */}
              <Tabs defaultValue="remove">
                <TabsList className="w-full">
                  <TabsTrigger value="remove" className="flex-1">
                    <Eraser className="w-4 h-4 mr-1" /> Remove
                  </TabsTrigger>
                  <TabsTrigger value="replace" className="flex-1">
                    <Palette className="w-4 h-4 mr-1" /> Replace
                  </TabsTrigger>
                  <TabsTrigger value="settings" className="flex-1">
                    <Sparkles className="w-4 h-4 mr-1" /> Settings
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="remove" className="space-y-4 mt-4">
                  <Button
                    className="w-full"
                    size="lg"
                    onClick={() => removeBgMutation.mutate()}
                    disabled={isProcessing}
                  >
                    {isProcessing ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</>
                    ) : (
                      <><Wand2 className="w-4 h-4 mr-2" /> Remove Background</>
                    )}
                  </Button>
                </TabsContent>

                <TabsContent value="replace" className="space-y-4 mt-4">
                  <Label>Background Color</Label>
                  <div className="grid grid-cols-4 gap-2">
                    {BACKGROUND_COLORS.map((color) => (
                      <button
                        key={color.value}
                        onClick={() => setBackgroundColor(color.value)}
                        className={`p-2 rounded-lg border text-center text-xs transition-all ${
                          backgroundColor === color.value
                            ? 'border-primary ring-2 ring-primary/20'
                            : 'border-muted hover:border-primary/50'
                        }`}
                      >
                        <span className="text-lg">{color.icon}</span>
                        <p className="mt-1">{color.name}</p>
                      </button>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Input
                      type="color"
                      value={backgroundColor || '#FFFFFF'}
                      onChange={(e) => setBackgroundColor(e.target.value)}
                      className="w-12 h-10 p-1"
                    />
                    <Input
                      value={backgroundColor}
                      onChange={(e) => setBackgroundColor(e.target.value)}
                      placeholder="Custom hex color"
                      className="flex-1"
                    />
                  </div>
                  <Button
                    className="w-full"
                    size="lg"
                    onClick={() => replaceBgMutation.mutate()}
                    disabled={isProcessing || !backgroundColor}
                  >
                    {isProcessing ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</>
                    ) : (
                      <><Palette className="w-4 h-4 mr-2" /> Replace Background</>
                    )}
                  </Button>
                </TabsContent>

                <TabsContent value="settings" className="space-y-4 mt-4">
                  <div className="space-y-3">
                    <div>
                      <Label>AI Method</Label>
                      <Select value={method} onValueChange={setMethod}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="auto">Auto (Best Quality)</SelectItem>
                          <SelectItem value="rembg">Rembg (Fast, Local)</SelectItem>
                          <SelectItem value="remove_bg_api">Remove.bg API</SelectItem>
                          <SelectItem value="basic">Basic (Fallback)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>Output Format</Label>
                      <Select value={outputFormat} onValueChange={setOutputFormat}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="png">PNG (Transparent)</SelectItem>
                          <SelectItem value="webp">WebP (Smaller)</SelectItem>
                          <SelectItem value="jpg">JPG (No Alpha)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center justify-between">
                      <Label>Refine Edges</Label>
                      <Switch checked={refineEdges} onCheckedChange={setRefineEdges} />
                    </div>
                  </div>
                </TabsContent>
              </Tabs>

              {/* Result Info & Actions */}
              {result && (
                <Card className="bg-muted/50">
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge variant="secondary" className="gap-1">
                        <Check className="w-3 h-3" /> {result.method_used}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {result.width}×{result.height} · {formatFileSize(result.file_size)}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1" onClick={handleDownload}>
                        <Download className="w-4 h-4 mr-1" /> Download
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowComparison(!showComparison)}
                      >
                        <Eye className="w-4 h-4 mr-1" /> {showComparison ? 'Hide' : 'Compare'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onImageProcessed?.(
                          `data:image/${result.format};base64,${result.image_base64}`,
                          result.format
                        )}
                      >
                        <ImageIcon className="w-4 h-4 mr-1" /> Use
                      </Button>
                    </div>
                    {showComparison && (
                      <div className="space-y-1">
                        <Label className="text-xs">Comparison Slider</Label>
                        <Slider
                          value={[comparisonPosition]}
                          onValueChange={([v]) => setComparisonPosition(v)}
                          min={0}
                          max={100}
                          step={1}
                        />
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Reset */}
              <Button
                variant="ghost"
                size="sm"
                className="w-full"
                onClick={() => {
                  setSelectedFile(null);
                  setPreviewUrl(null);
                  setResult(null);
                  setShowComparison(false);
                }}
              >
                <Undo2 className="w-4 h-4 mr-1" /> Choose Another Image
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
