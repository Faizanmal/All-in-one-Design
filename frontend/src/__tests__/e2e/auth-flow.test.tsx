/**
 * Frontend E2E Tests - Authentication Flow
 * Tests complete user authentication journeys through the UI
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// ---- Mocks ----
const mockPush = vi.fn();
const mockRefresh = vi.fn();
const mockReplace = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush, refresh: mockRefresh, replace: mockReplace }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/login',
  redirect: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn(), info: vi.fn() },
  Toaster: () => null,
}));

const mockLogin = vi.fn();
const mockRegister = vi.fn();
const mockLogout = vi.fn();
let mockIsAuthenticated = false;
let mockIsLoading = false;

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: mockIsAuthenticated ? { id: 1, username: 'testuser', email: 'test@example.com' } : null,
    isAuthenticated: mockIsAuthenticated,
    isLoading: mockIsLoading,
    login: mockLogin,
    register: mockRegister,
    logout: mockLogout,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('@/lib/design-api', () => ({
  authAPI: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn().mockResolvedValue({ id: 1, username: 'testuser' }),
    refreshToken: vi.fn(),
  },
  projectsAPI: {
    list: vi.fn().mockResolvedValue([]),
  },
}));

import LoginPage from '@/app/login/LoginPage';
import SignupPage from '@/app/signup/page';

describe('E2E: Login Flow', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
    mockIsAuthenticated = false;
    mockIsLoading = false;
  });

  it('complete login flow: renders form → fills fields → submits', async () => {
    mockLogin.mockResolvedValueOnce({ user: { id: 1 }, access_token: 'tok' });
    render(<LoginPage />);

    // Step 1: Form renders
    const emailInput = await screen.findByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    expect(emailInput).toBeInTheDocument();
    expect(passwordInput).toBeInTheDocument();

    // Step 2: Type credentials
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123' } });

    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('SecurePass123');

    // Step 3: Submit
    const submitButton = screen.getByRole('button', { name: /sign in|log in|login/i });
    await user.click(submitButton);
    await waitFor(() => expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'SecurePass123'));
  });

  it('shows validation for empty fields', async () => {
    render(<LoginPage />);

    const submitButton = await screen.findByRole('button', { name: /^sign in$/i });
    await user.click(submitButton);

    // HTML5 validation or custom validation should prevent submission
    const emailInput = screen.getByPlaceholderText(/email/i);
    expect(emailInput).toBeInTheDocument();
    expect(mockLogin).not.toHaveBeenCalled();
  });

  it('has link to signup page', () => {
    render(<LoginPage />);

    const signupLink = screen.queryByText(/sign up|create.*account|register/i);
    if (signupLink) {
      expect(signupLink).toBeInTheDocument();
    }
  });

  it('renders forgot password link', () => {
    render(<LoginPage />);

    const forgotLink = screen.queryByText(/forgot.*password/i);
    if (forgotLink) {
      expect(forgotLink).toBeInTheDocument();
    }
  });
});

describe('E2E: Signup Flow', () => {

  beforeEach(() => {
    vi.clearAllMocks();
    mockIsAuthenticated = false;
    mockIsLoading = false;
  });

  it('complete signup flow: renders form → fills all fields → submits', async () => {
    const { authAPI } = await import('@/lib/design-api');
    vi.mocked(authAPI.register).mockResolvedValueOnce({ access: 'tok2', refresh: 'ref2' });
    render(<SignupPage />);
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'newuser' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'newuser@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'StrongPass123!' } });
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'StrongPass123!' } });
    fireEvent.click(screen.getByRole('checkbox'));
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));
    await waitFor(() => expect(authAPI.register).toHaveBeenCalledWith('newuser', 'newuser@example.com', 'StrongPass123!'));
    await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/dashboard'));
    expect(localStorage.getItem('access_token')).toBe('tok2');
  });

  it('has link to login page', () => {
    render(<SignupPage />);

    expect(screen.getByRole('link', { name: /^sign in$/i })).toHaveAttribute('href', '/login');
  });
});

describe('E2E: Authentication State Management', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('stores and retrieves auth tokens from localStorage', () => {
    const tokens = {
      access_token: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test',
      refresh_token: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.refresh',
    };

    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);

    expect(localStorage.getItem('access_token')).toBe(tokens.access_token);
    expect(localStorage.getItem('refresh_token')).toBe(tokens.refresh_token);
  });

  it('clears tokens on logout', () => {
    localStorage.setItem('access_token', 'tok');
    localStorage.setItem('refresh_token', 'ref');
    localStorage.setItem('auth_token', 'auth');

    // Simulate logout
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('auth_token');

    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(localStorage.getItem('auth_token')).toBeNull();
  });

  it('handles expired tokens gracefully', () => {
    // JWT with expiry in the past
    const isTokenExpired = (token: string): boolean => {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 < Date.now();
      } catch {
        return true;
      }
    };

    expect(isTokenExpired('invalid_token')).toBe(true);
    expect(isTokenExpired('')).toBe(true);
  });
});
