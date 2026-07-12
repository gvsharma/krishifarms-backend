import type { Page } from "@playwright/test";

export type PerformanceMetrics = {
  /** Time to first contentful paint (ms). */
  fcp: number | null;
  /** Largest contentful paint (ms). */
  lcp: number | null;
  /** DOM content loaded (ms since navigation start). */
  domContentLoaded: number | null;
  /** Full load event (ms since navigation start). */
  loadEvent: number | null;
  /** Total navigation duration (ms). */
  loadTime: number | null;
};

/**
 * Collect Web Vitals-style metrics after navigation.
 * Call after `page.goto()` once the page has settled.
 */
export async function measurePerformance(page: Page): Promise<PerformanceMetrics> {
  return page.evaluate(async () => {
    const nav = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;

    const paintEntries = performance.getEntriesByType("paint");
    const fcpEntry = paintEntries.find((e) => e.name === "first-contentful-paint");

    let lcp: number | null = null;
    try {
      lcp = await new Promise<number | null>((resolve) => {
        let value: number | null = null;
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const last = entries[entries.length - 1];
          if (last) value = last.startTime;
        });
        observer.observe({ type: "largest-contentful-paint", buffered: true });
        setTimeout(() => {
          observer.disconnect();
          resolve(value);
        }, 500);
      });
    } catch {
      lcp = null;
    }

    return {
      fcp: fcpEntry ? fcpEntry.startTime : null,
      lcp,
      domContentLoaded: nav ? nav.domContentLoadedEventEnd - nav.startTime : null,
      loadEvent: nav ? nav.loadEventEnd - nav.startTime : null,
      loadTime: nav ? nav.duration : null,
    };
  });
}

/** Assert performance budgets (soft thresholds for smoke tests). */
export function assertPerformanceBudgets(
  metrics: PerformanceMetrics,
  budgets: Partial<{ fcp: number; lcp: number; loadTime: number }> = {},
): void {
  const defaults = { fcp: 3000, lcp: 4000, loadTime: 8000 };
  const limits = { ...defaults, ...budgets };

  if (metrics.fcp != null && metrics.fcp > limits.fcp) {
    throw new Error(`FCP ${Math.round(metrics.fcp)}ms exceeds budget ${limits.fcp}ms`);
  }
  if (metrics.lcp != null && metrics.lcp > limits.lcp) {
    throw new Error(`LCP ${Math.round(metrics.lcp)}ms exceeds budget ${limits.lcp}ms`);
  }
  if (metrics.loadTime != null && metrics.loadTime > limits.loadTime) {
    throw new Error(`Load time ${Math.round(metrics.loadTime)}ms exceeds budget ${limits.loadTime}ms`);
  }
}
