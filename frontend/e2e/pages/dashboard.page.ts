import { expect } from "@playwright/test";
import { BasePage } from "./base.page";

export class DashboardPage extends BasePage {
  readonly path = "/dashboard";
  readonly pageName = "Dashboard";

  async expectLoaded(): Promise<void> {
    await expect(this.page.getByRole("heading", { name: /^Home$/i })).toBeVisible();
    await expect(this.page.getByText(/Farm operations overview/i).first()).toBeVisible();
  }
}
