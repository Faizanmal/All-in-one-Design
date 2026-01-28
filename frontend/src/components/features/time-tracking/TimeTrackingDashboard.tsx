"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Clock, Play, Pause, Square, Calendar, DollarSign, TrendingUp, FileText } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface TimeEntry {
  id: number;
  project: string;
  task: string;
  duration: number;
  date: string;
  billable: boolean;
}

export const TimeTrackingDashboard: React.FC = () => {
  const [currentView, setCurrentView] = useState('timer');

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-6 w-6" />
            Time Tracking Dashboard
          </CardTitle>
          <CardDescription>Track time, manage projects, and generate invoices</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={currentView} onValueChange={setCurrentView}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="timer">Timer</TabsTrigger>
              <TabsTrigger value="entries">Time Entries</TabsTrigger>
              <TabsTrigger value="tasks">Tasks</TabsTrigger>
              <TabsTrigger value="reports">Reports</TabsTrigger>
            </TabsList>
            <TabsContent value="timer" className="space-y-4">
              <ActiveTimer />
              <WeeklyGoalProgress />
            </TabsContent>
            <TabsContent value="entries">
              <TimeEntryList />
            </TabsContent>
            <TabsContent value="tasks">
              <TaskBoard />
            </TabsContent>
            <TabsContent value="reports">
              <InvoiceBuilder />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export const ActiveTimer: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [time, setTime] = useState(0);
  const [project, setProject] = useState('');
  const [task, setTask] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning) {
      interval = setInterval(() => {
        setTime((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning]);

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStart = () => {
    if (!project || !task) {
      toast({ title: "Please fill in project and task", variant: "destructive" });
      return;
    }
    setIsRunning(true);
  };

  const handleStop = () => {
    setIsRunning(false);
    if (time > 0) {
      toast({ title: "Time entry saved", description: `Tracked ${formatTime(time)} for ${task}` });
      setTime(0);
      setProject('');
      setTask('');
    }
  };

  return (
    <Card className="border-2">
      <CardContent className="pt-6">
        <div className="text-center mb-6">
          <div className="text-6xl font-bold font-mono mb-2">{formatTime(time)}</div>
          <Badge variant={isRunning ? "default" : "secondary"}>
            {isRunning ? 'Running' : 'Stopped'}
          </Badge>
        </div>

        <div className="space-y-3 mb-6">
          <Select value={project} onValueChange={setProject}>
            <SelectTrigger>
              <SelectValue placeholder="Select project" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="website">Website Redesign</SelectItem>
              <SelectItem value="mobile">Mobile App</SelectItem>
              <SelectItem value="branding">Brand Guidelines</SelectItem>
            </SelectContent>
          </Select>
          <Input
            placeholder="What are you working on?"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            disabled={isRunning}
          />
        </div>

        <div className="flex gap-2">
          {!isRunning ? (
            <Button className="flex-1" onClick={handleStart}>
              <Play className="h-4 w-4 mr-2" />
              Start Timer
            </Button>
          ) : (
            <>
              <Button variant="outline" className="flex-1" onClick={() => setIsRunning(false)}>
                <Pause className="h-4 w-4 mr-2" />
                Pause
              </Button>
              <Button variant="destructive" className="flex-1" onClick={handleStop}>
                <Square className="h-4 w-4 mr-2" />
                Stop
              </Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export const TimeEntryList: React.FC = () => {
  const entries: TimeEntry[] = [
    { id: 1, project: 'Website Redesign', task: 'Homepage design', duration: 7200, date: 'Today', billable: true },
    { id: 2, project: 'Mobile App', task: 'UI components', duration: 5400, date: 'Today', billable: true },
    { id: 3, project: 'Brand Guidelines', task: 'Color palette', duration: 3600, date: 'Yesterday', billable: false },
    { id: 4, project: 'Website Redesign', task: 'About page', duration: 4200, date: 'Yesterday', billable: true },
  ];

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const totalToday = entries.filter(e => e.date === 'Today').reduce((sum, e) => sum + e.duration, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Total Today</p>
          <p className="text-2xl font-bold">{formatDuration(totalToday)}</p>
        </div>
        <Button variant="outline">
          <Calendar className="h-4 w-4 mr-2" />
          This Week
        </Button>
      </div>

      <ScrollArea className="h-[400px]">
        <div className="space-y-3">
          {entries.map((entry) => (
            <Card key={entry.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium">{entry.task}</p>
                      {entry.billable && <Badge variant="secondary">Billable</Badge>}
                    </div>
                    <p className="text-sm text-muted-foreground">{entry.project}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">{formatDuration(entry.duration)}</p>
                    <p className="text-sm text-muted-foreground">{entry.date}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};

export const TaskBoard: React.FC = () => {
  const tasks = [
    { id: 1, title: 'Design homepage', project: 'Website', status: 'In Progress', priority: 'High' },
    { id: 2, title: 'Create mockups', project: 'Mobile App', status: 'To Do', priority: 'Medium' },
    { id: 3, title: 'Review feedback', project: 'Brand', status: 'Done', priority: 'Low' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Task Board</h3>
        <Button>Add Task</Button>
      </div>
      <div className="grid gap-3">
        {tasks.map((task) => (
          <Card key={task.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium mb-1">{task.title}</p>
                  <p className="text-sm text-muted-foreground">{task.project}</p>
                </div>
                <div className="flex gap-2">
                  <Badge variant={task.priority === 'High' ? 'destructive' : task.priority === 'Medium' ? 'default' : 'secondary'}>
                    {task.priority}
                  </Badge>
                  <Badge variant="outline">{task.status}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export const WeeklyGoalProgress: React.FC = () => {
  const weeklyGoal = 40; // hours
  const completed = 28; // hours
  const percentage = (completed / weeklyGoal) * 100;

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Weekly Goal</p>
              <p className="text-2xl font-bold">{completed}h / {weeklyGoal}h</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-500" />
          </div>
          <Progress value={percentage} className="h-3" />
          <p className="text-sm text-muted-foreground">
            {(weeklyGoal - completed)}h remaining • {percentage.toFixed(0)}% complete
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export const InvoiceBuilder: React.FC = () => {
  const [hourlyRate, setHourlyRate] = useState('75');

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Generate Invoice
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Hourly Rate</label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="number"
                  value={hourlyRate}
                  onChange={(e) => setHourlyRate(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Period</label>
              <Select defaultValue="week">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">This Week</SelectItem>
                  <SelectItem value="month">This Month</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="p-4 border rounded-lg space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total Hours:</span>
              <span className="font-semibold">28h</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Billable Hours:</span>
              <span className="font-semibold">24h</span>
            </div>
            <div className="flex justify-between text-lg font-bold pt-2 border-t">
              <span>Total Amount:</span>
              <span>${(24 * parseFloat(hourlyRate)).toFixed(2)}</span>
            </div>
          </div>

          <Button className="w-full">
            <FileText className="h-4 w-4 mr-2" />
            Generate Invoice PDF
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};