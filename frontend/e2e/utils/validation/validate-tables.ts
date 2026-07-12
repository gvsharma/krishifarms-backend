import type { Page } from "@playwright/test";
import type { ValidationIssue, ValidationResult } from "./types";

export async function validateTables(page: Page): Promise<ValidationResult> {
  const start = Date.now();
  const issues: ValidationIssue[] = [];

  const tables = page.getByRole("table");
  const count = await tables.count();

  if (count === 0) {
    return {
      check: "tables",
      passed: true,
      issues: [],
      durationMs: Date.now() - start,
    };
  }

  for (let i = 0; i < count; i++) {
    const table = tables.nth(i);
    const headers = table.getByRole("columnheader");
    const headerCount = await headers.count();

    if (headerCount === 0) {
      issues.push({
        check: "tables",
        severity: "warning",
        message: `Table #${i + 1} has no column headers`,
      });
    } else {
      for (let h = 0; h < headerCount; h++) {
        await headers.nth(h).isVisible().catch(() => false);
      }
    }

    const scan = await table.evaluate((el) => {
      const cells = [...el.querySelectorAll("th, td")];
      const clipped: string[] = [];
      for (const cell of cells) {
        const html = cell as HTMLElement;
        const style = window.getComputedStyle(cell);
        if (
          (html.scrollWidth > html.clientWidth + 2 || html.scrollHeight > html.clientHeight + 2) &&
          ["hidden", "clip"].includes(style.overflow)
        ) {
          clipped.push((cell.textContent || "").trim().slice(0, 30));
        }
      }
      const pagination = document.querySelector(
        '[role="navigation"][aria-label*="pagination" i], .MuiTablePagination-root, [class*="pagination"]',
      );
      return { clipped, hasPagination: Boolean(pagination) };
    });

    for (const text of scan.clipped) {
      issues.push({
        check: "tables",
        severity: "warning",
        message: `Clipped table cell: "${text}"`,
      });
    }
  }

  const pagination = page.locator(
    '[role="navigation"][aria-label*="pagination" i], .MuiTablePagination-root',
  );
  if ((await pagination.count()) > 0) {
    const visible = await pagination.first().isVisible().catch(() => false);
    if (!visible) {
      issues.push({
        check: "tables",
        severity: "warning",
        message: "Pagination present but not visible",
      });
    }
  }

  return {
    check: "tables",
    passed: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
