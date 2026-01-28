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

declare global {
  interface Window {
    fabric: {
      Canvas: new (element: HTMLCanvasElement | string, options?: object) => Canvas;
      Object: new (options?: object) => FabricObj;
      IText: new (text: string, options?: object) => FabricObj;
      Text: new (text: string, options?: object) => FabricObj;
      Rect: new (options?: object) => FabricObj;
      Circle: new (options?: object) => FabricObj;
      Line: new (coords: number[], options?: object) => FabricObj;
      Group: new (objects: FabricObj[], options?: object) => FabricObj;
      ActiveSelection: new (objects: FabricObj[], options?: object) => FabricObj;
      Image: {
        fromURL: (url: string, callback: (img: FabricObj) => void) => void;
      };
    };
  }
}

export {};
