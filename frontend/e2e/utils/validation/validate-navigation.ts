import type { Page } from "@playwright/test";
import type { ValidationIssue, ValidationResult } from "./types";

export async function validateNavigation(page: Page): Promise<ValidationResult> {
  const start = Date.now();
  const issues: ValidationIssue[] = [];

  const scan = await page.evaluate(() => {
    function buildSelector(el: Element): string {
      const tag = el.tagName.toLowerCase();
      const role = el.getAttribute("role");
      const aria = el.getAttribute("aria-label");
      if (aria) return `${tag}[aria-label="${aria}"]`;
      if (role) return `${tag}[role="${role}"]`;
      return tag;
    }

    function overlapArea(
      a: { x: number; y: number; width: number; height: number },
      b: { x: number; y: number; width: number; height: number },
    ): number {
      const overlapX = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x));
      const overlapY = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
      return overlapX * overlapY;
    }

    const navParts = [
      ...document.querySelectorAll('nav, aside, header, [role="navigation"], [role="banner"], [aria-label*="breadcrumb" i]'),
    ];

    const boxes = navParts
      .filter((el) => {
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      })
      .map((el) => {
        const rect = el.getBoundingClientRect();
        return { selector: buildSelector(el), rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height } };
      });

    const overlaps: Array<{ a: string; b: string }> = [];
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const area = overlapArea(boxes[i].rect, boxes[j].rect);
        const smaller = Math.min(
          boxes[i].rect.width * boxes[i].rect.height,
          boxes[j].rect.width * boxes[j].rect.height,
        );
        if (smaller > 0 && area >= smaller * 0.4) {
          overlaps.push({ a: boxes[i].selector, b: boxes[j].selector });
        }
      }
    }

    const hasSidebar = Boolean(document.querySelector('aside, nav[aria-label*="sidebar" i], [class*="sidebar"]'));
    const hasHeader = Boolean(document.querySelector('header, [role="banner"]'));
    const hasBreadcrumb = Boolean(
      document.querySelector('[aria-label*="breadcrumb" i], nav[aria-label*="Breadcrumb" i], .MuiBreadcrumbs-root'),
    );

    return { overlaps, hasSidebar, hasHeader, hasBreadcrumb };
  });

  for (const overlap of scan.overlaps) {
    issues.push({
      check: "navigation",
      severity: "error",
      message: `Navigation overlap: "${overlap.a}" and "${overlap.b}"`,
    });
  }

  if (!scan.hasHeader) {
    issues.push({
      check: "navigation",
      severity: "warning",
      message: "No header/banner landmark detected",
    });
  }

  return {
    check: "navigation",
    passed: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
