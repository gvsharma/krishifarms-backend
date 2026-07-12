import { test } from "@playwright/test";
import { FarmerCreatePage, FarmersListPage } from "../../pages/farmers.page";
import { validateEntirePage } from "../../utils/validation/validate-entire-page";

test.describe("smoke — login flow", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("login page passes validation", async ({ page }) => {
    await page.goto("/login");
    await page.waitForLoadState("domcontentloaded");

    await validateEntirePage(page, {
      name: "login",
      skip: ["network", "visual", "responsive", "tables", "dialogs"],
      softFail: ["typography", "css", "performance", "contrast", "accessibility", "inputs"],
    });
  });
});

test.describe("smoke — farmers", () => {
  test("farmers list passes full page validation", async ({ page }) => {
    const farmers = new FarmersListPage(page);
    await farmers.goto();
    await farmers.waitForReady();
    await farmers.expectLoaded();

    await validateEntirePage(page, {
      name: "farmers-list",
      skip: ["visual", "responsive"],
      softFail: ["typography", "css", "performance", "contrast", "inputs", "accessibility"],
    });
  });

  test("farmer create form passes full page validation", async ({ page }) => {
    const create = new FarmerCreatePage(page);
    await create.goto();
    await create.waitForReady();

    await validateEntirePage(page, {
      name: "farmers-create",
      skip: ["visual", "responsive", "tables"],
      softFail: ["typography", "css", "performance", "contrast", "inputs"],
    });
  });
});
