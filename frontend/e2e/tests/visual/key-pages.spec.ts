import { test } from "@playwright/test";
import { DashboardPage } from "../../pages/dashboard.page";
import { FarmersListPage } from "../../pages/farmers.page";
import { SettingsUsersPage } from "../../pages/settings.page";
import { validateEntirePage } from "../../utils/validation/validate-entire-page";

const VISUAL_PAGES = [
  { PageClass: DashboardPage, name: "dashboard" },
  { PageClass: FarmersListPage, name: "farmers-list" },
  { PageClass: SettingsUsersPage, name: "settings-users" },
] as const;

for (const { PageClass, name } of VISUAL_PAGES) {
  test(`visual — ${name} matches baseline`, async ({ page }) => {
    const pageObj = new PageClass(page);
    await pageObj.goto();
    await pageObj.waitForReady();

    await validateEntirePage(page, {
      name,
      visualRegression: true,
      skip: ["responsive"],
      softFail: [
        "typography",
        "css",
        "performance",
        "contrast",
        "accessibility",
        "inputs",
        "buttons",
        "layout",
        "navigation",
        "tables",
        "dialogs",
      ],
    });
  });
}
