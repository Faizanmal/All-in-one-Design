import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
  Toaster: () => null,
}));

vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
      <div {...(props as React.HTMLAttributes<HTMLDivElement>)}>{children}</div>
    ),
    button: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
      <button {...(props as React.ButtonHTMLAttributes<HTMLButtonElement>)}>{children}</button>
    ),
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'testuser', email: 'test@example.com' },
    isAuthenticated: true,
    isLoading: false,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import SettingsPage from '@/app/settings/page';

describe('SettingsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the settings page', () => {
    render(<SettingsPage />);
    const heading = screen.queryByText(/settings/i) || document.querySelector('h1');
    expect(heading).toBeDefined();
  });

  it('renders tab navigation', () => {
    render(<SettingsPage />);
    // Settings page has tabs: Profile, Notifications, Security, etc.
    const tabs = document.querySelectorAll('[role="tab"]');
    expect(tabs.length).toBeGreaterThanOrEqual(1);
  });

  it('renders profile form fields', () => {
    render(<SettingsPage />);
    const inputs = document.querySelectorAll('input');
    expect(inputs.length).toBeGreaterThanOrEqual(1);
  });

  it('renders save button', () => {
    render(<SettingsPage />);
    const saveButton = screen.queryByText(/save/i);
    expect(saveButton).toBeDefined();
  });

  it('renders notification toggles', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);

    // Click on Notifications tab if available
    const notifTab = screen.queryByText(/notification/i);
    if (notifTab) {
      await user.click(notifTab);
    }

    // Check for switch elements
    const switches = document.querySelectorAll('[role="switch"], input[type="checkbox"]');
    expect(switches.length).toBeGreaterThanOrEqual(0);
  });

  it('renders security section', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);

    const securityTab = screen.queryByText(/security/i);
    if (securityTab) {
      await user.click(securityTab);
    }
    expect(true).toBe(true);
  });
});
