# Backend production deployment (EC2 + GitHub Actions)

Deploys KrishiFarms CRM to EC2 via **S3 + SSM Run Command** when a PR is merged to `main` (no SSH from GitHub runners). Uses the **same SSM orchestration** as [Gamya Couture](https://github.com/gvsharma/gamyaboutique) — see [docs/deploy/CI_CD.md](../docs/deploy/CI_CD.md#same-as-gamya-ssm-deploy-orchestration).

## Gamya parity at a glance

| | Gamya | KrishiFarms |
|---|-------|-------------|
| App path | `/opt/gamya-couture` | `/opt/krishifarms` |
| Nginx port | 8080 | **8082** |
| S3 artifact | `incoming/gamya-couture.jar` | `incoming/deploy.tar.gz` |
| Env sync | `sync-rds-env-from-ssm.sh` | `sync-env-from-ssm.sh` |
| SSM prefix | `/gamya-couture/dev/db/*` | `/krishifarms/dev/app/*`, `/krishifarms/dev/db/*` |
| Runtime | systemd JAR | Docker Compose + Alembic |
| Bootstrap | One-time manual (`ec2-bootstrap.sh`) | One-time manual (`ec2-bootstrap.sh`) |

## Folder structure

```
.github/workflows/
  ci.yml                              # PR + main: lint/test
  validate.yml                        # Reusable validation workflow
  deploy.yml                          # main only: bundle → S3 → SSM → Docker Compose

deploy/
  README.md                           # This file
  env/
    application.env.example           # EC2 runtime secrets template
  scripts/
    ec2-bootstrap.sh                  # One-time EC2 setup (Docker, directories)
    remote-deploy.sh                  # Idempotent deploy + backup + rollback
    sync-env-from-ssm.sh              # Optional SSM secret sync
    ssm-kickoff-deploy.sh             # Async deploy kickoff from SSM

infra/
  docker-compose.prod.yml             # Production stack (nginx :80, no bind mounts)

# On EC2 after bootstrap:
/opt/krishifarms/
  repo/                               # Extracted deploy bundle
  incoming/deploy.tar.gz              # Staging upload from GitHub Actions
  backup/deploy.tar.gz.<timestamp>    # Previous versions (auto-pruned)
  config/application.env              # Runtime secrets (never committed)
  logs/deploy.latest.log              # Deploy output
  scripts/remote-deploy.sh            # Copied each deploy
```

## GitHub configuration (required)

Configure in **gvsharma/krishifarms-backend** → Settings → Secrets and variables → Actions.

Use the **same secret names** as Gamyaboutique where applicable.

**Secret** (Actions → **Secrets** tab):

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_BACKEND_DEPLOY_ROLE_ARN` | Yes | IAM role ARN for OIDC deploy (same AWS account as Gamyaboutique) |

**Variables** (Actions → **Variables** tab):

| Variable | Required | Description |
|----------|----------|-------------|
| `DEPLOY_BUCKET` | Yes | S3 bucket for deploy artifacts (e.g. `krishifarms-dev-backend-deploy`) |
| `EC2_INSTANCE_ID` | **Yes** (shared Gamya EC2) | `i-0426cdc00ff15bfe9` — skips name-tag lookup |
| `EC2_HOST` | **Yes** (shared Gamya EC2) | `13.232.200.243` — health checks and smoke tests |
| `EC2_NAME_TAG` | No | `gamya-couture-dev-api` if instance ID omitted (auto-default when bucket name contains `krishifarms`) |
| `NGINX_LOCAL_PORT` | No | Default `8082` on shared dev host |
| `PUBLIC_HEALTH_CHECK_URL` | No | Default `http://<EC2_HOST>:8082/api/v1/health` |

Optional **secrets**: `SMOKE_TEST_EMAIL`, `SMOKE_TEST_PASSWORD`.

Full values: [`.github/DEPLOY_CONFIG.md`](../.github/DEPLOY_CONFIG.md).

## EC2 one-time setup

Same as Gamya: **manual, one-time** on the shared EC2 via Session Manager (not automated by GitHub Actions).

Connect via **AWS Session Manager** (region `ap-south-1`).

```bash
sudo dnf install -y git
git clone https://github.com/gvsharma/krishifarms-backend.git /tmp/krishifarms-backend
cd /tmp/krishifarms-backend
sudo APP_PATH=/opt/krishifarms bash deploy/scripts/ec2-bootstrap.sh
sudo APP_PATH=/opt/krishifarms bash deploy/scripts/sync-env-from-ssm.sh
# Or edit manually:
sudo nano /opt/krishifarms/config/application.env
sudo chmod 640 /opt/krishifarms/config/application.env
sudo chown root:krishifarms /opt/krishifarms/config/application.env
```

### SSM parameters (krishifarms-infra)

Create in Terraform or AWS Console (SecureString). EC2 instance role needs `ssm:GetParameter` on these paths:

| Parameter | Maps to `application.env` |
|-----------|---------------------------|
| `/krishifarms/dev/app/secret_key` | `SECRET_KEY` |
| `/krishifarms/dev/db/password` | `POSTGRES_PASSWORD`, `DATABASE_URL` |

Gamya equivalent: `/gamya-couture/dev/db/username`, `/gamya-couture/dev/db/password`.

## Deployment flow (automatic on merge to main)

```
PR merged → push to main
  → validate (ruff, docker build, security scan)
  → tar deploy bundle → OIDC assume AWS_BACKEND_DEPLOY_ROLE_ARN
  → Start EC2 if stopped; wait SSM Online
  → aws s3 cp bundle + scripts → s3://<DEPLOY_BUCKET>/incoming/
  → SSM kickoff → ssm-kickoff-deploy.sh
       → downloads artifacts, sync-env-from-ssm.sh
       → remote-deploy.sh (extract, docker compose up, alembic, health check, rollback)
  → Poll deploy.status via SSM until success/failed (36 × 10 s)
  → curl http://<EC2_HOST>:8082/api/v1/health
  → smoke-test-api.sh (with :8082)
```

## Frontend pairing (Vercel)

| Vercel | EC2 `application.env` |
|--------|----------------------|
| `NEXT_PUBLIC_API_BASE_URL=/api/v1` | — |
| `API_PROXY_TARGET=http://<EC2_IP>` | — |
| `NEXT_PUBLIC_SITE_URL=https://krishifarms.vercel.app` | `CORS_ORIGINS` must include this origin |

See `frontend/.env.example` and [docs/deploy/CI_CD.md](../docs/deploy/CI_CD.md).

## Rollback

Automatic: if health check fails, `remote-deploy.sh` restores the previous backup tarball.

Manual rollback on EC2:

```bash
sudo cp /opt/krishifarms/backup/deploy.tar.gz.<timestamp> /tmp/rollback.tar.gz
sudo rm -rf /opt/krishifarms/repo
sudo mkdir -p /opt/krishifarms/repo
sudo tar -xzf /tmp/rollback.tar.gz -C /opt/krishifarms/repo
cd /opt/krishifarms/repo
sudo cp /opt/krishifarms/config/application.env .env
sudo docker compose -f infra/docker-compose.prod.yml up -d --build
```
