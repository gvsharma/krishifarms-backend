# Frontend E2E (Playwright)

Enterprise Playwright framework for KrishiFarms CRM: page objects, `validateEntirePage()` validation suite, smoke/regression/visual/responsive/workflow projects, and GitHub Actions CI.

## Prerequisites

```bash
cd frontend
npm install
npx playwright install chromium
```

## Run locally

Against **deployed** CRM (default `https://krishifarms-backend.vercel.app`):

```bash
npm run test:e2e
npm run test:e2e:ui          # interactive UI mode
```

Against **local** Next.js (`npm run dev` in another terminal):

```bash
PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e
```

### Targeted suites

| Command | Project(s) | Scope |
|---------|------------|--------|
| `npm run test:e2e:smoke` | setup + smoke-chromium | Login, dashboard, navigation, farmers smoke (~10 tests) |
| `npm run test:e2e:workflow` | setup + workflow | Settings CRUD, operations, finance, farmer journey (~51 tests) |
| `npm run test:e2e:a11y` | setup + regression | Settings regression + a11y key pages (~14 tests) |
| `npm run test:e2e:visual` | setup + visual | Screenshot baselines (~4 tests) |
| `npm run test:e2e:visual:update` | setup + visual | Regenerate baselines |
| `npm run test:e2e:responsive` | setup + responsive + mobile-chrome | Viewport presets (~19 tests) |
| `npm run test:e2e:cross-browser` | setup + chromium + firefox + webkit | Full cross-browser (nightly) |

Run a single file:

```bash
npx playwright test e2e/tests/smoke/login.spec.ts
```

## Credentials

| Env | Default |
|-----|---------|
| `E2E_EMAIL` | `owner@krishifarms.local` |
| `E2E_PASSWORD` | `ChangeMe123!` |
| `PLAYWRIGHT_BASE_URL` | `https://krishifarms-backend.vercel.app` |

## Auth flow

1. Project `setup` runs `e2e/auth.setup.ts` → UI login → writes `e2e/.auth/user.json` (gitignored).
2. Spec projects reuse `storageState` (`krishi-access-token` in localStorage).
3. Login/workflow specs use empty `storageState` for fresh sign-in.

## Layout

```text
e2e/
  auth.setup.ts
  fixtures/
    auth.ts                  # loginViaUi, credentials
    index.ts                 # extended test fixture (POM + authedPage)
  pages/                     # Page Object Model (DashboardPage, FarmersListPage, …)
  test-data/                 # routes, labels, credentials
  utils/
    validation/              # validateEntirePage + per-check validators
    visual.ts                # overlap, horizontal scroll, clipped text
    a11y.ts                  # landmarks, tab order, named controls
    navigation.ts            # sidebar nav helpers
    common.ts                # ensureAuthenticated, list/shell helpers
    reports/                 # enterprise HTML validation reporter
  baselines/                 # visual regression PNG baselines
  tests/
    smoke/                   # login, dashboard, navigation, auth-farmers
    workflows/               # settings, operations, finance, farmer-journey
    regression/              # settings + a11y key pages
    visual/                  # screenshot regression (key-pages)
    responsive/              # viewport presets
  settings/                  # legacy helpers (re-exported by workflows/settings)
  operations/                # legacy helpers
  finance/                   # legacy helpers
  .auth/                     # generated; do not commit
```

## validateEntirePage()

One-liner enterprise validation on any page:

```ts
import { validateEntirePage } from "../utils/validation/validate-entire-page";

await validateEntirePage(page, {
  name: "dashboard",
  skip: ["visual", "responsive"],
  softFail: ["typography", "css", "performance"],
});
```

Checks: console errors, network, layout (no horizontal scroll), inputs, buttons, typography, tables, dialogs, navigation, accessibility (axe), contrast, CSS, performance. Optional: visual regression, responsive viewports.

## Visual validation utilities

In `e2e/utils/visual.ts`:

