import { expect, type Page } from "@playwright/test";
import type { ValidationIssue, ValidationResult } from "./types";

export async function validateDialogs(page: Page): Promise<ValidationResult> {
  const start = Date.now();
  const issues: ValidationIssue[] = [];

  const dialogs = page.getByRole("dialog");
  const count = await dialogs.count();

  if (count === 0) {
    return {
      check: "dialogs",
      passed: true,
      issues: [],
      durationMs: Date.now() - start,
    };
  }

  for (let i = 0; i < count; i++) {
    const dialog = dialogs.nth(i);
    if (!(await dialog.isVisible().catch(() => false))) continue;

    const metrics = await dialog.evaluate((el) => {
      const rect = el.getBoundingClientRect();
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const centered =
        Math.abs(centerX - vw / 2) < vw * 0.25 && Math.abs(centerY - vh / 2) < vh * 0.25;
      const backdrop = document.querySelector(
        '.MuiBackdrop-root, [class*="backdrop"], [data-backdrop="true"]',
      );
      const active = document.activeElement;
      const focusInDialog = el.contains(active);
      return {
        centered,
        hasBackdrop: Boolean(backdrop),
        focusInDialog,
        width: rect.width,
        height: rect.height,
        viewportWidth: vw,
        viewportHeight: vh,
      };
    });

    if (!metrics.centered) {
      issues.push({
        check: "dialogs",
        severity: "warning",
        message: `Dialog #${i + 1} not centered on screen`,
      });
    }
    if (!metrics.hasBackdrop) {
      issues.push({
        check: "dialogs",
        severity: "warning",
        message: `Dialog #${i + 1} missing backdrop`,
      });
    }
    if (!metrics.focusInDialog) {
      issues.push({
        check: "dialogs",
        severity: "warning",
        message: `Dialog #${i + 1} focus not trapped inside`,
      });
    }
    if (metrics.width > metrics.viewportWidth) {
      issues.push({
        check: "dialogs",
        severity: "error",
        message: `Dialog #${i + 1} wider than viewport`,
      });
    }
    if (metrics.height > metrics.viewportHeight * 0.95) {
      issues.push({
        check: "dialogs",
        severity: "warning",
        message: `Dialog #${i + 1} nearly full viewport height`,
      });
    }
  }

  return {
    check: "dialogs",
    passed: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}

/** Test escape closes an open dialog (call when a dialog is expected open). */
export async function assertDialogClosesOnEscape(page: Page): Promise<void> {
  const dialog = page.getByRole("dialog").first();
  await expect(dialog).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden({ timeout: 5_000 });
}
