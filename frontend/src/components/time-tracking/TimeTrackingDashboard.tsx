'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  Clock, Play, Pause, Square, Plus, Calendar, FileText,
  DollarSign, BarChart3, Users, Target, CheckCircle, Circle,
  MoreVertical, Trash2, Edit, ChevronDown, ChevronRight,
  ArrowUpDown, Filter, Download, Send, AlertCircle, Timer
} from 'lucide-react';

// Types
interface TimeEntry {
  id: string;
  projectId: string;
  projectName: string;
  taskId: string | null;
  taskName: string | null;
  description: string;
  startTime: string;
  endTime: string | null;
  duration: number; // seconds
  isBillable: boolean;
  hourlyRate: number;
}

interface Task {
  id: string;
  projectId: string;
  title: string;
  description: string;
  status: 'backlog' | 'todo' | 'in_progress' | 'review' | 'done';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigneeId: string | null;
  assigneeName: string | null;
  dueDate: string | null;
  estimatedHours: number;
  loggedHours: number;
  tags: string[];
}

interface Invoice {
  id: string;
  invoiceNumber: string;
  clientId: string;
  clientName: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  totalAmount: number;
  dueDate: string;
  entries: TimeEntry[];
}

interface WeeklyGoal {
  id: string;
  targetHours: number;
  loggedHours: number;
  weekStart: string;
}

// Active Timer Component
export function ActiveTimer({
  projectId,
  onStop,
}: {
  projectId?: string;
  onStop?: (entry: TimeEntry) => void;
}) {
  const [isRunning, setIsRunning] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [description, setDescription] = useState('');
  const [selectedProject, setSelectedProject] = useState(projectId || '');
  const [selectedTask, setSelectedTask] = useState('');
  const [isBillable, setIsBillable] = useState(true);
  const startTimeRef = useRef<Date | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning) {
      interval = setInterval(() => {
        if (startTimeRef.current) {
          setElapsed(Math.floor((Date.now() - startTimeRef.current.getTime()) / 1000));
        }
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
    setIsRunning(true);
    startTimeRef.current = new Date();
    
    fetch('/api/v1/time-tracking/tracker/start/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: selectedProject,
        task_id: selectedTask || null,
        description,
        is_billable: isBillable,
      }),
    }).catch(console.error);
  };

  const handleStop = async () => {
    setIsRunning(false);
    
    try {
      const response = await fetch('/api/v1/time-tracking/tracker/stop/', {
        method: 'POST',
      });
      const entry = await response.json();
      onStop?.(entry);
    } catch (error) {
      console.error('Failed to stop timer', error);
    }

    setElapsed(0);
    setDescription('');
    startTimeRef.current = null;
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <div className="flex items-center gap-4">
        {/* Description Input */}
        <div className="flex-1">
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What are you working on?"
            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
            disabled={isRunning}
          />
        </div>

        {/* Project Selector */}
        <select
          value={selectedProject}
          onChange={(e) => setSelectedProject(e.target.value)}
          className="px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg min-w-[150px]"
          disabled={isRunning}
        >
          <option value="">Select Project</option>
          <option value="1">Website Redesign</option>
          <option value="2">Mobile App</option>
          <option value="3">Brand Identity</option>
        </select>

        {/* Billable Toggle */}
        <button
          onClick={() => setIsBillable(!isBillable)}
          className={`p-3 rounded-lg ${isBillable ? 'bg-green-600' : 'bg-gray-700'}`}
          disabled={isRunning}
        >
          <DollarSign className="w-5 h-5" />
        </button>

        {/* Timer Display */}
        <div className="font-mono text-2xl font-bold min-w-[120px] text-center">
          {formatTime(elapsed)}
        </div>

        {/* Start/Stop Button */}
        <button
          onClick={isRunning ? handleStop : handleStart}
          className={`p-4 rounded-xl ${
            isRunning
              ? 'bg-red-600 hover:bg-red-700'
              : 'bg-green-600 hover:bg-green-700'
          }`}
        >
          {isRunning ? (
            <Square className="w-6 h-6 fill-white" />
          ) : (
            <Play className="w-6 h-6 fill-white" />
          )}
        </button>
      </div>
    </div>
  );
}

