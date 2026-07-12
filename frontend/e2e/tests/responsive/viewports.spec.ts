import { expect, test } from "@playwright/test";
import { ensureAuthenticated, expectNoPageErrors, trackPageErrors } from "../../utils/common";
import { expectNoHorizontalScroll } from "../../utils/visual";
import { VIEWPORTS, type ViewportPreset } from "../../utils/viewports";

const PRESETS: ViewportPreset[] = ["mobile", "tablet", "desktop", "laptop", "landscape", "portrait"];

const PAGES = [
  { path: "/dashboard", heading: /^Home$/i },
  { path: "/farmers", heading: /^Farmers$/i },
  { path: "/settings", heading: /^Settings$/i },
] as const;

test.describe("responsive — viewport presets", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  for (const preset of PRESETS) {
    for (const pg of PAGES) {
      test(`${pg.path} at ${preset} (${VIEWPORTS[preset].width}×${VIEWPORTS[preset].height})`, async ({
        page,
      }) => {
        const pageErrors = trackPageErrors(page);

        await page.setViewportSize(VIEWPORTS[preset]);
        await page.goto(pg.path);

        await expect(page.getByRole("heading", { name: pg.heading }).first()).toBeVisible({
          timeout: 20_000,
        });
        await expectNoHorizontalScroll(page);

        expectNoPageErrors(pageErrors);
      });
    }
  }
});
