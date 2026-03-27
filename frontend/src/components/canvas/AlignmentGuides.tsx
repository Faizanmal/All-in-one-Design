/**
 * Enterprise Alignment Guides Engine
 * High-performance smart snapping and alignment guides (Figma/Sketch style)
 */
'use client';

import { useEffect, useCallback, useRef } from 'react';
import type { FabricCanvas, FabricObject, FabricEvent } from '@/types/fabric';

// we need to access the top canvas context which isn't in the default
// FabricCanvas definition.  add a small helper type so we can avoid any.
type CanvasWithTopContext = FabricCanvas & { contextTop?: CanvasRenderingContext2D | null };

interface AlignmentGuidesProps {
  canvas: FabricCanvas | null;
  snapThreshold?: number;
  guideColor?: string;
  snapCenter?: boolean;
  snapEdges?: boolean;
}

interface GuideLine {
  type: 'vertical' | 'horizontal';
  position: number;
  start: number;
  end: number;
}

export function AlignmentGuides({
  canvas,
  snapThreshold = 8,
  guideColor = '#ff4b4b', // Figma-style red/pink
  snapCenter = true,
  snapEdges = true
}: AlignmentGuidesProps) {
  const activeGuidesRef = useRef<GuideLine[]>([]);
  const isMovingRef = useRef(false);

  // High-performance direct context drawing
  const drawGuidesOnContext = useCallback(() => {
    if (!canvas || activeGuidesRef.current.length === 0) return;

    // We draw on the top context so it overlays everything
    // TypeScript might complain about contextTop, so we use type assertion
    const ctx = (canvas as CanvasWithTopContext).contextTop;
    if (!ctx) return;

    ctx.save();
    ctx.beginPath();
    // modifying the drawing context is fine; eslint sometimes complains
    // that we're mutating a prop (canvas) because ctx was derived from it.
    // we explicitly disable that rule for this line.
    // eslint-disable-next-line react-hooks/immutability
    ctx.strokeStyle = guideColor;
    ctx.lineWidth = 1;
    ctx.setLineDash([0, 0]); // Solid crisp lines

    // Scale to match retina displays if fabric does viewport scaling
    const vpt = canvas.viewportTransform;
    if (vpt) {
      // transform context according to canvas zoom/pan
      ctx.transform(vpt[0], vpt[1], vpt[2], vpt[3], vpt[4], vpt[5]);
    }

    activeGuidesRef.current.forEach(guide => {
      if (guide.type === 'vertical') {
        ctx.moveTo(guide.position + 0.5, guide.start);
        ctx.lineTo(guide.position + 0.5, guide.end);
      } else {
        ctx.moveTo(guide.start, guide.position + 0.5);
        ctx.lineTo(guide.end, guide.position + 0.5);
      }
    });

    ctx.stroke();
    ctx.restore();
  }, [canvas, guideColor]);

  const clearGuides = useCallback(() => {
    activeGuidesRef.current = [];
    if (canvas) {
      // Trigger a re-render to clear the top context
      canvas.clearContext((canvas as CanvasWithTopContext).contextTop);
      canvas.renderAll();
    }
  }, [canvas]);

  const getObjBounds = (obj: FabricObject) => {
    obj.setCoords();
    const br = obj.getBoundingRect();
    return {
      left: br.left,
      right: br.left + br.width,
      center: br.left + br.width / 2,
      top: br.top,
      bottom: br.top + br.height,
      middle: br.top + br.height / 2,
      width: br.width,
      height: br.height
    };
  };

  const findSnapPoints = useCallback((movingObj: FabricObject) => {
    if (!canvas) return { x: undefined, y: undefined, guides: [] };

    const objects = canvas.getObjects().filter((obj) => obj !== movingObj && obj.visible);
    const movingBounds = getObjBounds(movingObj);
    const guides: GuideLine[] = [];

    let snapX: number | undefined = undefined;
    let snapY: number | undefined = undefined;

    // Viewport bounds
    const canvasWidth = canvas.getWidth();
    const canvasHeight = canvas.getHeight();

    // Calculate global line spans
    const vLineStart = -10000;
    const vLineEnd = 10000;

    // Check canvas center snapping
    if (snapCenter) {
      const cx = canvasWidth / 2;
      const cy = canvasHeight / 2;

      if (Math.abs(movingBounds.center - cx) < snapThreshold) {
        snapX = cx - movingBounds.width / 2;
        guides.push({ type: 'vertical', position: cx, start: vLineStart, end: vLineEnd });
      }
      if (Math.abs(movingBounds.middle - cy) < snapThreshold) {
        snapY = cy - movingBounds.height / 2;
        guides.push({ type: 'horizontal', position: cy, start: vLineStart, end: vLineEnd });
      }
    }

    // Check object snapping
    objects.forEach((obj) => {
      const targetBounds = getObjBounds(obj);

      // Vertical Checks (X axis)
      const vChecks = [];
      if (snapEdges) {
        vChecks.push(
          { movingPt: movingBounds.left, targetPt: targetBounds.left, offset: 0 },
          { movingPt: movingBounds.left, targetPt: targetBounds.right, offset: 0 },
          { movingPt: movingBounds.right, targetPt: targetBounds.left, offset: -movingBounds.width },
          { movingPt: movingBounds.right, targetPt: targetBounds.right, offset: -movingBounds.width }
        );
      }
      if (snapCenter) {
        vChecks.push(
          { movingPt: movingBounds.center, targetPt: targetBounds.center, offset: -movingBounds.width / 2 }
        );
      }

      for (const check of vChecks) {
        if (Math.abs(check.movingPt - check.targetPt) < snapThreshold && snapX === undefined) {
          snapX = check.targetPt + check.offset;
          guides.push({
            type: 'vertical',
            position: check.targetPt,
            start: Math.min(movingBounds.top, targetBounds.top) - 50,
            end: Math.max(movingBounds.bottom, targetBounds.bottom) + 50
          });
          break; // Prevent multiple X snaps to the same object
        }
      }

      // Horizontal Checks (Y axis)
      const hChecks = [];
      if (snapEdges) {
        hChecks.push(
          { movingPt: movingBounds.top, targetPt: targetBounds.top, offset: 0 },
          { movingPt: movingBounds.top, targetPt: targetBounds.bottom, offset: 0 },
          { movingPt: movingBounds.bottom, targetPt: targetBounds.top, offset: -movingBounds.height },
          { movingPt: movingBounds.bottom, targetPt: targetBounds.bottom, offset: -movingBounds.height }
        );
      }
      if (snapCenter) {
        hChecks.push(
          { movingPt: movingBounds.middle, targetPt: targetBounds.middle, offset: -movingBounds.height / 2 }
        );
      }

      for (const check of hChecks) {
        if (Math.abs(check.movingPt - check.targetPt) < snapThreshold && snapY === undefined) {
          snapY = check.targetPt + check.offset;
          guides.push({
            type: 'horizontal',
            position: check.targetPt,
            start: Math.min(movingBounds.left, targetBounds.left) - 50,
            end: Math.max(movingBounds.right, targetBounds.right) + 50
          });
          break; // Prevent multiple Y snaps to the same object
        }
      }
    });

    return { x: snapX, y: snapY, guides };
  }, [canvas, snapThreshold, snapEdges, snapCenter]);

  useEffect(() => {
    if (!canvas) return;

    const handleObjectMoving = (e: FabricEvent) => {
      if (!isMovingRef.current) return;

      const obj = e.target;
      // Exclude group scaling/rotation from snapping for stability
      if (!obj || obj.type === 'activeSelection') return;

      const { x, y, guides } = findSnapPoints(obj);

      let snapped = false;
      if (x !== undefined) {
        obj.set('left', x);
        snapped = true;
      }
      if (y !== undefined) {
        obj.set('top', y);
        snapped = true;
      }

      activeGuidesRef.current = guides;

      if (snapped) {
        obj.setCoords();
      }

      // Trigger a re-render to execute after:render hook
      canvas.requestRenderAll();
    };

    const handleBeforeRender = () => {
      if (canvas) {
        canvas.clearContext((canvas as CanvasWithTopContext).contextTop);
      }
    };

    const handleAfterRender = () => {
      if (isMovingRef.current && activeGuidesRef.current.length > 0) {
        drawGuidesOnContext();
      }
    };

    const handleMouseDown = () => {
      isMovingRef.current = true;
    };

    const handleMouseUp = () => {
      isMovingRef.current = false;
      clearGuides();
    };

    // Attach high-performance events
    canvas.on('object:moving', handleObjectMoving);
    canvas.on('mouse:down', handleMouseDown);
    canvas.on('mouse:up', handleMouseUp);
    canvas.on('before:render', handleBeforeRender);
    canvas.on('after:render', handleAfterRender);

    return () => {
      canvas.off('object:moving', handleObjectMoving);
      canvas.off('mouse:down', handleMouseDown);
      canvas.off('mouse:up', handleMouseUp);
      canvas.off('before:render', handleBeforeRender);
      canvas.off('after:render', handleAfterRender);
      clearGuides();
    };
  }, [canvas, findSnapPoints, drawGuidesOnContext, clearGuides]);

  return null;
}
