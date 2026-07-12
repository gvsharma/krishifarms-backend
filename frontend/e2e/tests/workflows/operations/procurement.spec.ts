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

  test("status filter changes list query without crash", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/procurement");
    await expectShellTitle(page, /^Procurement$/i);

    await page.getByLabel(/Status filter/i).click();
    await page.getByRole("option", { name: /Draft/i }).click();

    await expectListContent(page, /No procurements yet/i);
    expectNoPageErrors(pageErrors);
  });

  test("procurement detail page loads from list row or shows alert", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/procurement");
    await expectShellTitle(page, /^Procurement$/i);

    const outcome = await expectListContent(page, /No procurements yet/i);
    if (outcome !== "table") {
      test.info().annotations.push({
        type: "note",
        description: "No procurement rows — skipped detail navigation",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    const firstRow = page.getByRole("row").nth(1);
    await firstRow.click();

    await expect(
      page.getByRole("button", { name: /Back to board/i }).or(page.getByRole("alert")),
    ).toBeVisible({ timeout: 20_000 });

    expectNoPageErrors(pageErrors);
  });
});
