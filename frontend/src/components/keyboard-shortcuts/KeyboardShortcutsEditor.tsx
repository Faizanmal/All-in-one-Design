'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Keyboard,
  Search,
  RotateCcw,
  Check,
  Edit2,
  GraduationCap,
  Trophy,
  Flame,
  Target,
  Command,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
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
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';

interface Shortcut {
  action_id: string;
  name: string;
  description: string;
  category: string;
  key: string;
  default_key: string;
  is_custom: boolean;
  is_enabled: boolean;
  is_customizable: boolean;
}

interface ShortcutPreset {
  id: number;
  name: string;
  description: string;
  shortcut_count: number;
  icon?: string;
}

export function KeyboardShortcutsEditor() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('shortcuts');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [editingShortcut, setEditingShortcut] = useState<string | null>(null);
  const [newKeyBinding, setNewKeyBinding] = useState('');
  const [recordingKeys, setRecordingKeys] = useState(false);

  // Fetch shortcuts
  const { data: shortcutsData } = useQuery({
    queryKey: ['keyboard-shortcuts'],
    queryFn: async () => {
      const response = await fetch('/api/v1/projects/shortcuts/');
      if (!response.ok) throw new Error('Failed to fetch shortcuts');
      return response.json();
    },
  });

  // Fetch shortcuts by category
  useQuery({
    queryKey: ['keyboard-shortcuts-categories'],
    queryFn: async () => {
      const response = await fetch('/api/v1/projects/shortcuts/by_category/');
      if (!response.ok) throw new Error('Failed to fetch categories');
      return response.json();
    },
  });

  // Fetch presets
  const { data: presetsData } = useQuery({
    queryKey: ['shortcut-presets'],
    queryFn: async () => {
      const response = await fetch('/api/v1/projects/shortcut-presets/');
      if (!response.ok) throw new Error('Failed to fetch presets');
      return response.json();
    },
  });

  // Fetch learning stats
  const { data: learningStats } = useQuery({
    queryKey: ['shortcuts-learning-stats'],
    queryFn: async () => {
      const response = await fetch('/api/v1/projects/shortcuts-learning/stats/');
      if (!response.ok) throw new Error('Failed to fetch stats');
      return response.json();
    },
  });

  // Set shortcut mutation
  const setShortcutMutation = useMutation({
    mutationFn: async ({ actionId, key }: { actionId: string; key: string }) => {
      const response = await fetch('/api/v1/projects/shortcuts/set/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: actionId, key }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to set shortcut');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keyboard-shortcuts'] });
      setEditingShortcut(null);
      setNewKeyBinding('');
      toast({ title: 'Shortcut Updated', description: 'Keyboard shortcut has been updated.' });
    },
    onError: (error: Error) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    },
  });

  // Reset shortcut mutation
  const resetShortcutMutation = useMutation({
    mutationFn: async (actionId: string) => {
      const response = await fetch('/api/v1/projects/shortcuts/reset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: actionId }),
      });
      if (!response.ok) throw new Error('Failed to reset shortcut');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keyboard-shortcuts'] });
      toast({ title: 'Shortcut Reset', description: 'Shortcut reset to default.' });
    },
  });

  // Reset all mutations
  const resetAllMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/v1/projects/shortcuts/reset_all/', {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to reset shortcuts');
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['keyboard-shortcuts'] });
      toast({
        title: 'All Shortcuts Reset',
        description: `${data.reset_count} shortcuts reset to defaults.`,
      });
    },
  });

  // Apply preset mutation
  const applyPresetMutation = useMutation({
    mutationFn: async (presetId: number) => {
      const response = await fetch(`/api/v1/projects/shortcut-presets/${presetId}/apply/`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to apply preset');
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['keyboard-shortcuts'] });
      toast({
        title: 'Preset Applied',
        description: `${data.shortcuts_applied} shortcuts updated from ${data.preset_name}.`,
      });
    },
  });

  // Toggle learning mode
  const toggleLearningMutation = useMutation({
    mutationFn: async (enabled: boolean) => {
      const response = await fetch('/api/v1/projects/shortcuts-learning/toggle/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
      });
      if (!response.ok) throw new Error('Failed to toggle learning mode');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shortcuts-learning-stats'] });
      toast({
        title: 'Learning Mode',
        description: learningStats?.is_learning_mode ? 'Disabled' : 'Enabled',
      });
    },
  });

  // Key recording handler
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!recordingKeys) return;

      e.preventDefault();

      const parts: string[] = [];
      if (e.ctrlKey || e.metaKey) parts.push(navigator.platform.includes('Mac') ? 'Cmd' : 'Ctrl');
      if (e.altKey) parts.push('Alt');
      if (e.shiftKey) parts.push('Shift');

      const key = e.key.length === 1 ? e.key.toUpperCase() : e.key;
      if (!['Control', 'Alt', 'Shift', 'Meta'].includes(e.key)) {
        parts.push(key);
      }

      if (parts.length > 0) {
        setNewKeyBinding(parts.join('+'));
      }
    },
    [recordingKeys]
  );

  useEffect(() => {
    if (recordingKeys) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [recordingKeys, handleKeyDown]);

  // Filter shortcuts
  const filteredShortcuts =
    shortcutsData?.shortcuts?.filter((shortcut: Shortcut) => {
      const matchesSearch =
        shortcut.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        shortcut.key.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = filterCategory === 'all' || shortcut.category === filterCategory;
      return matchesSearch && matchesCategory;
    }) || [];

  // Get unique categories
  const categories = Array.from(
    new Set(shortcutsData?.shortcuts?.map((s: Shortcut) => s.category) || [])
  );

  const renderKeyBadge = (key: string) => {
    const parts = key.split('+');
    return (
      <div className="flex items-center gap-1">
        {parts.map((part, i) => (
          <Badge key={i} variant="outline" className="font-mono text-xs px-2">
            {part === 'Cmd' ? <Command className="h-3 w-3" /> : part}
          </Badge>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Keyboard className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Keyboard Shortcuts</CardTitle>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => resetAllMutation.mutate()}>
                <RotateCcw className="h-4 w-4 mr-1" />
                Reset All
              </Button>
            </div>
          </div>
          <CardDescription>
            Customize keyboard shortcuts and learn new ones
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="shortcuts">Shortcuts</TabsTrigger>
              <TabsTrigger value="presets">Presets</TabsTrigger>
              <TabsTrigger value="learning">
                <GraduationCap className="h-4 w-4 mr-1" />
                Learn
              </TabsTrigger>
            </TabsList>

            {/* Shortcuts Tab */}
            <TabsContent value="shortcuts" className="mt-4 space-y-4">
              <div className="flex gap-3">
                <div className="relative flex-1">
                  <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search shortcuts..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <Select value={filterCategory} onValueChange={setFilterCategory}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map((cat) => (
                      <SelectItem key={cat as string} value={cat as string}>
                        {cat as string}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <ScrollArea className="h-[400px]">
                <div className="space-y-1">
                  {filteredShortcuts.map((shortcut: Shortcut) => (
                    <div
                      key={shortcut.action_id}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{shortcut.name}</span>
                          {shortcut.is_custom && (
                            <Badge variant="secondary" className="text-xs">
                              Custom
                            </Badge>
                          )}
                          {!shortcut.is_enabled && (
                            <Badge variant="destructive" className="text-xs">
                              Disabled
                            </Badge>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground">{shortcut.category}</span>
                      </div>

                      <div className="flex items-center gap-2">
                        {editingShortcut === shortcut.action_id ? (
                          <div className="flex items-center gap-2">
                            <div
                              className={`px-3 py-1 border rounded min-w-[100px] text-center cursor-pointer ${
                                recordingKeys ? 'border-primary bg-primary/10' : ''
                              }`}
                              onClick={() => setRecordingKeys(!recordingKeys)}
                            >
                              {newKeyBinding || (recordingKeys ? 'Recording...' : 'Click to record')}
                            </div>
                            <Button
                              size="icon"
                              className="h-7 w-7"
                              onClick={() =>
                                setShortcutMutation.mutate({
                                  actionId: shortcut.action_id,
                                  key: newKeyBinding,
                                })
                              }
                              disabled={!newKeyBinding}
                            >
                              <Check className="h-4 w-4" />
                            </Button>
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-7 w-7"
                              onClick={() => {
                                setEditingShortcut(null);
                                setNewKeyBinding('');
                                setRecordingKeys(false);
                              }}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        ) : (
                          <>
                            {renderKeyBadge(shortcut.key)}
                            {shortcut.is_customizable && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7"
                                onClick={() => {
                                  setEditingShortcut(shortcut.action_id);
                                  setNewKeyBinding(shortcut.key);
                                }}
                              >
                                <Edit2 className="h-3 w-3" />
                              </Button>
                            )}
                            {shortcut.is_custom && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7"
                                onClick={() => resetShortcutMutation.mutate(shortcut.action_id)}
                              >
                                <RotateCcw className="h-3 w-3" />
                              </Button>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* Presets Tab */}
            <TabsContent value="presets" className="mt-4 space-y-4">
              <h4 className="font-medium">Application Presets</h4>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(presetsData?.application_presets || {}).map(
                  ([key, presetData]: [string, unknown]) => {
                    const preset = presetData as Record<string, unknown>;
                    return (
                    <Button
                      key={key}
                      variant="outline"
                      className="h-auto p-4 flex flex-col items-start"
                      onClick={() => {
                        toast({
                          title: 'Apply Preset',
                          description: `Applying ${preset.name as string} shortcuts...`,
                        });
                      }}
                    >
                      <span className="font-medium">{preset.name as string}</span>
                      <span className="text-xs text-muted-foreground">
                        {Object.keys(preset.mappings as object).length} shortcuts
                      </span>
                    </Button>
                  );
                  }
                )}
              </div>

              <h4 className="font-medium mt-6">Your Presets</h4>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {presetsData?.user_presets?.map((preset: ShortcutPreset) => (
                    <div
                      key={preset.id}
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                    >
                      <div>
                        <span className="font-medium">{preset.name}</span>
                        <div className="text-xs text-muted-foreground">
                          {preset.shortcut_count} shortcuts
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => applyPresetMutation.mutate(preset.id)}
                      >
                        Apply
                      </Button>
                    </div>
                  ))}

                  {(!presetsData?.user_presets || presetsData.user_presets.length === 0) && (
                    <div className="text-center py-8 text-muted-foreground">
                      <p>No custom presets yet</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* Learning Tab */}
            <TabsContent value="learning" className="mt-4 space-y-4">
              <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <GraduationCap className="h-6 w-6 text-primary" />
                  <div>
                    <span className="font-medium">Learning Mode</span>
                    <p className="text-xs text-muted-foreground">
                      Get hints when using the UI instead of shortcuts
                    </p>
                  </div>
                </div>
                <Switch
                  checked={learningStats?.is_learning_mode || false}
                  onCheckedChange={(checked) => toggleLearningMutation.mutate(checked)}
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2">
                      <Target className="h-5 w-5 text-primary" />
                      <div>
                        <div className="text-2xl font-bold">
                          {learningStats?.shortcuts_used_today || 0}
                        </div>
                        <div className="text-xs text-muted-foreground">Used Today</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2">
                      <Flame className="h-5 w-5 text-orange-500" />
                      <div>
                        <div className="text-2xl font-bold">
                          {learningStats?.current_streak || 0}
                        </div>
                        <div className="text-xs text-muted-foreground">Day Streak</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2">
                      <Trophy className="h-5 w-5 text-yellow-500" />
                      <div>
                        <div className="text-2xl font-bold">
                          {learningStats?.shortcuts_learned || 0}
                        </div>
                        <div className="text-xs text-muted-foreground">Mastered</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">Daily Goal</span>
                  <span className="text-sm text-muted-foreground">
                    {learningStats?.shortcuts_used_today || 0} / {learningStats?.daily_goal || 10}
                  </span>
                </div>
                <Progress
                  value={
                    ((learningStats?.shortcuts_used_today || 0) /
                      (learningStats?.daily_goal || 10)) *
                    100
                  }
                />
              </div>

              <div>
                <h4 className="font-medium mb-3">Shortcuts to Learn</h4>
                <div className="space-y-2">
                  {learningStats?.to_learn?.slice(0, 5).map((item: Record<string, unknown>, i: number) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                    >
                      <div>
                        <span className="font-medium">{item.shortcut__name as string}</span>
                        <div className="text-xs text-muted-foreground">
                          Used via UI {item.count as number} times
                        </div>
                      </div>
                      {renderKeyBadge(item.shortcut__default_key as string)}
                    </div>
                  ))}

                  {(!learningStats?.to_learn || learningStats.to_learn.length === 0) && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Trophy className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>You&apos;re using shortcuts like a pro!</p>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

export default KeyboardShortcutsEditor;
