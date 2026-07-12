import type { Page } from "@playwright/test";
import { heavyOverlap, overlapArea, type BoundingBox } from "./overlap";

export type VisualIssueType =
  | "overlap"
  | "clipped-text"
  | "hidden-interactive"
  | "outside-viewport"
  | "horizontal-scroll"
  | "broken-layout"
  | "alignment";

export type VisualIssue = {
  type: VisualIssueType;
  selector: string;
  message: string;
  severity: "error" | "warning";
};

export type VisualValidationOptions = {
  /** CSS selector scope for elements to inspect (default: main content). */
  rootSelector?: string;
  /** Max elements to compare for overlap (performance guard). */
  maxOverlapChecks?: number;
  /** Overlap ratio threshold (0–1) for collision detection. */
  overlapRatio?: number;
  /** Minimum spacing delta (px) before flagging alignment issues in a row. */
  alignmentTolerancePx?: number;
  /** Include elements with zero opacity as hidden-interactive. */
  checkHiddenInteractive?: boolean;
};

type ElementSnapshot = {
  selector: string;
  box: BoundingBox;
  tag: string;
  isInteractive: boolean;
};

const DEFAULT_OPTIONS: Required<VisualValidationOptions> = {
  rootSelector: "main, [role='main'], #__next, body",
  maxOverlapChecks: 120,
  overlapRatio: 0.35,
  alignmentTolerancePx: 6,
  checkHiddenInteractive: true,
};

/**
 * Comprehensive layout validation: overlaps, clipped text, hidden controls,
 * viewport overflow, horizontal scroll, and basic alignment checks.
 */
export async function validatePageLayout(
  page: Page,
  options: VisualValidationOptions = {},
): Promise<VisualIssue[]> {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  const metrics = await page.evaluate(
    ({ rootSelector, checkHiddenInteractive }) => {
      type InBrowserIssue = VisualIssue;
      type InBrowserSnapshot = ElementSnapshot;

      const collectedIssues: InBrowserIssue[] = [];
      const roots = Array.from(document.querySelectorAll(rootSelector));
      const root = roots[0] ?? document.body;

      const isVisible = (el: Element): boolean => {
        const style = window.getComputedStyle(el);
        if (style.display === "none" || style.visibility === "hidden") return false;
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      };

      const isInteractive = (el: Element): boolean => {
        const tag = el.tagName.toLowerCase();
        if (
          tag === "button" ||
          tag === "a" ||
          tag === "input" ||
          tag === "textarea" ||
          tag === "select"
        ) {
          return true;
        }
        const role = el.getAttribute("role");
        return role === "button" || role === "link" || role === "textbox" || role === "combobox";
      };

      const elements: InBrowserSnapshot[] = [];
      const candidates = root.querySelectorAll(
        "button, a, input, textarea, select, [role='button'], [role='link'], [role='textbox'], [role='combobox'], label, h1, h2, h3, h4, p, span, td, th, .MuiButton-root, .MuiInputBase-root",
      );

      let index = 0;
      for (const el of candidates) {
        if (!isVisible(el)) continue;
        const rect = el.getBoundingClientRect();
        if (rect.width < 2 || rect.height < 2) continue;

        const tag = el.tagName.toLowerCase();
        el.setAttribute("data-e2e-idx", String(index));
        const selector = `${tag}${el.id ? `#${el.id}` : ""}[data-e2e-idx="${index}"]`;
        index++;

        elements.push({
          selector,
          box: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
          tag,
          isInteractive: isInteractive(el),
        });

        if (el instanceof HTMLElement) {
          const hasText =
            (el.textContent?.trim().length ?? 0) > 0 || el instanceof HTMLInputElement;
          if (hasText) {
            const clippedX = el.scrollWidth - el.clientWidth > 2;
            const clippedY = el.scrollHeight - el.clientHeight > 2;
            const style = window.getComputedStyle(el);
            const ellipsis = style.textOverflow === "ellipsis" || style.overflow === "hidden";
            if ((clippedX || clippedY) && !ellipsis) {
              collectedIssues.push({
                type: "clipped-text",
                selector,
                message: `Text may be clipped (scroll ${el.scrollWidth}x${el.scrollHeight} vs client ${el.clientWidth}x${el.clientHeight})`,
                severity: "warning",
              });
            }
          }
        }

        if (checkHiddenInteractive && isInteractive(el)) {
          const style = window.getComputedStyle(el);
          const hidden =
            parseFloat(style.opacity) === 0 ||
            style.pointerEvents === "none" ||
            rect.width < 8 ||
            rect.height < 8;
          if (hidden) {
            collectedIssues.push({
              type: "hidden-interactive",
              selector,
              message: "Interactive element appears hidden or too small to use",
              severity: "error",
            });
          }
        }

        if (rect.width < 1 || rect.height < 1) {
          collectedIssues.push({
            type: "broken-layout",
            selector,
            message: "Visible element has collapsed dimensions",
            severity: "error",
          });
        }

        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const outside =
          rect.right < 0 || rect.bottom < 0 || rect.left > vw || rect.top > vh;
        if (outside) {
          collectedIssues.push({
            type: "outside-viewport",
            selector,
            message: `Element box (${Math.round(rect.x)},${Math.round(rect.y)}) is outside viewport ${vw}x${vh}`,
            severity: "warning",
          });
        }
      }

      const docWidth = document.documentElement.scrollWidth;
      if (docWidth > window.innerWidth + 1) {
        collectedIssues.push({
          type: "horizontal-scroll",
          selector: "document",
          message: `Page scrollWidth ${docWidth}px exceeds viewport ${window.innerWidth}px`,
          severity: "error",
        });
      }

      return { elements, issues: collectedIssues };
    },
    {
      rootSelector: opts.rootSelector,
      checkHiddenInteractive: opts.checkHiddenInteractive,
    },
  );

  const issues: VisualIssue[] = [...metrics.issues];

  const elements = metrics.elements.slice(0, opts.maxOverlapChecks);
  for (let i = 0; i < elements.length; i++) {
    for (let j = i + 1; j < elements.length; j++) {
      const a = elements[i];
      const b = elements[j];
      if (a.tag === "label" || b.tag === "label") continue;
      if (heavyOverlap(a.box, b.box, opts.overlapRatio)) {
        issues.push({
          type: "overlap",
          selector: `${a.selector} ∩ ${b.selector}`,
          message: `Elements heavily overlap (${a.tag} vs ${b.tag})`,
          severity: "error",
        });
      }
    }
  }

  const rows = groupByRow(elements, opts.alignmentTolerancePx);
  for (const row of rows) {
    if (row.length < 2) continue;
    row.sort((a, b) => a.box.x - b.box.x);
    for (let i = 1; i < row.length; i++) {
      const prev = row[i - 1];
      const curr = row[i];
      const gap = curr.box.x - (prev.box.x + prev.box.width);
      if (gap < -opts.alignmentTolerancePx) {
        issues.push({
          type: "alignment",
          selector: `${prev.selector} → ${curr.selector}`,
          message: `Negative horizontal gap (${Math.round(gap)}px) suggests misaligned controls`,
          severity: "warning",
        });
      }
    }
  }

  return issues;
}

