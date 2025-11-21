'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { teamsAPI, Comment } from '@/lib/teams-api';
import { MessageSquare, Send, MoreVertical, Check, Reply, AtSign } from 'lucide-react';

interface CommentThreadProps {
  projectId: number;
  teamId: number;
  canComment: boolean;
}

export default function CommentThread({ projectId, teamId, canComment }: CommentThreadProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const loadComments = useCallback(async () => {
    try {
      const data = await teamsAPI.getComments('project', projectId);
      setComments(data);
    } catch (error) {
      console.error('Failed to load comments:', error);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadComments();
  }, [loadComments]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const commentData: {
        team: number;
        project: number;
        content: string;
        parent?: number;
        mentions?: string[];
      } = {
        team: teamId,
        project: projectId,
        content: newComment,
      };

      if (replyingTo) {
        commentData.parent = replyingTo;
      }

      // Extract mentions (@username)
      const mentions = newComment.match(/@(\w+)/g);
      if (mentions) {
        commentData.mentions = mentions.map(m => m.substring(1));
      }

      const comment = await teamsAPI.createComment('project', projectId, commentData.content);
      setComments([comment, ...comments]);
      setNewComment('');
      setReplyingTo(null);
    } catch (error) {
      console.error('Failed to post comment:', error);
    }
  };

  const handleResolve = async (commentId: number) => {
    try {
      await teamsAPI.resolveComment(commentId, true);
      setComments(comments.map(c => 
        c.id === commentId ? { ...c, is_resolved: true } : c
      ));
    } catch (error) {
      console.error('Failed to resolve comment:', error);
    }
  };

  const handleDelete = async (commentId: number) => {
    if (!confirm('Are you sure you want to delete this comment?')) return;

    try {
      await teamsAPI.deleteComment(commentId);
      setComments(comments.filter(c => c.id !== commentId));
    } catch (error) {
      console.error('Failed to delete comment:', error);
    }
  };

  const getReplies = (parentId: number) => {
    return comments.filter(c => c.parent === parentId);
  };

  const topLevelComments = comments.filter(c => !c.parent);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return `${Math.round(diffInHours * 60)} minutes ago`;
    } else if (diffInHours < 24) {
      return `${Math.round(diffInHours)} hours ago`;
    } else if (diffInHours < 48) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  const CommentItem = ({ comment, isReply = false }: { comment: Comment; isReply?: boolean }) => (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`${isReply ? 'ml-12' : ''} mb-4`}
    >
      <div className={`bg-white rounded-lg p-4 shadow-sm ${
        comment.is_resolved ? 'opacity-60 bg-green-50' : ''
      }`}>
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-400 to-blue-400 flex items-center justify-center text-white text-sm font-semibold">
              {comment.user.username[0].toUpperCase()}
            </div>
            <div>
              <p className="font-medium text-sm">{comment.user.username}</p>
              <p className="text-xs text-gray-500">{formatDate(comment.created_at)}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {comment.is_resolved && (
              <span className="flex items-center gap-1 text-xs text-green-600 font-medium">
                <Check className="w-3 h-3" />
                Resolved
              </span>
            )}
            <button className="text-gray-400 hover:text-gray-600">
              <MoreVertical className="w-4 h-4" />
            </button>
          </div>
        </div>

        <p className="text-gray-700 mb-3 whitespace-pre-wrap">{comment.content}</p>

        {comment.mentions && comment.mentions.length > 0 && (
          <div className="flex items-center gap-2 mb-2 text-xs text-purple-600">
            <AtSign className="w-3 h-3" />
            <span>Mentioned: {comment.mentions.map(m => m.username).join(', ')}</span>
          </div>
        )}

        <div className="flex items-center gap-4 text-sm">
          {canComment && !comment.is_resolved && (
            <>
              <button
                onClick={() => setReplyingTo(comment.id)}
                className="flex items-center gap-1 text-purple-600 hover:text-purple-700 font-medium"
              >
                <Reply className="w-4 h-4" />
                Reply
              </button>
              <button
                onClick={() => handleResolve(comment.id)}
                className="flex items-center gap-1 text-green-600 hover:text-green-700 font-medium"
              >
                <Check className="w-4 h-4" />
                Resolve
              </button>
            </>
          )}
          <button
            onClick={() => handleDelete(comment.id)}
            className="text-red-600 hover:text-red-700 font-medium"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Replies */}
      {!isReply && getReplies(comment.id).map(reply => (
        <div key={reply.id} className="mt-2">
          <CommentItem comment={reply} isReply={true} />
        </div>
      ))}

      {/* Reply Form */}
      {replyingTo === comment.id && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="ml-12 mt-2"
        >
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-sm text-gray-600 mb-2">Replying to {comment.user.username}</p>
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Write a reply..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent text-sm"
                autoFocus
              />
              <button
                type="submit"
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => {
                  setReplyingTo(null);
                  setNewComment('');
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm"
              >
                Cancel
              </button>
            </form>
          </div>
        </motion.div>
      )}
    </motion.div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <MessageSquare className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold">Comments ({comments.length})</h3>
      </div>

      {/* New Comment Form */}
      {canComment && !replyingTo && (
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="bg-white rounded-lg shadow-sm p-4">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment... Use @username to mention someone"
              rows={3}
              className="w-full px-0 py-0 border-0 focus:ring-0 resize-none"
            />
            <div className="flex items-center justify-between mt-3 pt-3 border-t">
              <p className="text-xs text-gray-500">
                Tip: Use @username to mention team members
              </p>
              <button
                type="submit"
                disabled={!newComment.trim()}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
                Post Comment
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Comments List */}
      <div>
        {topLevelComments.length > 0 ? (
          <AnimatePresence>
            {topLevelComments.map(comment => (
              <CommentItem key={comment.id} comment={comment} />
            ))}
          </AnimatePresence>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No comments yet</p>
            {canComment && <p className="text-sm">Be the first to comment!</p>}
          </div>
        )}
      </div>
    </div>
  );
}
