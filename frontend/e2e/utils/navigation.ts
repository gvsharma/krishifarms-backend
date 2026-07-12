import { expect, type Page } from "@playwright/test";

/** Primary sidebar nav labels visible to OWNER/MANAGER. */
export const PRIMARY_NAV_LABELS = [
  "Dashboard",
  "Farmers",
  "Procurement",
  "Services",
  "Finance",
  "Users",
  "Master data",
  "Settings",
] as const;

/**
 * Assert key sidebar navigation links are visible (desktop drawer).
 */
export async function expectPrimaryNavVisible(page: Page): Promise<void> {
  for (const label of PRIMARY_NAV_LABELS) {
    await expect(
      page.getByRole("navigation").getByRole("link", { name: label }),
      `Nav link "${label}" should be visible`,
    ).toBeVisible({ timeout: 15_000 });
  }
}

/** Navigate via sidebar and assert destination heading. */
export async function navigateViaSidebar(
  page: Page,
  linkName: string | RegExp,
  expectedHeading: string | RegExp,
): Promise<void> {
  await page.getByRole("navigation").getByRole("link", { name: linkName }).click();
  await expect(page.getByRole("heading", { name: expectedHeading }).first()).toBeVisible({
    timeout: 20_000,
  });
}
