# Frontend E2E (Playwright)

Shared auth + smoke foundation for KrishiFarms CRM. Page-level specs live under `e2e/` (siblings add more).

## Prerequisites

```bash
cd frontend
npm install
npx playwright install chromium
```

## Run

Against **deployed** CRM (default):

```bash
npm run test:e2e
# or UI mode
npm run test:e2e:ui
```

Against **local** Next (`npm run dev` in another terminal):

```bash
PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e
```

## Credentials

| Env | Default |
|-----|---------|
| `E2E_EMAIL` | `gvsharma4@gmail.com` |
| `E2E_PASSWORD` | `admin123` |
| `PLAYWRIGHT_BASE_URL` | `https://krishifarms-backend.vercel.app` |

Override when needed:

```bash
E2E_EMAIL=owner@krishifarms.local E2E_PASSWORD='ChangeMe123!' npm run test:e2e
```

## Auth flow

1. Project `setup` runs `e2e/auth.setup.ts` once → UI login → writes `e2e/.auth/user.json` (gitignored).
2. Spec projects reuse that `storageState` (includes `krishi-access-token` in localStorage).

## Layout

```text
e2e/
  auth.setup.ts          # login once
  fixtures/auth.ts       # shared login helpers
  smoke/dashboard.spec.ts
  operations/            # farmers, procurement, field-services, farms/vehicles/workers
  finance/               # expenses, payments, collections
  .auth/                 # generated; do not commit
```
