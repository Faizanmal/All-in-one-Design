"use client";

import { Canvas, IText, Rect, Circle, Triangle, Path, Group } from 'fabric';
import type { FabricObject } from '@/types/fabric';

interface ComponentData {
  type: string;
  subtype?: string;
  content?: string;
  position: { x: number; y: number };
  size?: { width: number; height: number };
  style?: {
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
    fontSize?: number;
    fontFamily?: string;
    fontWeight?: string;
    textAlign?: string;
    rotation?: number;
    opacity?: number;
    shadow?: { x: number; y: number; blur: number; color: string };
    borderRadius?: number;
    backgroundColor?: string;
    color?: string;
    borderColor?: string;
    borderWidth?: number;
    padding?: number;
    margin?: number;
  };
  layer?: number;
  semantic?: string;
}

interface AIResultData {
  components?: ComponentData[];
  metadata?: Record<string, unknown>;
  layout?: Record<string, unknown>;
  grid?: Record<string, unknown>;
  interactions?: Array<Record<string, unknown>>;
}

export class AdvancedCanvasRenderer {
  private canvas: Canvas;

  constructor(canvas: Canvas) {
    this.canvas = canvas;
  }

  /**
   * Render AI-generated design on canvas
   */
  renderAIResult(result: AIResultData): void {
    const components = result.components || [];
    
    if (components.length === 0) {
      console.warn('No components to render');
      return;
    }

    console.log(`Rendering ${components.length} AI-generated components`);

    // Clear existing objects (except guidelines/grid)
    const objectsToRemove = this.canvas.getObjects().filter(
      (obj: FabricObject) => !obj.get('isGuideline') && !obj.get('isGrid')
    );
    objectsToRemove.forEach(obj => this.canvas.remove(obj));

    // Sort by layer to ensure proper stacking
    const sortedComponents = [...components].sort(
      (a, b) => (a.layer || 0) - (b.layer || 0)
    );

    // Render each component
    sortedComponents.forEach((component, index) => {
      try {
        this.renderComponent(component, index);
      } catch (error) {
        console.error(`Failed to render component ${index}:`, error);
      }
    });

    // Render guidelines if provided
    if (result.grid) {
      this.renderGuidelines(result.grid);
    }

    this.canvas.renderAll();
    console.log('AI design rendered successfully');
  }

  /**
   * Render a single component
   */
  private renderComponent(component: ComponentData, index: number): void {
    const { type } = component;

    let fabricObject: FabricObject | null = null;

    // Route to appropriate renderer based on type
    switch (type) {
      case 'text':
      case 'header':
      case 'footer':
      case 'navigation':
        fabricObject = this.renderText(component);
        break;

      case 'shape':
        fabricObject = this.renderShape(component);
        break;

      case 'background':
      case 'rectangle':
      case 'container':
      case 'card':
      case 'section':
        fabricObject = this.renderRectangle(component);
        break;

      case 'button':
        fabricObject = this.renderButton(component);
        break;

      case 'input':
      case 'form':
        fabricObject = this.renderInput(component);
        break;

      case 'icon':
      case 'symbol':
        fabricObject = this.renderIcon(component);
        break;

      case 'image':
        fabricObject = this.renderImagePlaceholder(component);
        break;

      case 'hero':
        fabricObject = this.renderHero(component);
        break;

      default:
        console.warn(`Unknown component type: ${type}, using rectangle`);
        fabricObject = this.renderRectangle(component);
    }

    if (fabricObject) {
      fabricObject.set({
        selectable: true,
        hasControls: true,
        hasBorders: true,
        data: { componentType: type, componentIndex: index },
      } as Partial<FabricObject>);

      this.canvas.add(fabricObject);
    }
  }

  /**
   * Render text component
   */
  private renderText(component: ComponentData): FabricObject {
    const { position, content, style } = component;

    const text = new IText(content || 'Text', {
      left: position.x,
      top: position.y,
      fontSize: style?.fontSize || 16,
      fontFamily: style?.fontFamily || 'Inter, Arial, sans-serif',
      fontWeight: style?.fontWeight || 'normal',
      fill: style?.fill || style?.color || '#000000',
      textAlign: (style?.textAlign as 'left' | 'center' | 'right' | 'justify') || 'left',
      angle: style?.rotation || 0,
      opacity: style?.opacity || 1,
    });

    if (style?.shadow) {
      text.set({
        shadow: {
          color: style.shadow.color,
          offsetX: style.shadow.x,
          offsetY: style.shadow.y,
          blur: style.shadow.blur,
        },
      });
    }

    return text as unknown as FabricObject;
  }

