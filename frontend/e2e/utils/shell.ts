import { expect, type Page } from "@playwright/test";
import { SELECTORS } from "./selectors";

/** Page shell title visible and not a fatal Next.js error page. */
export async function expectShellTitle(page: Page, title: string | RegExp): Promise<void> {
  await expect(page.getByRole("heading", { name: title }).first()).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByText(SELECTORS.shell.fatalError)).toHaveCount(0);
}

/** Settings module shell (alias for consistent naming in settings specs). */
export async function expectSettingsShell(page: Page, title: string | RegExp): Promise<void> {
  return expectShellTitle(page, title);
}

/**
 * List body settled: table, empty copy, or Alert (API soft-fail).
 */
export async function expectListContent(page: Page, emptyText: RegExp): Promise<void> {
  const table = page.getByRole("table");
  const empty = page.getByText(emptyText);
  const alert = page.getByRole("alert");

  await expect(table.or(empty).or(alert).first()).toBeVisible({ timeout: 20_000 });
}

/**
 * Catalog / list body must show a table, empty row copy, or error Alert — not a blank crash.
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

/**
 * Finance / list module: table, empty state heading, or error Alert.
 */
export async function expectListOrEmptyOrError(
  page: Page,
  options: { emptyTitle?: RegExp | string } = {},
): Promise<void> {
  const table = page.getByRole("table");
  const empty = options.emptyTitle
    ? page.getByRole("heading", { name: options.emptyTitle })
    : page.getByRole("heading", { name: SELECTORS.shell.emptyState });
  const alert = page.getByRole("alert");

  await expect(table.or(empty).or(alert).first()).toBeVisible({ timeout: 20_000 });
}
