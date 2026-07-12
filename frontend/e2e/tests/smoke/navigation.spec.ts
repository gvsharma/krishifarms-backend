import { expect, test } from "@playwright/test";
import { ensureAuthenticated, expectNoPageErrors, trackPageErrors } from "../../utils/common";
import { expectPrimaryNavVisible, navigateViaSidebar } from "../../utils/navigation";
import { expectNoHorizontalScroll } from "../../utils/visual";

test.describe("smoke — navigation", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("sidebar shows primary nav links without horizontal scroll", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/dashboard");
    await expectPrimaryNavVisible(page);
    await expectNoHorizontalScroll(page);

    expectNoPageErrors(pageErrors);
  });

  test("sidebar links navigate to key sections", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/dashboard");
    await navigateViaSidebar(page, "Farmers", /^Farmers$/i);
    await navigateViaSidebar(page, "Procurement", /^Procurement$/i);
    await navigateViaSidebar(page, "Settings", /^Settings$/i);

    expectNoPageErrors(pageErrors);
  });
});
