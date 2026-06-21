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

Copy `.env.example` to `.env.local`:

| Variable | Default (local) |
|----------|-----------------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8080/api/v1` |
| `API_PROXY_TARGET` | `http://localhost:8080` |

On Vercel: `NEXT_PUBLIC_API_BASE_URL=/api/v1` and `API_PROXY_TARGET=http://<EC2_IP>`.

## Architecture

See [docs/ui/FRONTEND_ARCHITECTURE.md](../docs/ui/FRONTEND_ARCHITECTURE.md) and [docs/ui/DESIGN_SYSTEM.md](../docs/ui/DESIGN_SYSTEM.md).
