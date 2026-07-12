import { expect, test } from "@playwright/test";
import {
  assertCreateDialogFieldsNotOverlapping,
  ensureAuthenticated,
  expectListOrEmptyOrError,
  expectNoPageErrors,
  trackPageErrors,
} from "./helpers";

test.describe("finance — expenses", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("loads page shell with empty/table/error content and no pageerror", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/expenses");

    await expect(page.getByRole("heading", { name: /^Expenses$/i })).toBeVisible();
    await expect(
      page.getByText(/Operational expenses, categories, and approval workflow/i),
    ).toBeVisible();

    await expectListOrEmptyOrError(page, { emptyTitle: /Expenses — coming soon/i });
    expectNoPageErrors(pageErrors);
  });

  test("create dialog fields do not overlap when present", async ({ page }) => {
    const pageErrors = trackPageErrors(page);
    await page.goto("/expenses");
    await expect(page.getByRole("heading", { name: /^Expenses$/i })).toBeVisible();

    await assertCreateDialogFieldsNotOverlapping(page, /^(Add|Create|New).*(expense)?/i);
    expectNoPageErrors(pageErrors);
  });
});
