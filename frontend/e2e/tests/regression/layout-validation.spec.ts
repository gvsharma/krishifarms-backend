import { test } from "@playwright/test";
import { ensureAuthenticated, expectNoPageErrors, trackPageErrors } from "../../utils/common";
import { validateEntirePage } from "../../utils/validation";
import { VIEWPORTS } from "../../utils/viewports";

test.describe("regression — layout validation", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("dashboard passes layout validation at desktop viewport", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/dashboard");
    await page.setViewportSize(VIEWPORTS.desktop);

    await validateEntirePage(page, {
      name: "dashboard",
      skip: ["network"],
      softFail: ["typography", "performance", "buttons", "contrast"],
      viewports: ["desktop"],
    });

    expectNoPageErrors(pageErrors);
  });
});
