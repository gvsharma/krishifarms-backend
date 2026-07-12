import { expect, test } from "@playwright/test";
import {
  assertCreateDialogFieldsNotOverlapping,
  ensureAuthenticated,
  expectListOrEmptyOrError,
  expectNoPageErrors,
  trackPageErrors,
} from "./helpers";

test.describe("finance — payments", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("loads page shell with empty/table/error content and no pageerror", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/payments");

    await expect(page.getByRole("heading", { name: /^Payments$/i })).toBeVisible();
    await expect(
      page.getByText(/Farmer payments, allocation, and settlement queue/i),
    ).toBeVisible();

    await expectListOrEmptyOrError(page, { emptyTitle: /Payments — coming soon/i });
    expectNoPageErrors(pageErrors);
  });

  test("create dialog fields do not overlap when present", async ({ page }) => {
    const pageErrors = trackPageErrors(page);
    await page.goto("/payments");
    await expect(page.getByRole("heading", { name: /^Payments$/i })).toBeVisible();

    await assertCreateDialogFieldsNotOverlapping(page, /^(Add|Create|New).*(payment)?/i);
    expectNoPageErrors(pageErrors);
  });
});
