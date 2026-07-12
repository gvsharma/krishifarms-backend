import { expect } from "@playwright/test";
import { SELECTORS } from "../utils/selectors";
import { BasePage } from "./base.page";

export class LoginPage extends BasePage {
  readonly path = "/login";
  readonly pageName = "Login";

  emailInput = this.page.getByLabel(/email/i);
  passwordInput = this.page.getByLabel(/^password/i);
  submitButton = this.page.getByRole("button", { name: SELECTORS.roles.loginButton });

  async login(email: string, password: string): Promise<void> {
    await this.goto();
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    await this.page.waitForURL((url) => !url.pathname.includes("/login"), { timeout: 45_000 });
    await this.page.waitForFunction(
      () => Boolean(localStorage.getItem("krishi-access-token")),
      null,
      { timeout: 15_000 },
    );
  }

  async expectOnPage(): Promise<void> {
    await expect(this.emailInput).toBeVisible();
    await expect(this.passwordInput).toBeVisible();
  }
}
