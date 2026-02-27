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
// WHITELABEL - White-Label & Agency Features
// ============================================

export interface Agency {
  id: string;
  name: string;
  slug: string;
  owner: string;
  logo?: string;
  primary_color: string;
  secondary_color: string;
  custom_domain?: string;
  custom_css?: string;
  email_from_name: string;
  email_from_address: string;
  support_email: string;
  is_active: boolean;
  subscription_plan: string;
  created_at: string;
  updated_at: string;
}

export interface Client {
  id: string;
  agency: string;
  name: string;
  email: string;
  company?: string;
  phone?: string;
  address?: string;
  status: 'active' | 'inactive' | 'pending';
  projects_count: number;
  total_spent: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ClientPortal {
  id: string;
  agency: string;
  client: string;
  access_token: string;
  portal_url: string;
  custom_branding: {
    logo?: string;
    colors?: Record<string, string>;
    welcome_message?: string;
  };
  allowed_features: string[];
  is_active: boolean;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ClientFeedback {
  id: string;
  portal: string;
  project: string;
  feedback_type: 'comment' | 'approval' | 'revision' | 'general';
  content: string;
  attachments: string[];
  status: 'pending' | 'reviewed' | 'resolved';
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
}

export interface APIKey {
  id: string;
  agency: string;
  name: string;
  key_prefix: string;
  permissions: string[];
  is_active: boolean;
  expires_at?: string;
  last_used_at?: string;
  created_at: string;
}

export interface AgencyBilling {
  id: string;
  agency: string;
  billing_cycle: 'monthly' | 'quarterly' | 'yearly';
  next_billing_date: string;
  payment_method: string;
  total_clients: number;
  total_projects: number;
  monthly_revenue: number;
  created_at: string;
}

export interface AgencyInvoice {
  id: string;
  agency: string;
  invoice_number: string;
  client?: string;
  amount: number;
  tax: number;
  total: number;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  due_date: string;
  paid_date?: string;
  line_items: Array<{
    description: string;
    quantity: number;
    unit_price: number;
    total: number;
  }>;
  notes?: string;
  created_at: string;
}

export interface BrandLibrary {
  id: string;
  agency: string;
  client?: string;
  name: string;
  logo: string;
  brand_colors: string[];
  typography: {
    headings: string;
    body: string;
    accent?: string;
  };
  guidelines: string;
  assets: string[];
  is_shared: boolean;
  created_at: string;
  updated_at: string;
}

// Hooks for Agencies
export function useAgencies() {
  return useQuery({
    queryKey: ['agencies'],
    queryFn: () => apiRequest<Agency[]>('/whitelabel/agencies/'),
  });
}

export function useAgency(agencyId: string) {
  return useQuery({
    queryKey: ['agency', agencyId],
    queryFn: () => apiRequest<Agency>(`/whitelabel/agencies/${agencyId}/`),
    enabled: !!agencyId,
  });
}

export function useCreateAgency() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Agency>) =>
      apiRequest<Agency>('/whitelabel/agencies/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agencies'] });
    },
  });
}

export function useUpdateAgency() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      data,
    }: {
      agencyId: string;
      data: Partial<Agency>;
    }) =>
      apiRequest<Agency>(`/whitelabel/agencies/${agencyId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['agency', variables.agencyId] });
      queryClient.invalidateQueries({ queryKey: ['agencies'] });
    },
  });
}

export function useUploadAgencyLogo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      formData,
    }: {
      agencyId: string;
      formData: FormData;
    }) => {
      const response = await fetch(
        `${API_BASE}/whitelabel/agencies/${agencyId}/upload_logo/`,
        {
          method: 'POST',
          body: formData,
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to upload logo');
      }

      return response.json();
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['agency', variables.agencyId] });
    },
  });
}

// Hooks for Clients
export function useClients(agencyId?: string) {
  return useQuery({
    queryKey: ['clients', agencyId],
    queryFn: () =>
      apiRequest<Client[]>(
        `/whitelabel/agencies/${agencyId}/clients/${agencyId ? '' : '?all=true'}`
      ),
    enabled: !!agencyId,
  });
}

export function useClient(agencyId: string, clientId: string) {
  return useQuery({
    queryKey: ['client', agencyId, clientId],
    queryFn: () =>
      apiRequest<Client>(`/whitelabel/agencies/${agencyId}/clients/${clientId}/`),
    enabled: !!agencyId && !!clientId,
  });
}

export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      data,
    }: {
      agencyId: string;
      data: Partial<Client>;
    }) =>
      apiRequest<Client>(`/whitelabel/agencies/${agencyId}/clients/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['clients', variables.agencyId] });
    },
  });
}

