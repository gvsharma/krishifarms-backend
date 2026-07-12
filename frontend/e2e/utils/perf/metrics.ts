import type { Page } from "@playwright/test";
import { getValidationContext } from "../validation/context";
import type { ValidationIssue, ValidationResult } from "../validation/types";

export interface PerformanceThresholds {
  maxLoadMs?: number;
  maxCls?: number;
  maxSlowApiMs?: number;
}

const DEFAULT_THRESHOLDS: Required<PerformanceThresholds> = {
  maxLoadMs: 8000,
  maxCls: 0.25,
  maxSlowApiMs: 3000,
};

export async function validatePerformance(
  page: Page,
  thresholds: PerformanceThresholds = {},
): Promise<ValidationResult> {
  const start = Date.now();
  const limits = { ...DEFAULT_THRESHOLDS, ...thresholds };
  const issues: ValidationIssue[] = [];

  const metrics = await page.evaluate(() => {
    const nav = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
    const loadTimeMs = nav ? nav.loadEventEnd - nav.startTime : 0;

    let cls = 0;
    for (const entry of performance.getEntriesByType("layout-shift")) {
      const ls = entry as PerformanceEntry & { value?: number; hadRecentInput?: boolean };
      if (!ls.hadRecentInput && ls.value) cls += ls.value;
    }

    const brokenImages: string[] = [];
    for (const img of document.querySelectorAll("img")) {
      if (img.naturalWidth === 0 && img.src) brokenImages.push(img.src);
    }

    const slowResources = performance
      .getEntriesByType("resource")
      .filter((r) => r.duration > 3000)
      .map((r) => ({ url: r.name, durationMs: Math.round(r.duration) }));

    return { loadTimeMs: Math.round(loadTimeMs), cls, brokenImages, slowResources };
  });

  const ctx = getValidationContext(page);

  if (metrics.loadTimeMs > limits.maxLoadMs) {
    issues.push({
      check: "performance",
      severity: "warning",
      message: `Load time ${metrics.loadTimeMs}ms exceeds ${limits.maxLoadMs}ms`,
      details: { loadTimeMs: metrics.loadTimeMs },
    });
  }

  if (metrics.cls > limits.maxCls) {
    issues.push({
      check: "performance",
      severity: "warning",
      message: `CLS ${metrics.cls.toFixed(3)} exceeds ${limits.maxCls}`,
      details: { cls: metrics.cls },
    });
  }

  for (const img of metrics.brokenImages) {
    issues.push({
      check: "performance",
      severity: "error",
      message: `Broken image: ${img}`,
    });
  }

  for (const req of ctx.slowRequests.filter((r) => r.durationMs > limits.maxSlowApiMs)) {
    issues.push({
      check: "performance",
      severity: "warning",
      message: `Slow API ${req.url} (${Math.round(req.durationMs)}ms)`,
      details: req as Record<string, unknown>,
    });
  }

  if (issues.length > 0) {
    console.warn("[validatePerformance]", issues.map((i) => i.message).join("\n"));
  }

  return {
    check: "performance",
    passed: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
