/** In-browser helpers injected via page.evaluate(). */

export type ElementRect = {
  tag: string;
  role: string | null;
  id: string | null;
  className: string | null;
  text: string;
  selector: string;
  rect: { x: number; y: number; width: number; height: number };
  isInteractive: boolean;
};

export type LayoutScanResult = {
  horizontalScroll: boolean;
  scrollWidth: number;
  viewportWidth: number;
  overlaps: Array<{ a: string; b: string; area: number }>;
  clipped: Array<{ selector: string; axis: "x" | "y" | "both" }>;
  outsideViewport: Array<{ selector: string; rect: ElementRect["rect"] }>;
  zeroSizeInputs: Array<{ selector: string; tag: string }>;
};

export type InputScanResult = {
  selector: string;
  tag: string;
  role: string | null;
  label: string;
  issues: string[];
  rect: { width: number; height: number };
};

export type ButtonScanResult = {
  selector: string;
  text: string;
  issues: string[];
  rect: { width: number; height: number };
};

export type TypographySample = {
  selector: string;
  text: string;
  fontFamily: string;
  fontSize: string;
  fontWeight: string;
  lineHeight: string;
};

export type ContrastSample = {
  selector: string;
  text: string;
  foreground: string;
  background: string;
  ratio: number;
  passesAA: boolean;
};

export type CssViolation = {
  selector: string;
  property: string;
  value: string;
  message: string;
};

export type PerformanceMetrics = {
  loadTimeMs: number;
  cls: number;
  brokenImages: string[];
  slowResources: Array<{ url: string; durationMs: number }>;
};

/** Build a short CSS selector for reporting. */
export function buildSelector(el: Element): string {
  const id = el.id ? `#${el.id}` : "";
  const role = el.getAttribute("role");
  const tag = el.tagName.toLowerCase();
  const testId = el.getAttribute("data-testid");
  if (testId) return `[data-testid="${testId}"]`;
  if (id) return id;
  if (role) return `${tag}[role="${role}"]`;
  const cls = (el.className || "").toString().split(/\s+/).filter(Boolean)[0];
  return cls ? `${tag}.${cls}` : tag;
}

export function isVisible(el: Element): boolean {
  const style = window.getComputedStyle(el);
  if (style.display === "none" || style.visibility === "hidden") return false;
  if (parseFloat(style.opacity) === 0) return false;
  const rect = el.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0;
}

export function isAncestor(a: Element, b: Element): boolean {
  return a.contains(b) || b.contains(a);
}

export function overlapArea(
  a: { x: number; y: number; width: number; height: number },
  b: { x: number; y: number; width: number; height: number },
): number {
  const overlapX = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x));
  const overlapY = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
  return overlapX * overlapY;
}

export function relativeLuminance(rgb: [number, number, number]): number {
  const [r, g, b] = rgb.map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

export function parseColor(color: string): [number, number, number] | null {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 1;
  const ctx = canvas.getContext("2d");
  if (!ctx) return null;
  ctx.fillStyle = color;
  ctx.fillRect(0, 0, 1, 1);
  const data = ctx.getImageData(0, 0, 1, 1).data;
  return [data[0], data[1], data[2]];
}

export function contrastRatio(fg: string, bg: string): number {
  const fgRgb = parseColor(fg);
  const bgRgb = parseColor(bg);
  if (!fgRgb || !bgRgb) return 0;
  const l1 = relativeLuminance(fgRgb);
  const l2 = relativeLuminance(bgRgb);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

export function getEffectiveBackground(el: Element): string {
  let current: Element | null = el;
  while (current) {
    const bg = window.getComputedStyle(current).backgroundColor;
    if (bg && bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent") return bg;
    current = current.parentElement;
  }
  return "rgb(255, 255, 255)";
}

export function isElementCovered(el: Element): boolean {
  const rect = el.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;
  const top = document.elementFromPoint(cx, cy);
  if (!top) return false;
  return top !== el && !el.contains(top) && !top.contains(el);
}
