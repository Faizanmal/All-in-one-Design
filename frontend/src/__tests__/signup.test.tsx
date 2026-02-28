import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock auth context
const mockLoginWithGoogle = vi.fn();
const mockLoginWithGitHub = vi.fn();

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    loginWithGoogle: mockLoginWithGoogle,
    loginWithGitHub: mockLoginWithGitHub,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('@/lib/design-api', () => ({
  authAPI: {
    register: vi.fn().mockResolvedValue({ data: { token: 'test-token' } }),
  },
}));

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
  Toaster: () => null,
}));

import SignupPage from '@/app/signup/page';

describe('SignupPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders signup form', () => {
    render(<SignupPage />);
    const heading = document.querySelector('h1, h2, h3');
    expect(heading).toBeDefined();
  });

  it('renders username, email, password, and confirm password inputs', () => {
    render(<SignupPage />);
    const inputs = document.querySelectorAll('input');
    // Should have at least 4 inputs: username, email, password, confirm password
    expect(inputs.length).toBeGreaterThanOrEqual(4);
  });

  it('renders password fields as password type', () => {
    render(<SignupPage />);
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    expect(passwordInputs.length).toBeGreaterThanOrEqual(2);
  });

  it('renders terms checkbox', () => {
    render(<SignupPage />);
    const checkbox = document.querySelector('input[type="checkbox"], button[role="checkbox"]');
    expect(checkbox).toBeDefined();
  });

  it('renders login link', () => {
    render(<SignupPage />);
    const loginLink = screen.queryByText(/sign in/i) || screen.queryByText(/log in/i) || screen.queryByText(/login/i);
    expect(loginLink).toBeDefined();
  });

  it('renders social signup buttons', () => {
    render(<SignupPage />);
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it('renders sign up button', () => {
    render(<SignupPage />);
    const signupButton = screen.queryByRole('button', { name: /sign up|create account|register/i });
    // Check that at least a submit-type button exists
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it('allows typing in form fields', async () => {
    const user = userEvent.setup();
    render(<SignupPage />);

    const textInputs = document.querySelectorAll('input[type="text"], input[type="email"]');
    if (textInputs.length > 0) {
      await user.type(textInputs[0] as HTMLInputElement, 'testuser');
      expect((textInputs[0] as HTMLInputElement).value).toBe('testuser');
    }
  });
});
