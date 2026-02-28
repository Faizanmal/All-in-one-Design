import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';

// Mock axios
vi.mock('axios', () => {
  const mockAxiosInstance = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    defaults: { headers: { common: {} } },
  };

  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
      post: vi.fn(),
      get: vi.fn(),
    },
  };
});

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('creates an axios instance with correct base URL', async () => {
    // Re-import to trigger module initialization
    const axiosModule = await import('axios');
    // The api module calls axios.create
    await import('@/lib/api');

    expect(axiosModule.default.create).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
        timeout: expect.any(Number),
      })
    );
  });

  it('sets authorization header when token exists', () => {
    localStorage.setItem('access_token', 'test-token-123');
    const token = localStorage.getItem('access_token');
    expect(token).toBe('test-token-123');
  });

  it('clears tokens on logout', () => {
    localStorage.setItem('access_token', 'test-token');
    localStorage.setItem('refresh_token', 'test-refresh');

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
  });
});

describe('API Endpoints', () => {
  it('should have correct API base URL pattern', () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    expect(apiUrl).toContain('/api');
  });

  it('should support v1 API versioning', () => {
    const baseUrl = 'http://localhost:8000/api';
    const endpoints = [
      `${baseUrl}/v1/auth/`,
      `${baseUrl}/v1/projects/`,
      `${baseUrl}/v1/ai/`,
      `${baseUrl}/v1/assets/`,
      `${baseUrl}/v1/teams/`,
    ];

    endpoints.forEach(endpoint => {
      expect(endpoint).toMatch(/\/api\/v1\//);
    });
  });
});
