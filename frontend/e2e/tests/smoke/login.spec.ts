import { expect, test } from "@playwright/test";
import { loginViaUi } from "../../fixtures/auth";
import { expectNoPageErrors, trackPageErrors } from "../../utils/common";
import { expectNoHorizontalScroll } from "../../utils/visual";

test.describe("smoke — login", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("owner can sign in and reach dashboard", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await loginViaUi(page);
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: /^Home$/i })).toBeVisible({
      timeout: 20_000,
    });
    await expectNoHorizontalScroll(page);

    expectNoPageErrors(pageErrors);
  });
});
