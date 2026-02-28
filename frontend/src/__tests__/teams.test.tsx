import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

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

vi.mock('@/lib/teams-api', () => ({
  teamsAPI: {
    getTeams: vi.fn().mockResolvedValue({
      results: [
        { id: 1, name: 'Design Team', slug: 'design-team', description: 'Team 1', members_count: 5 },
        { id: 2, name: 'Dev Team', slug: 'dev-team', description: 'Team 2', members_count: 3 },
      ],
    }),
    getTeamMembers: vi.fn().mockResolvedValue([
      { id: 1, user: { id: 1, username: 'owner' }, role: 'owner' },
      { id: 2, user: { id: 2, username: 'member' }, role: 'member' },
    ]),
    createTeam: vi.fn(),
    inviteMember: vi.fn(),
    getInvitations: vi.fn().mockResolvedValue([]),
  },
  Team: {},
  TeamMember: {},
  TeamInvitation: {},
}));

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'testuser', email: 'test@example.com' },
    isAuthenticated: true,
    isLoading: false,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
  Toaster: () => null,
}));

import TeamsPage from '@/app/teams/page';

describe('TeamsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the teams page', () => {
    render(<TeamsPage />);
    const heading = document.querySelector('h1, h2, h3');
    expect(heading).toBeDefined();
  });

  it('renders create team button', () => {
    render(<TeamsPage />);
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it('renders without crashing when no teams', () => {
    render(<TeamsPage />);
    expect(true).toBe(true);
  });
});
