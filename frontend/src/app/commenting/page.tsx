"use client";

import React, { useState } from 'react';
import Image from 'next/image';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  MessageSquare,
  Search,
  CheckCircle,
  Circle,
  MoreVertical,
  Reply,
  Smile,
  AtSign,
  Image as ImageIcon,
  Paperclip,
  Send,
  Pin,
  Trash2,
  Edit3,
  Flag,
  Bell,
  BellOff,
  MessageCircle,
  Users,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface User {
  id: number;
  username: string;
  full_name: string;
  avatar?: string;
}

interface Reaction {
  emoji: string;
  count: number;
  users: string[];
  hasReacted: boolean;
}

interface Comment {
  id: number;
  content: string;
  author: User;
  created_at: string;
  updated_at?: string;
  reactions: Reaction[];
  replies?: Comment[];
  is_pinned: boolean;
  is_resolved: boolean;
  attachments?: { id: number; name: string; type: string }[];
  mentions?: string[];
}

interface CommentThread {
  id: number;
  title: string;
  design_id: number;
  design_name: string;
  design_thumbnail: string;
  position_x: number;
  position_y: number;
  status: 'open' | 'resolved' | 'archived';
  priority: 'low' | 'medium' | 'high';
  comments: Comment[];
  participants: User[];
  created_by: User;
  created_at: string;
  last_activity: string;
  is_subscribed: boolean;
}