export function useUpdateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      clientId,
      data,
    }: {
      agencyId: string;
      clientId: string;
      data: Partial<Client>;
    }) =>
      apiRequest<Client>(`/whitelabel/agencies/${agencyId}/clients/${clientId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['client', variables.agencyId, variables.clientId],
      });
      queryClient.invalidateQueries({ queryKey: ['clients', variables.agencyId] });
    },
  });
}

export function useDeleteClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      clientId,
    }: {
      agencyId: string;
      clientId: string;
    }) =>
      apiRequest(`/whitelabel/agencies/${agencyId}/clients/${clientId}/`, {
        method: 'DELETE',
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['clients', variables.agencyId] });
    },
  });
}

// Hooks for Client Portals
export function useClientPortals(agencyId?: string) {
  return useQuery({
    queryKey: ['client-portals', agencyId],
    queryFn: () =>
      apiRequest<ClientPortal[]>(
        `/whitelabel/agencies/${agencyId}/portals/${agencyId ? '' : '?all=true'}`
      ),
    enabled: !!agencyId,
  });
}

export function useClientPortal(agencyId: string, portalId: string) {
  return useQuery({
    queryKey: ['client-portal', agencyId, portalId],
    queryFn: () =>
      apiRequest<ClientPortal>(`/whitelabel/agencies/${agencyId}/portals/${portalId}/`),
    enabled: !!agencyId && !!portalId,
  });
}

export function useCreateClientPortal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      data,
    }: {
      agencyId: string;
      data: Partial<ClientPortal>;
    }) =>
      apiRequest<ClientPortal>(`/whitelabel/agencies/${agencyId}/portals/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['client-portals', variables.agencyId] });
    },
  });
}

export function useUpdateClientPortal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      portalId,
      data,
    }: {
      agencyId: string;
      portalId: string;
      data: Partial<ClientPortal>;
    }) =>
      apiRequest<ClientPortal>(
        `/whitelabel/agencies/${agencyId}/portals/${portalId}/`,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['client-portal', variables.agencyId, variables.portalId],
      });
      queryClient.invalidateQueries({ queryKey: ['client-portals', variables.agencyId] });
    },
  });
}

// Hooks for Client Feedback
export function useClientFeedback(portalId?: string) {
  return useQuery({
    queryKey: ['client-feedback', portalId],
    queryFn: () =>
      apiRequest<ClientFeedback[]>(
        `/whitelabel/feedback/${portalId ? `?portal=${portalId}` : ''}`
      ),
    enabled: !!portalId,
  });
}

export function useSubmitClientFeedback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      access_token: string;
      feedback: Partial<ClientFeedback>;
    }) =>
      apiRequest<ClientFeedback>('/whitelabel/feedback/submit/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client-feedback'] });
    },
  });
}

// Hooks for API Keys
export function useAPIKeys(agencyId?: string) {
  return useQuery({
    queryKey: ['api-keys', agencyId],
    queryFn: () =>
      apiRequest<APIKey[]>(
        `/whitelabel/agencies/${agencyId}/api-keys/${agencyId ? '' : '?all=true'}`
      ),
    enabled: !!agencyId,
  });
}

