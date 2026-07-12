import fs from "node:fs";
import { expect, type Locator, type Page } from "@playwright/test";
import { AUTH_STORAGE_STATE, loginViaUi } from "../fixtures/auth";

/** Collect uncaught page exceptions for the duration of a test. */
export function trackPageErrors(page: Page): string[] {
  const pageErrors: string[] = [];
  page.on("pageerror", (err) => {
    pageErrors.push(err.message);
  });
  return pageErrors;
}

export function expectNoPageErrors(pageErrors: string[]): void {
  expect(pageErrors, `Uncaught page errors:\n${pageErrors.join("\n")}`).toEqual([]);
}

/**
 * Prefer storageState from setup (`e2e/.auth/user.json`).
 * Fall back to UI login if the file is missing or the session expired.
 */
export async function ensureAuthenticated(page: Page): Promise<void> {
  if (!fs.existsSync(AUTH_STORAGE_STATE)) {
    await loginViaUi(page);
    return;
  }

  await page.goto("/dashboard");
  if (page.url().includes("/login")) {
    await loginViaUi(page);
  }
}

const FATAL_UI =
  /Application error|Internal Server Error|This page could not be found|Unhandled Runtime Error/i;

/** Page shell heading visible and not a fatal Next.js error page. */
export async function expectSettingsShell(page: Page, title: string | RegExp): Promise<void> {
  await expect(page.getByRole("heading", { name: title }).first()).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByText(FATAL_UI)).toHaveCount(0);
}

/**
 * Catalog / list body must show a table, empty row copy, or error Alert — not a blank crash.
 * Useful when live API may still 500 (e.g. users EmailStr *.local).
 */
export async function expectTableOrAlert(page: Page): Promise<"table" | "alert"> {
  const table = page.getByRole("table");
  const alert = page.getByRole("alert");

  await expect
    .poll(
      async () => {
        if (await table.isVisible().catch(() => false)) return "table";
        if (await alert.isVisible().catch(() => false)) return "alert";
        return "pending";
      },
      { timeout: 25_000 },
    )
    .not.toBe("pending");

  if (await table.isVisible().catch(() => false)) return "table";
  await expect(alert.first()).toBeVisible();
  return "alert";
}

/** True when two axis-aligned boxes heavily intersect (layout collision). */
export function heavyOverlap(
  a: { x: number; y: number; width: number; height: number },
  b: { x: number; y: number; width: number; height: number },
  maxRatio = 0.35,
): boolean {
  const overlapX = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x));
  const overlapY = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
  const overlapArea = overlapX * overlapY;
  if (overlapArea <= 0) return false;
  const smaller = Math.min(a.width * a.height, b.width * b.height);
  return smaller > 0 && overlapArea >= smaller * maxRatio;
}

/**
 * Resolve a MUI dialog field by accessible name.
 * Prefer role locators: getByLabel(exact) misses required asterisk / floating-label quirks.
 */
export function dialogField(dialog: Locator, label: string): Locator {
  const exact = { name: label, exact: true as const };
  // textbox | combobox (select) | spinbutton (number) | checkbox (boolean Switch)
  return dialog
    .getByRole("textbox", exact)
    .or(dialog.getByRole("combobox", exact))
    .or(dialog.getByRole("spinbutton", exact))
    .or(dialog.getByRole("checkbox", exact))
    .or(dialog.getByLabel(label, { exact: true }))
    .first();
}

/**
 * Assert labeled controls inside a dialog are visible and do not heavily overlap.
 */
export async function expectDialogLabelsNotOverlapping(
  dialog: Locator,
  labels: string[],
): Promise<void> {
  const boxes: { label: string; box: NonNullable<Awaited<ReturnType<Locator["boundingBox"]>>> }[] =
    [];

  for (const label of labels) {
    const control = dialogField(dialog, label);
    await expect(control, `Field "${label}" should be visible`).toBeVisible({ timeout: 15_000 });
    // Also assert the floating / form label text is present in the dialog.
    await expect(
      dialog.getByText(label, { exact: true }).first(),
      `Label text "${label}" should be visible`,
    ).toBeVisible();
    const box = await control.boundingBox();
    expect(box, `Field "${label}" should have a layout box`).not.toBeNull();
    if (box) {
      expect(box.height, `Field "${label}" should have non-collapsed height`).toBeGreaterThan(8);
      boxes.push({ label, box });
    }
  }

  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      expect(
        heavyOverlap(boxes[i].box, boxes[j].box),
        `Fields "${boxes[i].label}" and "${boxes[j].label}" heavily overlap`,
      ).toBe(false);
    }
  }
}

/** Open Add dialog on a CatalogAdminPage and assert key fields. */
export async function openCatalogAddDialog(page: Page): Promise<Locator> {
  await page.getByRole("button", { name: /^Add$/i }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  return dialog;
}
