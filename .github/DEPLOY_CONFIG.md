# GitHub Actions deploy configuration (from krishifarms-infra)

Generated from Terraform dev apply. **Set these in GitHub → Settings → Secrets and variables → Actions** on `gvsharma/krishifarms-backend`.

Do not commit secrets to git. Re-sync after `terraform apply` in `krishifarms-infra/environments/dev`.

## Secret

| Name | Value |
|------|-------|
| `AWS_BACKEND_DEPLOY_ROLE_ARN` | `arn:aws:iam::085863558134:role/krishifarms-dev-gh-be-deploy-20260621161619959700000003` |

## Variables

| Name | Value | Required |
|------|-------|----------|
| `AWS_REGION` | `ap-south-1` | No (default `ap-south-1`) |
| `DEPLOY_BUCKET` | `krishifarms-dev-backend-deploy` | **Yes** |
| `EC2_INSTANCE_ID` | `i-0426cdc00ff15bfe9` | **Yes** (shared Gamya EC2 — skips name-tag lookup) |
| `EC2_HOST` | `13.232.200.243` | **Yes** (shared Gamya EC2 — health checks / smoke tests) |
| `EC2_NAME_TAG` | `gamya-couture-dev-api` | No (fallback if `EC2_INSTANCE_ID` unset; auto-default when `DEPLOY_BUCKET` contains `krishifarms`) |
| `NGINX_LOCAL_PORT` | `8082` | No (default `8082`) |
| `HEALTH_CHECK_URL` | `http://127.0.0.1:8082/api/v1/health` | No |
| `PUBLIC_HEALTH_CHECK_URL` | `http://13.232.200.243:8082/api/v1/health` | No |

## Sync automatically (optional)

From `krishifarms-infra` with `gh auth login` and a PAT in `KRISHIFARMS_GH_TOKEN`:

```bash
export GH_TOKEN=...
export GITHUB_BACKEND_REPOSITORY=gvsharma/krishifarms-backend
bash scripts/sync-backend-deploy-github-config.sh
```

## Shared EC2 notes

- **Same host as Gamya Couture** — EC2 tag `Name=gamya-couture-dev-api` (not `krishifarms-dev-api`).
- Instance `i-0426cdc00ff15bfe9` at `13.232.200.243`.
- KrishiFarms dev listens on **8082** (Gamya uses **8080**); app path `/opt/krishifarms`.
- `infra/docker-compose.prod.yml` publishes nginx as `${NGINX_HOST_PORT:-8082}:80` (override `NGINX_HOST_PORT` only if the host mapping changes).
- **Set `EC2_INSTANCE_ID` and `EC2_HOST` in GitHub Variables** — required for shared setup so deploy skips `{prefix}-api` lookup.
- Optional `EC2_NAME_TAG=gamya-couture-dev-api` if you omit `EC2_INSTANCE_ID` (workflow also auto-defaults when `DEPLOY_BUCKET` contains `krishifarms`).
- OIDC trust is on **`gvsharma/krishifarms-backend`**, not `krishifarms-crm`.
- EC2 must have `/opt/krishifarms` (bootstrap) and SSM Online.

## SSM parameters (Terraform / Console)

| Parameter | Type | Purpose |
|-----------|------|---------|
| `/krishifarms/dev/app/secret_key` | SecureString | FastAPI JWT signing |
| `/krishifarms/dev/db/password` | SecureString | Docker Postgres password |

Grant the shared EC2 instance role `ssm:GetParameter` on `arn:aws:ssm:ap-south-1:*:parameter/krishifarms/dev/*` (mirror Gamya `/gamya-couture/dev/db/*`).

## Verify

```bash
aws ssm describe-instance-information --filters "Key=InstanceIds,Values=i-0426cdc00ff15bfe9"
curl -sf http://13.232.200.243:8082/api/v1/health
```
