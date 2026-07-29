import { test } from "@playwright/test";
import {
  SettingsMasterDataPage,
  SettingsUsersPage,
  SettingsVillagesPage,
} from "../../pages/settings.page";
import { validateEntirePage } from "../../utils/validation/validate-entire-page";
import { ROUTES } from "../../test-data/routes";

test.describe("regression — settings", () => {
  test("settings users passes validateEntirePage", async ({ page }) => {
    const users = new SettingsUsersPage(page);
    await users.goto();
    await users.waitForReady();

    await validateEntirePage(page, {
      name: "settings-users",
      skip: ["visual", "responsive"],
      softFail: ["typography", "css", "performance", "contrast", "layout"],
    });
  });

  test("settings villages passes validateEntirePage", async ({ page }) => {
    const villages = new SettingsVillagesPage(page);
    await villages.goto();
    await villages.waitForReady();

    await validateEntirePage(page, {
      name: "settings-villages",
      skip: ["visual", "responsive"],
      softFail: ["typography", "css", "performance", "contrast", "layout"],
    });
  });

  test("settings master-data hub passes validateEntirePage", async ({ page }) => {
    const hub = new SettingsMasterDataPage(page);
    await hub.goto();
    await hub.waitForReady();

    await validateEntirePage(page, {
      name: "settings-master-data",
      skip: ["visual", "responsive", "tables"],
      softFail: ["typography", "css", "performance", "contrast", "layout"],
    });
  });
});

const CATALOG_ROUTES = [
  { path: ROUTES.masterDataCrops, name: "master-data-crops" },
  { path: ROUTES.masterDataBuyers, name: "master-data-buyers" },
  { path: "/settings/master-data/agents", name: "master-data-agents" },
  { path: "/settings/master-data/vehicle-types", name: "master-data-vehicle-types" },
];

for (const route of CATALOG_ROUTES) {
  test(`regression — ${route.name} passes validateEntirePage`, async ({ page }) => {
    await page.goto(route.path);
    await page.waitForLoadState("domcontentloaded");

    await validateEntirePage(page, {
      name: route.name,
      skip: ["visual", "responsive"],
      softFail: ["typography", "css", "performance", "contrast", "layout"],
    });
  });
}
