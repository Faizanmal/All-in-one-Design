"use client";

import React, { useState, useEffect } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import {
  Clock,
  Play,
  Pause,
  Square,
  Calendar,
  Timer,
  Edit3,
  Trash2,
  Download,
  FileText,
  Target,
  DollarSign,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface Project {
  id: number;
  name: string;
  color: string;
  client: string;
  hourly_rate: number;
  budget_hours: number;
  tracked_hours: number;
}

interface TimeEntry {
  id: number;
  project: Project;
  description: string;
  start_time: string;
  end_time?: string;
  duration: number;
  is_billable: boolean;
  is_running: boolean;
}


// Mock Data
const mockProjects: Project[] = [
  { id: 1, name: 'Website Redesign', color: '#3B82F6', client: 'Acme Corp', hourly_rate: 85, budget_hours: 120, tracked_hours: 78 },
  { id: 2, name: 'Mobile App UI', color: '#8B5CF6', client: 'TechStart Inc', hourly_rate: 95, budget_hours: 200, tracked_hours: 156 },
  { id: 3, name: 'Brand Identity', color: '#10B981', client: 'GreenLife', hourly_rate: 75, budget_hours: 40, tracked_hours: 32 },
  { id: 4, name: 'Marketing Campaign', color: '#F59E0B', client: 'Acme Corp', hourly_rate: 65, budget_hours: 60, tracked_hours: 45 },
];

const mockEntries: TimeEntry[] = [
  { id: 1, project: mockProjects[0], description: 'Homepage wireframes', start_time: '2024-02-20T09:00:00Z', end_time: '2024-02-20T11:30:00Z', duration: 9000, is_billable: true, is_running: false },
  { id: 2, project: mockProjects[1], description: 'Navigation component design', start_time: '2024-02-20T13:00:00Z', end_time: '2024-02-20T15:45:00Z', duration: 9900, is_billable: true, is_running: false },
  { id: 3, project: mockProjects[0], description: 'Client meeting', start_time: '2024-02-20T16:00:00Z', end_time: '2024-02-20T17:00:00Z', duration: 3600, is_billable: false, is_running: false },
  { id: 4, project: mockProjects[2], description: 'Logo concepts', start_time: '2024-02-19T10:00:00Z', end_time: '2024-02-19T14:00:00Z', duration: 14400, is_billable: true, is_running: false },
  { id: 5, project: mockProjects[3], description: 'Social media templates', start_time: '2024-02-19T15:00:00Z', end_time: '2024-02-19T18:00:00Z', duration: 10800, is_billable: true, is_running: false },
];

const formatDuration = (seconds: number): string => {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

const formatHours = (seconds: number): string => {
  const hrs = (seconds / 3600).toFixed(1);
  return `${hrs}h`;
};

// Timer Component
function ActiveTimer({ entry, onStop, onPause }: { entry: TimeEntry | null; onStop: () => void; onPause: () => void }) {
  const [elapsed, setElapsed] = useState(entry?.duration || 0);

  useEffect(() => {
    if (!entry?.is_running) return;
    const interval = setInterval(() => setElapsed(prev => prev + 1), 1000);
    return () => clearInterval(interval);
  }, [entry?.is_running]);

  if (!entry) {
    return (
      <div className="bg-gray-100 rounded-xl p-6 text-center">
        <Timer className="h-12 w-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">No active timer</p>
        <p className="text-sm text-gray-400">Start tracking time on a project</p>
      </div>
    );
  }

  return (
    <div className="bg-linear-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-white animate-pulse" />
          <span className="font-medium">{entry.project.name}</span>
        </div>
        <Badge className="bg-white/20 text-white border-0">{entry.is_billable ? 'Billable' : 'Non-billable'}</Badge>
      </div>
      <p className="text-blue-100 mb-4">{entry.description || 'No description'}</p>
      <div className="text-5xl font-mono font-bold mb-6 text-center">{formatDuration(elapsed)}</div>
      <div className="flex justify-center gap-3">
        <Button size="lg" variant="secondary" onClick={onPause} className="bg-white/20 hover:bg-white/30 text-white border-0">
          <Pause className="h-5 w-5 mr-2" />Pause
        </Button>
        <Button size="lg" onClick={onStop} className="bg-white text-purple-600 hover:bg-gray-100">
          <Square className="h-5 w-5 mr-2" />Stop
        </Button>
      </div>
    </div>
  );
}

// Time Entry Row Component
function TimeEntryRow({ entry, onEdit, onDelete }: { entry: TimeEntry; onEdit: () => void; onDelete: () => void }) {
  return (
    <div className="flex items-center gap-4 py-3 px-4 hover:bg-gray-50 rounded-lg group">
      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.project.color }} />
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 truncate">{entry.description || 'No description'}</p>
        <p className="text-sm text-gray-500">{entry.project.name}</p>
      </div>
      <div className="text-right">
        <p className="font-mono font-medium text-gray-900">{formatDuration(entry.duration)}</p>
        <p className="text-sm text-gray-500">
          {new Date(entry.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - 
          {entry.end_time ? new Date(entry.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'now'}
        </p>
      </div>
      <Badge variant="outline" className={entry.is_billable ? 'text-green-600 border-green-200' : 'text-gray-500'}>
        {entry.is_billable ? '$' : '-'}
      </Badge>
      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" size="sm" onClick={onEdit}><Edit3 className="h-4 w-4" /></Button>
        <Button variant="ghost" size="sm" onClick={onDelete}><Trash2 className="h-4 w-4 text-red-500" /></Button>
      </div>
    </div>
  );
}

// Project Card Component
function ProjectCard({ project }: { project: Project }) {
  const progress = (project.tracked_hours / project.budget_hours) * 100;
  const isOverBudget = progress > 100;

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: project.color }} />
            <div>
              <h4 className="font-medium text-gray-900">{project.name}</h4>
              <p className="text-sm text-gray-500">{project.client}</p>
            </div>
          </div>
          <Badge variant="outline">${project.hourly_rate}/hr</Badge>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Progress</span>
            <span className={isOverBudget ? 'text-red-600 font-medium' : 'text-gray-900'}>
              {project.tracked_hours}h / {project.budget_hours}h
            </span>
          </div>
          <Progress value={Math.min(progress, 100)} className={isOverBudget ? 'bg-red-100' : ''} />
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Earnings</span>
            <span className="text-green-600 font-medium">${(project.tracked_hours * project.hourly_rate).toLocaleString()}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function TimeTrackingPage() {
  const { toast } = useToast();
  const [entries, setEntries] = useState<TimeEntry[]>(mockEntries);
  const [projects] = useState<Project[]>(mockProjects);
  const [activeEntry, setActiveEntry] = useState<TimeEntry | null>(null);
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [description, setDescription] = useState('');
  const [isBillable, setIsBillable] = useState(true);

  const startTimer = () => {
    if (!selectedProject) {
      toast({ title: 'Error', description: 'Please select a project', variant: 'destructive' });
      return;
    }
    const project = projects.find(p => p.id.toString() === selectedProject);
    if (!project) return;

    const newEntry: TimeEntry = {
      id: Date.now(),
      project,
      description,
      start_time: new Date().toISOString(),
      duration: 0,
      is_billable: isBillable,
      is_running: true,
    };
    setActiveEntry(newEntry);
    setDescription('');
    toast({ title: 'Timer Started', description: `Tracking time for ${project.name}` });
  };

  const stopTimer = () => {
    if (!activeEntry) return;
    const stoppedEntry = { ...activeEntry, is_running: false, end_time: new Date().toISOString() };
    setEntries(prev => [stoppedEntry, ...prev]);
    setActiveEntry(null);
    toast({ title: 'Timer Stopped', description: `Entry saved: ${formatDuration(stoppedEntry.duration)}` });
  };

  const pauseTimer = () => {
    if (!activeEntry) return;
    setActiveEntry(prev => prev ? { ...prev, is_running: false } : null);
    toast({ title: 'Timer Paused' });
  };

  // Calculate stats
  const todayEntries = entries.filter(e => new Date(e.start_time).toDateString() === new Date().toDateString());
  const thisWeekEntries = entries;
  const stats = {
    todayHours: todayEntries.reduce((acc, e) => acc + e.duration, 0) / 3600,
    weekHours: thisWeekEntries.reduce((acc, e) => acc + e.duration, 0) / 3600,
    billableHours: thisWeekEntries.filter(e => e.is_billable).reduce((acc, e) => acc + e.duration, 0) / 3600,
    earnings: thisWeekEntries.filter(e => e.is_billable).reduce((acc, e) => acc + (e.duration / 3600) * e.project.hourly_rate, 0),
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-hidden p-6">
          <div className="max-w-7xl mx-auto h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                  <Clock className="h-7 w-7 text-blue-600" />Time Tracking
                </h1>
                <p className="text-gray-500">Track and manage your project time</p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline"><Download className="h-4 w-4 mr-2" />Export</Button>
                <Button variant="outline"><FileText className="h-4 w-4 mr-2" />Reports</Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg"><Timer className="h-5 w-5 text-blue-600" /></div>
                    <div>
                      <p className="text-sm text-gray-500">Today</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.todayHours.toFixed(1)}h</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 rounded-lg"><Calendar className="h-5 w-5 text-purple-600" /></div>
                    <div>
                      <p className="text-sm text-gray-500">This Week</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.weekHours.toFixed(1)}h</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg"><Target className="h-5 w-5 text-green-600" /></div>
                    <div>
                      <p className="text-sm text-gray-500">Billable</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.billableHours.toFixed(1)}h</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-amber-100 rounded-lg"><DollarSign className="h-5 w-5 text-amber-600" /></div>
                    <div>
                      <p className="text-sm text-gray-500">Earnings</p>
                      <p className="text-2xl font-bold text-gray-900">${stats.earnings.toLocaleString()}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content */}
            <div className="flex-1 grid grid-cols-3 gap-6 overflow-hidden">
              {/* Timer & Entry Form */}
              <div className="space-y-6">
                <ActiveTimer entry={activeEntry} onStop={stopTimer} onPause={pauseTimer} />

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">Start New Timer</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Select value={selectedProject} onValueChange={setSelectedProject}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select project" />
                      </SelectTrigger>
                      <SelectContent>
                        {projects.map(p => (
                          <SelectItem key={p.id} value={p.id.toString()}>
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded" style={{ backgroundColor: p.color }} />
                              {p.name}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Input placeholder="What are you working on?" value={description} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDescription(e.target.value)} />
                    <div className="flex items-center justify-between">
                      <label className="flex items-center gap-2 text-sm">
                        <input type="checkbox" checked={isBillable} onChange={(e) => setIsBillable(e.target.checked)} className="rounded border-gray-300" />
                        Billable
                      </label>
                      <Button onClick={startTimer} disabled={!!activeEntry}>
                        <Play className="h-4 w-4 mr-2" />Start Timer
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">Projects</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {projects.slice(0, 3).map(p => <ProjectCard key={p.id} project={p} />)}
                  </CardContent>
                </Card>
              </div>

              {/* Time Entries */}
              <div className="col-span-2 flex flex-col">
                <Card className="flex-1 flex flex-col overflow-hidden">
                  <CardHeader className="pb-3 flex-row items-center justify-between">
                    <CardTitle className="text-base">Time Entries</CardTitle>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm"><ChevronLeft className="h-4 w-4" /></Button>
                      <span className="text-sm font-medium">This Week</span>
                      <Button variant="ghost" size="sm"><ChevronRight className="h-4 w-4" /></Button>
                    </div>
                  </CardHeader>
                  <CardContent className="flex-1 overflow-hidden p-0">
                    <ScrollArea className="h-full">
                      <div className="px-6 pb-6">
                        {/* Today */}
                        <div className="mb-6">
                          <div className="flex items-center justify-between py-2 border-b border-gray-200 mb-2 sticky top-0 bg-white">
                            <span className="font-medium text-gray-900">Today</span>
                            <span className="text-sm text-gray-500">{formatHours(todayEntries.reduce((a, e) => a + e.duration, 0))}</span>
                          </div>
                          {todayEntries.length > 0 ? (
                            todayEntries.map(entry => (
                              <TimeEntryRow key={entry.id} entry={entry} onEdit={() => {}} onDelete={() => setEntries(prev => prev.filter(e => e.id !== entry.id))} />
                            ))
                          ) : (
                            <p className="text-center py-8 text-gray-400">No entries today</p>
                          )}
                        </div>

                        {/* Yesterday */}
                        <div>
                          <div className="flex items-center justify-between py-2 border-b border-gray-200 mb-2 sticky top-0 bg-white">
                            <span className="font-medium text-gray-900">Yesterday</span>
                            <span className="text-sm text-gray-500">{formatHours(entries.filter(e => {
                              const d = new Date(e.start_time);
                              const y = new Date();
                              y.setDate(y.getDate() - 1);
                              return d.toDateString() === y.toDateString();
                            }).reduce((a, e) => a + e.duration, 0))}</span>
                          </div>
                          {entries.filter(e => {
                            const d = new Date(e.start_time);
                            const y = new Date();
                            y.setDate(y.getDate() - 1);
                            return d.toDateString() === y.toDateString();
                          }).map(entry => (
                            <TimeEntryRow key={entry.id} entry={entry} onEdit={() => {}} onDelete={() => setEntries(prev => prev.filter(e => e.id !== entry.id))} />
                          ))}
                        </div>
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
