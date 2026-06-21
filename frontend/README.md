# KrishiFarms CRM — Frontend (placeholder)

The frontend is not implemented yet. This directory holds **Vercel configuration** matching the [Gamya Couture](https://github.com/gvsharma/gamyaboutique) deployment pattern.

**Planned stack:** Next.js App Router (same as Gamyaboutique)

---

## Vercel setup (when frontend is ready)

1. Import GitHub repo `gvsharma/krishifarms-backend` in Vercel
2. Set **Root Directory** = `frontend`
3. Framework preset: Next.js
4. Production branch: `main`

### Environment variables (Production)

| Variable | Example |
|----------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | `/api/v1` |
| `API_PROXY_TARGET` | `http://<EC2_PUBLIC_IP>` |
| `NEXT_PUBLIC_SITE_URL` | `https://krishifarms.vercel.app` |

**Why proxy:** Browser calls same-origin `/api/v1`; Vercel rewrites to EC2 HTTP backend (avoids mixed content). Same pattern as Gamyaboutique `frontend/next.config.ts`.

### Backend CORS

Set `CORS_ORIGINS` in `/opt/krishifarms/config/application.env` to include `NEXT_PUBLIC_SITE_URL`.

---

## Reference

See Gamyaboutique frontend: `/Users/venkatgorinta/Desktop/gamya-boutique/frontend/`

Full CI/CD docs: [docs/deploy/CI_CD.md](../docs/deploy/CI_CD.md)
