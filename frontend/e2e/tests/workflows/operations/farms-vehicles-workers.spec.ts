import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectNoPageErrors,
  expectShellTitle,
  trackPageErrors,
} from "./helpers";

test.describe("operations — farms / vehicles / workers", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("/farms loads", async ({ page }) => {
    const pageErrors = trackPageErrors(page);
    await page.goto("/farms");
    await expectShellTitle(page, /^Farms$/i);
    await expect(page.getByText(/Farms — coming soon/i)).toBeVisible();
    expectNoPageErrors(pageErrors);
  });

  test("/vehicles loads", async ({ page }) => {
    const pageErrors = trackPageErrors(page);
    await page.goto("/vehicles");
    await expectShellTitle(page, /^Vehicles$/i);
    await expect(page.getByText(/Vehicles — coming soon/i)).toBeVisible();
    expectNoPageErrors(pageErrors);
  });

  test("/workers loads", async ({ page }) => {
    const pageErrors = trackPageErrors(page);
    await page.goto("/workers");
    await expectShellTitle(page, /^Workers$/i);
    await expect(page.getByText(/Workers — coming soon/i)).toBeVisible();
    expectNoPageErrors(pageErrors);
  });
});
