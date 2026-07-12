import { expect } from "@playwright/test";
import { BasePage } from "./base.page";

export class FarmersListPage extends BasePage {
  readonly path = "/farmers";
  readonly pageName = "Farmers List";

  async expectLoaded(): Promise<void> {
    await expect(this.page.getByRole("heading", { name: /^Farmers$/i })).toBeVisible();
    await expect(this.page.getByPlaceholder(/Search name, phone, or code/i)).toBeVisible();
  }
}

export class FarmerCreatePage extends BasePage {
  readonly path = "/farmers/new";
  readonly pageName = "Farmer Create";

  async expectLoaded(): Promise<void> {
    await expect(this.page.getByRole("heading", { name: /^Add farmer$/i })).toBeVisible();
  }
}
