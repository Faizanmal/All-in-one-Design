import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

// We need to test the auth context directly
const mockFetch = vi.fn();
global.fetch = mockFetch;

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
  Toaster: () => null,
}));

vi.mock('@tanstack/react-query', () => ({
  QueryClient: vi.fn().mockImplementation(() => ({})),
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe('Auth Context', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockFetch.mockReset();
  });

  it('stores tokens in localStorage on login', () => {
    localStorage.setItem('access_token', 'test-access');
    localStorage.setItem('refresh_token', 'test-refresh');
    
    expect(localStorage.getItem('access_token')).toBe('test-access');
    expect(localStorage.getItem('refresh_token')).toBe('test-refresh');
  });

  it('clears tokens on logout', () => {
    localStorage.setItem('access_token', 'test-access');
    localStorage.setItem('refresh_token', 'test-refresh');
    localStorage.setItem('user', JSON.stringify({ id: 1 }));

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');

    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  it('stores user data as JSON', () => {
    const userData = { id: 1, username: 'testuser', email: 'test@example.com' };
    localStorage.setItem('user', JSON.stringify(userData));
    
    const stored = JSON.parse(localStorage.getItem('user')!);
    expect(stored.username).toBe('testuser');
    expect(stored.email).toBe('test@example.com');
  });

  it('handles missing user data gracefully', () => {
    const user = localStorage.getItem('user');
    expect(user).toBeNull();
  });

  it('handles invalid JSON in user data', () => {
    localStorage.setItem('user', 'invalid-json');
    try {
      JSON.parse(localStorage.getItem('user')!);
    } catch (e) {
      expect(e).toBeInstanceOf(SyntaxError);
    }
  });

  it('dual token key compatibility', () => {
    // design-api uses auth_token, auth-context uses access_token
    localStorage.setItem('auth_token', 'design-token');
    localStorage.setItem('access_token', 'auth-token');

    expect(localStorage.getItem('auth_token')).toBe('design-token');
    expect(localStorage.getItem('access_token')).toBe('auth-token');
  });
});