export function useCreateAPIKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      data,
    }: {
      agencyId: string;
      data: Partial<APIKey>;
    }) =>
      apiRequest<APIKey>(`/whitelabel/agencies/${agencyId}/api-keys/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys', variables.agencyId] });
    },
  });
}

export function useDeleteAPIKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      keyId,
    }: {
      agencyId: string;
      keyId: string;
    }) =>
      apiRequest(`/whitelabel/agencies/${agencyId}/api-keys/${keyId}/`, {
        method: 'DELETE',
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys', variables.agencyId] });
    },
  });
}

// Hooks for Agency Billing
export function useAgencyBilling(agencyId: string) {
  return useQuery({
    queryKey: ['agency-billing', agencyId],
    queryFn: () =>
      apiRequest<AgencyBilling>(`/whitelabel/agencies/${agencyId}/billing/`),
    enabled: !!agencyId,
  });
}

// Hooks for Agency Invoices
export function useAgencyInvoices(agencyId?: string, clientId?: string) {
  return useQuery({
    queryKey: ['agency-invoices', agencyId, clientId],
    queryFn: () => {
      let url = `/whitelabel/agencies/${agencyId}/invoices/`;
      if (clientId) url += `?client=${clientId}`;
      return apiRequest<AgencyInvoice[]>(url);
    },
    enabled: !!agencyId,
  });
}

export function useAgencyInvoice(agencyId: string, invoiceId: string) {
  return useQuery({
    queryKey: ['agency-invoice', agencyId, invoiceId],
    queryFn: () =>
      apiRequest<AgencyInvoice>(
        `/whitelabel/agencies/${agencyId}/invoices/${invoiceId}/`
      ),
    enabled: !!agencyId && !!invoiceId,
  });
}

export function useCreateAgencyInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      data,
    }: {
      agencyId: string;
      data: Partial<AgencyInvoice>;
    }) =>
      apiRequest<AgencyInvoice>(`/whitelabel/agencies/${agencyId}/invoices/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['agency-invoices', variables.agencyId] });
    },
  });
}

export function useUpdateAgencyInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      agencyId,
      invoiceId,
      data,
    }: {
      agencyId: string;
      invoiceId: string;
      data: Partial<AgencyInvoice>;
    }) =>
      apiRequest<AgencyInvoice>(
        `/whitelabel/agencies/${agencyId}/invoices/${invoiceId}/`,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['agency-invoice', variables.agencyId, variables.invoiceId],
      });
      queryClient.invalidateQueries({ queryKey: ['agency-invoices', variables.agencyId] });
    },
  });
}

export function useSendInvoice() {
  return useMutation({
    mutationFn: async ({
      agencyId,
      invoiceId,
    }: {
      agencyId: string;
      invoiceId: string;
    }) =>
      apiRequest(`/whitelabel/agencies/${agencyId}/invoices/${invoiceId}/send/`, {
        method: 'POST',
      }),
  });
}

// Hooks for Brand Library
export function useBrandLibraries(agencyId?: string, clientId?: string) {
  return useQuery({
    queryKey: ['brand-libraries', agencyId, clientId],
    queryFn: () => {
      let url = `/whitelabel/brand-library/`;
      const params = [];
      if (agencyId) params.push(`agency=${agencyId}`);
      if (clientId) params.push(`client=${clientId}`);
      if (params.length) url += `?${params.join('&')}`;
      return apiRequest<BrandLibrary[]>(url);
    },
  });
}

export function useBrandLibrary(libraryId: string) {
  return useQuery({
    queryKey: ['brand-library', libraryId],
    queryFn: () => apiRequest<BrandLibrary>(`/whitelabel/brand-library/${libraryId}/`),
    enabled: !!libraryId,
  });
}

export function useCreateBrandLibrary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<BrandLibrary>) =>
      apiRequest<BrandLibrary>('/whitelabel/brand-library/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brand-libraries'] });
    },
  });
}

export function useUpdateBrandLibrary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      libraryId,
      data,
    }: {
      libraryId: string;
      data: Partial<BrandLibrary>;
    }) =>
      apiRequest<BrandLibrary>(`/whitelabel/brand-library/${libraryId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['brand-library', variables.libraryId] });
      queryClient.invalidateQueries({ queryKey: ['brand-libraries'] });
    },
  });
}

export function useDeleteBrandLibrary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (libraryId: string) =>
      apiRequest(`/whitelabel/brand-library/${libraryId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brand-libraries'] });
    },
  });
}

// Access Client Portal
export function useAccessClientPortal(accessToken: string) {
  return useQuery({
    queryKey: ['client-portal-access', accessToken],
    queryFn: () =>
      apiRequest<ClientPortal>(`/whitelabel/portal-access/${accessToken}/`),
    enabled: !!accessToken,
  });
}
