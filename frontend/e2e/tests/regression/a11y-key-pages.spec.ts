import { expect, test } from "@playwright/test";
import { loginViaUi } from "../../fixtures/auth";
import { ensureAuthenticated, expectNoPageErrors, trackPageErrors } from "../../utils/common";
import { collectTabOrder, expectMainLandmark, expectNamedControls } from "../../utils/a11y";

test.describe("accessibility — key pages", () => {
  test.describe("login (unauthenticated)", () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test("login page has labeled fields and tab order", async ({ page }) => {
      const pageErrors = trackPageErrors(page);

      await page.goto("/login");
      await expect(page.getByLabel(/email/i)).toBeVisible();
      await expect(page.getByLabel(/^password/i)).toBeVisible();
      await expect(page.getByRole("button", { name: /^(Next|Sign in)$/i })).toBeVisible();

      const tabOrder = await collectTabOrder(page, 6);
      expect(tabOrder.length).toBeGreaterThanOrEqual(2);

      expectNoPageErrors(pageErrors);
    });
  });

  test("dashboard exposes main landmark and named controls", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await ensureAuthenticated(page);
    await page.goto("/dashboard");

    await expectMainLandmark(page);
    await expectNamedControls(page, ["link", "button"], 3);

    expectNoPageErrors(pageErrors);
  });

  test("farmers list has accessible search and table structure", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await ensureAuthenticated(page);
    await page.goto("/farmers");

    await expect(page.getByPlaceholder(/Search name, phone, or code/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /^Search$/i })).toBeVisible();

    const table = page.getByRole("table");
    const empty = page.getByText(/No farmers found/i);
    const alert = page.getByRole("alert");

    await expect(table.or(empty).or(alert).first()).toBeVisible({ timeout: 20_000 });

    if (await table.isVisible().catch(() => false)) {
      await expect(page.getByRole("columnheader").first()).toBeVisible();
    }

    expectNoPageErrors(pageErrors);
  });

  test("settings users dialog fields have accessible names", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await ensureAuthenticated(page);
    await page.goto("/settings/users");

    const addBtn = page.getByRole("button", { name: /Add user/i });
    if ((await addBtn.count()) === 0) {
      test.info().annotations.push({
        type: "note",
        description: "Add user hidden — skipped dialog a11y check",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    await addBtn.click();
    const dialog = page.getByRole("dialog");
    await expect(dialog.getByLabel("Full name", { exact: true })).toBeVisible();
    await expect(dialog.getByLabel("Email", { exact: true })).toBeVisible();
    await expect(dialog.getByLabel("Role", { exact: true })).toBeVisible();

    await dialog.getByRole("button", { name: /Cancel/i }).click();
    expectNoPageErrors(pageErrors);
  });
});

test.describe("accessibility — authenticated login flow", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("loginViaUi reaches dashboard with token", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await loginViaUi(page);
    await expect(page.getByRole("heading", { name: /^Home$/i })).toBeVisible();

    const hasToken = await page.evaluate(() =>
      Boolean(localStorage.getItem("krishi-access-token")),
    );
    expect(hasToken).toBe(true);

    expectNoPageErrors(pageErrors);
  });
});