// Time Entry List Component
export function TimeEntryList({
  entries,
  onEdit,
  onDelete,
}: {
  entries: TimeEntry[];
  onEdit: (entry: TimeEntry) => void;
  onDelete: (id: string) => void;
}) {
  const formatDuration = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hrs}h ${mins}m`;
  };

  const groupedByDate = entries.reduce((acc, entry) => {
    const date = new Date(entry.startTime).toLocaleDateString();
    if (!acc[date]) acc[date] = [];
    acc[date].push(entry);
    return acc;
  }, {} as Record<string, TimeEntry[]>);

  return (
    <div className="space-y-6">
      {Object.entries(groupedByDate).map(([date, dateEntries]) => {
        const totalDuration = dateEntries.reduce((sum, e) => sum + e.duration, 0);
        
        return (
          <div key={date}>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-gray-400">{date}</h3>
              <span className="text-sm text-gray-500">
                Total: {formatDuration(totalDuration)}
              </span>
            </div>
            
            <div className="space-y-2">
              {dateEntries.map((entry) => (
                <div
                  key={entry.id}
                  className="flex items-center gap-4 p-3 bg-gray-800 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="font-medium text-white">{entry.description || 'No description'}</div>
                    <div className="text-sm text-gray-400">
                      {entry.projectName}
                      {entry.taskName && ` • ${entry.taskName}`}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    {entry.isBillable && (
                      <DollarSign className="w-4 h-4 text-green-400" />
                    )}
                    <span className="font-mono text-gray-300">
                      {formatDuration(entry.duration)}
                    </span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => onEdit(entry)}
                        className="p-1.5 hover:bg-gray-700 rounded"
                      >
                        <Edit className="w-4 h-4 text-gray-400" />
                      </button>
                      <button
                        onClick={() => onDelete(entry.id)}
                        className="p-1.5 hover:bg-gray-700 rounded"
                      >
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Kanban Task Board Component
export function TaskBoard({
  projectId,
  tasks,
  onUpdateTask,
  onDeleteTask,
}: {
  projectId: string;
  tasks: Task[];
  onUpdateTask: (taskId: string, updates: Partial<Task>) => void;
  onDeleteTask: (taskId: string) => void;
}) {
  const columns = [
    { id: 'backlog', name: 'Backlog', color: 'gray' },
    { id: 'todo', name: 'To Do', color: 'blue' },
    { id: 'in_progress', name: 'In Progress', color: 'amber' },
    { id: 'review', name: 'Review', color: 'purple' },
    { id: 'done', name: 'Done', color: 'green' },
  ];

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-gray-500';
    }
  };

  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    e.dataTransfer.setData('taskId', taskId);
  };

  const handleDrop = (e: React.DragEvent, status: Task['status']) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('taskId');
    onUpdateTask(taskId, { status });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map((column) => {
        const columnTasks = tasks.filter((t) => t.status === column.id);
        
        return (
          <div
            key={column.id}
            className="flex-shrink-0 w-72 bg-gray-800 rounded-xl p-4"
            onDrop={(e) => handleDrop(e, column.id as Task['status'])}
            onDragOver={handleDragOver}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white">{column.name}</h3>
              <span className="px-2 py-0.5 bg-gray-700 text-gray-400 rounded text-sm">
                {columnTasks.length}
              </span>
            </div>

            <div className="space-y-3">
              {columnTasks.map((task) => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, task.id)}
                  className="p-3 bg-gray-700 rounded-lg cursor-grab active:cursor-grabbing"
                >
                  <div className="flex items-start gap-2 mb-2">
                    <div className={`w-2 h-2 rounded-full mt-2 ${getPriorityColor(task.priority)}`} />
                    <div className="flex-1">
                      <div className="font-medium text-white text-sm">{task.title}</div>
                    </div>
                  </div>

                  {task.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {task.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-1.5 py-0.5 bg-gray-600 text-gray-300 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {task.loggedHours}/{task.estimatedHours}h
                    </div>
                    {task.dueDate && (
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(task.dueDate).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <button className="w-full mt-3 p-2 border border-dashed border-gray-600 text-gray-400 rounded-lg hover:border-gray-500 hover:text-gray-300 flex items-center justify-center gap-1">
              <Plus className="w-4 h-4" />
              Add Task
            </button>
          </div>
        );
      })}
    </div>
  );
}

// Weekly Goals Component
export function WeeklyGoalProgress({ goal }: { goal: WeeklyGoal }) {
  const percentage = Math.min((goal.loggedHours / goal.targetHours) * 100, 100);
  
  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Weekly Goal</h3>
        <span className="text-sm text-gray-400">
          Week of {new Date(goal.weekStart).toLocaleDateString()}
        </span>
      </div>

      <div className="flex items-end gap-4 mb-3">
        <div className="text-3xl font-bold">{goal.loggedHours.toFixed(1)}h</div>
        <div className="text-gray-400">of {goal.targetHours}h goal</div>
      </div>

      <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${
            percentage >= 100 ? 'bg-green-500' : percentage >= 75 ? 'bg-blue-500' : 'bg-amber-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="mt-2 text-sm text-gray-400">
        {percentage >= 100
          ? '🎉 Goal achieved!'
          : `${(goal.targetHours - goal.loggedHours).toFixed(1)}h remaining`}
      </div>
    </div>
  );
}

// Invoice Builder Component
export function InvoiceBuilder({
  entries,
  onCreateInvoice,
}: {
  entries: TimeEntry[];
  onCreateInvoice: (invoice: Partial<Invoice>) => void;
}) {
  const [selectedEntries, setSelectedEntries] = useState<string[]>([]);
  const [clientId, setClientId] = useState('');
  const [dueDate, setDueDate] = useState('');

  const billableEntries = entries.filter((e) => e.isBillable && !selectedEntries.includes(e.id));
  const selected = entries.filter((e) => selectedEntries.includes(e.id));
  const totalAmount = selected.reduce((sum, e) => sum + (e.duration / 3600) * e.hourlyRate, 0);

  const handleCreate = () => {
    onCreateInvoice({
      clientId,
      dueDate,
      entries: selected,
      totalAmount,
    });
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 text-white">
      <h3 className="font-semibold text-lg mb-4">Create Invoice</h3>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Client</label>
          <select
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg"
          >
            <option value="">Select Client</option>
            <option value="1">Acme Corp</option>
            <option value="2">TechStart Inc</option>
            <option value="3">Design Agency</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Due Date</label>
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg"
          />
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-400 mb-3">
          Billable Time Entries ({billableEntries.length} available)
        </h4>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {billableEntries.map((entry) => (
            <label
              key={entry.id}
              className="flex items-center gap-3 p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-650"
            >
              <input
                type="checkbox"
                checked={selectedEntries.includes(entry.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedEntries([...selectedEntries, entry.id]);
                  } else {
                    setSelectedEntries(selectedEntries.filter((id) => id !== entry.id));
                  }
                }}
                className="w-4 h-4 rounded bg-gray-600"
              />
              <div className="flex-1">
                <div className="text-sm">{entry.description}</div>
                <div className="text-xs text-gray-400">{entry.projectName}</div>
              </div>
              <div className="text-sm font-mono">
                ${((entry.duration / 3600) * entry.hourlyRate).toFixed(2)}
              </div>
            </label>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg mb-6">
        <span className="font-medium">Total Amount</span>
        <span className="text-2xl font-bold">${totalAmount.toFixed(2)}</span>
      </div>

      <button
        onClick={handleCreate}
        disabled={selectedEntries.length === 0 || !clientId}
        className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium disabled:opacity-50"
      >
        Create Invoice
      </button>
    </div>
  );
}

// Main Time Tracking Dashboard
export function TimeTrackingDashboard({ projectId }: { projectId?: string }) {
  const [entries, setEntries] = useState<TimeEntry[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [weeklyGoal, setWeeklyGoal] = useState<WeeklyGoal | null>(null);
  const [activeTab, setActiveTab] = useState<'time' | 'tasks' | 'invoices'>('time');

  const loadData = React.useCallback(async () => {
    try {
      const [entriesRes, tasksRes, goalRes] = await Promise.all([
        fetch(`/api/v1/time-tracking/entries/?project=${projectId || ''}`),
        fetch(`/api/v1/time-tracking/tasks/?project=${projectId || ''}`),
        fetch('/api/v1/time-tracking/goals/current/'),
      ]);

      const entriesData = await entriesRes.json();
      const tasksData = await tasksRes.json();
      const goalData = await goalRes.json();

      setEntries(entriesData.results || entriesData);
      setTasks(tasksData.results || tasksData);
      setWeeklyGoal(goalData);
    } catch (error) {
      // Mock data
      setEntries([
        {
          id: '1',
          projectId: '1',
          projectName: 'Website Redesign',
          taskId: '1',
          taskName: 'Homepage Design',
          description: 'Working on hero section',
          startTime: new Date().toISOString(),
          endTime: new Date().toISOString(),
          duration: 3600,
          isBillable: true,
          hourlyRate: 75,
        },
      ]);
      setTasks([
        {
          id: '1',
          projectId: '1',
          title: 'Homepage Design',
          description: 'Design the new homepage layout',
          status: 'in_progress',
          priority: 'high',
          assigneeId: '1',
          assigneeName: 'John Doe',
          dueDate: new Date(Date.now() + 86400000 * 3).toISOString(),
          estimatedHours: 8,
          loggedHours: 3,
          tags: ['design', 'urgent'],
        },
      ]);
      setWeeklyGoal({
        id: '1',
        targetHours: 40,
        loggedHours: 28.5,
        weekStart: new Date().toISOString(),
      });
    }
  }, [projectId]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [entriesRes, tasksRes, goalRes] = await Promise.all([
          fetch(`/api/v1/time-tracking/entries/?project=${projectId || ''}`),
          fetch(`/api/v1/time-tracking/tasks/?project=${projectId || ''}`),
          fetch('/api/v1/time-tracking/goals/current/'),
        ]);

        const entriesData = await entriesRes.json();
        const tasksData = await tasksRes.json();
        const goalData = await goalRes.json();

        setEntries(entriesData.results || entriesData);
        setTasks(tasksData.results || tasksData);
        setWeeklyGoal(goalData);
      } catch (error) {
        // Mock data
        setEntries([
          {
            id: '1',
            projectId: '1',
            projectName: 'Website Redesign',
            taskId: '1',
            taskName: 'Homepage Design',
            startTime: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            endTime: null,
            duration: 7200000,
            description: 'Working on homepage design',
            isBillable: true,
            tags: ['design', 'frontend'],
          },
        ]);
        setTasks([
          {
            id: '1',
            projectId: '1',
            name: 'Homepage Design',
            description: 'Design the main homepage',
            estimatedHours: 8,
            actualHours: 6.5,
            status: 'in_progress',
            priority: 'high',
            assignedTo: '1',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
        ]);
        setWeeklyGoal({ hours: 40, achieved: 32 });
      }
    };

    fetchData();
  }, [projectId]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold">Time Tracking</h1>

        {/* Active Timer */}
        <ActiveTimer
          projectId={projectId}
          onStop={(entry) => setEntries([entry, ...entries])}
        />

        {/* Weekly Goal */}
        {weeklyGoal && <WeeklyGoalProgress goal={weeklyGoal} />}

        {/* Tabs */}
        <div className="flex border-b border-gray-700">
          {(['time', 'tasks', 'invoices'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-medium capitalize transition-colors ${
                activeTab === tab
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {tab === 'time' ? 'Time Entries' : tab}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'time' && (
          <TimeEntryList
            entries={entries}
            onEdit={(entry) => console.log('Edit', entry)}
            onDelete={(id) => setEntries(entries.filter((e) => e.id !== id))}
          />
        )}

        {activeTab === 'tasks' && (
          <TaskBoard
            projectId={projectId || ''}
            tasks={tasks}
            onUpdateTask={(taskId, updates) => {
              setTasks(tasks.map((t) => (t.id === taskId ? { ...t, ...updates } : t)));
            }}
            onDeleteTask={(taskId) => setTasks(tasks.filter((t) => t.id !== taskId))}
          />
        )}

        {activeTab === 'invoices' && (
          <InvoiceBuilder
            entries={entries}
            onCreateInvoice={(invoice) => console.log('Create invoice', invoice)}
          />
        )}
      </div>
    </div>
  );
}

export default TimeTrackingDashboard;
