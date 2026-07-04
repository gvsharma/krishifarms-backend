# KrishiFarms CRM — Frontend

Next.js 15 App Router UI for farm operations CRM. Deployed on Vercel with API proxy to EC2 backend.

**Design inspiration:** [Farm Management SaaS Dashboard (Dribbble)](https://dribbble.com/shots/27437443-Farm-Management-SaaS-Dashboard)

## Stack

- Next.js 15 · TypeScript · Tailwind CSS · shadcn-style components
- TanStack Query · Zustand · next-themes
- Plus Jakarta Sans + Noto Sans Telugu

## Local development

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — redirects to `/dashboard`.

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Development server |
| `npm run build` | Production build |
| `npm run lint` | ESLint (Next.js) |
| `npm start` | Serve production build |

## Environment

Copy `.env.local.example` to `.env.local` for local development:

| Variable | Local default |
|----------|---------------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8080/api/v1` |
| `API_PROXY_TARGET` | `http://localhost:8080` |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000` |

### Vercel (Production)

Set in the Vercel dashboard (**Settings → Environment Variables**) or rely on defaults in `vercel.json`:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_BASE_URL` | `/api/v1` |
| `API_PROXY_TARGET` | `http://13.232.200.243:8082` |
| `NEXT_PUBLIC_SITE_URL` | `https://krishifarms-backend.vercel.app` |

Browser calls same-origin `/api/v1`; Next.js rewrites proxy to EC2 nginx on port **8082** (avoids mixed content). Update EC2 `CORS_ORIGINS` to include `NEXT_PUBLIC_SITE_URL`.

## Architecture

See [docs/ui/FRONTEND_ARCHITECTURE.md](../docs/ui/FRONTEND_ARCHITECTURE.md) and [docs/ui/DESIGN_SYSTEM.md](../docs/ui/DESIGN_SYSTEM.md).
