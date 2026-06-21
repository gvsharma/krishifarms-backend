# KrishiFarms Backend

Farm, Procurement, Logistics, Rental, Workforce, and Financial Management CRM backend.

## Stack

- Python 3.12
- FastAPI
- PostgreSQL 16
- Redis 7
- AWS S3 (documents)
- Docker Compose (EC2-friendly, no RDS/NAT/VPC endpoints required)

## Phase 1 Modules Included

- Auth (JWT login, refresh, logout)
- Users and Roles (RBAC)
- Villages, Crop Types, Expense Categories
- Documents (S3 presigned upload/download)
- Audit logs and activity feed
- Dashboard summary
- Database seed for default organization and owner user

## Quick Start (Local)

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
docker compose -f infra/docker-compose.yml exec api python scripts/seed.py
```

API:

- Root: `http://localhost:8000/`
- API base: `http://localhost:8000/api/v1`
- Swagger: `http://localhost:8000/api/v1/docs`
- Nginx proxy: `http://localhost:8080/api/v1`

Default owner credentials (change immediately):

- Email: `owner@krishifarms.local`
- Password: `ChangeMe123!`

## Example Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@krishifarms.local","password":"ChangeMe123!"}'
```

## Project Structure

```text
app/
  core/           # config, db, security, dependencies
  modules/        # domain modules
  shared/         # permissions, audit, s3
infra/
  docker-compose.yml
  nginx/
  scripts/backup.sh
alembic/
scripts/seed.py
```

## EC2 Deployment Notes

- Run everything on one EC2 instance using `infra/docker-compose.yml`
- Keep PostgreSQL data on EBS (`pgdata` volume)
- Use IAM instance role for S3 access (leave AWS keys empty in `.env`)
- Schedule `infra/scripts/backup.sh` with cron for nightly `pg_dump` to local disk and optional S3 upload
- Set `DEBUG=false` and a strong `SECRET_KEY` in production

## Next Phases

- Phase 2: Farmers, Procurement, Farmer Ledger
- Phase 3: Farmer Payments, Expenses, Collections
- Phase 4: Farms, Workers, Work Orders, Attendance
- Phase 5+: Fleet, Rentals, AI integrations
