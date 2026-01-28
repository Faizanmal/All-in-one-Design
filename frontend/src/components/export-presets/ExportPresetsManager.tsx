'use client';

import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Download,
  Plus,
  Trash2,
  Edit2,
  Copy,
  Clock,
  Play,
  Pause,
  Calendar,
  Settings,
  FolderDown,
  Image,
  FileCode,
  CheckCircle,
  XCircle,
  Loader2,
  MoreVertical,
  Smartphone,
  Monitor,
  Globe,
  Printer,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Slider } from '@/components/ui/slider';
import { useToast } from '@/hooks/use-toast';

interface ExportPreset {
  id: number;
  name: string;
  description: string;
  format: string;
  scale: string;
  quality: number;
  is_default: boolean;
  include_background: boolean;
  optimize_for_web: boolean;
}

interface ExportBundle {
  id: number;
  name: string;
  description: string;
  platform: string;
  preset_count: number;
}

interface ScheduledExport {
  id: number;
  name: string;
  schedule_type: string;
  status: string;
  next_run: string | null;
  last_run: string | null;
  run_count: number;
}

interface ExportHistory {
  id: number;
  status: string;
  format: string;
  file_count: number;
  total_size: number;
  duration_ms: number;
  created_at: string;
}

const FORMAT_OPTIONS = [
  { value: 'png', label: 'PNG', icon: Image },
  { value: 'jpg', label: 'JPEG', icon: Image },
  { value: 'svg', label: 'SVG', icon: FileCode },
  { value: 'pdf', label: 'PDF', icon: FileCode },
  { value: 'webp', label: 'WebP', icon: Image },
];

const SCALE_OPTIONS = ['0.5x', '1x', '1.5x', '2x', '3x', '4x'];

const PLATFORM_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  ios: Smartphone,
  android: Smartphone,
  web: Globe,
  desktop: Monitor,
  print: Printer,
};

interface ExportPresetsManagerProps {
  projectId: number;
}

