import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

vi.mock('@/lib/auth-context', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="auth-provider">{children}</div>
  ),
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
  }),
}));

vi.mock('@tanstack/react-query', () => ({
  QueryClient: vi.fn().mockImplementation(() => ({
    defaultOptions: {},
  })),
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="query-provider">{children}</div>
  ),
}));

vi.mock('sonner', () => ({
  Toaster: () => <div data-testid="toaster" />,
  toast: { success: vi.fn(), error: vi.fn() },
}));

vi.mock('@/components/theme-provider', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="theme-provider">{children}</div>
  ),
}));

import { Providers } from '@/components/providers';

describe('Providers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders children correctly', () => {
    render(
      <Providers>
        <div data-testid="child">Hello</div>
      </Providers>
    );
    expect(screen.getByTestId('child')).toBeDefined();
    expect(screen.getByText('Hello')).toBeDefined();
  });

  it('wraps children with QueryClientProvider', () => {
    render(
      <Providers>
        <span>Test</span>
      </Providers>
    );
    expect(screen.getByTestId('query-provider')).toBeDefined();
  });

  it('wraps children with ThemeProvider', () => {
    render(
      <Providers>
        <span>Test</span>
      </Providers>
    );
    expect(screen.getByTestId('theme-provider')).toBeDefined();
  });

  it('wraps children with AuthProvider', () => {
    render(
      <Providers>
        <span>Test</span>
      </Providers>
    );
    expect(screen.getByTestId('auth-provider')).toBeDefined();
  });

  it('renders Toaster', () => {
    render(
      <Providers>
        <span>Test</span>
      </Providers>
    );
    expect(screen.getByTestId('toaster')).toBeDefined();
  });
});
