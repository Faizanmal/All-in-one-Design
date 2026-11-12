import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { AIAssistantPanel } from '@/components/ai/AIAssistantPanel';
import apiClient from '@/lib/design-api';
import type { FabricCanvas } from '@/types/fabric';

const { toast, fromURL } = vi.hoisted(() => ({ toast: vi.fn(), fromURL: vi.fn() }));
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast }) }));
vi.mock('@/lib/design-api', () => ({ default: { post: vi.fn() } }));
vi.mock('fabric', () => ({ FabricImage: { fromURL } }));

function canvasFixture() {
  return {
    getObjects: () => [{ type: 'rect', left: 20, top: 30, angle: 0, getScaledWidth: () => 100, getScaledHeight: () => 50 }],
    getWidth: () => 800, getHeight: () => 600,
    add: vi.fn(), centerObject: vi.fn(), setActiveObject: vi.fn(), requestRenderAll: vi.fn(),
  };
}

function selectTab(name: string) {
  fireEvent.mouseDown(screen.getByRole('tab', { name }), { button: 0, ctrlKey: false });
}

describe('AI assistant actions', () => {
  beforeEach(() => vi.resetAllMocks());

  it('sends actual canvas geometry and displays the returned layout critique', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ data: { success: true, critique: { summary: 'Increase the gutter between cards.' } } });
    render(<AIAssistantPanel canvas={canvasFixture() as unknown as FabricCanvas} />);
    selectTab('Analyze');
    fireEvent.click(screen.getByRole('button', { name: 'Analyze Layout' }));
    expect(await screen.findByText('Increase the gutter between cards.')).toBeInTheDocument();
    expect(apiClient.post).toHaveBeenCalledWith('/ai/critique-design/', expect.objectContaining({
      width: 800, height: 600, element_count: 1,
      elements: [{ type: 'rect', left: 20, top: 30, width: 100, height: 50, angle: 0 }],
    }));
  });

  it('does not spend an AI request when there is no canvas', () => {
    render(<AIAssistantPanel canvas={null} />);
    selectTab('Analyze');
    fireEvent.click(screen.getByRole('button', { name: 'Typography Report' }));
    expect(apiClient.post).not.toHaveBeenCalled();
    expect(toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' }));
  });

  it('generates an image and inserts it into the canvas on request', async () => {
    const canvas = canvasFixture();
    const image = { width: 1024, height: 1024, scale: vi.fn(), setCoords: vi.fn() };
    fromURL.mockResolvedValue(image);
    vi.mocked(apiClient.post).mockResolvedValue({ data: { image_url: 'https://assets.example.com/generated.png' } });
    render(<AIAssistantPanel canvas={canvas as unknown as FabricCanvas} />);
    selectTab('Tools');
    fireEvent.change(screen.getByLabelText('Image description'), { target: { value: 'A mountain illustration' } });
    fireEvent.click(screen.getByRole('button', { name: 'AI Image Generation' }));
    expect(await screen.findByRole('link', { name: 'Open generated image' })).toHaveAttribute('href', 'https://assets.example.com/generated.png');
    expect(canvas.add).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Add image to canvas' }));
    await waitFor(() => expect(canvas.add).toHaveBeenCalledWith(image));
    expect(fromURL).toHaveBeenCalledWith('https://assets.example.com/generated.png', { crossOrigin: 'anonymous' });
    expect(canvas.centerObject).toHaveBeenCalledWith(image);
    expect(image.scale).toHaveBeenCalledWith(600 / 1024);
  });

  it('reports provider failure instead of showing a successful analysis', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ data: { success: false, error: 'Service unavailable' } });
    render(<AIAssistantPanel canvas={canvasFixture() as unknown as FabricCanvas} />);
    selectTab('Analyze');
    fireEvent.click(screen.getByRole('button', { name: 'Typography Report' }));
    await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Analysis failed', variant: 'destructive' })));
    expect(screen.queryByText('Typography recommendations')).not.toBeInTheDocument();
  });
});