export function ExportPresetsManager({ projectId }: ExportPresetsManagerProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('presets');
  const [isCreatePresetOpen, setIsCreatePresetOpen] = useState(false);
  const [isScheduleOpen, setIsScheduleOpen] = useState(false);
  const [newPreset, setNewPreset] = useState({
    name: '',
    description: '',
    format: 'png',
    scale: '1x',
    quality: 90,
    include_background: true,
    optimize_for_web: true,
  });

  // Fetch presets
  const { data: presetsData } = useQuery({
    queryKey: ['export-presets'],
    queryFn: async () => {
      const response = await fetch('/api/v1/projects/export-presets/');
      if (!response.ok) throw new Error('Failed to fetch presets');
      return response.json();
    },
  });

  // Fetch bundles
  const { data: bundlesData } = useQuery({
    queryKey: ['export-bundles'],
    queryFn: async () => {
      const response = await fetch('/api/v1/projects/export-bundles/');
      if (!response.ok) throw new Error('Failed to fetch bundles');
      return response.json();
    },
  });

  // Fetch scheduled exports
  const { data: scheduledData } = useQuery({
    queryKey: ['scheduled-exports', projectId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/projects/scheduled-exports/?project_id=${projectId}`);
      if (!response.ok) throw new Error('Failed to fetch scheduled exports');
      return response.json();
    },
  });

  // Fetch history
  const { data: historyData } = useQuery({
    queryKey: ['export-history', projectId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/projects/export-history/?project_id=${projectId}`);
      if (!response.ok) throw new Error('Failed to fetch history');
      return response.json();
    },
  });

  // Create preset mutation
  const createPresetMutation = useMutation({
    mutationFn: async (preset: typeof newPreset) => {
      const response = await fetch('/api/v1/projects/export-presets/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preset),
      });
      if (!response.ok) throw new Error('Failed to create preset');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['export-presets'] });
      setIsCreatePresetOpen(false);
      setNewPreset({
        name: '',
        description: '',
        format: 'png',
        scale: '1x',
        quality: 90,
        include_background: true,
        optimize_for_web: true,
      });
      toast({ title: 'Preset Created', description: 'Export preset has been created.' });
    },
  });

  // Quick export mutation
  const quickExportMutation = useMutation({
    mutationFn: async ({ format, scale }: { format: string; scale: string }) => {
      const response = await fetch('/api/v1/projects/export/quick/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, format, scale }),
      });
      if (!response.ok) throw new Error('Failed to export');
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['export-history', projectId] });
      toast({ title: 'Export Complete', description: `${data.files?.length || 0} files exported.` });
    },
  });

  // Export with preset mutation
  const exportWithPresetMutation = useMutation({
    mutationFn: async (presetId: number) => {
      const response = await fetch('/api/v1/projects/export/with_preset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, preset_id: presetId }),
      });
      if (!response.ok) throw new Error('Failed to export');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['export-history', projectId] });
      toast({ title: 'Export Complete', description: 'Export completed successfully.' });
    },
  });

  // Delete preset mutation
  const deletePresetMutation = useMutation({
    mutationFn: async (presetId: number) => {
      const response = await fetch(`/api/v1/projects/export-presets/${presetId}/`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete preset');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['export-presets'] });
      toast({ title: 'Preset Deleted', description: 'Export preset has been deleted.' });
    },
  });

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Download className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Export Manager</CardTitle>
            </div>
            <div className="flex gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button>
                    <Download className="h-4 w-4 mr-2" />
                    Quick Export
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-48">
                  {FORMAT_OPTIONS.map((format) => (
                    <DropdownMenuItem
                      key={format.value}
                      onClick={() => quickExportMutation.mutate({ format: format.value, scale: '1x' })}
                    >
                      <format.icon className="h-4 w-4 mr-2" />
                      {format.label} (1x)
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => quickExportMutation.mutate({ format: 'png', scale: '2x' })}
                  >
                    {/* eslint-disable-next-line jsx-a11y/alt-text */}
                    <Image className="h-4 w-4 mr-2" aria-hidden="true" />
                    PNG (2x Retina)
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
          <CardDescription>
            Manage export presets, scheduled exports, and export history
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="presets">Presets</TabsTrigger>
              <TabsTrigger value="bundles">Bundles</TabsTrigger>
              <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>

            {/* Presets Tab */}
            <TabsContent value="presets" className="mt-4 space-y-4">
              <div className="flex justify-between">
                <h4 className="font-medium">Your Presets</h4>
                <Dialog open={isCreatePresetOpen} onOpenChange={setIsCreatePresetOpen}>
                  <DialogTrigger asChild>
                    <Button size="sm">
                      <Plus className="h-4 w-4 mr-1" />
                      New Preset
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create Export Preset</DialogTitle>
                      <DialogDescription>
                        Save your export settings for quick reuse
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium">Name</label>
                        <Input
                          value={newPreset.name}
                          onChange={(e) => setNewPreset({ ...newPreset, name: e.target.value })}
                          placeholder="e.g., Web 2x"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium">Format</label>
                          <Select
                            value={newPreset.format}
                            onValueChange={(value) => setNewPreset({ ...newPreset, format: value })}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {FORMAT_OPTIONS.map((f) => (
                                <SelectItem key={f.value} value={f.value}>
                                  {f.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <label className="text-sm font-medium">Scale</label>
                          <Select
                            value={newPreset.scale}
                            onValueChange={(value) => setNewPreset({ ...newPreset, scale: value })}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {SCALE_OPTIONS.map((s) => (
                                <SelectItem key={s} value={s}>
                                  {s}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Quality: {newPreset.quality}%</label>
                        <Slider
                          value={[newPreset.quality]}
                          onValueChange={([value]) => setNewPreset({ ...newPreset, quality: value })}
                          min={10}
                          max={100}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <label className="text-sm font-medium">Include Background</label>
                        <Switch
                          checked={newPreset.include_background}
                          onCheckedChange={(checked) =>
                            setNewPreset({ ...newPreset, include_background: checked })
                          }
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <label className="text-sm font-medium">Optimize for Web</label>
                        <Switch
                          checked={newPreset.optimize_for_web}
                          onCheckedChange={(checked) =>
                            setNewPreset({ ...newPreset, optimize_for_web: checked })
                          }
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsCreatePresetOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={() => createPresetMutation.mutate(newPreset)}>
                        Create Preset
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>

              <ScrollArea className="h-[300px]">
                <div className="space-y-2">
                  {presetsData?.presets?.map((preset: ExportPreset) => (
                    <div
                      key={preset.id}
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary/10 rounded flex items-center justify-center">
                          {/* eslint-disable-next-line jsx-a11y/alt-text */}
                          <Image className="h-5 w-5 text-primary" aria-hidden="true" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{preset.name}</span>
                            {preset.is_default && (
                              <Badge variant="secondary" className="text-xs">
                                Default
                              </Badge>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {preset.format.toUpperCase()} • {preset.scale} • {preset.quality}%
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => exportWithPresetMutation.mutate(preset.id)}
                          disabled={exportWithPresetMutation.isPending}
                        >
                          {exportWithPresetMutation.isPending ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Download className="h-4 w-4" />
                          )}
                        </Button>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent>
                            <DropdownMenuItem>
                              <Edit2 className="h-4 w-4 mr-2" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Copy className="h-4 w-4 mr-2" />
                              Duplicate
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-destructive"
                              onClick={() => deletePresetMutation.mutate(preset.id)}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  ))}

                  {(!presetsData?.presets || presetsData.presets.length === 0) && (
                    <div className="text-center py-8 text-muted-foreground">
                      <FolderDown className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>No presets yet</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* Bundles Tab */}
            <TabsContent value="bundles" className="mt-4 space-y-4">
              <h4 className="font-medium">Platform Bundles</h4>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(bundlesData?.platform_bundles || {}).map(([key, bundleData]: [string, unknown]) => {
                  const bundle = bundleData as Record<string, unknown>;
                  const PlatformIcon = PLATFORM_ICONS[key] || Globe;
                  return (
                    <Button
                      key={key}
                      variant="outline"
                      className="h-auto p-4 flex flex-col items-start"
                      onClick={() => {
                        toast({
                          title: `${bundle.name as string} Export`,
                          description: 'Bundle export started...',
                        });
                      }}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <PlatformIcon className="h-4 w-4" />
                        <span className="font-medium">{bundle.name as string}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {(bundle.presets as unknown[] | undefined)?.length || 0} export sizes
                      </span>
                    </Button>
                  );
                })}
              </div>

              <h4 className="font-medium mt-6">Your Bundles</h4>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {bundlesData?.bundles?.map((bundle: ExportBundle) => (
                    <div
                      key={bundle.id}
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                    >
                      <div>
                        <span className="font-medium">{bundle.name}</span>
                        <div className="text-xs text-muted-foreground">
                          {bundle.preset_count} presets • {bundle.platform}
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* Scheduled Tab */}
            <TabsContent value="scheduled" className="mt-4 space-y-4">
              <div className="flex justify-between">
                <h4 className="font-medium">Scheduled Exports</h4>
                <Button size="sm" onClick={() => setIsScheduleOpen(true)}>
                  <Plus className="h-4 w-4 mr-1" />
                  Schedule Export
                </Button>
              </div>

              <ScrollArea className="h-[300px]">
                <div className="space-y-2">
                  {scheduledData?.scheduled_exports?.map((scheduled: ScheduledExport) => (
                    <div
                      key={scheduled.id}
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            scheduled.status === 'active'
                              ? 'bg-green-500'
                              : scheduled.status === 'paused'
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                        />
                        <div>
                          <span className="font-medium">{scheduled.name}</span>
                          <div className="text-xs text-muted-foreground flex items-center gap-2">
                            <Clock className="h-3 w-3" />
                            {scheduled.schedule_type}
                            {scheduled.next_run && (
                              <>
                                <span>•</span>
                                Next: {new Date(scheduled.next_run).toLocaleDateString()}
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          {scheduled.status === 'active' ? (
                            <Pause className="h-4 w-4" />
                          ) : (
                            <Play className="h-4 w-4" />
                          )}
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <Settings className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}

                  {(!scheduledData?.scheduled_exports ||
                    scheduledData.scheduled_exports.length === 0) && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>No scheduled exports</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* History Tab */}
            <TabsContent value="history" className="mt-4 space-y-4">
              <h4 className="font-medium">Export History</h4>

              <ScrollArea className="h-[300px]">
                <div className="space-y-2">
                  {historyData?.history?.map((item: ExportHistory) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        {item.status === 'completed' ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : item.status === 'failed' ? (
                          <XCircle className="h-5 w-5 text-red-500" />
                        ) : (
                          <Loader2 className="h-5 w-5 animate-spin" />
                        )}
                        <div>
                          <div className="font-medium">
                            {item.format.toUpperCase()} Export
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {item.file_count} files • {formatFileSize(item.total_size)} •{' '}
                            {item.duration_ms}ms
                          </div>
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(item.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}

                  {(!historyData?.history || historyData.history.length === 0) && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>No export history</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

export default ExportPresetsManager;
