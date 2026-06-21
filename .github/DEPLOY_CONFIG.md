# GitHub Actions deploy configuration (from krishifarms-infra)

Generated from Terraform dev apply. **Set these in GitHub → Settings → Secrets and variables → Actions** on `gvsharma/krishifarms-backend`.

Do not commit secrets to git. Re-sync after `terraform apply` in `krishifarms-infra/environments/dev`.

## Secret

| Name | Value |
|------|-------|
| `AWS_BACKEND_DEPLOY_ROLE_ARN` | `arn:aws:iam::085863558134:role/krishifarms-dev-gh-be-deploy-20260621161619959700000003` |

## Variables

| Name | Value |
|------|-------|
| `AWS_REGION` | `ap-south-1` |
| `DEPLOY_BUCKET` | `krishifarms-dev-backend-deploy` |
| `EC2_INSTANCE_ID` | `i-0426cdc00ff15bfe9` |
| `EC2_HOST` | `13.232.200.243` |
| `NGINX_LOCAL_PORT` | `8082` |
| `HEALTH_CHECK_URL` | `http://127.0.0.1:8082/api/v1/health` |
| `PUBLIC_HEALTH_CHECK_URL` | `http://13.232.200.243:8082/api/v1/health` |

## Sync automatically (optional)

From `krishifarms-infra` with `gh auth login` and a PAT in `KRISHIFARMS_GH_TOKEN`:

```bash
export GH_TOKEN=...
export GITHUB_BACKEND_REPOSITORY=gvsharma/krishifarms-backend
bash scripts/sync-backend-deploy-github-config.sh
```

## Shared EC2 notes

- Same host as Gamya Couture (`gamya-couture-dev-api`).
- KrishiFarms dev listens on **8082** (Gamya uses **8080**).
- OIDC trust is on **`gvsharma/krishifarms-backend`**, not `krishifarms-crm`.
- EC2 must have `/opt/krishifarms` (bootstrap) and SSM Online.

## Verify

```bash
aws ssm describe-instance-information --filters "Key=InstanceIds,Values=i-0426cdc00ff15bfe9"
curl -sf http://13.232.200.243:8082/api/v1/health
```