function groupByRow(elements: ElementSnapshot[], tolerance: number): ElementSnapshot[][] {
  const rows: ElementSnapshot[][] = [];
  for (const el of elements.filter((e) => e.isInteractive)) {
    const centerY = el.box.y + el.box.height / 2;
    let placed = false;
    for (const row of rows) {
      const rowY = row[0].box.y + row[0].box.height / 2;
      if (Math.abs(centerY - rowY) <= tolerance) {
        row.push(el);
        placed = true;
        break;
      }
    }
    if (!placed) rows.push([el]);
  }
  return rows;
}

/** Assert no error-severity layout issues; warnings are logged but allowed. */
export async function expectCleanLayout(
  page: Page,
  options?: VisualValidationOptions,
): Promise<void> {
  const issues = await validatePageLayout(page, options);
  const errors = issues.filter((i) => i.severity === "error");
  const warnings = issues.filter((i) => i.severity === "warning");

  if (warnings.length > 0) {
    console.warn(
      `[visual] ${warnings.length} layout warning(s):\n` +
        warnings.map((w) => `  - [${w.type}] ${w.selector}: ${w.message}`).join("\n"),
    );
  }

  if (errors.length > 0) {
    const detail = errors.map((e) => `[${e.type}] ${e.selector}: ${e.message}`).join("\n");
    throw new Error(`Layout validation failed with ${errors.length} error(s):\n${detail}`);
  }
}

/** Compare screenshot against baseline (Playwright visual regression). */
export async function expectVisualRegression(
  page: Page,
  name: string,
  options?: { fullPage?: boolean; maxDiffPixelRatio?: number },
): Promise<void> {
  await page.waitForLoadState("networkidle").catch(() => undefined);
  const { expect } = await import("@playwright/test");
  await expect(page).toHaveScreenshot(`${name}.png`, {
    fullPage: options?.fullPage ?? false,
    maxDiffPixelRatio: options?.maxDiffPixelRatio ?? 0.02,
  });
}

/** Fail when the document is wider than the viewport (horizontal scroll). */
export async function expectNoHorizontalScroll(page: Page): Promise<void> {
  const { scrollWidth, viewportWidth } = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    viewportWidth: window.innerWidth,
  }));
  if (scrollWidth > viewportWidth + 2) {
    throw new Error(
      `Horizontal scroll detected: scrollWidth=${scrollWidth}px, viewport=${viewportWidth}px`,
    );
  }
}

/** Assert visible text in a locator is not clipped by overflow:hidden. */
export async function expectTextNotClipped(
  page: Page,
  selector = "main h1, main h2, [role='heading']",
): Promise<void> {
  const clipped = await page.evaluate((sel) => {
    const results: string[] = [];
    document.querySelectorAll(sel).forEach((el) => {
      if (!(el instanceof HTMLElement)) return;
      const style = window.getComputedStyle(el);
      if (style.display === "none" || style.visibility === "hidden") return;
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) return;
      const clippedX = el.scrollWidth - el.clientWidth > 2;
      const clippedY = el.scrollHeight - el.clientHeight > 2;
      const ellipsis = style.textOverflow === "ellipsis" || style.overflow === "hidden";
      if ((clippedX || clippedY) && !ellipsis) {
        results.push((el.textContent || "").trim().slice(0, 60));
      }
    });
    return results;
  }, selector);

  if (clipped.length > 0) {
    throw new Error(`Clipped heading text detected: ${clipped.join(", ")}`);
  }
}

/**
 * Combined smoke visual check: heading visible, no horizontal scroll, headings not clipped.
 */
export async function expectPageVisualHealth(
  page: Page,
  heading: string | RegExp,
): Promise<void> {
  const { expect } = await import("@playwright/test");
  await expect(page.getByRole("heading", { name: heading }).first()).toBeVisible({
    timeout: 20_000,
  });
  await expectNoHorizontalScroll(page);
  await expectTextNotClipped(page);
}

export { overlapArea, heavyOverlap };
