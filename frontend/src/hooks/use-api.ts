'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { meetingsAPI, actionItemsAPI, notesAPI, tagsAPI } from '@/lib/api';
import type { Meeting, ActionItem, Tag } from '@/lib/api';

// Meetings
export function useMeetings(params?: {
  search?: string;
  status?: string;
  ordering?: string;
  page?: number;
}) {
  return useQuery({
    queryKey: ['meetings', params],
    queryFn: () => meetingsAPI.list(params),
  });
}

export function useMeeting(id: string) {
  return useQuery({
    queryKey: ['meetings', id],
    queryFn: () => meetingsAPI.get(id),
    enabled: !!id,
  });
}

export function useMeetingStats() {
  return useQuery({
    queryKey: ['meetings', 'stats'],
    queryFn: () => meetingsAPI.getStats(),
  });
}

export function useAnalytics(days: number = 30) {
  return useQuery({
    queryKey: ['meetings', 'analytics', days],
    queryFn: () => meetingsAPI.getAnalytics(days),
  });
}

export function useUploadMeeting() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (formData: FormData) => meetingsAPI.create(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] });
      queryClient.invalidateQueries({ queryKey: ['meetings', 'stats'] });
    },
  });
}

export function useUpdateMeeting() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Meeting> }) =>
      meetingsAPI.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] });
      queryClient.invalidateQueries({ queryKey: ['meetings', variables.id] });
    },
  });
}

export function useDeleteMeeting() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => meetingsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] });
      queryClient.invalidateQueries({ queryKey: ['meetings', 'stats'] });
    },
  });
}

export function useShareMeeting() {
  return useMutation({
    mutationFn: (id: string) => meetingsAPI.share(id),
  });
}

// Action Items
export function useActionItems(params?: {
  search?: string;
  status?: string;
  priority?: string;
  meeting?: string;
  ordering?: string;
  page?: number;
}) {
  return useQuery({
    queryKey: ['action-items', params],
    queryFn: () => actionItemsAPI.list(params),
  });
}

export function useActionItem(id: string) {
  return useQuery({
    queryKey: ['action-items', id],
    queryFn: () => actionItemsAPI.get(id),
    enabled: !!id,
  });
}

export function useCreateActionItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Partial<ActionItem>) => actionItemsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['action-items'] });
      queryClient.invalidateQueries({ queryKey: ['meetings', 'stats'] });
    },
  });
}

export function useUpdateActionItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ActionItem> }) =>
      actionItemsAPI.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['action-items'] });
      queryClient.invalidateQueries({ queryKey: ['action-items', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['meetings', 'stats'] });
    },
  });
}

export function useCompleteActionItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => actionItemsAPI.complete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['action-items'] });
      queryClient.invalidateQueries({ queryKey: ['meetings', 'stats'] });
    },
  });
}

export function useDeleteActionItem() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => actionItemsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['action-items'] });
      queryClient.invalidateQueries({ queryKey: ['meetings', 'stats'] });
    },
  });
}

// Meeting Notes
export function useMeetingNotes(meetingId?: string) {
  return useQuery({
    queryKey: ['notes', meetingId],
    queryFn: () => notesAPI.list(meetingId),
    enabled: !!meetingId,
  });
}

export function useCreateNote() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { meeting: string; content: string; timestamp?: number }) =>
      notesAPI.create(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['notes', variables.meeting] });
    },
  });
}

export function useDeleteNote() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => notesAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
    },
  });
}

// Tags
export function useTags() {
  return useQuery({
    queryKey: ['tags'],
    queryFn: () => tagsAPI.list(),
  });
}

export function useCreateTag() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { name: string; color?: string }) => tagsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });
}

export function useUpdateTag() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Tag> }) =>
      tagsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });
}

export function useDeleteTag() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => tagsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      queryClient.invalidateQueries({ queryKey: ['meetings'] });
    },
  });
}

// Favorites
export function useToggleFavorite() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => meetingsAPI.toggleFavorite(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] });
      queryClient.invalidateQueries({ queryKey: ['meetings', id] });
    },
  });
}

export function useFavorites() {
  return useQuery({
    queryKey: ['meetings', 'favorites'],
    queryFn: () => meetingsAPI.getFavorites(),
  });
}