  /**
   * Render shape component (circle, triangle, star, etc.)
   */
  private renderShape(component: ComponentData): FabricObject {
    const { subtype, position, size, style } = component;

    const width = size?.width || 100;
    const height = size?.height || 100;

    let shape: FabricObject;

    switch (subtype) {
      case 'circle':
        shape = new Circle({
          left: position.x,
          top: position.y,
          radius: Math.min(width, height) / 2,
          fill: style?.fill || '#3B82F6',
          stroke: style?.stroke || undefined,
          strokeWidth: style?.strokeWidth || 0,
          angle: style?.rotation || 0,
          opacity: style?.opacity || 1,
        }) as unknown as FabricObject;
        break;

      case 'triangle':
        shape = new Triangle({
          left: position.x,
          top: position.y,
          width: width,
          height: height,
          fill: style?.fill || '#3B82F6',
          stroke: style?.stroke || undefined,
          strokeWidth: style?.strokeWidth || 0,
          angle: style?.rotation || 0,
          opacity: style?.opacity || 1,
        }) as unknown as FabricObject;
        break;

      case 'star':
        shape = this.createStar(position, width, style);
        break;

      default:
        // Default to rectangle
        shape = new Rect({
          left: position.x,
          top: position.y,
          width: width,
          height: height,
          fill: style?.fill || '#3B82F6',
          stroke: style?.stroke || undefined,
          strokeWidth: style?.strokeWidth || 0,
          rx: style?.borderRadius || 0,
          ry: style?.borderRadius || 0,
          angle: style?.rotation || 0,
          opacity: style?.opacity || 1,
        }) as unknown as FabricObject;
    }

    return shape;
  }

  /**
   * Render rectangle/container component
   */
  private renderRectangle(component: ComponentData): FabricObject {
    const { position, size, style } = component;

    const rect = new Rect({
      left: position.x,
      top: position.y,
      width: size?.width || 200,
      height: size?.height || 100,
      fill: style?.fill || style?.backgroundColor || '#F3F4F6',
      stroke: style?.stroke || style?.borderColor || undefined,
      strokeWidth: style?.strokeWidth || style?.borderWidth || 0,
      rx: style?.borderRadius || 0,
      ry: style?.borderRadius || 0,
      angle: style?.rotation || 0,
      opacity: style?.opacity || 1,
    });

    if (style?.shadow) {
      rect.set({
        shadow: {
          color: style.shadow.color,
          offsetX: style.shadow.x,
          offsetY: style.shadow.y,
          blur: style.shadow.blur,
        },
      });
    }

    return rect as unknown as FabricObject;
  }

  /**
   * Render button component
   */
  private renderButton(component: ComponentData): FabricObject {
    const { position, size, style, content } = component;

    const buttonWidth = size?.width || 150;
    const buttonHeight = size?.height || 40;

    // Create button background
    const bg = new Rect({
      left: position.x,
      top: position.y,
      width: buttonWidth,
      height: buttonHeight,
      fill: style?.backgroundColor || style?.fill || '#3B82F6',
      stroke: style?.borderColor || style?.stroke || undefined,
      strokeWidth: style?.borderWidth || style?.strokeWidth || 0,
      rx: style?.borderRadius || 8,
      ry: style?.borderRadius || 8,
      opacity: style?.opacity || 1,
    });

    // Create button text
    const text = new IText(content || 'Button', {
      left: position.x + buttonWidth / 2,
      top: position.y + buttonHeight / 2,
      fontSize: style?.fontSize || 14,
      fontFamily: style?.fontFamily || 'Inter, Arial, sans-serif',
      fontWeight: style?.fontWeight || '600',
      fill: style?.color || '#FFFFFF',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
    });

    // Group button elements
    const group = new Group([bg as unknown as FabricObject, text as unknown as FabricObject], {
      left: position.x,
      top: position.y,
      selectable: true,
    });

    return group as unknown as FabricObject;
  }

  /**
   * Render input component
   */
  private renderInput(component: ComponentData): FabricObject {
    const { position, size, style, content } = component;

    const inputWidth = size?.width || 250;
    const inputHeight = size?.height || 40;

    const input = new Rect({
      left: position.x,
      top: position.y,
      width: inputWidth,
      height: inputHeight,
      fill: '#FFFFFF',
      stroke: style?.borderColor || '#D1D5DB',
      strokeWidth: style?.borderWidth || 1,
      rx: style?.borderRadius || 4,
      ry: style?.borderRadius || 4,
      opacity: style?.opacity || 1,
    });

    // Placeholder text
    const placeholder = new IText(content || 'Input field', {
      left: position.x + 12,
      top: position.y + inputHeight / 2,
      fontSize: 14,
      fontFamily: 'Inter, Arial, sans-serif',
      fill: '#9CA3AF',
      originY: 'center',
    });

    const group = new Group([input as unknown as FabricObject, placeholder as unknown as FabricObject], {
      left: position.x,
      top: position.y,
      selectable: true,
    });

    return group as unknown as FabricObject;
  }

