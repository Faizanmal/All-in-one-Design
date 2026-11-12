import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { GeneralAnalyticsDashboard } from '@/components/features/general-analytics/GeneralAnalyticsDashboard';
import apiClient from '@/lib/design-api';

vi.mock('@/lib/design-api', () => ({ default: { get: vi.fn(), post: vi.fn() } }));

const dashboard = {
  projects: { total: 0, this_week: 0, this_month: 0 },
  ai_usage: { today: { requests: 0, tokens: null, cost: null }, this_month: { requests: 0, tokens: null, cost: null } },
  activity: { today: 0, this_week: 0 },
  assets: { total: 0, storage_bytes: 0, storage_mb: 0 }, daily_chart_data: [],
};

function respond({ requests = 0, rate = null as number | null } = {}) {
  vi.mocked(apiClient.get).mockImplementation(async url => {
    if (url === '/v1/analytics/dashboard/') return { data: dashboard };
    if (url === '/v1/analytics/activities/recent/') return { data: [] };
    if (url === '/v1/analytics/ai-usage/summary/?days=30') return { data: { summary: { total_requests: requests, total_tokens: 0, total_cost: '0.000000', success_rate: rate }, by_service: { layout_generation: { count: requests, tokens: 0, cost: '0.000000' } } } };
    throw new Error(`Unexpected endpoint: ${url}`);
  });
}

describe('live analytics', () => {
  beforeEach(() => { vi.resetAllMocks(); respond(); });

  it('renders an empty account without invented events or numbers', async () => {
    render(<GeneralAnalyticsDashboard />);
    expect(screen.getByRole('status')).toHaveTextContent('Loading analytics');
    await screen.findByText('No recent activity.');
    expect(screen.getByText('0 created this week')).toBeInTheDocument();
    expect(screen.getByText('0 assets')).toBeInTheDocument();
    expect(apiClient.get).toHaveBeenCalledWith('/v1/analytics/dashboard/');
    expect(screen.queryByText('Website Redesign')).not.toBeInTheDocument();
  });

  it('shows a retryable error when the API fails and recovers on retry', async () => {
    vi.mocked(apiClient.get).mockRejectedValue(new Error('Unavailable'));
    render(<GeneralAnalyticsDashboard />);
    expect(await screen.findByRole('alert')).toHaveTextContent('Unable to load analytics');
    expect(screen.queryByText('Total projects')).not.toBeInTheDocument();
    respond();
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }));
    await screen.findByText('No recent activity.');
  });

  it('converts fractional success rates and accepts decimal cost strings', async () => {
    respond({ requests: 4, rate: 0.75 });
    render(<GeneralAnalyticsDashboard />);
    await screen.findByText('No recent activity.');
    fireEvent.mouseDown(screen.getByRole('tab', { name: 'AI usage' }), { button: 0, ctrlKey: false });
    await waitFor(() => expect(screen.getByText(/Success rate: 75.0%/)).toBeInTheDocument());
    expect(screen.getByText('layout generation')).toBeInTheDocument();
  });
});
