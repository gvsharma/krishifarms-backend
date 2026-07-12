import type { Page } from "@playwright/test";
import { SELECTORS } from "../utils/selectors";
import { validateEntirePage, type ValidateEntirePageOptions } from "../utils/validation/validate-entire-page";

export abstract class BasePage {
  constructor(protected readonly page: Page) {}

  abstract readonly path: string;
  abstract readonly pageName: string;

  async goto(): Promise<void> {
    await this.page.goto(this.path);
  }

  async waitForReady(): Promise<void> {
    await this.page.waitForLoadState("domcontentloaded");
    await this.page.getByText(SELECTORS.shell.fatalError).waitFor({ state: "detached", timeout: 5_000 }).catch(() => undefined);
  }

  async validate(options?: ValidateEntirePageOptions) {
    return validateEntirePage(this.page, {
      name: this.pageName,
      ...options,
    });
  }
}
