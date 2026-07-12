import fs from "node:fs";
import { expect, type Page } from "@playwright/test";
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
 * Main shell title visible and not stuck on a Next/fatal error page.
 * Soft: API failures may show an MUI Alert instead of blank crash.
 */
export async function expectShellTitle(
  page: Page,
  title: string | RegExp,
): Promise<void> {
  await expect(page.getByRole("heading", { name: title }).first()).toBeVisible({
    timeout: 20_000,
  });
  await expect(
    page.getByText(
      /Application error|Internal Server Error|This page could not be found|Unhandled Runtime Error/i,
    ),
  ).toHaveCount(0);
}

/**
 * List body settled: table, empty copy, or Alert (API soft-fail).
 */
export async function expectListContent(
  page: Page,
  emptyText: RegExp,
): Promise<void> {
  const table = page.getByRole("table");
  const empty = page.getByText(emptyText);
  const alert = page.getByRole("alert");

  await expect(table.or(empty).or(alert).first()).toBeVisible({ timeout: 20_000 });
}

type Box = { x: number; y: number; width: number; height: number };

function overlapArea(a: Box, b: Box): number {
  const overlapX = Math.max(
    0,
    Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x),
  );
  const overlapY = Math.max(
    0,
    Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y),
  );
  return overlapX * overlapY;
}

/** Assert labeled form controls are visible and not heavily stacked. */
export async function expectLabeledFieldsNotOverlapping(
  page: Page,
  labels: string[],
): Promise<void> {
  const boxes: Box[] = [];

  for (const label of labels) {
    const field = page.getByLabel(label, { exact: true }).first();
    await expect(field, `Field "${label}" should be visible`).toBeVisible({
      timeout: 15_000,
    });
    const box = await field.boundingBox();
    expect(box, `Field "${label}" should have a layout box`).not.toBeNull();
    if (box) boxes.push(box);
  }

  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i];
      const b = boxes[j];
      const area = overlapArea(a, b);
      const smaller = Math.min(a.width * a.height, b.width * b.height);
      expect(
        area,
        `Fields "${labels[i]}" and "${labels[j]}" overlap too much (${area}px²)`,
      ).toBeLessThan(smaller * 0.4);
    }
  }
}