  /**
   * Render icon component
   */
  private renderIcon(component: ComponentData): FabricObject {
    const { position, size, style } = component;

    const iconSize = Math.min(size?.width || 40, size?.height || 40);

    // Create a simple circle icon placeholder
    const icon = new Circle({
      left: position.x,
      top: position.y,
      radius: iconSize / 2,
      fill: style?.fill || style?.backgroundColor || '#6366F1',
      stroke: style?.stroke || undefined,
      strokeWidth: style?.strokeWidth || 0,
      opacity: style?.opacity || 1,
    });

    return icon as unknown as FabricObject;
  }

  /**
   * Render image placeholder component
   */
  private renderImagePlaceholder(component: ComponentData): FabricObject {
    const { position, size, style } = component;

    const imgWidth = size?.width || 300;
    const imgHeight = size?.height || 200;

    // Image container
    const container = new Rect({
      left: position.x,
      top: position.y,
      width: imgWidth,
      height: imgHeight,
      fill: '#E5E7EB',
      stroke: style?.borderColor || '#D1D5DB',
      strokeWidth: 1,
      rx: style?.borderRadius || 4,
      ry: style?.borderRadius || 4,
      opacity: style?.opacity || 1,
    });

    // Image icon (diagonal lines)
    const line1 = new Path('M 0 0 L 1 1', {
      left: position.x,
      top: position.y,
      stroke: '#9CA3AF',
      strokeWidth: 2,
      scaleX: imgWidth,
      scaleY: imgHeight,
      selectable: false,
    });

    const line2 = new Path('M 1 0 L 0 1', {
      left: position.x,
      top: position.y,
      stroke: '#9CA3AF',
      strokeWidth: 2,
      scaleX: imgWidth,
      scaleY: imgHeight,
      selectable: false,
    });

    const group = new Group([container as unknown as FabricObject, line1 as unknown as FabricObject, line2 as unknown as FabricObject], {
      left: position.x,
      top: position.y,
      selectable: true,
    });

    return group as unknown as FabricObject;
  }

  /**
   * Render hero section
   */
  private renderHero(component: ComponentData): FabricObject {
    const { position, size, style } = component;

    const heroWidth = size?.width || 800;
    const heroHeight = size?.height || 400;

    // Hero background
    const bg = new Rect({
      left: position.x,
      top: position.y,
      width: heroWidth,
      height: heroHeight,
      fill: style?.backgroundColor || style?.fill || '#F9FAFB',
      stroke: style?.borderColor,
      strokeWidth: style?.borderWidth || 0,
      rx: style?.borderRadius || 0,
      ry: style?.borderRadius || 0,
      opacity: style?.opacity || 1,
    });

    return bg as unknown as FabricObject;
  }

  /**
   * Create a star shape
   */
  private createStar(
    position: { x: number; y: number },
    size: number,
    style?: ComponentData['style']
  ): FabricObject {
    const points = 5;
    const outerRadius = size / 2;
    const innerRadius = outerRadius / 2;
    const cx = position.x + outerRadius;
    const cy = position.y + outerRadius;

    let pathData = '';
    for (let i = 0; i < points * 2; i++) {
      const radius = i % 2 === 0 ? outerRadius : innerRadius;
      const angle = (i * Math.PI) / points - Math.PI / 2;
      const x = cx + radius * Math.cos(angle);
      const y = cy + radius * Math.sin(angle);
      pathData += i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`;
    }
    pathData += ' Z';

    const star = new Path(pathData, {
      left: position.x,
      top: position.y,
      fill: style?.fill || '#FBBF24',
      stroke: style?.stroke,
      strokeWidth: style?.strokeWidth || 0,
      angle: style?.rotation || 0,
      opacity: style?.opacity || 1,
    });

    return star as unknown as FabricObject;
  }

  /**
   * Render guidelines/grid
   */
  private renderGuidelines(gridData: Record<string, unknown>): void {
    const enabled = gridData.enabled;
    if (!enabled) return;

    const guides = (gridData.guides as Array<{ type: string; position: number }>) || [];
    const canvasWidth = this.canvas.getWidth();
    const canvasHeight = this.canvas.getHeight();

    guides.forEach(guide => {
      let line: FabricObject;

      if (guide.type === 'horizontal') {
        line = new Path(`M 0 ${guide.position} L ${canvasWidth} ${guide.position}`, {
          stroke: '#EC4899',
          strokeWidth: 1,
          strokeDashArray: [5, 5],
          selectable: false,
          evented: false,
          opacity: 0.5,
        }) as unknown as FabricObject;
      } else {
        line = new Path(`M ${guide.position} 0 L ${guide.position} ${canvasHeight}`, {
          stroke: '#EC4899',
          strokeWidth: 1,
          strokeDashArray: [5, 5],
          selectable: false,
          evented: false,
          opacity: 0.5,
        }) as unknown as FabricObject;
      }

      line.set('isGuideline', true);
      this.canvas.add(line);
    });
  }
}

export default AdvancedCanvasRenderer;
