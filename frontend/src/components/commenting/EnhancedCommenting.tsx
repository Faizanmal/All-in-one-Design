'use client';

import React, { useState, useCallback, useRef } from 'react';
import {
  MessageSquare,
  Video,
  Mic,
  AtSign,
  Send,
  Check,
  MoreVertical,
  Reply,
  Smile,
  Paperclip,
  X,
  User,
  Clock,
  Plus,
  Play,
  AlertCircle,
  ThumbsUp,
  Heart,
  Laugh,
  Frown,
  Eye
} from 'lucide-react';

interface CommentAuthor {
  id: string;
  name: string;
  avatar?: string;
}

interface Reaction {
  type: 'like' | 'love' | 'laugh' | 'sad' | 'fire' | 'celebrate';
  count: number;
  users: string[];
}

interface Comment {
  id: string;
  author: CommentAuthor;
  content: string;
  type: 'text' | 'voice' | 'video' | 'annotation';
  mediaUrl?: string;
  mediaDuration?: number;
  createdAt: Date;
  isResolved: boolean;
  mentions: string[];
  reactions: Reaction[];
  replies: Comment[];
}

interface CommentThread {
  id: string;
  elementId?: string;
  position?: { x: number; y: number };
  status: 'open' | 'resolved' | 'archived';
  comments: Comment[];
  assignee?: CommentAuthor;
  priority: 'low' | 'medium' | 'high';
  tags: string[];
}

interface ReviewSession {
  id: string;
  name: string;
  status: 'draft' | 'in_review' | 'approved' | 'changes_requested' | 'rejected';
  reviewers: { user: CommentAuthor; decision?: string; comment?: string }[];
  deadline?: Date;
}

interface EnhancedCommentingProps {
  onThreadCreate?: (thread: CommentThread) => void;
  onCommentAdd?: (threadId: string, comment: Comment) => void;
  onMention?: (userId: string) => void;
}

const REACTION_ICONS: Record<string, React.ElementType> = {
  like: ThumbsUp,
  love: Heart,
  laugh: Laugh,
  sad: Frown,
  fire: AlertCircle,
  celebrate: Smile
};

const INITIAL_THREADS: CommentThread[] = [
  {
    id: 'thread_1',
    status: 'open',
    priority: 'high',
    tags: ['design', 'urgent'],
    assignee: { id: 'user_1', name: 'Jane Doe' },
    comments: [
      {
        id: 'comment_1',
        author: { id: 'user_2', name: 'John Smith' },
        content: 'Can we adjust the spacing here? It feels a bit cramped.',
        type: 'text',
        createdAt: new Date(Date.now() - 3600000),
        isResolved: false,
        mentions: [],
        reactions: [{ type: 'like', count: 2, users: ['user_1', 'user_3'] }],
        replies: [
          {
            id: 'reply_1',
            author: { id: 'user_1', name: 'Jane Doe' },
            content: '@John I\'ll fix this in the next iteration.',
            type: 'text',
            createdAt: new Date(Date.now() - 1800000),
            isResolved: false,
            mentions: ['user_2'],
            reactions: [],
            replies: []
          }
        ]
      }
    ],
    position: { x: 100, y: 200 },
    elementId: 'element_1'
  }
];

