import { expect, test } from "@playwright/test";
import { ensureAuthenticated } from "../../utils/auth-helpers";
import { validateEntirePage } from "../../utils/validation/validate-entire-page";

test.describe("workflows — settings users CRUD dialog", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("open Add user dialog and validate", async ({ page }) => {
    await page.goto("/settings/users");
    await page.waitForLoadState("domcontentloaded");

    const addBtn = page.getByRole("button", { name: /Add user/i });
    if ((await addBtn.count()) === 0) {
      test.skip(true, "Add user button hidden (permission)");
      return;
    }

    await addBtn.click();
    await expect(page.getByRole("dialog")).toBeVisible();

    await validateEntirePage(page, {
      name: "settings-users-add-dialog",
      skip: ["visual", "responsive", "network"],
      softFail: ["typography", "css", "performance", "contrast"],
    });

    await page.getByRole("button", { name: /Cancel/i }).click();
  });
});

test.describe("workflows — villages add dialog", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("open Add village dialog and validate", async ({ page }) => {
    await page.goto("/settings/villages");
    await page.waitForLoadState("domcontentloaded");

    await page.getByRole("button", { name: /^Add$/i }).click();
    await expect(page.getByRole("dialog")).toBeVisible();

    await validateEntirePage(page, {
      name: "settings-villages-add-dialog",
      skip: ["visual", "responsive"],
      softFail: ["typography", "css", "performance", "contrast"],
    });

    await page.getByRole("button", { name: /Cancel/i }).click();
  });
});
