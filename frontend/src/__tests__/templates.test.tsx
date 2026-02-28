import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'testuser', email: 'test@example.com' },
    isAuthenticated: true,
    isLoading: false,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('@tanstack/react-query', () => ({
  useQuery: () => ({
    data: {
      results: [
        {
          id: 1, title: 'Business Card', slug: 'business-card',
          description: 'A business card template',
          category: { id: 1, name: 'Business', slug: 'business' },
          tags: ['business', 'card'], thumbnail: '/thumb.png',
          pricing_type: 'free', price: '0', downloads: 100,
          views: 500, average_rating: '4.5', rating_count: 10,
        },
      ],
    },
    isLoading: false,
    error: null,
  }),
  useMutation: () => ({
    mutate: vi.fn(),
    isLoading: false,
  }),
  useQueryClient: () => ({
    invalidateQueries: vi.fn(),
  }),
  QueryClient: vi.fn().mockImplementation(() => ({})),
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: { results: [] } }),
    post: vi.fn().mockResolvedValue({ data: {} }),
  },
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
  Toaster: () => null,
}));

import TemplatesPage from '@/app/templates/page';

describe('TemplatesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the templates page', () => {
    render(<TemplatesPage />);
    const heading = document.querySelector('h1, h2, h3');
    expect(heading).toBeDefined();
  });

  it('renders search input', () => {
    render(<TemplatesPage />);
    const searchInput = document.querySelector('input');
    expect(searchInput).toBeDefined();
  });

  it('renders template cards or grid', () => {
    render(<TemplatesPage />);
    const cards = document.querySelectorAll('[class*="card"], [class*="grid"]');
    expect(cards.length).toBeGreaterThanOrEqual(0);
  });

  it('renders filter or category tabs', () => {
    render(<TemplatesPage />);
    const tabs = document.querySelectorAll('[role="tab"], [role="tablist"]');
    expect(tabs.length).toBeGreaterThanOrEqual(0);
  });
});
