# Backend production deployment (EC2 + GitHub Actions)

Deploys KrishiFarms CRM to EC2 via **S3 + SSM Run Command** when a PR is merged to `main` (no SSH from GitHub runners). Mirrors the [Gamya Couture](https://github.com/gvsharma/gamyaboutique) CI/CD pattern.

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
| `DEPLOY_BUCKET` | Yes* | S3 bucket for deploy artifacts (e.g. `krishifarms-dev-backend-deploy`) |
| `EC2_INSTANCE_ID` | No | Auto-resolved by tag `{prefix}-api` if missing |
| `EC2_HOST` | No | Auto-resolved from EC2 public IP at deploy time |
| `SMOKE_TEST_EMAIL` | No | Owner email for post-deploy smoke tests |
| `SMOKE_TEST_PASSWORD` | No | Owner password for post-deploy smoke tests |

\* `DEPLOY_BUCKET` can be a **Variable** instead of a secret (Gamyaboutique uses Variables tab).

## EC2 one-time setup

Connect via **AWS Session Manager** (region `ap-south-1`).

```bash
sudo dnf install -y git
git clone https://github.com/gvsharma/krishifarms-backend.git
cd krishifarms-backend
sudo APP_PATH=/opt/krishifarms bash deploy/scripts/ec2-bootstrap.sh
sudo nano /opt/krishifarms/config/application.env
# Set SECRET_KEY, POSTGRES_PASSWORD, CORS_ORIGINS
sudo chmod 640 /opt/krishifarms/config/application.env
sudo chown root:krishifarms /opt/krishifarms/config/application.env
```

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
  → Poll deploy.status via SSM until success/failed
  → curl http://<EC2_HOST>/api/v1/health
  → smoke-test-api.sh
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