export function EnhancedCommenting({ onThreadCreate, onCommentAdd, onMention: _onMention }: EnhancedCommentingProps) {
  const [threads, setThreads] = useState<CommentThread[]>(INITIAL_THREADS);
  const [selectedThread, setSelectedThread] = useState<CommentThread | null>(null);
  const [activeTab, setActiveTab] = useState<'threads' | 'review'>('threads');
  const [newComment, setNewComment] = useState('');
  const [commentType, setCommentType] = useState<'text' | 'voice' | 'video'>('text');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [showMentions, setShowMentions] = useState(false);
  const [filter, setFilter] = useState<'all' | 'open' | 'resolved'>('all');
  const [reviewSession, _setReviewSession] = useState<ReviewSession | null>(null);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const teamMembers: CommentAuthor[] = [
    { id: 'user_1', name: 'Jane Doe' },
    { id: 'user_2', name: 'John Smith' },
    { id: 'user_3', name: 'Alex Johnson' },
    { id: 'user_4', name: 'Sarah Williams' },
  ];

  const filteredThreads = threads.filter(thread => {
    if (filter === 'open') return thread.status === 'open';
    if (filter === 'resolved') return thread.status === 'resolved';
    return true;
  });

  const handleSendComment = useCallback(() => {
    if (!newComment.trim() || !selectedThread) return;

    const mentions = newComment.match(/@(\w+)/g)?.map(m => m.slice(1)) || [];
    
    const comment: Comment = {
      id: `comment_${Date.now()}`,
      author: { id: 'current_user', name: 'You' },
      content: newComment,
      type: commentType,
      createdAt: new Date(),
      isResolved: false,
      mentions,
      reactions: [],
      replies: []
    };

    setThreads(threads.map(t => 
      t.id === selectedThread.id 
        ? { ...t, comments: [...t.comments, comment] }
        : t
    ));
    setSelectedThread({
      ...selectedThread,
      comments: [...selectedThread.comments, comment]
    });
    setNewComment('');
    onCommentAdd?.(selectedThread.id, comment);
  }, [newComment, selectedThread, commentType, threads, onCommentAdd]);

  const handleStartRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia(
        commentType === 'video' ? { video: true, audio: true } : { audio: true }
      );
      
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      
      const chunks: Blob[] = [];
      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: commentType === 'video' ? 'video/webm' : 'audio/webm' });
        // In production, upload blob to server
        console.log('Recording complete:', blob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      recorder.start();
      setIsRecording(true);
      
      const interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      return () => clearInterval(interval);
    } catch (error) {
      console.error('Recording error:', error);
    }
  }, [commentType]);

  const handleStopRecording = useCallback(() => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setRecordingTime(0);
    }
  }, []);

  const handleCreateThread = useCallback(() => {
    const newThread: CommentThread = {
      id: `thread_${Date.now()}`,
      status: 'open',
      priority: 'medium',
      tags: [],
      comments: []
    };
    setThreads([...threads, newThread]);
    setSelectedThread(newThread);
    onThreadCreate?.(newThread);
  }, [threads, onThreadCreate]);

  const handleResolveThread = useCallback((threadId: string) => {
    setThreads(threads.map(t =>
      t.id === threadId ? { ...t, status: 'resolved' as const } : t
    ));
    if (selectedThread?.id === threadId) {
      setSelectedThread({ ...selectedThread, status: 'resolved' });
    }
  }, [threads, selectedThread]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex h-full bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Sidebar - Thread List */}
      <div className="w-80 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Comments</h2>
            <button
              onClick={handleCreateThread}
              className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
          
          {/* Tabs */}
          <div className="flex gap-1 mb-3">
            <button
              onClick={() => setActiveTab('threads')}
              className={`flex-1 py-2 text-sm font-medium rounded-lg ${
                activeTab === 'threads'
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Threads
            </button>
            <button
              onClick={() => setActiveTab('review')}
              className={`flex-1 py-2 text-sm font-medium rounded-lg ${
                activeTab === 'review'
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Review
            </button>
          </div>

          {/* Filter */}
          <div className="flex gap-1">
            {['all', 'open', 'resolved'].map(f => (
              <button
                key={f}
                onClick={() => setFilter(f as 'all' | 'open' | 'resolved')}
                className={`px-3 py-1 text-xs rounded-full capitalize ${
                  filter === f
                    ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Thread List */}
        <div className="flex-1 overflow-auto">
          {activeTab === 'threads' && (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredThreads.map(thread => (
                <button
                  key={thread.id}
                  onClick={() => setSelectedThread(thread)}
                  className={`w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 ${
                    selectedThread?.id === thread.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-2 h-2 mt-2 rounded-full ${
                      thread.status === 'open' ? 'bg-blue-500' : 'bg-green-500'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 dark:text-white text-sm">
                          {thread.comments[0]?.author.name || 'New Thread'}
                        </span>
                        {thread.priority === 'high' && (
                          <span className="px-1.5 py-0.5 text-xs bg-red-100 text-red-700 rounded">
                            High
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 truncate mt-1">
                        {thread.comments[0]?.content || 'No messages yet'}
                      </p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          {thread.comments.length}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          2h ago
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {activeTab === 'review' && (
            <div className="p-4">
              {reviewSession ? (
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                    <h4 className="font-medium text-gray-900 dark:text-white">{reviewSession.name}</h4>
                    <p className="text-sm text-gray-500 capitalize mt-1">{reviewSession.status.replace('_', ' ')}</p>
                  </div>
                  <div className="space-y-2">
                    {reviewSession.reviewers.map((reviewer, i) => (
                      <div key={i} className="flex items-center gap-3 p-2">
                        <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
                          <User className="w-4 h-4 text-gray-500" />
                        </div>
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {reviewer.user.name}
                          </div>
                          {reviewer.decision && (
                            <div className="text-xs text-gray-500">{reviewer.decision}</div>
                          )}
                        </div>
                        {reviewer.decision === 'approved' && <Check className="w-5 h-5 text-green-500" />}
                        {reviewer.decision === 'changes_requested' && <AlertCircle className="w-5 h-5 text-yellow-500" />}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Eye className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p className="font-medium">No active review</p>
                  <button className="mt-3 text-sm text-blue-600 hover:underline">
                    Start a review session
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Content - Thread Detail */}
      <div className="flex-1 flex flex-col">
        {selectedThread ? (
          <>
            {/* Thread Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${
                  selectedThread.status === 'open' ? 'bg-blue-500' : 'bg-green-500'
                }`} />
                <span className="font-medium text-gray-900 dark:text-white">
                  Thread #{selectedThread.id.split('_')[1]}
                </span>
                {selectedThread.tags.map(tag => (
                  <span key={tag} className="px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 rounded-full">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="flex items-center gap-2">
                {selectedThread.status === 'open' && (
                  <button
                    onClick={() => handleResolveThread(selectedThread.id)}
                    className="flex items-center gap-2 px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700"
                  >
                    <Check className="w-4 h-4" />
                    Resolve
                  </button>
                )}
                <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                  <MoreVertical className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>

            {/* Comments */}
            <div className="flex-1 overflow-auto p-4 space-y-4">
              {selectedThread.comments.map(comment => (
                <div key={comment.id} className="space-y-3">
                  <div className="flex gap-3">
                    <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center shrink-0">
                      <User className="w-4 h-4 text-gray-500" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-gray-900 dark:text-white text-sm">
                          {comment.author.name}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(comment.createdAt).toLocaleTimeString()}
                        </span>
                      </div>
                      
                      {comment.type === 'text' && (
                        <p className="text-sm text-gray-700 dark:text-gray-300">{comment.content}</p>
                      )}
                      
                      {comment.type === 'voice' && (
                        <div className="flex items-center gap-2 p-2 bg-gray-100 dark:bg-gray-700 rounded-lg w-48">
                          <button className="p-2 bg-blue-500 text-white rounded-full">
                            <Play className="w-3 h-3" />
                          </button>
                          <div className="flex-1 h-8 flex items-center gap-0.5">
                            {Array.from({ length: 20 }).map((_, i) => (
                              <div
                                key={i}
                                className="flex-1 bg-blue-300 rounded-full"
                                style={{ height: `${Math.random() * 100}%` }}
                              />
                            ))}
                          </div>
                          <span className="text-xs text-gray-500">0:12</span>
                        </div>
                      )}
                      
                      {comment.type === 'video' && (
                        <div className="relative w-64 h-36 bg-gray-900 rounded-lg overflow-hidden">
                          <div className="absolute inset-0 flex items-center justify-center">
                            <button className="p-3 bg-white/20 rounded-full">
                              <Play className="w-6 h-6 text-white" />
                            </button>
                          </div>
                          <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/60">
                            <span className="text-xs text-white">0:45</span>
                          </div>
                        </div>
                      )}

                      {/* Reactions */}
                      {comment.reactions.length > 0 && (
                        <div className="flex gap-1 mt-2">
                          {comment.reactions.map((reaction, i) => {
                            const Icon = REACTION_ICONS[reaction.type];
                            return (
                              <button
                                key={i}
                                className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-xs hover:bg-gray-200 dark:hover:bg-gray-600"
                              >
                                <Icon className="w-3 h-3" />
                                {reaction.count}
                              </button>
                            );
                          })}
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center gap-3 mt-2">
                        <button
                          onClick={() => setShowEmojiPicker(true)}
                          className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                        >
                          <Smile className="w-3 h-3" />
                          React
                        </button>
                        <button className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1">
                          <Reply className="w-3 h-3" />
                          Reply
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Replies */}
                  {comment.replies.length > 0 && (
                    <div className="ml-11 space-y-3 border-l-2 border-gray-200 dark:border-gray-700 pl-4">
                      {comment.replies.map(reply => (
                        <div key={reply.id} className="flex gap-3">
                          <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center shrink-0">
                            <User className="w-3 h-3 text-gray-500" />
                          </div>
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-medium text-gray-900 dark:text-white text-xs">
                                {reply.author.name}
                              </span>
                              <span className="text-xs text-gray-500">
                                {new Date(reply.createdAt).toLocaleTimeString()}
                              </span>
                            </div>
                            <p className="text-sm text-gray-700 dark:text-gray-300">{reply.content}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Comment Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              {/* Comment Type Selector */}
              <div className="flex items-center gap-2 mb-3">
                {[
                  { type: 'text', icon: MessageSquare, label: 'Text' },
                  { type: 'voice', icon: Mic, label: 'Voice' },
                  { type: 'video', icon: Video, label: 'Video' },
                ].map(ct => (
                  <button
                    key={ct.type}
                    onClick={() => setCommentType(ct.type as 'text' | 'video' | 'voice')}
                    className={`flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg ${
                      commentType === ct.type
                        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600'
                        : 'text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <ct.icon className="w-3 h-3" />
                    {ct.label}
                  </button>
                ))}
              </div>

              {commentType === 'text' ? (
                <div className="flex items-end gap-2">
                  <div className="flex-1 relative">
                    <textarea
                      ref={textareaRef}
                      value={newComment}
                      onChange={(e) => {
                        setNewComment(e.target.value);
                        if (e.target.value.endsWith('@')) {
                          setShowMentions(true);
                        }
                      }}
                      placeholder="Add a comment... Use @ to mention"
                      rows={2}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 resize-none"
                    />
                    
                    {/* Mentions Dropdown */}
                    {showMentions && (
                      <div className="absolute bottom-full left-0 mb-1 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1">
                        {teamMembers.map(member => (
                          <button
                            key={member.id}
                            onClick={() => {
                              setNewComment(newComment.slice(0, -1) + `@${member.name} `);
                              setShowMentions(false);
                            }}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                          >
                            <div className="w-6 h-6 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center">
                              <User className="w-3 h-3" />
                            </div>
                            {member.name}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                      <AtSign className="w-5 h-5 text-gray-500" />
                    </button>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                      <Paperclip className="w-5 h-5 text-gray-500" />
                    </button>
                    <button
                      onClick={handleSendComment}
                      disabled={!newComment.trim()}
                      className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center p-6 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  {isRecording ? (
                    <div className="flex items-center gap-4">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                      <span className="font-mono text-lg text-gray-900 dark:text-white">
                        {formatTime(recordingTime)}
                      </span>
                      <button
                        onClick={handleStopRecording}
                        className="p-3 bg-red-600 text-white rounded-full hover:bg-red-700"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={handleStartRecording}
                      className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700"
                    >
                      {commentType === 'voice' ? <Mic className="w-5 h-5" /> : <Video className="w-5 h-5" />}
                      Start Recording
                    </button>
                  )}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="font-medium">Select a thread or create a new one</p>
              <p className="text-sm mt-1">Click on the canvas to add a comment</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default EnhancedCommenting;
