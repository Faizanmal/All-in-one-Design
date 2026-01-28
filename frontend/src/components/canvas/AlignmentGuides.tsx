/**
 * Alignment Guides Component
 * Smart snapping and alignment guides like Figma/Sketch
 */
'use client';

import { useEffect, useCallback, useRef } from 'react';
import type { FabricCanvas, FabricObject, FabricEvent } from '@/types/fabric';
interface AlignmentGuidesProps {
  canvas: FabricCanvas | null;
  snapThreshold?: number;
  showDistances?: boolean;
}

interface Guide {
  type: 'vertical' | 'horizontal';
  position: number;
  color: string;
}

export function AlignmentGuides({ 
  canvas, 
  snapThreshold = 5,
  showDistances = true 
}: AlignmentGuidesProps) {
  const guidesRef = useRef<Guide[]>([]);
  const canvasWrapperRef = useRef<HTMLDivElement | null>(null);

  // Calculate object bounds
  const getObjectBounds = useCallback((obj: FabricObject) => {
    const matrix = obj.calcTransformMatrix();
    const bounds = obj.getBoundingRect();
    
    return {
      left: bounds.left,
      top: bounds.top,
      right: bounds.left + bounds.width,
      bottom: bounds.top + bounds.height,
      centerX: bounds.left + bounds.width / 2,
      centerY: bounds.top + bounds.height / 2,
      width: bounds.width,
      height: bounds.height,
    };
  }, []);

  // Find snap points
  const findSnapPoints = useCallback((movingObj: FabricObject) => {
    if (!canvas) return { x: null, y: null, guides: [] };

    const objects = canvas.getObjects().filter((obj) => obj !== movingObj && obj.visible);
    const movingBounds = getObjectBounds(movingObj);
    const guides: Guide[] = [];
    
    let snapX: number | null = null;
    let snapY: number | null = null;

    // Canvas center lines
    const canvasWidth = canvas.width || 0;
    const canvasHeight = canvas.height || 0;
    const canvasCenterX = canvasWidth / 2;
    const canvasCenterY = canvasHeight / 2;

    // Check alignment with canvas center
    if (Math.abs(movingBounds.centerX - canvasCenterX) < snapThreshold) {
      snapX = canvasCenterX - movingBounds.width / 2;
      guides.push({ type: 'vertical', position: canvasCenterX, color: '#FF00FF' });
    }
    if (Math.abs(movingBounds.centerY - canvasCenterY) < snapThreshold) {
      snapY = canvasCenterY - movingBounds.height / 2;
      guides.push({ type: 'horizontal', position: canvasCenterY, color: '#FF00FF' });
    }

    // Check alignment with other objects
    objects.forEach((obj) => {
      const bounds = getObjectBounds(obj);

      // Vertical alignment checks
      const verticalChecks = [
        { point: movingBounds.left, target: bounds.left, label: 'left' },
        { point: movingBounds.left, target: bounds.right, label: 'left-right' },
        { point: movingBounds.right, target: bounds.left, label: 'right-left' },
        { point: movingBounds.right, target: bounds.right, label: 'right' },
        { point: movingBounds.centerX, target: bounds.centerX, label: 'center' },
      ];

      verticalChecks.forEach(({ point, target }) => {
        if (Math.abs(point - target) < snapThreshold && snapX === null) {
          snapX = movingBounds.left + (target - point);
          guides.push({ type: 'vertical', position: target, color: '#00FF00' });
        }
      });

      // Horizontal alignment checks
      const horizontalChecks = [
        { point: movingBounds.top, target: bounds.top, label: 'top' },
        { point: movingBounds.top, target: bounds.bottom, label: 'top-bottom' },
        { point: movingBounds.bottom, target: bounds.top, label: 'bottom-top' },
        { point: movingBounds.bottom, target: bounds.bottom, label: 'bottom' },
        { point: movingBounds.centerY, target: bounds.centerY, label: 'middle' },
      ];

      horizontalChecks.forEach(({ point, target }) => {
        if (Math.abs(point - target) < snapThreshold && snapY === null) {
          snapY = movingBounds.top + (target - point);
          guides.push({ type: 'horizontal', position: target, color: '#00FF00' });
        }
      });
    });

    return { x: snapX, y: snapY, guides };
  }, [canvas, getObjectBounds, snapThreshold]);

  // Draw guides on canvas
  const drawGuides = useCallback((guides: Guide[]) => {
    if (!canvas) return;

    // Clear previous guides
    const existingGuides = canvas.getObjects().filter((obj) => (obj as any).isGuide);
    existingGuides.forEach((guide) => canvas.remove(guide));

    // Draw new guides
    guides.forEach(guide => {
      let line;
      if (guide.type === 'vertical') {
        line = new window.fabric.Line(
          [guide.position, 0, guide.position, canvas.height],
          {
            stroke: guide.color,
            strokeWidth: 1,
            strokeDashArray: [5, 5],
            selectable: false,
            evented: false,
            isGuide: true,
          }
        );
      } else {
        line = new window.fabric.Line(
          [0, guide.position, canvas.width!, guide.position],
          {
            stroke: guide.color,
            strokeWidth: 1,
            strokeDashArray: [5, 5],
            selectable: false,
            evented: false,
            isGuide: true,
          }
        );
      }
      canvas.add(line);
    });

    canvas.renderAll();
  }, [canvas]);

  // Clear guides
  const clearGuides = useCallback(() => {
    if (!canvas) return;
    const guides = canvas.getObjects().filter((obj) => (obj as any).isGuide);
    guides.forEach((guide) => canvas.remove(guide));
    canvas.renderAll();
  }, [canvas]);

  // Setup event handlers
  useEffect(() => {
    if (!canvas) return;

    let isMoving = false;

    const handleObjectMoving = (e: FabricEvent) => {
      const obj = e.target;
      if (!obj || !isMoving) return;

      const { x, y, guides } = findSnapPoints(obj);

      // Apply snapping
      if (x !== null) obj.set('left', x);
      if (y !== null) obj.set('top', y);

      // Draw guides
      drawGuides(guides);
      guidesRef.current = guides;
    };

    const handleMouseDown = () => {
      isMoving = true;
    };

    const handleMouseUp = () => {
      isMoving = false;
      clearGuides();
    };

    const handleObjectModified = () => {
      clearGuides();
    };

    canvas.on('object:moving', handleObjectMoving);
    canvas.on('mouse:down', handleMouseDown);
    canvas.on('mouse:up', handleMouseUp);
    canvas.on('object:modified', handleObjectModified);

    return () => {
      canvas.off('object:moving', handleObjectMoving);
      canvas.off('mouse:down', handleMouseDown);
      canvas.off('mouse:up', handleMouseUp);
      canvas.off('object:modified', handleObjectModified);
      clearGuides();
    };
  }, [canvas, findSnapPoints, drawGuides, clearGuides]);

  return null; // This component doesn't render anything visible
}
