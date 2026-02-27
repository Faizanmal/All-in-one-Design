'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error.message || `API Error: ${response.statusText}`);
  }

  return response.json();
}

// ============================================
// DESIGN SYSTEMS - Design System Builder
// ============================================

export interface DesignSystem {
  id: string;
  name: string;
  description: string;
  organization: string;
  version: string;
  is_public: boolean;
  share_link?: string;
  created_at: string;
  updated_at: string;
}

export interface DesignToken {
  id: string;
  design_system: string;
  name: string;
  category: 'color' | 'typography' | 'spacing' | 'shadow' | 'border' | 'other';
  value: string | number | Record<string, unknown>;
  token_type: string;
  description?: string;
  aliases: string[];
  created_at: string;
  updated_at: string;
}

export interface ComponentDefinition {
  id: string;
  design_system: string;
  name: string;
  category: string;
  description: string;
  props: Array<{
    name: string;
    type: string;
    default?: unknown;
    required: boolean;
  }>;
  variants: Array<{
    name: string;
    props: Record<string, unknown>;
  }>;
  states: string[];
  figma_node_id?: string;
  code_snippet?: string;
  created_at: string;
  updated_at: string;
}

export interface StyleGuide {
  id: string;
  design_system: string;
  section: string;
  content: string;
  order: number;
  examples: Array<{
    title: string;
    code: string;
    preview?: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface DocumentationPage {
  id: string;
  design_system: string;
  title: string;
  slug: string;
  content: string;
  parent?: string;
  order: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenCategory {
  name: string;
  count: number;
}

// Hooks for Design Systems
export function useDesignSystems(organizationId?: string) {
  return useQuery({
    queryKey: ['design-systems', organizationId],
    queryFn: () =>
      apiRequest<DesignSystem[]>(
        `/design-systems/systems/${organizationId ? `?organization=${organizationId}` : ''}`
      ),
  });
}

export function useDesignSystem(systemId: string) {
  return useQuery({
    queryKey: ['design-system', systemId],
    queryFn: () => apiRequest<DesignSystem>(`/design-systems/systems/${systemId}/`),
    enabled: !!systemId,
  });
}

export function useCreateDesignSystem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<DesignSystem>) =>
      apiRequest<DesignSystem>('/design-systems/systems/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['design-systems'] });
    },
  });
}

export function useUpdateDesignSystem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      data,
    }: {
      systemId: string;
      data: Partial<DesignSystem>;
    }) =>
      apiRequest<DesignSystem>(`/design-systems/systems/${systemId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['design-system', variables.systemId] });
      queryClient.invalidateQueries({ queryKey: ['design-systems'] });
    },
  });
}

export function useDeleteDesignSystem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (systemId: string) =>
      apiRequest(`/design-systems/systems/${systemId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['design-systems'] });
    },
  });
}

export function usePublishDesignSystem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (systemId: string) =>
      apiRequest(`/design-systems/systems/${systemId}/publish/`, {
        method: 'POST',
      }),
    onSuccess: (_, systemId) => {
      queryClient.invalidateQueries({ queryKey: ['design-system', systemId] });
    },
  });
}

// Hooks for Design Tokens
export function useDesignTokens(systemId: string, category?: string) {
  return useQuery({
    queryKey: ['design-tokens', systemId, category],
    queryFn: () =>
      apiRequest<DesignToken[]>(
        `/design-systems/systems/${systemId}/tokens/${category ? `?category=${category}` : ''}`
      ),
    enabled: !!systemId,
  });
}

export function useDesignToken(systemId: string, tokenId: string) {
  return useQuery({
    queryKey: ['design-token', systemId, tokenId],
    queryFn: () =>
      apiRequest<DesignToken>(`/design-systems/systems/${systemId}/tokens/${tokenId}/`),
    enabled: !!systemId && !!tokenId,
  });
}

