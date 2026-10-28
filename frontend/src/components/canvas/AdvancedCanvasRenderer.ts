"use client";

import { Canvas, IText, Rect, Circle, Triangle, Path, Group, Point } from 'fabric';
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

// Fabric 7 changed the default origin to center/center. AI component
// coordinates are top-left anchored, so every object built from them must pin
// the origin explicitly or it renders half its width up and to the left.
const TOP_LEFT = { originX: 'left', originY: 'top' } as const;

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

    // Measure real Fabric bounds and center/scale to the actual canvas
    const metadata = result.metadata || {};
    const layout = result.layout || {};
    const isLogo =
      metadata.logotype != null ||
      metadata.source === 'ai-logo-designer' ||
      metadata.category === 'logo';
    const isAbsoluteShell =
      metadata.layout_mode === 'ui_shell' ||
      metadata.layout_mode === 'graphic_shell' ||
      metadata.layout_mode === 'logo_shell' ||
      metadata.category === 'ui_ux' ||
      layout.type === 'ui_dashboard_fixed' ||
      (typeof layout.type === 'string' && (
        layout.type.startsWith('graphic_') || layout.type.startsWith('logo_')
      ));

    // Match page chrome so white cards don't vanish on a white editor canvas
    const pageBg =
      (typeof metadata.page_background === 'string' && metadata.page_background) ||
      (isAbsoluteShell && metadata.category === 'ui_ux' ? '#F1F5F9' : undefined);
    if (pageBg) {
      this.canvas.set({ backgroundColor: pageBg });
    }

    // Engine shells use absolute full-canvas coords — never re-fit
    // (re-fitting mixes viewport bounds with scene coords and breaks the shell).
    if (!isAbsoluteShell) {
      this.fitAndCenterContent({
        center: true,
        targetFill: isLogo ? 0.5 : 0.94,
        enlargeIfSmall: true,
        maxEnlarge: isLogo ? 2.5 : 8,
        skipFullBleedBackgrounds: !isLogo,
      });
    } else if (metadata.layout_mode === 'ui_shell' || metadata.category === 'ui_ux') {
      // Keep KPI chrome above chart bars (no clipPath — it was hiding bars in Fabric 7)
      this.canvas.getObjects().forEach((obj: FabricObject) => {
        const layer = (obj as FabricObject & { aiLayer?: number }).aiLayer ?? 0;
        const stamped = (obj as FabricObject & { aiSubtype?: string }).aiSubtype;
        if (stamped === 'kpi_card' || layer >= 20) {
          this.canvas.bringObjectToFront(obj);
        }
      });
    }

    this.canvas.renderAll();
    console.log('AI design rendered successfully');
  }

  /**
   * After Fabric objects exist, center (and optionally scale) them using
   * measured bounding boxes — more accurate than declared LLM sizes.
   */
  private fitAndCenterContent(options: {
    center?: boolean;
    targetFill?: number;
    enlargeIfSmall?: boolean;
    maxEnlarge?: number;
    skipFullBleedBackgrounds?: boolean;
    pinTopLeft?: boolean;
  } = {}): void {
    const {
      center = true,
      targetFill = 0.9,
      enlargeIfSmall = false,
      maxEnlarge = 2.5,
      skipFullBleedBackgrounds = false,
      pinTopLeft = false,
    } = options;

    const canvasW = this.canvas.getWidth();
    const canvasH = this.canvas.getHeight();

    const allObjects = this.canvas.getObjects().filter(
      (obj: FabricObject) => !obj.get('isGuideline') && !obj.get('isGrid')
    );
    if (allObjects.length === 0) return;

    const objectSceneBounds = (obj: FabricObject): { left: number; top: number; width: number; height: number } => {
      // Use axis-aligned bounding box so rotated shapes (logo triangles, etc.)
      // don't report a false top-left that skews centering.
      if (typeof obj.getBoundingRect === 'function') {
        const rect = obj.getBoundingRect();
        return {
          left: rect.left,
          top: rect.top,
          width: Math.max(1, rect.width),
          height: Math.max(1, rect.height),
        };
      }
      const left = obj.left ?? 0;
      const top = obj.top ?? 0;
      const width = typeof obj.getScaledWidth === 'function' ? obj.getScaledWidth() : (obj.width || 0) * (obj.scaleX || 1);
      const height = typeof obj.getScaledHeight === 'function' ? obj.getScaledHeight() : (obj.height || 0) * (obj.scaleY || 1);
      return { left, top, width, height };
    };

    const isFullBleed = (obj: FabricObject): boolean => {
      const rect = objectSceneBounds(obj);
      return (
        rect.left <= 8 &&
        rect.top <= 8 &&
        rect.width >= canvasW * 0.9 &&
        rect.height >= canvasH * 0.9
      );
    };

    const objects = skipFullBleedBackgrounds
      ? allObjects.filter((obj) => !isFullBleed(obj))
      : allObjects;
    const measureTargets = objects.length > 0 ? objects : allObjects;

    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    measureTargets.forEach((obj) => {
      const rect = objectSceneBounds(obj);
      minX = Math.min(minX, rect.left);
      minY = Math.min(minY, rect.top);
      maxX = Math.max(maxX, rect.left + rect.width);
      maxY = Math.max(maxY, rect.top + rect.height);
    });

    if (!Number.isFinite(minX) || !Number.isFinite(minY)) return;

    const contentW = Math.max(1, maxX - minX);
    const contentH = Math.max(1, maxY - minY);
    const padding = Math.min(canvasW, canvasH) * 0.02;
    const maxW = Math.max(1, canvasW - padding * 2);
    const maxH = Math.max(1, canvasH - padding * 2);

    let scale = 1;
    if (contentW > maxW || contentH > maxH) {
      scale = Math.min(maxW / contentW, maxH / contentH);
    } else if (enlargeIfSmall) {
      const enlarge = Math.min(
        (maxW * targetFill) / contentW,
        (maxH * targetFill) / contentH
      );
      if (enlarge > 1 && enlarge <= maxEnlarge) {
        scale = enlarge;
      }
    }

    const contentCenterX = (minX + maxX) / 2;
    const contentCenterY = (minY + maxY) / 2;
    const targetCenterX = canvasW / 2;
    const targetCenterY = canvasH / 2;

    const transformTargets = skipFullBleedBackgrounds ? objects : allObjects;

    transformTargets.forEach((obj) => {
      const left = obj.left ?? 0;
      const top = obj.top ?? 0;
      let nextLeft: number;
      let nextTop: number;
      if (pinTopLeft) {
        nextLeft = padding + (left - minX) * scale;
        nextTop = padding + (top - minY) * scale;
      } else if (center) {
        nextLeft = targetCenterX + (left - contentCenterX) * scale;
        nextTop = targetCenterY + (top - contentCenterY) * scale;
      } else {
        nextLeft = left * scale;
        nextTop = top * scale;
      }

      obj.set({
        left: nextLeft,
        top: nextTop,
        scaleX: (obj.scaleX || 1) * scale,
        scaleY: (obj.scaleY || 1) * scale,
      });
      obj.setCoords();
    });

    // Keep full-bleed page backgrounds pinned after transforms
    if (skipFullBleedBackgrounds) {
      allObjects.filter(isFullBleed).forEach((obj) => {
        const baseW = Math.max(1, obj.width || canvasW);
        const baseH = Math.max(1, obj.height || canvasH);
        obj.set({
          left: 0,
          top: 0,
          scaleX: canvasW / baseW,
          scaleY: canvasH / baseH,
        });
        obj.setCoords();
      });
    }
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

      case 'circle':
        fabricObject = this.renderShape({ ...component, subtype: component.subtype || 'circle' });
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
        data: {
          componentType: type,
          componentIndex: index,
          subtype: component.subtype,
          layer: component.layer,
        },
        aiSubtype: component.subtype,
        aiLayer: component.layer ?? 0,
      } as Partial<FabricObject>);

      this.canvas.add(fabricObject);
    }
  }

  /**
   * Render text component
   */
  private renderText(component: ComponentData): FabricObject {
    const { position, content, style, size } = component;
    const textAlign =
      (style?.textAlign as 'left' | 'center' | 'right' | 'justify') || 'left';
    const boxWidth = size?.width;
    const isCentered = textAlign === 'center';

    const text = new IText(content || 'Text', {
      left: isCentered && boxWidth ? position.x + boxWidth / 2 : position.x,
      top: position.y,
      width: boxWidth || undefined,
      fontSize: style?.fontSize || 16,
      fontFamily: style?.fontFamily || 'Inter, Arial, sans-serif',
      fontWeight: style?.fontWeight || 'normal',
      fill: style?.fill || style?.color || '#000000',
      textAlign,
      originX: isCentered ? 'center' : 'left',
      originY: 'top',
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
      case 'ellipse': {
        const radius = Math.min(width, height) / 2;
        shape = new Circle({
          ...TOP_LEFT,
          left: position.x,
          top: position.y,
          radius,
          fill: style?.fill || '#3B82F6',
          stroke: style?.stroke || undefined,
          strokeWidth: style?.strokeWidth || 0,
          angle: style?.rotation || 0,
          opacity: style?.opacity || 1,
        }) as unknown as FabricObject;
        break;
      }

      case 'triangle':
        shape = new Triangle({
          ...TOP_LEFT,
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
        shape = this.createStar(position, Math.min(width, height), style);
        break;

      default:
        // Default to rectangle
        shape = new Rect({
          ...TOP_LEFT,
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
    const { position, size, style, subtype } = component;
    const isCard = (subtype || '').toLowerCase().includes('card');
    const defaultStroke = isCard || (style?.fill || '').toUpperCase() === '#FFFFFF'
      ? '#E2E8F0'
      : undefined;

    const rect = new Rect({
      ...TOP_LEFT,
      left: position.x,
      top: position.y,
      width: size?.width || 200,
      height: size?.height || 100,
      fill: style?.fill || style?.backgroundColor || '#F8FAFC',
      stroke: style?.stroke || style?.borderColor || defaultStroke,
      strokeWidth: style?.strokeWidth ?? style?.borderWidth ?? (defaultStroke ? 1 : 0),
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
   * Render button component — children use local coords to avoid Group double-offset
   */
  private renderButton(component: ComponentData): FabricObject {
    const { position, size, style, content } = component;

    const buttonWidth = size?.width || 150;
    const buttonHeight = size?.height || 40;

    const bg = new Rect({
      ...TOP_LEFT,
      left: 0,
      top: 0,
      width: buttonWidth,
      height: buttonHeight,
      fill: style?.backgroundColor || style?.fill || '#3B82F6',
      stroke: style?.borderColor || style?.stroke || undefined,
      strokeWidth: style?.borderWidth || style?.strokeWidth || 0,
      rx: style?.borderRadius || 8,
      ry: style?.borderRadius || 8,
      opacity: style?.opacity || 1,
    });

    const text = new IText(content || 'Button', {
      left: buttonWidth / 2,
      top: buttonHeight / 2,
      fontSize: style?.fontSize || 14,
      fontFamily: style?.fontFamily || 'Inter, Arial, sans-serif',
      fontWeight: style?.fontWeight || '600',
      fill: style?.color || '#FFFFFF',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
    });

    const group = new Group([bg as unknown as FabricObject, text as unknown as FabricObject], {
      ...TOP_LEFT,
      left: position.x,
      top: position.y,
      selectable: true,
    });

    return group as unknown as FabricObject;
  }

  /**
   * Render input component — children use local coords
   */
  private renderInput(component: ComponentData): FabricObject {
    const { position, size, style, content } = component;

    const inputWidth = size?.width || 250;
    const inputHeight = size?.height || 40;

    const input = new Rect({
      ...TOP_LEFT,
      left: 0,
      top: 0,
      width: inputWidth,
      height: inputHeight,
      fill: '#FFFFFF',
      stroke: style?.borderColor || '#D1D5DB',
      strokeWidth: style?.borderWidth || 1,
      rx: style?.borderRadius || 4,
      ry: style?.borderRadius || 4,
      opacity: style?.opacity || 1,
    });

    const placeholder = new IText(content || 'Input field', {
      left: 12,
      top: inputHeight / 2,
      fontSize: 14,
      fontFamily: 'Inter, Arial, sans-serif',
      fill: '#9CA3AF',
      originX: 'left',
      originY: 'center',
    });

    const group = new Group([input as unknown as FabricObject, placeholder as unknown as FabricObject], {
      ...TOP_LEFT,
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

    const icon = new Circle({
      ...TOP_LEFT,
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
   * Render image placeholder — a solid plate only.
   * Never use Path + scaleX/scaleY for the X decoration: Fabric scales the
   * stroke with the path, so a 1×1 diagonal scaled to 876×968 becomes the
   * giant gray diamonds that were destroying graphic layouts.
   */
  private renderImagePlaceholder(component: ComponentData): FabricObject {
    const { position, size, style, content } = component;

    const imgWidth = size?.width || 300;
    const imgHeight = size?.height || 200;
    const fill = style?.fill || style?.backgroundColor || '#E5E7EB';
    const radius = style?.borderRadius || 12;
    const label = (content || '').trim();
    const showLabel = Boolean(label && imgWidth >= 120 && imgHeight >= 80);

    const container = new Rect({
      ...TOP_LEFT,
      left: 0,
      top: 0,
      width: imgWidth,
      height: imgHeight,
      fill,
      stroke: style?.borderColor || undefined,
      strokeWidth: style?.borderWidth || style?.strokeWidth || 0,
      rx: radius,
      ry: radius,
      opacity: style?.opacity || 1,
    });

    if (!showLabel) {
      container.set({ left: position.x, top: position.y });
      return container as unknown as FabricObject;
    }

    const fontSize = Math.max(12, Math.min(18, Math.round(imgWidth / 40)));
    const caption = new IText(label, {
      left: imgWidth / 2,
      top: imgHeight / 2,
      fontSize,
      fontFamily: 'Inter, Arial, sans-serif',
      fontWeight: '500',
      fill: '#FFFFFF',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      opacity: 0.85,
      selectable: false,
      evented: false,
    });

    return new Group(
      [container as unknown as FabricObject, caption as unknown as FabricObject],
      {
        ...TOP_LEFT,
        left: position.x,
        top: position.y,
        selectable: true,
      }
    ) as unknown as FabricObject;
  }

  /**
   * Render hero section
   */
  private renderHero(component: ComponentData): FabricObject {
    const { position, size, style } = component;

    const heroWidth = size?.width || 800;
    const heroHeight = size?.height || 400;

    const bg = new Rect({
      ...TOP_LEFT,
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
   * Create a star shape using local path coordinates (avoids double-offset)
   */
  private createStar(
    position: { x: number; y: number },
    size: number,
    style?: ComponentData['style']
  ): FabricObject {
    const points = 5;
    const outerRadius = size / 2;
    const innerRadius = outerRadius / 2;
    const cx = outerRadius;
    const cy = outerRadius;

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
      ...TOP_LEFT,
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
          ...TOP_LEFT,
          stroke: '#EC4899',
          strokeWidth: 1,
          strokeDashArray: [5, 5],
          selectable: false,
          evented: false,
          opacity: 0.5,
        }) as unknown as FabricObject;
      } else {
        line = new Path(`M ${guide.position} 0 L ${guide.position} ${canvasHeight}`, {
          ...TOP_LEFT,
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
