import fs from "node:fs";
import path from "node:path";
import { expect, type Page, type TestInfo } from "@playwright/test";

/** Auth storage written by foundation setup (relative to Playwright project root = frontend/). */
export const AUTH_STORAGE_STATE = "e2e/.auth/user.json";

const AUTH_FILE_ABS = path.join(__dirname, "..", ".auth", "user.json");

export const hasAuthStorageState = fs.existsSync(AUTH_FILE_ABS);

export const E2E_EMAIL = process.env.E2E_EMAIL ?? "owner@krishifarms.local";
export const E2E_PASSWORD = process.env.E2E_PASSWORD ?? "ChangeMe123!";

/** Uncaught page exceptions collected during a test. */
export type PageGuards = {
  pageErrors: string[];
  consoleErrors: string[];
  assertNoPageErrors: () => void;
};

/**
 * Fail on uncaught exceptions (pageerror). Console errors are recorded for soft checks.
 * Call `assertNoPageErrors()` at the end of each test.
 */
export function attachPageGuards(page: Page): PageGuards {
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];

  page.on("pageerror", (err) => {
    pageErrors.push(err.message);
  });

  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    const text = msg.text();
    // Ignore noisy third-party / hydration noise that is not an app crash.
    if (/Download the React DevTools|favicon\.ico|net::ERR_/i.test(text)) return;
    consoleErrors.push(text);
  });

  return {
    pageErrors,
    consoleErrors,
    assertNoPageErrors: () => {
      expect(pageErrors, `Uncaught pageerror(s):\n${pageErrors.join("\n")}`).toEqual([]);
    },
  };
}

/** Interactive login when storageState is not available yet. */
export async function loginViaUi(page: Page): Promise<void> {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible({
    timeout: 20_000,
  });
  await page.getByLabel("Email").fill(E2E_EMAIL);
  await page.getByLabel("Password", { exact: true }).fill(E2E_PASSWORD);
  await page.getByRole("button", { name: "Next" }).click();
  await page.waitForURL((url) => !url.pathname.startsWith("/login"), { timeout: 30_000 });
}

/**
 * Use project storageState when present; otherwise log in via /login before each test.
 * Pass into `test.describe` via `test.use` + `beforeEach`.
 */
export async function ensureAuthenticated(page: Page): Promise<void> {
  if (hasAuthStorageState) return;
  await loginViaUi(page);
}

/** Storage state option for describe blocks when the auth file exists. */
export function authDescribeOptions(): { storageState: string } | Record<string, never> {
  return hasAuthStorageState ? { storageState: AUTH_STORAGE_STATE } : {};
}

const FATAL_UI =
  /Application error|Internal Server Error|This page could not be found|Unhandled Runtime Error|Something went wrong/i;

/**
 * Assert the route rendered main content (MUI h1 or PageShell h1) and is not a fatal error page.
 * Soft: if the list API fails, an MUI Alert is acceptable instead of a blank crash.
 */
export async function expectPageShellLoaded(
  page: Page,
  title: string | RegExp,
  options?: { allowAlert?: boolean },
): Promise<void> {
  const allowAlert = options?.allowAlert ?? true;

  await expect(page.getByRole("heading", { name: title }).first()).toBeVisible({
    timeout: 20_000,
  });

  const fatal = page.getByText(FATAL_UI);
  await expect(fatal).toHaveCount(0);

  if (allowAlert) {
    const alert = page.getByRole("alert");
    const hasAlert = (await alert.count()) > 0;
    if (hasAlert) {
      // Soft path: API failure surfaced as Alert — page still usable.
      await expect(alert.first()).toBeVisible();
    }
  }
}

/** True when two boxes overlap in both axes (layout collision). */
export function boxesOverlap(
  a: { x: number; y: number; width: number; height: number },
  b: { x: number; y: number; width: number; height: number },
  pad = 2,
): boolean {
  return !(
    a.x + a.width <= b.x + pad ||
    b.x + b.width <= a.x + pad ||
    a.y + a.height <= b.y + pad ||
    b.y + b.height <= a.y + pad
  );
}

type Box = { x: number; y: number; width: number; height: number };

/** Assert labeled controls are visible and pairwise non-overlapping. */
export async function expectLabeledFieldsVisible(
  page: Page,
  labels: string[],
): Promise<void> {
  const boxes: { label: string; box: Box }[] = [];

  for (const label of labels) {
    const field = page.getByLabel(label, { exact: true }).first();
    await expect(field, `Field "${label}" should be visible`).toBeVisible({
      timeout: 15_000,
    });
    const box = await field.boundingBox();
    expect(box, `Field "${label}" should have a layout box`).not.toBeNull();
    if (box) boxes.push({ label, box });
  }

  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      const overlap = boxesOverlap(boxes[i].box, boxes[j].box);
      expect(
        overlap,
        `Fields "${boxes[i].label}" and "${boxes[j].label}" should not overlap`,
      ).toBe(false);
    }
  }
}

export function annotateAuthMode(testInfo: TestInfo): void {
  testInfo.annotations.push({
    type: "auth",
    description: hasAuthStorageState
      ? `storageState: ${AUTH_STORAGE_STATE}`
      : "UI login fallback (/login)",
  });
}
