import fs from "node:fs";
import { expect, type Page } from "@playwright/test";
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

export const FATAL_UI =
  /Application error|Internal Server Error|This page could not be found|Unhandled Runtime Error/i;

/** Page shell heading visible and not a fatal Next.js error page. */
export async function expectShellTitle(
  page: Page,
  title: string | RegExp,
): Promise<void> {
  await expect(page.getByRole("heading", { name: title }).first()).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByText(FATAL_UI)).toHaveCount(0);
}

/**
 * List body settled: table, empty copy, or Alert (API soft-fail).
 */
export async function expectListContent(
  page: Page,
  emptyText: RegExp,
): Promise<"table" | "empty" | "alert"> {
  const table = page.getByRole("table");
  const empty = page.getByText(emptyText);
  const alert = page.getByRole("alert");

  await expect(table.or(empty).or(alert).first()).toBeVisible({ timeout: 20_000 });

  if (await table.isVisible().catch(() => false)) return "table";
  if (await empty.isVisible().catch(() => false)) return "empty";
  return "alert";
}

export { expectLabeledFieldsNotOverlapping } from "./dialog";
