/**
 * Comments Panel Component
 * Displays and manages comments on designs
 */
'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { MessageCircle, Check, Reply, MoreVertical } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Comment {
  id: number;
  user: {
    id: number;
    username: string;
    first_name?: string;
    last_name?: string;
  };
  content: string;
  anchor_position?: { x: number; y: number };
  anchor_element_id?: string;
  is_resolved: boolean;
  resolved_by?: any;
  resolved_at?: string;
  replies_count: number;
  replies?: Comment[];
  created_at: string;
  updated_at: string;
}

export function CommentsPanel({ 
  projectId, 
  onCommentClick 
}: { 
  projectId: number;
  onCommentClick?: (comment: Comment) => void;
}) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState<number | null>(null);
  const [replyContent, setReplyContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [showResolved, setShowResolved] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [projectId, showResolved]);

  const fetchComments = async () => {
    try {
      const url = showResolved 
        ? `/api/projects/comments/?project_id=${projectId}`
        : `/api/projects/comments/unresolved/?project_id=${projectId}`;
      
      const res = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (res.ok) {
        const data = await res.json();
        setComments(data);
      }
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('/api/projects/comments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          project: projectId,
          content: newComment,
          anchor_position: null,
          parent_comment: null
        })
      });

      if (res.ok) {
        setNewComment('');
        fetchComments();
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddReply = async (parentId: number) => {
    if (!replyContent.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('/api/projects/comments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          project: projectId,
          content: replyContent,
          parent_comment: parentId
        })
      });

      if (res.ok) {
        setReplyContent('');
        setReplyingTo(null);
        fetchComments();
      }
    } catch (error) {
      console.error('Failed to add reply:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (commentId: number, isResolved: boolean) => {
    try {
      const res = await fetch(`/api/projects/comments/${commentId}/resolve/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          is_resolved: !isResolved
        })
      });

      if (res.ok) {
        fetchComments();
      }
    } catch (error) {
      console.error('Failed to resolve comment:', error);
    }
  };

  const getUserInitials = (user: Comment['user']) => {
    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    return user.username.substring(0, 2).toUpperCase();
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <MessageCircle className="w-5 h-5" />
            Comments
          </h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowResolved(!showResolved)}
          >
            {showResolved ? 'Hide Resolved' : 'Show Resolved'}
          </Button>
        </div>

        {/* New Comment Input */}
        <div className="space-y-2">
          <Textarea
            placeholder="Add a comment..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            rows={3}
          />
          <Button
            onClick={handleAddComment}
            disabled={loading || !newComment.trim()}
            size="sm"
            className="w-full"
          >
            Post Comment
          </Button>
        </div>
      </div>

      {/* Comments List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {comments.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No comments yet. Be the first to comment!
          </div>
        ) : (
          comments.map((comment) => (
            <Card 
              key={comment.id}
              className={`cursor-pointer hover:shadow-md transition-shadow ${
                comment.is_resolved ? 'opacity-60' : ''
              }`}
              onClick={() => onCommentClick?.(comment)}
            >
              <CardContent className="p-4">
                {/* Comment Header */}
                <div className="flex items-start gap-3 mb-2">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback>
                      {getUserInitials(comment.user)}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm">
                        {comment.user.first_name || comment.user.username}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
                      </span>
                      {comment.is_resolved && (
                        <Badge variant="secondary" className="text-xs">
                          <Check className="w-3 h-3 mr-1" />
                          Resolved
                        </Badge>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {comment.content}
                    </p>

                    {/* Comment Actions */}
                    <div className="flex items-center gap-2 mt-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          setReplyingTo(comment.id);
                        }}
                      >
                        <Reply className="w-3 h-3 mr-1" />
                        Reply {comment.replies_count > 0 && `(${comment.replies_count})`}
                      </Button>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleResolve(comment.id, comment.is_resolved);
                        }}
                      >
                        <Check className="w-3 h-3 mr-1" />
                        {comment.is_resolved ? 'Unresolve' : 'Resolve'}
                      </Button>
                    </div>

                    {/* Reply Input */}
                    {replyingTo === comment.id && (
                      <div className="mt-3 space-y-2">
                        <Textarea
                          placeholder="Write a reply..."
                          value={replyContent}
                          onChange={(e) => setReplyContent(e.target.value)}
                          rows={2}
                        />
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleAddReply(comment.id)}
                            disabled={loading || !replyContent.trim()}
                          >
                            Reply
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setReplyingTo(null);
                              setReplyContent('');
                            }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    )}

                    {/* Replies */}
                    {comment.replies && comment.replies.length > 0 && (
                      <div className="mt-3 pl-4 border-l-2 space-y-3">
                        {comment.replies.map((reply) => (
                          <div key={reply.id} className="flex items-start gap-2">
                            <Avatar className="w-6 h-6">
                              <AvatarFallback className="text-xs">
                                {getUserInitials(reply.user)}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <div className="text-xs text-gray-600 mb-1">
                                <span className="font-medium">{reply.user.username}</span>
                                {' • '}
                                <span>{formatDistanceToNow(new Date(reply.created_at), { addSuffix: true })}</span>
                              </div>
                              <p className="text-sm">{reply.content}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
