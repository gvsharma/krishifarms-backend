import type { Page } from "@playwright/test";
import type { ValidationIssue, ValidationResult } from "./types";

const MIN_WIDTH = 40;
const MIN_HEIGHT = 32;

export async function validateAllInputs(page: Page): Promise<ValidationResult> {
  const start = Date.now();

  const scan = await page.evaluate(
    ({ minWidth, minHeight }) => {
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

      function getLabel(el: Element): string {
        const aria = el.getAttribute("aria-label");
        if (aria) return aria;
        const root = el.closest(".MuiFormControl-root, .MuiTextField-root");
        const rootLabel = root?.querySelector("label");
        if (rootLabel?.textContent) return rootLabel.textContent.trim();
        const id = el.id;
        if (id) {
          const label = document.querySelector(`label[for="${id}"]`);
          if (label?.textContent) return label.textContent.trim();
        }
        return (el.getAttribute("placeholder") || "").trim().slice(0, 40);
      }

      function measureTarget(el: Element): Element {
        const formControl = el.closest(
          ".MuiFormControl-root, .MuiTextField-root, .MuiAutocomplete-root, fieldset, [class*='Field-root'], [class*='field']",
        );
        if (formControl) return formControl;
        const inputBase = el.closest(".MuiInputBase-root, .MuiSelect-root, [role='combobox']");
        if (inputBase) return inputBase;
        return el;
      }

      function getMeasuredRect(el: Element): DOMRect {
        const target = measureTarget(el);
        const rect = target.getBoundingClientRect();
        if (rect.height >= minHeight) return rect;
        // Include vertical padding from parent form control when MUI reports compact inner height
        const parent = target.parentElement;
        if (parent) {
          const parentRect = parent.getBoundingClientRect();
          if (parentRect.height > rect.height) return parentRect;
        }
        return rect;
      }

      function hasVisibleBorder(el: Element): boolean {
        const targets = [el, measureTarget(el)];
        for (const target of targets) {
          const style = window.getComputedStyle(target);
          if (style.border && style.border !== "none" && style.borderWidth !== "0px") return true;
          if (style.outline && style.outline !== "none" && style.outlineWidth !== "0px") return true;
          if (style.boxShadow && style.boxShadow !== "none") return true;
        }
        return false;
      }

      function isElementCovered(el: Element): boolean {
        const target = measureTarget(el);
        const rect = target.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const top = document.elementFromPoint(cx, cy);
        if (!top) return false;
        return top !== target && !target.contains(top) && !top.contains(target);
      }

      function shouldSkip(el: Element): boolean {
        const cls = (el.className || "").toString();
        if (cls.includes("MuiSelect-nativeInput")) return true;
        if (cls.includes("MuiInputBase-input") && el.closest(".MuiSelect-root")) return true;
        const style = window.getComputedStyle(el);
        if (parseFloat(style.opacity) === 0 && cls.includes("nativeInput")) return true;
        if (el.getAttribute("aria-hidden") === "true") return true;
        if ((el as HTMLInputElement).type === "hidden") return true;
        return false;
      }

      const selector =
        'input:not([type="hidden"]):not([type="submit"]):not([type="button"]), textarea, select, [role="textbox"], [role="combobox"], [role="checkbox"], [role="radio"], [role="switch"]';

      const elements = [...document.querySelectorAll(selector)];
      const seen = new Set<Element>();
      const results: Array<{
        selector: string;
        tag: string;
        role: string | null;
        label: string;
        issues: string[];
        rect: { width: number; height: number };
      }> = [];

      for (const el of elements) {
        if (shouldSkip(el)) continue;

        const target = measureTarget(el);
        if (seen.has(target)) continue;
        seen.add(target);

        const style = window.getComputedStyle(target);
        const rect = getMeasuredRect(el);
        const issues: string[] = [];

        if (style.display === "none") issues.push("display:none");
        if (parseFloat(style.opacity) === 0) issues.push("opacity:0");
        if (style.pointerEvents === "none" && !el.closest(".Mui-disabled")) {
          issues.push("pointer-events:none");
        }
        if (rect.width < minWidth || rect.height < minHeight) {
          issues.push(`size ${Math.round(rect.width)}×${Math.round(rect.height)} < ${minWidth}×${minHeight}`);
        }
        if (!hasVisibleBorder(target)) {
          issues.push("missing visible border/outline");
        }
        if (isElementCovered(el)) issues.push("hidden behind another element");

        const html = target as HTMLElement;
        if (html.scrollWidth > html.clientWidth + 2 || html.scrollHeight > html.clientHeight + 2) {
          const overflow = style.overflow;
          if (["hidden", "clip"].includes(overflow)) {
            issues.push("clipped content");
          }
        }

        if (issues.length > 0) {
          results.push({
            selector: buildSelector(target),
            tag: el.tagName.toLowerCase(),
            role: el.getAttribute("role"),
            label: getLabel(el),
            issues,
            rect: { width: rect.width, height: rect.height },
          });
        }
      }

      return results;
    },
    { minWidth: MIN_WIDTH, minHeight: MIN_HEIGHT },
  );

  const issues: ValidationIssue[] = scan.map((item) => ({
    check: "inputs",
    severity: "error",
    message: `Input "${item.label || item.selector}": ${item.issues.join(", ")}`,
    selector: item.selector,
    details: item as Record<string, unknown>,
  }));

  if (issues.length > 0) {
    console.warn("[validateAllInputs]", issues.map((i) => i.message).join("\n"));
  }

  return {
    check: "inputs",
    passed: issues.length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
