import { expect, test } from "@playwright/test";
import {
  assertCreateDialogFieldsNotOverlapping,
  ensureAuthenticated,
  expectListOrEmptyOrError,
  expectNoPageErrors,
  trackPageErrors,
} from "./helpers";

test.describe("finance — collections", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("loads page shell with empty/table/error content and no pageerror", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/collections");

    await expect(page.getByRole("heading", { name: /^Collections$/i })).toBeVisible();
    await expect(
      page.getByText(/Daily collection entries, weighment, and quality checks/i),
    ).toBeVisible();

    await expectListOrEmptyOrError(page, { emptyTitle: /Collections — coming soon/i });
    expectNoPageErrors(pageErrors);
  });

  test("create dialog fields do not overlap when present", async ({ page }) => {
    const pageErrors = trackPageErrors(page);
    await page.goto("/collections");
    await expect(page.getByRole("heading", { name: /^Collections$/i })).toBeVisible();

    await assertCreateDialogFieldsNotOverlapping(page, /^(Add|Create|New).*(collection)?/i);
    expectNoPageErrors(pageErrors);
  });
});
