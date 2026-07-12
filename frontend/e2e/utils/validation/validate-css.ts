import type { Page } from "@playwright/test";
import type { ValidationIssue, ValidationResult } from "./types";

export async function validateCSS(page: Page): Promise<ValidationResult> {
  const start = Date.now();

  const violations = await page.evaluate(() => {
    function buildSelector(el: Element): string {
      const tag = el.tagName.toLowerCase();
      const id = el.id ? `#${el.id}` : "";
      if (id) return id;
      const cls = (el.className || "").toString().split(/\s+/).filter(Boolean)[0];
      return cls ? `${tag}.${cls}` : tag;
    }

    const targets = [
      ...document.querySelectorAll("button, input, textarea, select, [role='button'], .MuiCard-root, .MuiPaper-root, nav, header, aside"),
    ];

    const results: Array<{ selector: string; property: string; value: string; message: string }> = [];

    for (const el of targets.slice(0, 50)) {
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) continue;

      const opacity = parseFloat(style.opacity);
      if (opacity < 0.4) {
        results.push({
          selector: buildSelector(el),
          property: "opacity",
          value: style.opacity,
          message: "Opacity below 0.4 may reduce usability",
        });
      }

      const zIndex = style.zIndex;
      if (zIndex !== "auto" && parseInt(zIndex, 10) > 9999) {
        results.push({
          selector: buildSelector(el),
          property: "z-index",
          value: zIndex,
          message: "Extremely high z-index",
        });
      }

      const padding = parseFloat(style.paddingTop) + parseFloat(style.paddingBottom);
      if (el.tagName === "BUTTON" && padding < 4) {
        results.push({
          selector: buildSelector(el),
          property: "padding",
          value: style.padding,
          message: "Button vertical padding too tight",
        });
      }

      const borderRadius = style.borderRadius;
      if (el.tagName === "BUTTON" && borderRadius === "0px") {
        results.push({
          selector: buildSelector(el),
          property: "border-radius",
          value: borderRadius,
          message: "Button has no border radius",
        });
      }
    }

    return results;
  });

  const issues: ValidationIssue[] = violations.map((v) => ({
    check: "css",
    severity: v.property === "opacity" ? "warning" : "info",
    message: `${v.message} (${v.property}=${v.value}) on ${v.selector}`,
    selector: v.selector,
    details: v as Record<string, unknown>,
  }));

  return {
    check: "css",
    passed: true,
    issues,
    durationMs: Date.now() - start,
  };
}
