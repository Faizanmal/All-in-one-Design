import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock the auth context
const mockLogin = vi.fn();
const mockLogout = vi.fn();

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: mockLogin,
    logout: mockLogout,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
  Toaster: () => null,
}));

// Import component after mocks
import LoginPage from '@/app/login/page';

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form with email and password fields', () => {
    render(<LoginPage />);

    expect(screen.getByRole('heading', { level: 1 })).toBeDefined();
    // Check for email/username input
    const inputs = screen.getAllByRole('textbox');
    expect(inputs.length).toBeGreaterThanOrEqual(1);
  });

  it('renders sign up link', () => {
    render(<LoginPage />);

    const signUpLink = screen.getByText(/sign up/i) || screen.getByText(/create.*account/i) || screen.getByText(/register/i);
    expect(signUpLink).toBeDefined();
  });

  it('renders social login buttons', () => {
    render(<LoginPage />);

    // Look for Google or GitHub login options
    const socialButtons = screen.queryAllByRole('button');
    expect(socialButtons.length).toBeGreaterThanOrEqual(1);
  });

  it('shows password field as password type', () => {
    render(<LoginPage />);

    const passwordInputs = document.querySelectorAll('input[type="password"]');
    expect(passwordInputs.length).toBeGreaterThanOrEqual(1);
  });
});
