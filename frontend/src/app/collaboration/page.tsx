'use client';

import { useState, useEffect, useCallback } from 'react';
import { tasksApi, teamChatApi, chatMessagesApi, Task, TeamChat, ChatMessage } from '@/lib/collaboration-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { 
  CheckSquare, 
  MessageCircle, 
  Plus, 
  Send, 
  Calendar,
  User,
  Smile
} from 'lucide-react';

export default function CollaborationPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [chats, setChats] = useState<TeamChat[]>([]);
  const [selectedChat, setSelectedChat] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDesc, setNewTaskDesc] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');
  const [newMessage, setNewMessage] = useState('');
  const { toast } = useToast();

  // Load tasks
  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      const response = await tasksApi.list();
      setTasks(response.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load tasks',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  // Load chats
  const loadChats = useCallback(async () => {
    try {
      const response = await teamChatApi.list();
      setChats(response.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load chats',
        variant: 'destructive',
      });
    }
  }, [toast]);

  // Load messages for selected chat
  const loadMessages = useCallback(async (chatId: number) => {
    try {
      const response = await teamChatApi.getMessages(chatId);
      setMessages(response.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load messages',
        variant: 'destructive',
      });
    }
  }, [toast]);

  // ...existing code...

  useEffect(() => {
    loadTasks();
    loadChats();
  }, [loadTasks, loadChats]);

  useEffect(() => {
    if (selectedChat) {
      loadMessages(selectedChat);
    }
  }, [selectedChat, loadMessages]);

  // Create task
  const handleCreateTask = async () => {
    if (!newTaskTitle.trim()) return;
    
    try {
      // Note: You'll need to provide team ID from context/state
      await tasksApi.create({
        team: 1, // Replace with actual team ID
        title: newTaskTitle,
        description: newTaskDesc,
        priority: newTaskPriority,
      });
      setNewTaskTitle('');
      setNewTaskDesc('');
      setNewTaskPriority('medium');
      toast({
        title: 'Success',
        description: 'Task created successfully',
      });
      loadTasks();
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to create task',
        variant: 'destructive',
      });
    }
  };

  // Update task status
  const handleUpdateTaskStatus = async (taskId: number, status: string) => {
    try {
      await tasksApi.updateStatus(taskId, status);
      toast({
        title: 'Success',
        description: 'Task status updated',
      });
      loadTasks();
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to update task status',
        variant: 'destructive',
      });
    }
  };

  // Send message and add emoji reaction using chatMessagesApi and Smile icon
  const handleSendMessage = async () => {
    if (!selectedChat || !newMessage.trim()) return;
    try {
      await teamChatApi.sendMessage(selectedChat, newMessage);
      // Example: Add a smile reaction to the last message
      if (messages.length > 0) {
        await chatMessagesApi.addReaction(messages[messages.length - 1].id, '😊');
      }
      setNewMessage('');
      loadMessages(selectedChat);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to send message',
        variant: 'destructive',
      });
    }
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'default';
      case 'in_progress': return 'secondary';
      case 'review': return 'outline';
      default: return 'destructive';
    }
  };

  // Get priority badge color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'destructive';
      case 'high': return 'secondary';
      case 'medium': return 'outline';
      default: return 'default';
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Team Collaboration</h1>
        <p className="text-muted-foreground">Manage tasks and communicate with your team</p>
      </div>

      <Tabs defaultValue="tasks" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="tasks">
            <CheckSquare className="w-4 h-4 mr-2" />
            Tasks
          </TabsTrigger>
          <TabsTrigger value="chat">
            <MessageCircle className="w-4 h-4 mr-2" />
            Team Chat
          </TabsTrigger>
        </TabsList>

        <TabsContent value="tasks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create New Task</CardTitle>
              <CardDescription>Add a new task for your team</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                placeholder="Task title"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
              />
              <Textarea
                placeholder="Task description"
                value={newTaskDesc}
                onChange={(e) => setNewTaskDesc(e.target.value)}
              />
              <Select value={newTaskPriority} onValueChange={(v) => setNewTaskPriority(v as 'low' | 'medium' | 'high' | 'urgent')}>
                <SelectTrigger>
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={handleCreateTask}>
                <Plus className="w-4 h-4 mr-2" />
                Create Task
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Team Tasks</CardTitle>
              <CardDescription>All tasks for your team</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p>Loading tasks...</p>
              ) : tasks.length === 0 ? (
                <p className="text-muted-foreground">No tasks yet</p>
              ) : (
                <div className="space-y-3">
                  {tasks.map((task) => (
                    <Card key={task.id}>
                      <CardContent className="pt-6">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <h3 className="font-semibold">{task.title}</h3>
                            <div className="flex gap-2">
                              <Badge variant={getStatusColor(task.status)}>
                                {task.status.replace('_', ' ')}
                              </Badge>
                              <Badge variant={getPriorityColor(task.priority)}>
                                {task.priority}
                              </Badge>
                            </div>
                          </div>
                          <p className="text-sm text-muted-foreground">{task.description}</p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            {task.assigned_to && (
                              <span className="flex items-center gap-1">
                                <User className="w-3 h-3" />
                                {task.assigned_to.username}
                              </span>
                            )}
                            {task.due_date && (
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(task.due_date).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                          <div className="flex gap-2 mt-2">
                            <Select
                              value={task.status}
                              onValueChange={(status) => handleUpdateTaskStatus(task.id, status)}
                            >
                              <SelectTrigger className="w-[180px]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="todo">To Do</SelectItem>
                                <SelectItem value="in_progress">In Progress</SelectItem>
                                <SelectItem value="review">Review</SelectItem>
                                <SelectItem value="completed">Completed</SelectItem>
                                <SelectItem value="cancelled">Cancelled</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="chat" className="space-y-4">
          <div className="grid grid-cols-12 gap-4">
            <Card className="col-span-4">
              <CardHeader>
                <CardTitle>Chat Rooms</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {chats.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No chat rooms</p>
                  ) : (
                    chats.map((chat) => (
                      <Button
                        key={chat.id}
                        variant={selectedChat === chat.id ? 'default' : 'outline'}
                        className="w-full justify-start"
                        onClick={() => setSelectedChat(chat.id)}
                      >
                        <MessageCircle className="w-4 h-4 mr-2" />
                        {chat.name}
                      </Button>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="col-span-8">
              <CardHeader>
                <CardTitle>Messages</CardTitle>
              </CardHeader>
              <CardContent>
                {!selectedChat ? (
                  <p className="text-muted-foreground">Select a chat room to view messages</p>
                ) : (
                  <>
                    <div className="space-y-3 mb-4 max-h-96 overflow-y-auto">
                      {messages.length === 0 ? (
                        <p className="text-muted-foreground">No messages yet</p>
                      ) : (
                        messages.map((message) => (
                          <div key={message.id} className="flex gap-2 items-center">
                            <div className="flex-1">
                              <p className="font-semibold text-sm">{message.user.username}</p>
                              <p className="text-sm">{message.content}</p>
                              <p className="text-xs text-muted-foreground">
                                {new Date(message.created_at).toLocaleString()}
                              </p>
                            </div>
                            {/* Use Smile icon as a reaction button */}
                            <Button variant="ghost" size="icon" onClick={() => chatMessagesApi.addReaction(message.id, '😊')}>
                              <Smile className="w-4 h-4" />
                            </Button>
                          </div>
                        ))
                      )}
                    </div>
                    
                    <div className="flex gap-2">
                      <Input
                        placeholder="Type a message..."
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      />
                      <Button onClick={handleSendMessage}>
                        <Send className="w-4 h-4" />
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
