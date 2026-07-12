import type { Page } from "@playwright/test";
import type { ValidationIssue, ValidationResult } from "./types";

export async function validateAllButtons(page: Page): Promise<ValidationResult> {
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

    function isElementCovered(el: Element): boolean {
      const rect = el.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const top = document.elementFromPoint(cx, cy);
      if (!top) return false;
      return top !== el && !el.contains(top) && !top.contains(el);
    }

    const buttons = [
      ...document.querySelectorAll('button, [role="button"], input[type="submit"], input[type="button"]'),
    ];

    const results: Array<{
      selector: string;
      text: string;
      issues: string[];
      rect: { width: number; height: number };
    }> = [];

    for (const el of buttons) {
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      const issues: string[] = [];
      const text = (el.textContent || el.getAttribute("aria-label") || "").trim().slice(0, 50);

      if (style.display === "none") issues.push("display:none");
      if (style.visibility === "hidden") issues.push("visibility:hidden");
      if (parseFloat(style.opacity) === 0) issues.push("opacity:0");
      if (style.pointerEvents === "none") issues.push("pointer-events:none");
      if (rect.width < 32 || rect.height < 28) {
        issues.push(`size ${Math.round(rect.width)}×${Math.round(rect.height)} too small`);
      }
      if (isElementCovered(el)) issues.push("not clickable (covered)");
      if ((el as HTMLButtonElement).disabled) issues.push("disabled");

      const html = el as HTMLElement;
      if (html.scrollWidth > html.clientWidth + 2) {
        issues.push("text clipped horizontally");
      }

      const icon = el.querySelector("svg, img, [class*='icon']");
      if (icon && text) {
        const iconRect = icon.getBoundingClientRect();
        const textNodes = [...el.childNodes].filter((n) => n.nodeType === Node.TEXT_NODE && n.textContent?.trim());
        if (textNodes.length > 0 && iconRect.width > 0) {
          const textEl = el;
          const textRect = textEl.getBoundingClientRect();
          if (Math.abs(iconRect.top - textRect.top) > 12) {
            issues.push("icon/text vertical misalignment");
          }
        }
      }

      if (issues.length > 0) {
        results.push({
          selector: buildSelector(el),
          text,
          issues,
          rect: { width: rect.width, height: rect.height },
        });
      }
    }

    return results;
  });

  const issues: ValidationIssue[] = scan
    .filter((b) => !b.issues.includes("disabled"))
    .map((item) => ({
      check: "buttons",
      severity: item.issues.some((i) => i.includes("covered") || i.includes("clipped")) ? "error" : "warning",
      message: `Button "${item.text || item.selector}": ${item.issues.join(", ")}`,
      selector: item.selector,
      details: item as Record<string, unknown>,
    }));

  if (issues.length > 0) {
    console.warn("[validateAllButtons]", issues.map((i) => i.message).join("\n"));
  }

  return {
    check: "buttons",
    passed: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
