export type BoundingBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export function overlapArea(a: BoundingBox, b: BoundingBox): number {
  const overlapX = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x));
  const overlapY = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
  return overlapX * overlapY;
}

/** True when two axis-aligned boxes heavily intersect (layout collision). */
export function heavyOverlap(a: BoundingBox, b: BoundingBox, maxRatio = 0.35): boolean {
  const area = overlapArea(a, b);
  if (area <= 0) return false;
  const smaller = Math.min(a.width * a.height, b.width * b.height);
  return smaller > 0 && area >= smaller * maxRatio;
}
