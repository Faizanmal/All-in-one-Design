import { beforeEach, describe, expect, it, vi } from 'vitest';
import apiClient from '@/lib/design-api';
import { requestDesignAssistant } from '@/lib/design-assistant-api';

vi.mock('@/lib/design-api', () => ({ default: { post: vi.fn() } }));

describe('design assistant requests', () => {
  beforeEach(() => vi.resetAllMocks());

  it('uses the configured authenticated client and preserves the layout result', async () => {
    const result = { success: true, optimization: { improvements: [{ issue: 'Crowded', suggestion: 'Increase spacing' }] } };
    vi.mocked(apiClient.post).mockResolvedValue({ data: result });
    await expect(requestDesignAssistant('optimize-layout', { width: 1200, height: 800 })).resolves.toEqual(result);
    expect(apiClient.post).toHaveBeenCalledWith('/ai/optimize-layout/', { width: 1200, height: 800 });
  });

  it('treats a provider failure in a 200 response as an error', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ data: { success: false, error: 'Provider unavailable' } });
    await expect(requestDesignAssistant('suggest-typography', {})).rejects.toThrow('Provider unavailable');
  });

  it('propagates HTTP failures instead of inventing a result', async () => {
    vi.mocked(apiClient.post).mockRejectedValue(new Error('Quota exceeded'));
    await expect(requestDesignAssistant('generate-image', { prompt: 'A tree' })).rejects.toThrow('Quota exceeded');
  });

  it('shows the API error when a quota or configuration check rejects a request', async () => {
    vi.mocked(apiClient.post).mockRejectedValue({ isAxiosError: true, response: { data: { error: 'AI quota exceeded' } } });
    await expect(requestDesignAssistant('generate-image', { prompt: 'A tree' })).rejects.toThrow('AI quota exceeded');
  });
});
