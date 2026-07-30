# Hamali (porter) work tracking

**Status:** Live (backend + web + Android branch)  
**Role code:** `HAMALI`  
**Display name:** Hamali / Porter

## Purpose

Hamalis (porters) see **read-only** summaries of their work:

- Bags handled per day, broken down by farmer
- Tips received per farmer
- Weekly and monthly rollups

They log in with **mobile number** (OTP/password) — accounts are **admin-created only** (no self-registration).

## Data model

Table `hamali_work_entries`:

| Column | Description |
|--------|-------------|
| `worker_id` | Links to `workers` |
| `farmer_id` | Farmer they helped |
| `work_date` | Calendar day |
| `bag_count` | Bags handled |
| `tip_amount` | INR tip from farmer |
| `procurement_id` | Optional link |

`users.worker_id` must be set for HAMALI logins (auto-created on user create when role is HAMALI).

## API (`/api/v1`)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| GET | `/hamali/me/daily` | `hamali_work:read` | Self; scoped by `users.worker_id` |
| GET | `/hamali/me/summary` | `hamali_work:read` | `period=week\|month` |
| GET | `/hamali/work-entries` | `hamali_work:read` | HAMALI sees own rows only |
| POST | `/hamali/work-entries` | `hamali_work:create` | Manager / supervisor |
| PATCH | `/hamali/work-entries/{id}` | `hamali_work:update` | Manager / supervisor |
| DELETE | `/hamali/work-entries/{id}` | `hamali_work:delete` | Manager / owner |
| GET/POST | `/hamali/workers` | `workers:read/create` | Worker profiles |

## RBAC

| Role | Access |
|------|--------|
| `HAMALI` | View own daily/weekly/monthly summaries only |
| `SUPERVISOR` | Log work entries |
| `MANAGER` / `OWNER` | Full hamali work CRUD + user provisioning |

Mobile permissions: `HAMALI_VIEW`, `REPORT_VIEW`, `SETTINGS_VIEW` — no create/update.

## Web UI

- `/hamali` — hamali portal (read-only)
- `/settings/hamali` — supervisors log bags/tips

## Android

Feature package `feature/hamali/` — see `krishifarms-mobile` branch `feature/hamali-viewer-role`.