export function useCreateDesignToken() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      data,
    }: {
      systemId: string;
      data: Partial<DesignToken>;
    }) =>
      apiRequest<DesignToken>(`/design-systems/systems/${systemId}/tokens/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['design-tokens', variables.systemId] });
    },
  });
}

export function useUpdateDesignToken() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      tokenId,
      data,
    }: {
      systemId: string;
      tokenId: string;
      data: Partial<DesignToken>;
    }) =>
      apiRequest<DesignToken>(
        `/design-systems/systems/${systemId}/tokens/${tokenId}/`,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['design-token', variables.systemId, variables.tokenId],
      });
      queryClient.invalidateQueries({ queryKey: ['design-tokens', variables.systemId] });
    },
  });
}

export function useDeleteDesignToken() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      tokenId,
    }: {
      systemId: string;
      tokenId: string;
    }) =>
      apiRequest(`/design-systems/systems/${systemId}/tokens/${tokenId}/`, {
        method: 'DELETE',
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['design-tokens', variables.systemId] });
    },
  });
}

export function useExportTokens() {
  return useMutation({
    mutationFn: async ({
      systemId,
      format,
    }: {
      systemId: string;
      format: 'json' | 'css' | 'scss' | 'js';
    }) => {
      const response = await fetch(
        `${API_BASE}/design-systems/systems/${systemId}/tokens/export/?format=${format}`,
        {
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to export tokens');
      }

      return response.blob();
    },
  });
}

// Hooks for Component Definitions
export function useComponentDefinitions(systemId: string, category?: string) {
  return useQuery({
    queryKey: ['component-definitions', systemId, category],
    queryFn: () =>
      apiRequest<ComponentDefinition[]>(
        `/design-systems/systems/${systemId}/components/${category ? `?category=${category}` : ''}`
      ),
    enabled: !!systemId,
  });
}

export function useComponentDefinition(systemId: string, componentId: string) {
  return useQuery({
    queryKey: ['component-definition', systemId, componentId],
    queryFn: () =>
      apiRequest<ComponentDefinition>(
        `/design-systems/systems/${systemId}/components/${componentId}/`
      ),
    enabled: !!systemId && !!componentId,
  });
}

export function useCreateComponentDefinition() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      data,
    }: {
      systemId: string;
      data: Partial<ComponentDefinition>;
    }) =>
      apiRequest<ComponentDefinition>(
        `/design-systems/systems/${systemId}/components/`,
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['component-definitions', variables.systemId],
      });
    },
  });
}

export function useUpdateComponentDefinition() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      componentId,
      data,
    }: {
      systemId: string;
      componentId: string;
      data: Partial<ComponentDefinition>;
    }) =>
      apiRequest<ComponentDefinition>(
        `/design-systems/systems/${systemId}/components/${componentId}/`,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['component-definition', variables.systemId, variables.componentId],
      });
      queryClient.invalidateQueries({
        queryKey: ['component-definitions', variables.systemId],
      });
    },
  });
}

export function useDeleteComponentDefinition() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      componentId,
    }: {
      systemId: string;
      componentId: string;
    }) =>
      apiRequest(`/design-systems/systems/${systemId}/components/${componentId}/`, {
        method: 'DELETE',
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['component-definitions', variables.systemId],
      });
    },
  });
}

// Hooks for Style Guide
export function useStyleGuides(systemId: string) {
  return useQuery({
    queryKey: ['style-guides', systemId],
    queryFn: () =>
      apiRequest<StyleGuide[]>(`/design-systems/systems/${systemId}/style-guide/`),
    enabled: !!systemId,
  });
}

export function useCreateStyleGuide() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      data,
    }: {
      systemId: string;
      data: Partial<StyleGuide>;
    }) =>
      apiRequest<StyleGuide>(`/design-systems/systems/${systemId}/style-guide/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['style-guides', variables.systemId] });
    },
  });
}

export function useUpdateStyleGuide() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      guideId,
      data,
    }: {
      systemId: string;
      guideId: string;
      data: Partial<StyleGuide>;
    }) =>
      apiRequest<StyleGuide>(
        `/design-systems/systems/${systemId}/style-guide/${guideId}/`,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['style-guides', variables.systemId] });
    },
  });
}

// Hooks for Documentation Pages
export function useDocumentationPages(systemId: string) {
  return useQuery({
    queryKey: ['documentation-pages', systemId],
    queryFn: () =>
      apiRequest<DocumentationPage[]>(`/design-systems/systems/${systemId}/docs/`),
    enabled: !!systemId,
  });
}

export function useDocumentationPage(systemId: string, pageId: string) {
  return useQuery({
    queryKey: ['documentation-page', systemId, pageId],
    queryFn: () =>
      apiRequest<DocumentationPage>(`/design-systems/systems/${systemId}/docs/${pageId}/`),
    enabled: !!systemId && !!pageId,
  });
}

export function useCreateDocumentationPage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      data,
    }: {
      systemId: string;
      data: Partial<DocumentationPage>;
    }) =>
      apiRequest<DocumentationPage>(`/design-systems/systems/${systemId}/docs/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['documentation-pages', variables.systemId],
      });
    },
  });
}

export function useUpdateDocumentationPage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      pageId,
      data,
    }: {
      systemId: string;
      pageId: string;
      data: Partial<DocumentationPage>;
    }) =>
      apiRequest<DocumentationPage>(
        `/design-systems/systems/${systemId}/docs/${pageId}/`,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['documentation-page', variables.systemId, variables.pageId],
      });
      queryClient.invalidateQueries({
        queryKey: ['documentation-pages', variables.systemId],
      });
    },
  });
}

export function useDeleteDocumentationPage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      systemId,
      pageId,
    }: {
      systemId: string;
      pageId: string;
    }) =>
      apiRequest(`/design-systems/systems/${systemId}/docs/${pageId}/`, {
        method: 'DELETE',
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['documentation-pages', variables.systemId],
      });
    },
  });
}

// Utility Hooks
export function useTokenCategories() {
  return useQuery({
    queryKey: ['token-categories'],
    queryFn: () => apiRequest<TokenCategory[]>('/design-systems/token-categories/'),
  });
}

export function usePublicDesignSystem(shareLink: string) {
  return useQuery({
    queryKey: ['public-design-system', shareLink],
    queryFn: () =>
      apiRequest<DesignSystem>(`/design-systems/public/${shareLink}/`),
    enabled: !!shareLink,
  });
}
