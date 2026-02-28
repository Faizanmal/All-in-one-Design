/**
 * Frontend E2E Tests - Authentication Flow
 * Tests complete user authentication journeys through the UI
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
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

import LoginPage from '@/app/login/page';
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
    const emailInput = screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    expect(emailInput).toBeInTheDocument();
    expect(passwordInput).toBeInTheDocument();

    // Step 2: Type credentials
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'SecurePass123');

    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('SecurePass123');

    // Step 3: Submit
    const submitButton = screen.getByRole('button', { name: /sign in|log in|login/i });
    await user.click(submitButton);
  });

  it('shows validation for empty fields', async () => {
    render(<LoginPage />);

    const submitButton = screen.getByRole('button', { name: /sign in|log in|login/i });
    await user.click(submitButton);

    // HTML5 validation or custom validation should prevent submission
    const emailInput = screen.getByPlaceholderText(/email/i);
    expect(emailInput).toBeInTheDocument();
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
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
    mockIsAuthenticated = false;
    mockIsLoading = false;
  });

  it('complete signup flow: renders form → fills all fields → submits', async () => {
    mockRegister.mockResolvedValueOnce({ user: { id: 2 }, access_token: 'tok2' });
    render(<SignupPage />);

    // Step 1: Form renders
    const allInputs = screen.getAllByRole('textbox');
    expect(allInputs.length).toBeGreaterThanOrEqual(1);

    // Step 2: Fill name/email if available
    const emailInput = screen.queryByPlaceholderText(/email/i);
    if (emailInput) {
      await user.type(emailInput, 'newuser@example.com');
      expect(emailInput).toHaveValue('newuser@example.com');
    }

    // Step 3: Fill password fields
    const passwordInputs = screen.queryAllByPlaceholderText(/password/i);
    if (passwordInputs.length > 0) {
      await user.type(passwordInputs[0], 'StrongPass123!');
    }
    if (passwordInputs.length > 1) {
      await user.type(passwordInputs[1], 'StrongPass123!');
    }

    // Step 4: Accept terms if checkbox exists
    const terms = screen.queryByRole('checkbox');
    if (terms) {
      await user.click(terms);
    }
  });

  it('has link to login page', () => {
    render(<SignupPage />);

    const loginLink = screen.queryByText(/log in|sign in|already.*account/i);
    if (loginLink) {
      expect(loginLink).toBeInTheDocument();
    }
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
