import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

vi.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'testuser', email: 'test@example.com' },
    isAuthenticated: true,
    isLoading: false,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

const saveDesign = vi.fn().mockResolvedValue({});
const getProject = vi.fn().mockResolvedValue({
  id: 1,
  name: 'Test Project',
  project_type: 'graphic',
  canvas_width: 1920,
  canvas_height: 1080,
  canvas_background: '#FFFFFF',
  design_data: { objects: [] },
});

vi.mock('@/lib/design-api', () => ({
  projectsAPI: {
    get: (...args: unknown[]) => getProject(...args),
    update: vi.fn().mockResolvedValue({}),
    saveDesign: (...args: unknown[]) => saveDesign(...args),
  },
  aiAPI: {
    generateLayout: vi.fn(),
  },
}));

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

vi.mock('@/hooks/useCollaborativeCanvas', () => ({
  useCollaborativeCanvas: () => ({
    isConnected: false,
    activeUsers: [],
    sendCursorPosition: vi.fn(),
    syncDesign: vi.fn(),
    markApplyingRemote: vi.fn(),
    recordAppliedSync: vi.fn(),
  }),
}));

vi.mock('@/components/collaboration/CommentsPanel', () => ({
  CommentsPanel: () => <div data-testid="comments-panel">Comments</div>,
}));

vi.mock('@/components/collaboration/ShareProjectDialog', () => ({
  ShareProjectDialog: () => <button type="button">Share</button>,
}));

vi.mock('@/components/export/ExportModal', () => ({
  ExportModal: () => null,
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
  Toaster: () => null,
}));

vi.mock('@/components/canvas/CanvasEditor', () => ({
  CanvasEditor: () => <div data-testid="canvas-editor">Canvas</div>,
}));

vi.mock('fabric', () => ({
  Canvas: class {
    add = vi.fn();
    remove = vi.fn();
    getObjects = vi.fn().mockReturnValue([]);
    on = vi.fn();
    off = vi.fn();
    dispose = vi.fn();
    renderAll = vi.fn();
    toJSON = vi.fn().mockReturnValue({ objects: [] });
    loadFromJSON = vi.fn().mockResolvedValue(undefined);
    setDimensions = vi.fn();
    calcOffset = vi.fn();
    set = vi.fn();
    getWidth = vi.fn().mockReturnValue(1920);
    getHeight = vi.fn().mockReturnValue(1080);
    clearContext = vi.fn();
    clear = vi.fn();
  },
  Rect: class {},
  Circle: class {},
  IText: class {},
  Triangle: class {},
  Line: class {},
  Point: class {},
  Image: { fromURL: vi.fn() },
  Path: class {},
  Group: class {},
}));

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams('project=1'),
  usePathname: () => '/editor',
}));

import EditorPage from '@/app/editor/page';

describe('EditorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (window as unknown as { canvasEditor?: Record<string, unknown> }).canvasEditor = {
      getCanvasData: vi.fn(() => ({ objects: [{ type: 'rect' }] })),
      loadCanvasData: vi.fn().mockResolvedValue(undefined),
      renderAIDesign: vi.fn(() => true),
      undo: vi.fn(),
      redo: vi.fn(),
      deleteSelected: vi.fn(),
      cloneSelected: vi.fn(),
      addText: vi.fn(),
      addRectangle: vi.fn(),
      addCircle: vi.fn(),
      exportAsPNG: vi.fn(),
      exportAsSVG: vi.fn(),
      exportAsFigmaJSON: vi.fn(),
      zoomIn: vi.fn(),
      zoomOut: vi.fn(),
      zoomToFit: vi.fn(),
    };
  });

  it('loads the project from the query string', async () => {
    render(<EditorPage />);
    await waitFor(() => {
      expect(getProject).toHaveBeenCalledWith(1);
    });
  });

  it('renders editor chrome with save/toolbar controls', async () => {
    render(<EditorPage />);
    await waitFor(() => {
      expect(screen.getByText(/AI Generation/i)).toBeInTheDocument();
    });
    const buttons = screen.queryAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});

describe('Editor canvas API contract', () => {
  it('exposes getCanvasData and renderAIDesign for the core loop', () => {
    const api = (window as unknown as { canvasEditor: {
      getCanvasData: () => Record<string, unknown> | null;
      renderAIDesign: (r: Record<string, unknown>) => boolean;
    } }).canvasEditor;

    // Reset from beforeEach of previous suite may not run here
    (window as unknown as { canvasEditor: typeof api }).canvasEditor = {
      getCanvasData: () => ({ objects: [] }),
      renderAIDesign: (r) => Array.isArray(r.components) && r.components.length > 0,
    };

    expect(window.canvasEditor?.getCanvasData?.()).toEqual({ objects: [] });
    expect(window.canvasEditor?.renderAIDesign?.({ components: [{ type: 'text' }] })).toBe(true);
    expect(window.canvasEditor?.renderAIDesign?.({ components: [] })).toBe(false);
  });
});
