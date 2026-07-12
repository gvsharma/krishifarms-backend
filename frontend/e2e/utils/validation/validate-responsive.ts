import type { Page } from "@playwright/test";
import { VIEWPORTS, type ViewportPreset } from "../viewports";
import { validateLayout } from "./validate-layout";
import { validateNavigation } from "./validate-navigation";
import type { ValidationIssue, ValidationResult } from "./types";

export async function validateResponsive(
  page: Page,
  viewports: ViewportPreset[] = ["desktop", "laptop", "tablet", "mobilePortrait", "mobileLandscape"],
): Promise<ValidationResult> {
  const start = Date.now();
  const issues: ValidationIssue[] = [];
  const original = page.viewportSize();

  for (const preset of viewports) {
    const size = VIEWPORTS[preset];
    await page.setViewportSize(size);

    const layout = await validateLayout(page);
    for (const issue of layout.issues.filter((i) => i.severity === "error")) {
      issues.push({
        ...issue,
        message: `[${preset}] ${issue.message}`,
        details: { ...issue.details, viewport: preset },
      });
    }

    const nav = await validateNavigation(page);
    for (const issue of nav.issues.filter((i) => i.severity === "error")) {
      issues.push({
        ...issue,
        message: `[${preset}] ${issue.message}`,
        details: { ...issue.details, viewport: preset },
      });
    }
  }

  if (original) {
    await page.setViewportSize(original);
  }

  return {
    check: "responsive",
    passed: issues.length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
