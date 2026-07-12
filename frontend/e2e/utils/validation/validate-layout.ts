import type { Page } from "@playwright/test";
import type { LayoutScanResult } from "./browser-scripts";
import type { ValidationIssue, ValidationResult } from "./types";

export async function validateLayout(page: Page): Promise<ValidationResult> {
  const start = Date.now();
  const scan = await page.evaluate(() => {
    function buildSelector(el: Element): string {
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

    function isVisible(el: Element): boolean {
      // Modal underlays / decorative icons — not interactive layout defects
      if (el.closest('[aria-hidden="true"]')) return false;
      const style = window.getComputedStyle(el);
      if (style.display === "none" || style.visibility === "hidden") return false;
      if (parseFloat(style.opacity) === 0) return false;
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    }

    function overlapArea(
      a: { x: number; y: number; width: number; height: number },
      b: { x: number; y: number; width: number; height: number },
    ): number {
      const overlapX = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x));
      const overlapY = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
      return overlapX * overlapY;
    }

    function isFormLabelPair(aEl: Element, bEl: Element): boolean {
      if (aEl.tagName === "LABEL" || bEl.tagName === "LABEL") return true;
      const aId = aEl.id || "";
      const bId = bEl.id || "";
      if (aId.endsWith("-label") && bId === aId.replace(/-label$/, "")) return true;
      if (bId.endsWith("-label") && aId === bId.replace(/-label$/, "")) return true;
      const aFor = aEl.getAttribute("for");
      const bFor = bEl.getAttribute("for");
      if (aFor && bId === aFor) return true;
      if (bFor && aId === bFor) return true;
      // MUI: label + input share FormControl wrapper
      const aRoot = aEl.closest(".MuiFormControl-root, .MuiTextField-root, label, [class*='Field']");
      const bRoot = bEl.closest(".MuiFormControl-root, .MuiTextField-root, label, [class*='Field']");
      if (aRoot && bRoot && aRoot === bRoot) return true;
      return false;
    }

    /** Show/hide password controls intentionally sit inside the field hit area. */
    function isPasswordToggleOverlap(aEl: Element, bEl: Element): boolean {
      const toggleOf = (el: Element): Element | null => {
        const btn =
          el.closest("button, [role='button']") ||
          (el.tagName === "BUTTON" || el.getAttribute("role") === "button" ? el : null);
        if (!btn) return null;
        const label = (btn.getAttribute("aria-label") || "").toLowerCase();
        if (label.includes("password")) return btn;
        // Absolute adornment inside a relative field wrapper (premium Input)
        if (
          (btn.classList.contains("absolute") ||
            (typeof btn.className === "string" && btn.className.includes("absolute"))) &&
          btn.closest(".relative, [class*='relative']")
        ) {
          return btn;
        }
        return null;
      };
      const inputOf = (el: Element): Element | null => {
        if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") return el;
        if (el.getAttribute("role") === "textbox") return el;
        return null;
      };

      const toggle = toggleOf(aEl) || toggleOf(bEl);
      const input = inputOf(aEl) || inputOf(bEl);
      if (!toggle || !input) return false;
      if (toggleOf(aEl) && toggleOf(bEl)) return false;
      if (inputOf(aEl) && inputOf(bEl)) return false;

      const wrap =
        input.closest(
          ".relative, .MuiInputAdornment-root, .MuiInputBase-root, [class*='items-center']",
        ) || input.parentElement;
      return Boolean(wrap && wrap.contains(toggle));
    }

    /** Dialog overlays page content — cross-layer boxes are expected, not defects. */
    function isCrossDialogLayerOverlap(aEl: Element, bEl: Element): boolean {
      const aInDialog = Boolean(aEl.closest('[role="dialog"]'));
      const bInDialog = Boolean(bEl.closest('[role="dialog"]'));
      return aInDialog !== bInDialog;
    }

    const interactiveSelector =
      'button, a[href], input, textarea, select, [role="button"], [role="link"], [role="textbox"], [role="combobox"], h1, h2, h3, nav, header, aside, th, td, [data-testid]';

    const elements = [...document.querySelectorAll(interactiveSelector)].filter(isVisible);
    const boxes = elements.map((el) => {
      const rect = el.getBoundingClientRect();
      return {
        selector: buildSelector(el),
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        el,
      };
    });

    const overlaps: LayoutScanResult["overlaps"] = [];
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i];
        const b = boxes[j];
        if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
        if (isFormLabelPair(a.el, b.el)) continue;
        if (isPasswordToggleOverlap(a.el, b.el)) continue;
        if (isCrossDialogLayerOverlap(a.el, b.el)) continue;
        const area = overlapArea(a.rect, b.rect);
        if (area <= 0) continue;
        const smaller = Math.min(a.rect.width * a.rect.height, b.rect.width * b.rect.height);
        if (smaller > 0 && area >= smaller * 0.35) {
          overlaps.push({ a: a.selector, b: b.selector, area });
        }
      }
    }

    const clipped: LayoutScanResult["clipped"] = [];
    for (const el of elements) {
      const style = window.getComputedStyle(el);
      if (!["hidden", "clip"].includes(style.overflow) && style.textOverflow !== "ellipsis") continue;
      const html = el as HTMLElement;
      if (html.scrollWidth > html.clientWidth + 2) {
        clipped.push({ selector: buildSelector(el), axis: "x" });
      }
      if (html.scrollHeight > html.clientHeight + 2) {
        clipped.push({ selector: buildSelector(el), axis: "y" });
      }
    }

    const outsideViewport: LayoutScanResult["outsideViewport"] = [];
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    for (const box of boxes) {
      const { rect } = box;
      if (rect.x + rect.width < 0 || rect.y + rect.height < 0 || rect.x > vw || rect.y > vh) {
        outsideViewport.push({ selector: box.selector, rect: box.rect });
      }
    }

    const zeroSizeInputs: LayoutScanResult["zeroSizeInputs"] = [];
    const inputs = [...document.querySelectorAll("input, textarea, select, [role='textbox'], [role='combobox']")];
    for (const input of inputs) {
      if (!isVisible(input)) continue;
      const rect = input.getBoundingClientRect();
      if (rect.width < 2 || rect.height < 2) {
        zeroSizeInputs.push({ selector: buildSelector(input), tag: input.tagName.toLowerCase() });
      }
    }

    const scrollWidth = document.documentElement.scrollWidth;
    const viewportWidth = window.innerWidth;

    return {
      horizontalScroll: scrollWidth > viewportWidth + 2,
      scrollWidth,
      viewportWidth,
      overlaps: overlaps.slice(0, 20),
      clipped: clipped.slice(0, 20),
      outsideViewport: outsideViewport.slice(0, 20),
      zeroSizeInputs,
    } satisfies LayoutScanResult;
  });

  const issues: ValidationIssue[] = [];

  if (scan.horizontalScroll) {
    issues.push({
      check: "layout",
      severity: "error",
      message: `Horizontal scroll detected (scrollWidth=${scan.scrollWidth}, viewport=${scan.viewportWidth})`,
    });
  }

  for (const overlap of scan.overlaps) {
    issues.push({
      check: "layout",
      severity: "error",
      message: `Elements overlap: "${overlap.a}" and "${overlap.b}" (area=${Math.round(overlap.area)}px²)`,
      details: overlap,
    });
  }

  for (const clip of scan.clipped) {
    issues.push({
      check: "layout",
      severity: "warning",
      message: `Clipped content on ${clip.selector} (axis=${clip.axis})`,
      selector: clip.selector,
    });
  }

    for (const outside of scan.outsideViewport) {
      // Table rows/cells scroll inside containers — not a page-level defect
      if (outside.selector.includes("td") || outside.selector.includes("role=\"row\"")) continue;
      issues.push({
        check: "layout",
        severity: "warning",
        message: `Element outside viewport: ${outside.selector}`,
        selector: outside.selector,
      });
    }

  for (const input of scan.zeroSizeInputs) {
    issues.push({
      check: "layout",
      severity: "error",
      message: `Zero-size input: ${input.selector}`,
      selector: input.selector,
    });
  }

  if (issues.length > 0) {
    console.warn("[validateLayout]", issues.map((i) => i.message).join("\n"));
  }

  return {
    check: "layout",
    passed: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
