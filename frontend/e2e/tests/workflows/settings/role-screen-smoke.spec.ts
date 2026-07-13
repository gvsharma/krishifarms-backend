import { expect, test, type Page } from "@playwright/test";
import { e2eCredentials } from "../../../fixtures/auth";
import { LoginPage } from "../../../pages/login.page";
import { FATAL_UI, expectNoPageErrors, trackPageErrors } from "../../../utils/common";

/**
 * Thin role × screen smoke: login as known seeded/demo users and hit main routes.
 *
 * Credentials (do not invent passwords):
 * - OWNER: `e2eCredentials()` / `E2E_EMAIL` + `E2E_PASSWORD` (always required)
 * - MANAGER / AGENT: `docs/DEMO_DATA.md` demo users (`DemoPass123!`) — skipped if login fails
 * - SUPERVISOR / DRIVER / FARMER: only when `E2E_<ROLE>_EMAIL` + `E2E_<ROLE>_PASSWORD` are set
 */

type RoleRoute = { path: string; heading: RegExp };

type RoleSmokeUser = {
  role: string;
  email: string;
  password: string;
  routes: RoleRoute[];
  /** If false, skip the test when login fails (demo seed may be absent). */
  required: boolean;
};

const OWNER_ROUTES: RoleRoute[] = [
  { path: "/dashboard", heading: /^Home$/i },
  { path: "/farmers", heading: /^Farmers$/i },
  { path: "/procurement", heading: /^Procurement$/i },
  { path: "/field-services", heading: /^Field services$/i },
  { path: "/payments", heading: /^Payments$|^Finance$/i },
  { path: "/settings", heading: /^Settings$/i },
];

const AGENT_ROUTES: RoleRoute[] = [
  { path: "/dashboard", heading: /^Home$/i },
  { path: "/farmers", heading: /^Farmers$/i },
  { path: "/field-services", heading: /^Field services$/i },
];

const PERMISSION_TOAST = /Missing permission|Access denied|Forbidden|not authorized/i;

function optionalRole(
  role: string,
  envEmail: string,
  envPassword: string,
  fallbackEmail: string | undefined,
  fallbackPassword: string | undefined,
  routes: RoleRoute[],
): RoleSmokeUser | null {
  const email = process.env[envEmail] || fallbackEmail;
  const password = process.env[envPassword] || fallbackPassword;
  if (!email || !password) return null;
  return {
    role,
    email,
    password,
    routes,
    required: Boolean(process.env[envEmail] && process.env[envPassword]),
  };
}

function roleUsers(): RoleSmokeUser[] {
  const owner = e2eCredentials();
  const users: RoleSmokeUser[] = [
    {
      role: "OWNER",
      email: owner.email,
      password: owner.password,
      routes: OWNER_ROUTES,
      required: true,
    },
  ];

  const manager = optionalRole(
    "MANAGER",
    "E2E_MANAGER_EMAIL",
    "E2E_MANAGER_PASSWORD",
    "manager@demo.krishifarms.local",
    "DemoPass123!",
    OWNER_ROUTES,
  );
  if (manager) users.push(manager);

  const agent = optionalRole(
    "AGENT",
    "E2E_AGENT_EMAIL",
    "E2E_AGENT_PASSWORD",
    "agent@demo.krishifarms.local",
    "DemoPass123!",
    AGENT_ROUTES,
  );
  if (agent) users.push(agent);

  for (const role of ["SUPERVISOR", "DRIVER", "FARMER"] as const) {
    const extra = optionalRole(
      role,
      `E2E_${role}_EMAIL`,
      `E2E_${role}_PASSWORD`,
      undefined,
      undefined,
      AGENT_ROUTES,
    );
    if (extra) users.push(extra);
  }

  return users;
}

async function loginAs(page: Page, email: string, password: string): Promise<boolean> {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.emailInput.fill(email);
  await loginPage.passwordInput.fill(password);
  await loginPage.submitButton.click();
  try {
    await page.waitForURL((url) => !url.pathname.includes("/login"), { timeout: 45_000 });
    await page.waitForFunction(
      () => Boolean(localStorage.getItem("krishi-access-token")),
      null,
      { timeout: 15_000 },
    );
    return true;
  } catch {
    return false;
  }
}

async function assertNoPermissionToast(page: Page): Promise<void> {
  await expect(page.getByText(PERMISSION_TOAST)).toHaveCount(0);
}

test.describe("workflow — role × screen smoke", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  for (const user of roleUsers()) {
    test(`${user.role} can open key routes`, async ({ page }) => {
      const pageErrors = trackPageErrors(page);
      const ok = await loginAs(page, user.email, user.password);
      if (!ok) {
        if (user.required) {
          throw new Error(`Required login failed for ${user.role} (${user.email})`);
        }
        test.skip(true, `Demo/env user unavailable: ${user.role} (${user.email})`);
        return;
      }

      for (const route of user.routes) {
        await page.goto(route.path);
        await expect(page.getByRole("heading", { name: route.heading }).first()).toBeVisible({
          timeout: 20_000,
        });
        await expect(page.getByText(FATAL_UI)).toHaveCount(0);
        await assertNoPermissionToast(page);
      }

      expectNoPageErrors(pageErrors);
    });
  }
});