// Mock Data
const currentUser: User = { id: 1, username: 'john_doe', full_name: 'John Doe', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=john' };

const mockUsers: User[] = [
  currentUser,
  { id: 2, username: 'jane_smith', full_name: 'Jane Smith', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=jane' },
  { id: 3, username: 'mike_wilson', full_name: 'Mike Wilson', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=mike' },
  { id: 4, username: 'sarah_jones', full_name: 'Sarah Jones', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=sarah' },
];

const mockThreads: CommentThread[] = [
  {
    id: 1, title: 'Header alignment issue', design_id: 1, design_name: 'Homepage Redesign',
    design_thumbnail: 'https://picsum.photos/seed/d1/200/150', position_x: 45, position_y: 12,
    status: 'open', priority: 'high',
    comments: [
      {
        id: 1, content: 'The header logo seems misaligned on mobile viewports. Can we adjust the spacing?',
        author: mockUsers[1], created_at: '2024-02-20T10:30:00Z',
        reactions: [{ emoji: '👍', count: 2, users: ['mike_wilson', 'sarah_jones'], hasReacted: false }],
        is_pinned: true, is_resolved: false, mentions: ['mike_wilson'],
      },
      {
        id: 2, content: '@jane_smith I\'ll take a look at this. What\'s the exact viewport width where it breaks?',
        author: mockUsers[2], created_at: '2024-02-20T11:45:00Z',
        reactions: [], is_pinned: false, is_resolved: false, mentions: ['jane_smith'],
      },
      {
        id: 3, content: 'It breaks around 768px. Here\'s a screenshot attached.',
        author: mockUsers[1], created_at: '2024-02-20T14:00:00Z',
        reactions: [{ emoji: '🙏', count: 1, users: ['mike_wilson'], hasReacted: false }],
        is_pinned: false, is_resolved: false,
        attachments: [{ id: 1, name: 'screenshot-mobile.png', type: 'image' }],
      },
    ],
    participants: [mockUsers[1], mockUsers[2], mockUsers[3]],
    created_by: mockUsers[1], created_at: '2024-02-20T10:30:00Z', last_activity: '2024-02-20T14:00:00Z',
    is_subscribed: true,
  },
  {
    id: 2, title: 'Color contrast accessibility', design_id: 1, design_name: 'Homepage Redesign',
    design_thumbnail: 'https://picsum.photos/seed/d1/200/150', position_x: 30, position_y: 65,
    status: 'resolved', priority: 'medium',
    comments: [
      {
        id: 4, content: 'The button text color doesn\'t meet WCAG AA contrast requirements against the background.',
        author: mockUsers[3], created_at: '2024-02-18T09:00:00Z',
        reactions: [], is_pinned: false, is_resolved: true,
      },
      {
        id: 5, content: 'Fixed! Changed the text color to #FFFFFF which now passes AA standards.',
        author: currentUser, created_at: '2024-02-18T16:30:00Z',
        reactions: [{ emoji: '✅', count: 2, users: ['sarah_jones', 'jane_smith'], hasReacted: false }],
        is_pinned: false, is_resolved: true,
      },
    ],
    participants: [mockUsers[3], currentUser],
    created_by: mockUsers[3], created_at: '2024-02-18T09:00:00Z', last_activity: '2024-02-18T16:30:00Z',
    is_subscribed: false,
  },
  {
    id: 3, title: 'Footer links layout', design_id: 2, design_name: 'Product Page',
    design_thumbnail: 'https://picsum.photos/seed/d2/200/150', position_x: 50, position_y: 90,
    status: 'open', priority: 'low',
    comments: [
      {
        id: 6, content: 'Should we use a 3-column or 4-column layout for the footer links?',
        author: currentUser, created_at: '2024-02-19T13:00:00Z',
        reactions: [], is_pinned: false, is_resolved: false,
      },
    ],
    participants: [currentUser],
    created_by: currentUser, created_at: '2024-02-19T13:00:00Z', last_activity: '2024-02-19T13:00:00Z',
    is_subscribed: true,
  },
];

const timeAgo = (date: string) => {
  const now = new Date();
  const then = new Date(date);
  const diff = (now.getTime() - then.getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high': return 'text-red-600 bg-red-50 border-red-200';
    case 'medium': return 'text-amber-600 bg-amber-50 border-amber-200';
    default: return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

// Comment Component
function CommentItem({ comment, onReply, onReact }: { comment: Comment; onReply: (id: number) => void; onReact: (id: number, emoji: string) => void }) {
  const [showReactions, setShowReactions] = useState(false);
  const reactions = ['👍', '❤️', '🎉', '😄', '🤔', '👀'];

  return (
    <div className={`flex gap-3 ${comment.is_pinned ? 'bg-amber-50 p-3 rounded-lg -mx-3' : ''}`}>
      <Avatar className="h-8 w-8">
        <AvatarImage src={comment.author.avatar} />
        <AvatarFallback>{comment.author.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
      </Avatar>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-gray-900 text-sm">{comment.author.full_name}</span>
          <span className="text-xs text-gray-400">{timeAgo(comment.created_at)}</span>
          {comment.is_pinned && <Pin className="h-3 w-3 text-amber-500" />}
          {comment.is_resolved && <CheckCircle className="h-3.5 w-3.5 text-green-500" />}
        </div>
        <p className="text-sm text-gray-700 whitespace-pre-wrap">{comment.content}</p>
        
        {comment.attachments && comment.attachments.length > 0 && (
          <div className="flex gap-2 mt-2">
            {comment.attachments.map(att => (
              <div key={att.id} className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 rounded text-xs text-gray-600">
                <ImageIcon className="h-3 w-3" />{att.name}
              </div>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2 mt-2">
          {comment.reactions.map((reaction, i) => (
            <button key={i} onClick={() => onReact(comment.id, reaction.emoji)}
              className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border ${
                reaction.hasReacted ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
              }`}>
              <span>{reaction.emoji}</span>
              <span>{reaction.count}</span>
            </button>
          ))}
          <div className="relative">
            <button onClick={() => setShowReactions(!showReactions)} className="p-1 rounded hover:bg-gray-100">
              <Smile className="h-4 w-4 text-gray-400" />
            </button>
            {showReactions && (
              <div className="absolute left-0 top-full mt-1 flex gap-1 p-2 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                {reactions.map(emoji => (
                  <button key={emoji} onClick={() => { onReact(comment.id, emoji); setShowReactions(false); }}
                    className="p-1 hover:bg-gray-100 rounded">{emoji}</button>
                ))}
              </div>
            )}
          </div>
          <button onClick={() => onReply(comment.id)} className="flex items-center gap-1 px-2 py-0.5 rounded text-xs text-gray-500 hover:bg-gray-100">
            <Reply className="h-3 w-3" />Reply
          </button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild><button className="p-1 rounded hover:bg-gray-100"><MoreVertical className="h-3 w-3 text-gray-400" /></button></DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              <DropdownMenuItem><Edit3 className="h-3.5 w-3.5 mr-2" />Edit</DropdownMenuItem>
              <DropdownMenuItem><Pin className="h-3.5 w-3.5 mr-2" />Pin Comment</DropdownMenuItem>
              <DropdownMenuItem><Flag className="h-3.5 w-3.5 mr-2" />Report</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-red-600"><Trash2 className="h-3.5 w-3.5 mr-2" />Delete</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  );
}

// Thread Card Component
function ThreadCard({ thread, isSelected, onClick }: { thread: CommentThread; isSelected: boolean; onClick: () => void }) {
  return (
    <div onClick={onClick}
      className={`p-4 border-b border-gray-100 cursor-pointer transition-colors ${
        isSelected ? 'bg-blue-50 border-l-2 border-l-blue-500' : 'hover:bg-gray-50'
      }`}>
      <div className="flex items-start gap-3">
        <div className="w-12 h-12 rounded bg-gray-200 overflow-hidden shrink-0">
          <Image src={thread.design_thumbnail} alt="" className="w-full h-full object-cover" width={320} height={180} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium text-gray-900 text-sm truncate">{thread.title}</span>
            {thread.status === 'resolved' && <CheckCircle className="h-4 w-4 text-green-500 shrink-0" />}
          </div>
          <p className="text-xs text-gray-500 mb-2">{thread.design_name}</p>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={`text-xs py-0 ${getPriorityColor(thread.priority)}`}>
              {thread.priority}
            </Badge>
            <span className="text-xs text-gray-400">{thread.comments.length} comments</span>
            <span className="text-xs text-gray-400">• {timeAgo(thread.last_activity)}</span>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-1 mt-3">
        {thread.participants.slice(0, 3).map((p, i) => (
          <Avatar key={p.id} className="h-6 w-6 border-2 border-white" style={{ marginLeft: i > 0 ? '-8px' : 0 }}>
            <AvatarImage src={p.avatar} />
            <AvatarFallback className="text-xs">{p.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
          </Avatar>
        ))}
        {thread.participants.length > 3 && (
          <span className="text-xs text-gray-400 ml-1">+{thread.participants.length - 3}</span>
        )}
      </div>
    </div>
  );
}

export default function CommentingPage() {
  const { toast } = useToast();
  const [threads, setThreads] = useState<CommentThread[]>(mockThreads);
  const [selectedThread, setSelectedThread] = useState<CommentThread | null>(mockThreads[0]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'open' | 'resolved'>('all');
  const [newComment, setNewComment] = useState('');
  const [_replyingTo, setReplyingTo] = useState<number | null>(null);

  const handleAddComment = () => {
    if (!newComment.trim() || !selectedThread) return;
    const comment: Comment = {
      id: Date.now(), content: newComment, author: currentUser,
      created_at: new Date().toISOString(), reactions: [], is_pinned: false, is_resolved: false,
    };
    setThreads(prev => prev.map(t => t.id === selectedThread.id ? { ...t, comments: [...t.comments, comment], last_activity: new Date().toISOString() } : t));
    setSelectedThread(prev => prev ? { ...prev, comments: [...prev.comments, comment] } : null);
    setNewComment('');
    toast({ title: 'Comment Added', description: 'Your comment has been posted' });
  };

  const handleReact = (commentId: number, emoji: string) => {
    // Update reaction logic here
    toast({ title: 'Reaction Added', description: `Added ${emoji} reaction` });
  };

  const handleResolve = (threadId: number) => {
    setThreads(prev => prev.map(t => t.id === threadId ? { ...t, status: t.status === 'resolved' ? 'open' : 'resolved' } : t));
    setSelectedThread(prev => prev?.id === threadId ? { ...prev, status: prev.status === 'resolved' ? 'open' : 'resolved' } : prev);
    toast({ title: 'Updated', description: 'Thread status updated' });
  };

  const filteredThreads = threads.filter(t => {
    if (searchTerm && !t.title.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    if (statusFilter !== 'all' && t.status !== statusFilter) return false;
    return true;
  });

  const stats = {
    total: threads.length,
    open: threads.filter(t => t.status === 'open').length,
    resolved: threads.filter(t => t.status === 'resolved').length,
    highPriority: threads.filter(t => t.priority === 'high' && t.status === 'open').length,
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-hidden flex">
          {/* Thread List */}
          <div className="w-96 border-r border-gray-200 bg-white flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-blue-600" />Comments
                </h2>
                <Button size="sm"><MessageCircle className="h-4 w-4 mr-1" />New Thread</Button>
              </div>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input placeholder="Search threads..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-9" />
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-2 p-4 border-b border-gray-200">
              <div className="text-center">
                <div className="text-lg font-bold text-gray-900">{stats.total}</div>
                <div className="text-xs text-gray-500">Total</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-blue-600">{stats.open}</div>
                <div className="text-xs text-gray-500">Open</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-green-600">{stats.resolved}</div>
                <div className="text-xs text-gray-500">Resolved</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-red-600">{stats.highPriority}</div>
                <div className="text-xs text-gray-500">Urgent</div>
              </div>
            </div>

            {/* Filters */}
            <div className="flex gap-1 p-2 border-b border-gray-200">
              {(['all', 'open', 'resolved'] as const).map(status => (
                <button key={status} onClick={() => setStatusFilter(status)}
                  className={`flex-1 py-1.5 px-3 rounded text-sm font-medium transition-colors ${
                    statusFilter === status ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
                  }`}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>

            {/* Thread List */}
            <ScrollArea className="flex-1">
              {filteredThreads.map(thread => (
                <ThreadCard key={thread.id} thread={thread} isSelected={selectedThread?.id === thread.id} onClick={() => setSelectedThread(thread)} />
              ))}
              {filteredThreads.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <MessageSquare className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p>No threads found</p>
                </div>
              )}
            </ScrollArea>
          </div>

          {/* Thread Detail */}
          <div className="flex-1 flex flex-col bg-white">
            {selectedThread ? (
              <>
                {/* Thread Header */}
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-semibold text-gray-900">{selectedThread.title}</h3>
                        <Badge variant="outline" className={getPriorityColor(selectedThread.priority)}>{selectedThread.priority}</Badge>
                        {selectedThread.status === 'resolved' && <Badge className="bg-green-100 text-green-700 border-0">Resolved</Badge>}
                      </div>
                      <p className="text-sm text-gray-500">
                        {selectedThread.design_name} • Started by {selectedThread.created_by.full_name} • {timeAgo(selectedThread.created_at)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleResolve(selectedThread.id)}>
                        {selectedThread.status === 'resolved' ? <><Circle className="h-4 w-4 mr-1" />Reopen</> : <><CheckCircle className="h-4 w-4 mr-1" />Resolve</>}
                      </Button>
                      <Button variant="outline" size="sm">
                        {selectedThread.is_subscribed ? <><BellOff className="h-4 w-4 mr-1" />Mute</> : <><Bell className="h-4 w-4 mr-1" />Subscribe</>}
                      </Button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild><Button variant="ghost" size="sm"><MoreVertical className="h-4 w-4" /></Button></DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>Edit Thread</DropdownMenuItem>
                          <DropdownMenuItem>Change Priority</DropdownMenuItem>
                          <DropdownMenuItem>Archive</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-red-600">Delete Thread</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>

                  {/* Participants */}
                  <div className="flex items-center gap-2 mt-3">
                    <Users className="h-4 w-4 text-gray-400" />
                    <div className="flex items-center gap-1">
                      {selectedThread.participants.map((p, i) => (
                        <Avatar key={p.id} className="h-6 w-6 border-2 border-white" style={{ marginLeft: i > 0 ? '-4px' : 0 }}>
                          <AvatarImage src={p.avatar} />
                          <AvatarFallback className="text-xs">{p.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                        </Avatar>
                      ))}
                    </div>
                    <span className="text-sm text-gray-500">{selectedThread.participants.length} participants</span>
                  </div>
                </div>

                {/* Comments */}
                <ScrollArea className="flex-1 p-4">
                  <div className="space-y-6">
                    {selectedThread.comments.map(comment => (
                      <CommentItem key={comment.id} comment={comment} onReply={(id) => setReplyingTo(id)} onReact={handleReact} />
                    ))}
                  </div>
                </ScrollArea>

                {/* Comment Input */}
                <div className="p-4 border-t border-gray-200">
                  <div className="flex gap-3">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={currentUser.avatar} />
                      <AvatarFallback>JD</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <Textarea placeholder="Add a comment..." value={newComment} onChange={(e) => setNewComment(e.target.value)}
                        className="min-h-[80px] resize-none mb-2" />
                      <div className="flex items-center justify-between">
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm"><AtSign className="h-4 w-4" /></Button>
                          <Button variant="ghost" size="sm"><Smile className="h-4 w-4" /></Button>
                          <Button variant="ghost" size="sm"><Paperclip className="h-4 w-4" /></Button>
                          <Button variant="ghost" size="sm"><ImageIcon className="h-4 w-4" /></Button>
                        </div>
                        <Button onClick={handleAddComment} disabled={!newComment.trim()}><Send className="h-4 w-4 mr-2" />Send</Button>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg font-medium">Select a thread</p>
                  <p className="text-sm">Choose a conversation to view comments</p>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
