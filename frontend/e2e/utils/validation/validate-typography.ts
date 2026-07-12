import type { Page } from "@playwright/test";
import type { ValidationIssue, ValidationResult } from "./types";

export async function validateTypography(page: Page): Promise<ValidationResult> {
  const start = Date.now();

  const samples = await page.evaluate(() => {
    function buildSelector(el: Element): string {
      const tag = el.tagName.toLowerCase();
      const id = el.id ? `#${el.id}` : "";
      if (id) return id;
      return tag;
    }

    const targets = [...document.querySelectorAll("h1, h2, h3, h4, p, label, button, th, td, a")].filter(
      (el) => {
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0 && (el.textContent || "").trim().length > 0;
      },
    );

    return targets.slice(0, 30).map((el) => {
      const style = window.getComputedStyle(el);
      return {
        selector: buildSelector(el),
        text: (el.textContent || "").trim().slice(0, 40),
        fontFamily: style.fontFamily,
        fontSize: style.fontSize,
        fontWeight: style.fontWeight,
        lineHeight: style.lineHeight,
      };
    });
  });

  const issues: ValidationIssue[] = [];

  for (const sample of samples) {
    const fontSize = parseFloat(sample.fontSize);
    if (fontSize < 10) {
      issues.push({
        check: "typography",
        severity: "warning",
        message: `Font size ${sample.fontSize} too small on "${sample.text}" (${sample.selector})`,
        selector: sample.selector,
      });
    }
    if (sample.fontFamily.includes("monospace") && !sample.selector.startsWith("code")) {
      issues.push({
        check: "typography",
        severity: "info",
        message: `Unexpected monospace on "${sample.text}"`,
        selector: sample.selector,
      });
    }
    const lineHeight = parseFloat(sample.lineHeight);
    if (!Number.isNaN(lineHeight) && lineHeight < 1.1) {
      issues.push({
        check: "typography",
        severity: "warning",
        message: `Tight line-height ${sample.lineHeight} on "${sample.text}"`,
        selector: sample.selector,
      });
    }
  }

  return {
    check: "typography",
    passed: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
