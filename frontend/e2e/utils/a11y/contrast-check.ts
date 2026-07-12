import type { Page } from "@playwright/test";
import type { ValidationIssue, ValidationResult } from "../validation/types";

const MIN_AA_RATIO = 4.5;
const MIN_AA_LARGE_RATIO = 3;

export async function validateColorContrast(page: Page): Promise<ValidationResult> {
  const start = Date.now();

  const samples = await page.evaluate(
    ({ minAA, minAALarge }) => {
      function parseColor(color: string): [number, number, number] | null {
        const canvas = document.createElement("canvas");
        canvas.width = canvas.height = 1;
        const ctx = canvas.getContext("2d");
        if (!ctx) return null;
        ctx.fillStyle = color;
        ctx.fillRect(0, 0, 1, 1);
        const data = ctx.getImageData(0, 0, 1, 1).data;
        return [data[0], data[1], data[2]];
      }

      function relativeLuminance(rgb: [number, number, number]): number {
        const [r, g, b] = rgb.map((c) => {
          const s = c / 255;
          return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
        });
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
      }

      function contrastRatio(fg: string, bg: string): number {
        const fgRgb = parseColor(fg);
        const bgRgb = parseColor(bg);
        if (!fgRgb || !bgRgb) return 0;
        const l1 = relativeLuminance(fgRgb);
        const l2 = relativeLuminance(bgRgb);
        const lighter = Math.max(l1, l2);
        const darker = Math.min(l1, l2);
        return (lighter + 0.05) / (darker + 0.05);
      }

      function getEffectiveBackground(el: Element): string {
        let current: Element | null = el;
        while (current) {
          const bg = window.getComputedStyle(current).backgroundColor;
          if (bg && bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent") return bg;
          current = current.parentElement;
        }
        return "rgb(255, 255, 255)";
      }

      function buildSelector(el: Element): string {
        const tag = el.tagName.toLowerCase();
        const id = el.id ? `#${el.id}` : "";
        if (id) return id;
        return tag;
      }

      const targets = [
        ...document.querySelectorAll("p, span, label, button, a, h1, h2, h3, th, td, input, textarea"),
      ].filter((el) => (el.textContent || "").trim().length > 0 || el.tagName === "INPUT");

      const results: Array<{
        selector: string;
        text: string;
        foreground: string;
        background: string;
        ratio: number;
        passesAA: boolean;
      }> = [];

      for (const el of targets.slice(0, 40)) {
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) continue;

        const fg = style.color;
        const bg = getEffectiveBackground(el);
        const ratio = contrastRatio(fg, bg);
        const fontSize = parseFloat(style.fontSize);
        const isLarge = fontSize >= 18 || (fontSize >= 14 && parseInt(style.fontWeight, 10) >= 700);
        const required = isLarge ? minAALarge : minAA;
        const passesAA = ratio >= required;

        if (!passesAA) {
          results.push({
            selector: buildSelector(el),
            text: (el.textContent || "").trim().slice(0, 40),
            foreground: fg,
            background: bg,
            ratio: Math.round(ratio * 100) / 100,
            passesAA,
          });
        }
      }

      return results;
    },
    { minAA: MIN_AA_RATIO, minAALarge: MIN_AA_LARGE_RATIO },
  );

  const issues: ValidationIssue[] = samples.map((s) => ({
    check: "contrast",
    severity: "error",
    message: `WCAG AA contrast ${s.ratio}:1 on "${s.text}" (fg=${s.foreground}, bg=${s.background})`,
    selector: s.selector,
    details: s as Record<string, unknown>,
  }));

  if (issues.length > 0) {
    console.warn("[validateColorContrast]", issues.map((i) => i.message).join("\n"));
  }

  return {
    check: "contrast",
    passed: issues.length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
