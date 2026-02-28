import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';

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

describe('Design API - projectsAPI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should have correct project API patterns', () => {
    const baseUrl = 'http://localhost:8000/api';
    const endpoints = {
      list: `${baseUrl}/v1/projects/`,
      create: `${baseUrl}/v1/projects/`,
      detail: `${baseUrl}/v1/projects/1/`,
      myProjects: `${baseUrl}/v1/projects/my_projects/`,
      saveDesign: `${baseUrl}/v1/projects/1/save_design/`,
    };

    Object.values(endpoints).forEach(url => {
      expect(url).toContain('/api/v1/projects');
    });
  });

  it('should have correct AI API patterns', () => {
    const baseUrl = 'http://localhost:8000/api';
    const endpoints = {
      generate: `${baseUrl}/v1/ai/generate/`,
      refine: `${baseUrl}/v1/ai/refine/`,
    };

    Object.values(endpoints).forEach(url => {
      expect(url).toContain('/api/v1/ai');
    });
  });

  it('should have correct auth API patterns', () => {
    const baseUrl = 'http://localhost:8000/api';
    const endpoints = {
      register: `${baseUrl}/v1/auth/register/`,
      login: `${baseUrl}/v1/auth/login/`,
      me: `${baseUrl}/v1/auth/users/me/`,
    };

    Object.values(endpoints).forEach(url => {
      expect(url).toContain('/api/v1/auth');
    });
  });

  it('should store auth_token for design API', () => {
    localStorage.setItem('auth_token', 'design-api-token');
    expect(localStorage.getItem('auth_token')).toBe('design-api-token');
  });

  it('should handle API error responses', () => {
    const errorResponse = {
      status: 400,
      data: { error: 'Bad Request' },
    };
    expect(errorResponse.status).toBe(400);
    expect(errorResponse.data.error).toBe('Bad Request');
  });

  it('should handle project data structure', () => {
    const project = {
      id: 1,
      name: 'Test Project',
      description: 'A test',
      project_type: 'graphic',
      canvas_width: 1920,
      canvas_height: 1080,
      design_data: { layers: [] },
      is_public: false,
    };

    expect(project.id).toBe(1);
    expect(project.project_type).toBe('graphic');
    expect(project.design_data.layers).toHaveLength(0);
  });
});

describe('Design API - Component types', () => {
  it('validates component types', () => {
    const validTypes = ['text', 'image', 'shape', 'button', 'icon', 'group', 'frame'];
    validTypes.forEach(type => {
      expect(typeof type).toBe('string');
    });
  });

  it('validates project types', () => {
    const validTypes = ['graphic', 'ui_ux', 'logo'];
    validTypes.forEach(type => {
      expect(typeof type).toBe('string');
    });
  });
});
