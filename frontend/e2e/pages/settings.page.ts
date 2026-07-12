import { expect } from "@playwright/test";
import { BasePage } from "./base.page";

export class SettingsUsersPage extends BasePage {
  readonly path = "/settings/users";
  readonly pageName = "Settings Users";

  async expectLoaded(): Promise<void> {
    await expect(this.page.getByRole("heading", { name: "Users" }).first()).toBeVisible();
  }
}

export class SettingsVillagesPage extends BasePage {
  readonly path = "/settings/villages";
  readonly pageName = "Settings Villages";

  async expectLoaded(): Promise<void> {
    await expect(this.page.getByRole("heading", { name: "Villages" }).first()).toBeVisible();
  }
}

export class SettingsMasterDataPage extends BasePage {
  readonly path = "/settings/master-data";
  readonly pageName = "Settings Master Data";

  async expectLoaded(): Promise<void> {
    await expect(this.page.getByRole("heading", { name: /Master data/i }).first()).toBeVisible();
  }
}
