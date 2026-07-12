import fs from "node:fs";
import { expect, type Locator, type Page } from "@playwright/test";
import { AUTH_STORAGE_STATE, loginViaUi } from "../fixtures/auth";

/** Collect uncaught page errors for the duration of a test. */
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
 * If missing or session expired (redirected to /login), fall back to UI login.
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

/**
 * List / module body must show a table, empty state, or error Alert — not a silent blank.
 */
export async function expectListOrEmptyOrError(
  page: Page,
  options: { emptyTitle?: RegExp | string } = {},
): Promise<void> {
  const table = page.getByRole("table");
  const empty = options.emptyTitle
    ? page.getByRole("heading", { name: options.emptyTitle })
    : page.getByRole("heading", { name: /coming soon|no .+ found|nothing here/i });
  const alert = page.getByRole("alert");

  await expect(table.or(empty).or(alert).first()).toBeVisible({ timeout: 20_000 });
}

/** Open a create dialog/button if present and assert labeled fields do not heavily overlap. */
export async function assertCreateDialogFieldsNotOverlapping(
  page: Page,
  openButtonName: RegExp,
): Promise<boolean> {
  const openBtn = page.getByRole("button", { name: openButtonName });
  if ((await openBtn.count()) === 0) {
    return false;
  }

  await openBtn.first().click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();

  const fields = dialog.locator(
    'input:not([type="hidden"]), textarea, [role="combobox"], .MuiInputBase-root',
  );
  const count = await fields.count();
  if (count < 2) {
    await expect(dialog.locator("label, .MuiFormLabel-root").first()).toBeVisible();
    return true;
  }

  const boxes: NonNullable<Awaited<ReturnType<Locator["boundingBox"]>>>[] = [];
  for (let i = 0; i < Math.min(count, 8); i++) {
    const field = fields.nth(i);
    if (!(await field.isVisible())) continue;
    const box = await field.boundingBox();
    if (box && box.width > 0 && box.height > 0) {
      boxes.push(box);
    }
  }

  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i];
      const b = boxes[j];
      const overlapX = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x));
      const overlapY = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
      const overlapArea = overlapX * overlapY;
      const smaller = Math.min(a.width * a.height, b.width * b.height);
      // Allow tiny overlap from shared borders; fail on heavy intersection (stacked/overlapping fields).
      expect(
        overlapArea,
        `Form fields ${i} and ${j} overlap too much (${overlapArea}px²)`,
      ).toBeLessThan(smaller * 0.4);
    }
  }

  return true;
}
