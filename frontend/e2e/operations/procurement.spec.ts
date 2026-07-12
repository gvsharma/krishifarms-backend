import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectListContent,
  expectNoPageErrors,
  expectShellTitle,
  trackPageErrors,
} from "./helpers";

test.describe("operations — procurement", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("list loads with filter / table / empty / alert and no pageerror", async ({
    page,
  }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/procurement");
    await expectShellTitle(page, /^Procurement$/i);
    await expect(page.getByText(/Intake tickets from draft through confirmation/i)).toBeVisible();
    await expect(page.getByLabel(/Status filter/i)).toBeVisible();
    await expect(page.getByRole("link", { name: /New procurement/i })).toBeVisible();

    await expectListContent(page, /No procurements yet/i);
    expectNoPageErrors(pageErrors);
  });
});
