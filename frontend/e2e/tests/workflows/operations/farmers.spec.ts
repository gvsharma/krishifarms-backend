import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectListContent,
  expectNoPageErrors,
  expectShellTitle,
  trackPageErrors,
} from "./helpers";

test.describe("operations — farmers", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("list loads with search / table / empty / alert and no pageerror", async ({
    page,
  }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/farmers");
    await expectShellTitle(page, /^Farmers$/i);
    await expect(
      page.getByText(/Farmer registry with village assignments/i),
    ).toBeVisible();

    await expect(page.getByPlaceholder(/Search name, phone, or code/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /^Search$/i })).toBeVisible();

    await expectListContent(page, /No farmers found/i);
    expectNoPageErrors(pageErrors);
  });

  test("create form fields visible at /farmers/new", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/farmers/new");
    await expectShellTitle(page, /^Add farmer$/i);

    const fullName = page.getByLabel("Full name", { exact: true });
    const alert = page.getByRole("alert");

    await expect(fullName.or(alert).first()).toBeVisible({ timeout: 20_000 });

    if (await fullName.isVisible().catch(() => false)) {
      await expect(page.getByLabel("Full name (Telugu)")).toBeVisible();
      await expect(page.getByLabel("Primary phone")).toBeVisible();
      await expect(page.getByLabel("District")).toBeVisible();
      await expect(page.getByLabel("Mandal")).toBeVisible();
      await expect(page.getByLabel("Village")).toBeVisible();
      await expect(page.getByLabel("Notes")).toBeVisible();
      await expect(page.getByRole("button", { name: /Create farmer/i })).toBeVisible();
    }

    expectNoPageErrors(pageErrors);
  });

  test("search filters farmers list without page errors", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/farmers");
    await expectShellTitle(page, /^Farmers$/i);

    await page.getByPlaceholder(/Search name, phone, or code/i).fill("zzz-nonexistent-e2e");
    await page.getByRole("button", { name: /^Search$/i }).click();

    await expectListContent(page, /No farmers found/i);
    expectNoPageErrors(pageErrors);
  });

  test("create form validation keeps submit disabled until required fields filled", async ({
    page,
  }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/farmers/new");
    await expectShellTitle(page, /^Add farmer$/i);

    const submit = page.getByRole("button", { name: /Create farmer/i });
    const alert = page.getByRole("alert");

    if (await alert.isVisible().catch(() => false)) {
      test.info().annotations.push({
        type: "note",
        description: "Villages API unavailable — skipped create validation",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    await expect(submit).toBeDisabled();
    await page.getByLabel("Full name", { exact: true }).fill("E2E Farmer");
    await expect(submit).toBeDisabled();

    expectNoPageErrors(pageErrors);
  });

  test("farmer detail page loads from list row or shows alert", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/farmers");
    await expectShellTitle(page, /^Farmers$/i);

    const outcome = await expectListContent(page, /No farmers found/i);
    if (outcome !== "table") {
      test.info().annotations.push({
        type: "note",
        description: "No farmer rows — skipped detail navigation",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    const firstRow = page.getByRole("row").nth(1);
    await firstRow.click();

    await expect(
      page.getByRole("heading").filter({ hasNotText: /^Farmers$/i }).first(),
    ).toBeVisible({ timeout: 20_000 });
    await expect(
      page.getByRole("button", { name: /Back to list/i }).or(page.getByRole("alert")),
    ).toBeVisible();

    if (await page.getByRole("button", { name: /Back to list/i }).isVisible().catch(() => false)) {
      await expect(page.getByRole("button", { name: /^Edit$/i })).toBeVisible();
    }

    expectNoPageErrors(pageErrors);
  });
});
