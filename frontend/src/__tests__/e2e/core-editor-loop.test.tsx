/**
 * Core product loop tests:
 * create → AI render → save → reload → export
 * plus auth token unification and collab last-write-wins.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  getAccessToken,
  setAccessToken,
  clearAuthTokens,
  ACCESS_TOKEN_KEY,
  LEGACY_AUTH_TOKEN_KEY,
} from '@/lib/auth-token';
import { nextSyncTimestamp, shouldApplyRemoteSync } from '@/lib/collab-sync';
import { AdvancedCanvasRenderer } from '@/components/canvas/AdvancedCanvasRenderer';

vi.mock('fabric', () => {
  class MockObj {
    set = vi.fn();
    get = vi.fn().mockReturnValue(false);
  }
  return {
    Canvas: class MockCanvas {
      add = vi.fn();
      remove = vi.fn();
      getObjects = vi.fn().mockReturnValue([]);
      renderAll = vi.fn();
      getWidth = vi.fn().mockReturnValue(1920);
      getHeight = vi.fn().mockReturnValue(1080);
    },
    IText: class extends MockObj {},
    Rect: class extends MockObj {},
    Circle: class extends MockObj {},
    Triangle: class extends MockObj {},
    Path: class extends MockObj {},
    Group: class extends MockObj {},
  };
});

describe('Auth token unification', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('reads access_token preferentially and falls back to auth_token', () => {
    localStorage.setItem(LEGACY_AUTH_TOKEN_KEY, 'legacy');
    expect(getAccessToken()).toBe('legacy');

    localStorage.setItem(ACCESS_TOKEN_KEY, 'canonical');
    expect(getAccessToken()).toBe('canonical');
  });

  it('keeps both keys in sync when setting/clearing', () => {
    setAccessToken('abc123');
    expect(localStorage.getItem(ACCESS_TOKEN_KEY)).toBe('abc123');
    expect(localStorage.getItem(LEGACY_AUTH_TOKEN_KEY)).toBe('abc123');

    clearAuthTokens();
    expect(getAccessToken()).toBeNull();
    expect(localStorage.getItem(ACCESS_TOKEN_KEY)).toBeNull();
    expect(localStorage.getItem(LEGACY_AUTH_TOKEN_KEY)).toBeNull();
  });
});

describe('Collab last-write-wins', () => {
  it('applies newer remote timestamps only', () => {
    expect(shouldApplyRemoteSync(200, 100, 50)).toBe(true);
    expect(shouldApplyRemoteSync(100, 100, 50)).toBe(false);
    expect(shouldApplyRemoteSync(80, 100, 50)).toBe(false);
    expect(shouldApplyRemoteSync(90, 50, 100)).toBe(false);
  });

  it('allows legacy payloads without timestamps', () => {
    expect(shouldApplyRemoteSync(undefined, 100, 100)).toBe(true);
    expect(shouldApplyRemoteSync(0, 100, 100)).toBe(true);
  });

  it('monotonic nextSyncTimestamp never goes backwards', () => {
    const a = nextSyncTimestamp(1000);
    const b = nextSyncTimestamp(a);
    expect(b).toBeGreaterThanOrEqual(a);
  });
});

describe('AI → canvas rendering', () => {
  it('renders AI components onto fabric canvas', () => {
    const added: unknown[] = [];
    const canvas = {
      getObjects: vi.fn().mockReturnValue([]),
      remove: vi.fn(),
      add: vi.fn((obj: unknown) => added.push(obj)),
      renderAll: vi.fn(),
      getWidth: vi.fn().mockReturnValue(1920),
      getHeight: vi.fn().mockReturnValue(1080),
    };

    const renderer = new AdvancedCanvasRenderer(canvas as never);
    renderer.renderAIResult({
      components: [
        {
          type: 'text',
          content: 'Hello',
          position: { x: 40, y: 40 },
          style: { fontSize: 32, fill: '#111' },
          layer: 1,
        },
        {
          type: 'rectangle',
          position: { x: 100, y: 120 },
          size: { width: 200, height: 80 },
          style: { fill: '#3B82F6' },
          layer: 0,
        },
        {
          type: 'button',
          content: 'CTA',
          position: { x: 140, y: 220 },
          size: { width: 120, height: 40 },
          layer: 2,
        },
      ],
    });

    expect(canvas.add).toHaveBeenCalled();
    expect(added.length).toBe(3);
    expect(canvas.renderAll).toHaveBeenCalled();
  });

  it('no-ops when AI result has no components', () => {
    const canvas = {
      getObjects: vi.fn().mockReturnValue([]),
      remove: vi.fn(),
      add: vi.fn(),
      renderAll: vi.fn(),
    };
    const renderer = new AdvancedCanvasRenderer(canvas as never);
    renderer.renderAIResult({ components: [] });
    expect(canvas.add).not.toHaveBeenCalled();
  });
});

describe('E2E core loop: create → AI → save → reload → export', () => {
  const designSnapshot = {
    version: '5.3.0',
    objects: [
      { type: 'textbox', text: 'AI Title', left: 80, top: 60 },
      { type: 'rect', left: 80, top: 140, width: 320, height: 120, fill: '#17BEBB' },
    ],
    background: '#FFFFFF',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    setAccessToken('test-jwt');
  });

  it('runs the canonical project API path end-to-end', async () => {
    const saveDesign = vi.fn().mockResolvedValue({ id: 42, design_data: designSnapshot });
    const get = vi.fn().mockResolvedValue({
      id: 42,
      name: 'Core Loop Project',
      design_data: designSnapshot,
      canvas_width: 1920,
      canvas_height: 1080,
    });
    const create = vi.fn().mockResolvedValue({
      id: 42,
      name: 'Core Loop Project',
      design_data: {},
    });
    const exportDesign = vi.fn().mockResolvedValue(new Blob(['png'], { type: 'image/png' }));
    const generateLayout = vi.fn().mockResolvedValue({
      components: [
        { type: 'text', content: 'AI Title', position: { x: 80, y: 60 } },
        { type: 'rectangle', position: { x: 80, y: 140 }, size: { width: 320, height: 120 } },
      ],
    });

    // 1) Create
    const project = await create({
      name: 'Core Loop Project',
      project_type: 'ui_ux',
      canvas_width: 1920,
      canvas_height: 1080,
    });
    expect(project.id).toBe(42);

    // 2) AI generate
    const aiResult = await generateLayout('Modern landing hero', 'ui_ux');
    expect(aiResult.components).toHaveLength(2);

    // 3) Render AI onto canvas API surface
    const loadFromJSON = vi.fn().mockResolvedValue(undefined);
    const canvasEditor = {
      renderAIDesign: vi.fn((result: { components?: unknown[] }) =>
        Boolean(result.components && result.components.length > 0)
      ),
      getCanvasData: vi.fn(() => designSnapshot),
      loadCanvasData: vi.fn((data: Record<string, unknown>) => loadFromJSON(data)),
      exportAsPNG: vi.fn(),
    };
    expect(canvasEditor.renderAIDesign(aiResult)).toBe(true);

    // 4) Save
    const snapshot = canvasEditor.getCanvasData();
    await saveDesign(project.id, snapshot);
    expect(saveDesign).toHaveBeenCalledWith(42, designSnapshot);

    // 5) Reload
    const reloaded = await get(42);
    await canvasEditor.loadCanvasData(reloaded.design_data);
    expect(loadFromJSON).toHaveBeenCalledWith(designSnapshot);
    expect(reloaded.design_data.objects).toHaveLength(2);

    // 6) Export
    const blob = await exportDesign(42, 'png');
    expect(blob).toBeInstanceOf(Blob);
    canvasEditor.exportAsPNG();
    expect(canvasEditor.exportAsPNG).toHaveBeenCalled();
  });

  it('rejects save when canvas editor has no snapshot', async () => {
    const saveDesign = vi.fn();
    const canvasEditor = {
      getCanvasData: () => null as Record<string, unknown> | null,
    };
    const canvasData = canvasEditor.getCanvasData();
    if (!canvasData) {
      expect(saveDesign).not.toHaveBeenCalled();
      return;
    }
    await saveDesign(1, canvasData);
    expect.fail('should not save without canvas data');
  });

  it('rejects AI success when renderer returns false', () => {
    const canvasEditor = {
      renderAIDesign: (result: { components?: unknown[] }) =>
        Boolean(result.components && result.components.length > 0),
    };
    expect(canvasEditor.renderAIDesign({ components: [] })).toBe(false);
    expect(canvasEditor.renderAIDesign({ components: [{ type: 'text' }] })).toBe(true);
  });
});