- `expectNoHorizontalScroll` — no sideways page scroll
- `expectTextNotClipped` — headings not truncated
- `expectLabeledFieldsNotOverlapping` / `expectDialogLabelsNotOverlapping` — form layout collisions
- `expectPageVisualHealth` — combined smoke visual check
- `validateVisualIssues` — programmatic overlap/clip/scroll scan

## Adding tests

**Quick smoke test:**

```ts
import { expect, test } from "@playwright/test";
import { ensureAuthenticated, expectNoPageErrors, trackPageErrors } from "../../utils/common";
import { expectPageVisualHealth } from "../../utils/visual";

test.beforeEach(async ({ page }) => await ensureAuthenticated(page));

test("my page loads", async ({ page }) => {
  const pageErrors = trackPageErrors(page);
  await page.goto("/my-route");
  await expectPageVisualHealth(page, /My page/i);
  expectNoPageErrors(pageErrors);
});
```

**Enterprise validation (POM):**

```ts
import { test } from "@playwright/test";
import { MyPage } from "../../pages/my.page";
import { validateEntirePage } from "../../utils/validation/validate-entire-page";

test("my page passes validation", async ({ page }) => {
  const p = new MyPage(page);
  await p.goto();
  await p.waitForReady();
  await validateEntirePage(page, { name: "my-page", skip: ["visual"] });
});
```

## Visual baselines

Baselines live under `e2e/baselines/{projectName}/`. Regenerate after intentional UI changes:

```bash
npm run test:e2e:visual:update
git add e2e/baselines/
```

## CI/CD

| File | Role |
|------|------|
| [`.github/workflows/e2e.yml`](../../.github/workflows/e2e.yml) | Reusable Playwright job |
| [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) | Invokes validate + e2e |

| Trigger | E2E scope |
|---------|-----------|
| PR → `main` | `setup` + `smoke-chromium` + `workflow` |
| Push → `main` | `setup` + `smoke-chromium` + `regression` + `workflow` |
| Nightly cron (02:30 UTC) | Full suite (all projects, cross-browser) |
| `workflow_dispatch` | Full suite |

CI builds the PR frontend, **wakes shared EC2 if stopped**, waits for API health, proxies to EC2 (`API_PROXY_TARGET`), starts `npm run start` on port 3000, then runs Playwright.

### Artifacts

- **HTML report** — `playwright-report-<run_id>` (always, 14-day retention)
- **Test results** — trace/screenshots/video in `test-results-<run_id>` (14-day retention)

Download from GitHub Actions → **Artifacts**.

### Blocking merges on failures

1. **Settings → Branches → Branch protection** for `main`.
2. Enable **Require status checks to pass**.
3. Add required check: **`E2E (Playwright)`** (match job name in Actions UI).
4. Optionally require **`Validate`** from the same `ci.yml` workflow.

PRs cannot merge until smoke + workflow tests pass.

## Playwright projects

| Project | Tests |
|---------|-------|
| `setup` | `auth.setup.ts` |
| `smoke-chromium` | `tests/smoke/*.spec.ts` |
| `workflow` | `tests/workflows/*.spec.ts` |
| `regression` | `tests/regression/*.spec.ts` |
| `visual` | `tests/visual/*.spec.ts` |
| `responsive` / `mobile-chrome` | `tests/responsive/*.spec.ts` |
| `chromium` / `firefox` / `webkit` | All specs (nightly cross-browser) |

## Test coverage map

| Suite | Coverage |
|-------|----------|
| Smoke | Login, dashboard, navigation, farmers list/create |
| Workflows — settings | Users, villages, master-data catalogs, CRUD dialogs |
| Workflows — operations | Farmers (list/create/detail/search), procurement (list/filter/detail), field-services (list/new/detail/edit) |
| Workflows — finance | Expenses, payments, collections |
| Workflow | Login → create farmer → dashboard |
| Regression | Settings pages + a11y (tab order, landmarks, ARIA) |
| Visual | Dashboard, farmers, settings-users baselines |
| Responsive | Dashboard + farmers across desktop/tablet/mobile |
