// Fabric.js type definitions for our use case
// Compatible with fabric npm package
import type { Canvas, FabricObject as FabricObj } from 'fabric';

export type FabricCanvas = Canvas;
export type FabricObject = FabricObj;

export interface FabricEvent {
  e?: Event;
  target?: FabricObject;
  selected?: FabricObject[];
}

export {};
