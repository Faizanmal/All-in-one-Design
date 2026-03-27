"use client";

import { AuthProvider } from '@/lib/auth-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';
import { get, set, del } from 'idb-keyval';
import { Toaster } from 'sonner';
import { ThemeProvider } from '@/components/theme-provider';
import React from 'react';

// Create the IndexedDB persister explicitly for web environments
const idbValidKey = (key: string) => `react-query-persist-${key}`;

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 60 * 24, // 24 hours to keep data in cache
      retry: 2,
      refetchOnWindowFocus: true,
      refetchOnReconnect: 'always',
    },
    mutations: {
      // Setup global optimistic UI defaults
      retry: 3,
    }
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  // create persister lazily only on client
  const persister = React.useMemo(() => {
    if (typeof window === 'undefined') return null;
    return createAsyncStoragePersister({
      storage: {
        getItem: async (key) => await get(idbValidKey(key)),
        setItem: async (key, value) => await set(idbValidKey(key), value),
        removeItem: async (key) => await del(idbValidKey(key)),
      },
    });
  }, []);

  const coreContent = (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <AuthProvider>
        {children}
        <Toaster />
      </AuthProvider>
    </ThemeProvider>
  );

  if (!persister) {
    // SSR return normal provider to allow hydration
    return (
      <QueryClientProvider client={queryClient}>
        {coreContent}
      </QueryClientProvider>
    );
  }

  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{ persister, maxAge: 1000 * 60 * 60 * 24 * 7 }} // 7 days max cache
    >
      {coreContent}
    </PersistQueryClientProvider>
  );
}
