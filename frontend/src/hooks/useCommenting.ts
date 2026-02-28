import { useState, useCallback, useEffect } from 'react';

const API_BASE = '/api/v1/comments';

interface Comment {
  id: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
  };
  content: string;
  comment_type: 'text' | 'voice' | 'video' | 'annotation';
  media_url?: string;
  created_at: string;
  mentions: string[];
  reactions: Array<{ type: string; count: number; users: string[] }>;
}

interface CommentThread {
  id: string;
  element_id?: string;
  position?: { x: number; y: number };
  status: 'open' | 'resolved' | 'archived';
  comments: Comment[];
  assignee?: { id: string; name: string };
  priority: 'low' | 'medium' | 'high';
  tags: string[];
}

interface ReviewSession {
  id: string;
  name: string;
  status: 'draft' | 'in_review' | 'approved' | 'changes_requested' | 'rejected';
  reviewers: Array<{
    user: { id: string; name: string };
    decision?: string;
    comment?: string;
  }>;
  deadline?: string;
}

export function useCommenting(projectId?: string) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [threads, setThreads] = useState<CommentThread[]>([]);
  const [activeThread, setActiveThread] = useState<CommentThread | null>(null);
  const [reviewSession, setReviewSession] = useState<ReviewSession | null>(null);

  const fetchThreads = useCallback(async (status?: 'open' | 'resolved' | 'all') => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const url = status && status !== 'all'
        ? `${API_BASE}/threads/?project=${projectId}&status=${status}`
        : `${API_BASE}/threads/?project=${projectId}`;
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setThreads(data.results || data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const createThread = useCallback(async (
    elementId?: string,
    position?: { x: number; y: number },
    initialComment?: string
  ): Promise<CommentThread> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/threads/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project: projectId,
          element_id: elementId,
          position,
          initial_comment: initialComment
        })
      });
      if (!response.ok) throw new Error('Failed to create thread');
      const thread = await response.json();
      setThreads(prev => [...prev, thread]);
      return thread;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const addComment = useCallback(async (
    threadId: string,
    content: string,
    type: 'text' | 'voice' | 'video' | 'annotation' = 'text',
    mediaFile?: File,
    mentions?: string[]
  ): Promise<Comment> => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('thread', threadId);
      formData.append('content', content);
      formData.append('comment_type', type);
      if (mediaFile) formData.append('media_file', mediaFile);
      if (mentions) formData.append('mentions', JSON.stringify(mentions));

      const response = await fetch(`${API_BASE}/comments/`, {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('Failed to add comment');
      const comment = await response.json();
      
      setThreads(prev => prev.map(t => 
        t.id === threadId 
          ? { ...t, comments: [...t.comments, comment] }
          : t
      ));
      
      return comment;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addReaction = useCallback(async (
    commentId: string,
    reactionType: 'like' | 'love' | 'laugh' | 'sad' | 'fire' | 'celebrate'
  ) => {
    try {
      const response = await fetch(`${API_BASE}/comments/${commentId}/react/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reaction_type: reactionType })
      });
      if (!response.ok) throw new Error('Failed to add reaction');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const resolveThread = useCallback(async (threadId: string): Promise<CommentThread> => {
    try {
      const response = await fetch(`${API_BASE}/threads/${threadId}/resolve/`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to resolve thread');
      const thread = await response.json();
      setThreads(prev => prev.map(t => t.id === threadId ? thread : t));
      return thread;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const reopenThread = useCallback(async (threadId: string): Promise<CommentThread> => {
    try {
      const response = await fetch(`${API_BASE}/threads/${threadId}/reopen/`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to reopen thread');
      const thread = await response.json();
      setThreads(prev => prev.map(t => t.id === threadId ? thread : t));
      return thread;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const assignThread = useCallback(async (threadId: string, userId: string): Promise<CommentThread> => {
    try {
      const response = await fetch(`${API_BASE}/threads/${threadId}/assign/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      if (!response.ok) throw new Error('Failed to assign thread');
      const thread = await response.json();
      setThreads(prev => prev.map(t => t.id === threadId ? thread : t));
      return thread;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const createReviewSession = useCallback(async (
    name: string,
    reviewerIds: string[],
    deadline?: string
  ): Promise<ReviewSession> => {
    try {
      const response = await fetch(`${API_BASE}/reviews/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project: projectId,
          name,
          reviewer_ids: reviewerIds,
          deadline
        })
      });
      if (!response.ok) throw new Error('Failed to create review session');
      const session = await response.json();
      setReviewSession(session);
      return session;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, [projectId]);

  const submitReviewDecision = useCallback(async (
    sessionId: string,
    decision: 'approved' | 'changes_requested' | 'rejected',
    comment?: string
  ) => {
    try {
      const response = await fetch(`${API_BASE}/reviews/${sessionId}/submit_decision/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, comment })
      });
      if (!response.ok) throw new Error('Failed to submit decision');
      const session = await response.json();
      setReviewSession(session);
      return session;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const getUnreadCount = useCallback(async (): Promise<number> => {
    try {
      const response = await fetch(`${API_BASE}/notifications/unread_count/`);
      if (!response.ok) throw new Error('Failed to get unread count');
      const data = await response.json();
      return data.count;
    } catch (_err) {
      return 0;
    }
  }, []);

  const markNotificationsRead = useCallback(async (notificationIds?: string[]) => {
    try {
      if (notificationIds) {
        await Promise.all(
          notificationIds.map(id => 
            fetch(`${API_BASE}/notifications/${id}/mark_read/`, { method: 'POST' })
          )
        );
      } else {
        await fetch(`${API_BASE}/notifications/mark_all_read/`, { method: 'POST' });
      }
    } catch (err) {
      console.error('Failed to mark notifications as read:', err);
    }
  }, []);

  useEffect(() => {
    if (projectId) {
      fetchThreads();
    }
  }, [projectId, fetchThreads]);

  return {
    isLoading,
    error,
    threads,
    activeThread,
    reviewSession,
    setActiveThread,
    createThread,
    addComment,
    addReaction,
    resolveThread,
    reopenThread,
    assignThread,
    createReviewSession,
    submitReviewDecision,
    getUnreadCount,
    markNotificationsRead,
    refresh: fetchThreads
  };
}

export default useCommenting;
