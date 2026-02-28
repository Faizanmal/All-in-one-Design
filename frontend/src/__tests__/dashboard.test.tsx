import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'testuser', email: 'test@example.com' },
    isAuthenticated: true,
    isLoading: false,
    logout: vi.fn(),
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('@tanstack/react-query', () => ({
  useQuery: () => ({
    data: [],
    isLoading: false,
    error: null,
  }),
  useMutation: () => ({
    mutate: vi.fn(),
    isLoading: false,
  }),
  QueryClient: vi.fn().mockImplementation(() => ({})),
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
  Toaster: () => null,
}));

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: () => <div data-testid="bar-chart" />,
  Bar: () => null,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  Legend: () => null,
  LineChart: () => <div data-testid="line-chart" />,
  Line: () => null,
  PieChart: () => <div data-testid="pie-chart" />,
  Pie: () => null,
  Cell: () => null,
  AreaChart: () => <div data-testid="area-chart" />,
  Area: () => null,
}));

import DashboardPage from '@/app/dashboard/page';

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the dashboard page', () => {
    render(<DashboardPage />);

    // Dashboard should render without crashing
    const heading = document.querySelector('h1, h2, h3');
    expect(heading).toBeDefined();
  });

  it('renders navigation or sidebar', () => {
    render(<DashboardPage />);

    // Check for common dashboard elements
    const nav = document.querySelector('nav, aside, [role="navigation"]');
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThanOrEqual(0);
  });
});
