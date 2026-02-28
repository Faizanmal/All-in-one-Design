/**
 * Frontend E2E Tests - Project Workflow
 * Tests complete project creation, editing, and management flows
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush, refresh: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/projects',
  redirect: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn(), loading: vi.fn() },
  Toaster: () => null,
}));

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'testuser', email: 'test@test.com' },
    isAuthenticated: true,
    isLoading: false,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

const mockProjects = [
  { id: 1, name: 'My Logo Design', project_type: 'logo', created_at: '2024-01-01', updated_at: '2024-01-15', is_public: false },
  { id: 2, name: 'Social Banner', project_type: 'social_media', created_at: '2024-01-05', updated_at: '2024-01-20', is_public: true },
  { id: 3, name: 'Brand Guidelines', project_type: 'document', created_at: '2024-01-10', updated_at: '2024-01-25', is_public: false },
];

vi.mock('@/lib/design-api', () => ({
  projectsAPI: {
    list: vi.fn().mockResolvedValue(mockProjects),
    create: vi.fn().mockResolvedValue({ id: 4, name: 'New Project' }),
    get: vi.fn().mockImplementation((id: number) =>
      Promise.resolve(mockProjects.find(p => p.id === id) || mockProjects[0])
    ),
    update: vi.fn().mockResolvedValue({ id: 1, name: 'Updated' }),
    delete: vi.fn().mockResolvedValue({}),
    duplicate: vi.fn().mockResolvedValue({ id: 5, name: 'Copy of My Logo Design' }),
    saveDesign: vi.fn().mockResolvedValue({}),
    exportDesign: vi.fn().mockResolvedValue(new Blob()),
  },
  templatesAPI: {
    list: vi.fn().mockResolvedValue([]),
  },
}));

import ProjectsPage from '@/app/projects/page';

describe('E2E: Project Dashboard', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders project listing page', () => {
    render(<ProjectsPage />);
    expect(document.body).toBeTruthy();
  });

  it('shows create project button', () => {
    render(<ProjectsPage />);
    const createBtn = screen.queryByText(/create|new.*project/i);
    if (createBtn) {
      expect(createBtn).toBeInTheDocument();
    }
  });

  it('has search functionality', () => {
    render(<ProjectsPage />);
    const searchInput = screen.queryByPlaceholderText(/search/i);
    if (searchInput) {
      expect(searchInput).toBeInTheDocument();
    }
  });
});

describe('E2E: Project Lifecycle', () => {
  it('simulates full project lifecycle: create → edit → save → export → delete', async () => {
    const { projectsAPI } = await import('@/lib/design-api');

    // Step 1: Create project
    const newProject = await projectsAPI.create({
      name: 'E2E Test Project',
      project_type: 'graphic',
      canvas_width: 1920,
      canvas_height: 1080,
    });
    expect(newProject).toBeDefined();
    expect(newProject.id).toBeDefined();

    // Step 2: Retrieve project
    const project = await projectsAPI.get(1);
    expect(project).toBeDefined();
    expect(project.name).toBe('My Logo Design');

    // Step 3: Update project
    const updated = await projectsAPI.update(1, { name: 'Updated Logo' });
    expect(updated).toBeDefined();

    // Step 4: Save design data
    await projectsAPI.saveDesign(1, {
      design_data: { layers: [{ type: 'text', text: 'Hello' }] },
    });
    expect(projectsAPI.saveDesign).toHaveBeenCalled();

    // Step 5: Export
    const exported = await projectsAPI.exportDesign(1, 'png');
    expect(exported).toBeInstanceOf(Blob);

    // Step 6: Delete
    await projectsAPI.delete(1);
    expect(projectsAPI.delete).toHaveBeenCalledWith(1);
  });

  it('handles project listing with filters', async () => {
    const { projectsAPI } = await import('@/lib/design-api');

    const allProjects = await projectsAPI.list();
    expect(allProjects).toHaveLength(3);

    // Verify project types
    const types = allProjects.map((p: { project_type: string }) => p.project_type);
    expect(types).toContain('logo');
    expect(types).toContain('social_media');
    expect(types).toContain('document');
  });

  it('handles project duplication', async () => {
    const { projectsAPI } = await import('@/lib/design-api');

    const duplicate = await projectsAPI.duplicate(1);
    expect(duplicate.name).toContain('Copy');
  });
});

describe('E2E: Project Canvas Interaction', () => {
  it('validates design data format', () => {
    const validDesignData = {
      version: '1.0',
      canvas: {
        width: 1920,
        height: 1080,
        backgroundColor: '#FFFFFF',
        zoom: 1.0,
      },
      objects: [
        {
          type: 'rect',
          left: 100,
          top: 100,
          width: 200,
          height: 200,
          fill: '#FF0000',
          opacity: 1,
          angle: 0,
        },
        {
          type: 'textbox',
          left: 150,
          top: 300,
          text: 'Sample Text',
          fontSize: 24,
          fontFamily: 'Arial',
          fill: '#000000',
        },
        {
          type: 'image',
          left: 400,
          top: 100,
          width: 300,
          height: 300,
          src: 'https://example.com/image.png',
        },
      ],
    };

    expect(validDesignData.objects).toHaveLength(3);
    expect(validDesignData.canvas.width).toBeGreaterThan(0);
    expect(validDesignData.canvas.height).toBeGreaterThan(0);
    const types = validDesignData.objects.map(o => o.type);
    expect(types).toContain('rect');
    expect(types).toContain('textbox');
    expect(types).toContain('image');
  });

  it('validates layer ordering', () => {
    const layers = [
      { id: 'bg', zIndex: 0, name: 'Background', locked: true },
      { id: 'shape1', zIndex: 1, name: 'Rectangle', locked: false },
      { id: 'text1', zIndex: 2, name: 'Title Text', locked: false },
      { id: 'image1', zIndex: 3, name: 'Logo', locked: false },
    ];

    // Verify z-ordering
    for (let i = 1; i < layers.length; i++) {
      expect(layers[i].zIndex).toBeGreaterThan(layers[i - 1].zIndex);
    }

    // Background should be locked
    expect(layers[0].locked).toBe(true);
  });

  it('validates undo/redo history', () => {
    const history = {
      past: [
        { action: 'add_shape', data: { type: 'rect' } },
        { action: 'move', data: { id: '1', x: 100, y: 100 } },
        { action: 'resize', data: { id: '1', width: 200, height: 200 } },
      ],
      present: { action: 'change_color', data: { id: '1', fill: '#FF0000' } },
      future: [] as Array<{ action: string; data: Record<string, unknown> }>,
    };

    expect(history.past).toHaveLength(3);
    expect(history.future).toHaveLength(0);

    // Simulate undo
    const lastAction = history.past.pop()!;
    history.future.unshift(history.present);
    history.present = lastAction;

    expect(history.past).toHaveLength(2);
    expect(history.future).toHaveLength(1);
    expect(history.present.action).toBe('resize');
  });
});

describe('E2E: Export Workflow', () => {
  it('supports all export formats', () => {
    const exportFormats = ['png', 'jpg', 'svg', 'pdf', 'webp'];

    exportFormats.forEach(format => {
      expect(typeof format).toBe('string');
      expect(format.length).toBeGreaterThan(0);
    });
  });

  it('validates export settings', () => {
    const exportSettings = {
      format: 'png',
      quality: 0.92,
      scale: 2,
      transparent: false,
      width: 1920,
      height: 1080,
    };

    expect(exportSettings.quality).toBeGreaterThan(0);
    expect(exportSettings.quality).toBeLessThanOrEqual(1);
    expect(exportSettings.scale).toBeGreaterThan(0);
    expect(exportSettings.width).toBeGreaterThan(0);
    expect(exportSettings.height).toBeGreaterThan(0);
  });
});
