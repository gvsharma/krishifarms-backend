# Gamya Couture — remove managed RDS (`gamya-couture-dev-pg`)

KrishiFarms shares EC2 `i-0426cdc00ff15bfe9` with Gamya. The only RDS in ap-south-1 is **`gamya-couture-dev-pg`** (Gamya Terraform, not Aurora). Remove it to stop RDS billing and EC2+RDS cron coupling.

## KrishiFarms repo (this repo)

On each deploy to `main`, `github-predeploy.sh` already:

1. Writes Supabase `DATABASE_URL` to SSM (when `SUPABASE_DB_PASSWORD` is set)
2. Runs `configure-compute-scheduler-ec2-only.sh` — drops `DB_INSTANCE_IDENTIFIER` from Lambda `gamya-couture-dev-cost-scheduler`

## Gamya Couture infra repo (required to destroy RDS)

Terraform changes are in **`patches/gamya-couture-infra-remove-rds.patch`** (generated from `gvsharma/gamya-couture-infra`).

### Apply the patch

```bash
git clone https://github.com/gvsharma/gamya-couture-infra.git
cd gamya-couture-infra
git checkout -b cursor/remove-rds-1066
git apply /path/to/krishifarms-backend/patches/gamya-couture-infra-remove-rds.patch
git add -A && git commit -m "Remove managed RDS (enable_rds=false)"
git push -u origin cursor/remove-rds-1066
# Open PR → merge to default branch → Terraform apply destroys gamya-couture-dev-pg
```

### What the patch does

| Change | Effect |
|--------|--------|
| `enable_rds = false` in `environments/dev/ci.tfvars` | Terraform **destroys** RDS instance + subnet group + SSM DB params |
| `module.rds` `count` | Optional RDS; `moved` block migrates state `module.rds` → `module.rds[0]` |
| `module.scheduler` | `schedule_rds = false` — EC2-only 06:00 / 11:00 IST |
| `ci-backend-deploy-iam` | No `rds:StartDBInstance` on deploy role |

See also `docs/RDS_REMOVAL.md` in gamya-couture-infra after patch apply.

### Manual destroy (if Terraform apply blocked)

```bash
aws rds delete-db-instance \
  --region ap-south-1 \
  --db-instance-identifier gamya-couture-dev-pg \
  --skip-final-snapshot \
  --delete-automated-backups
```

Then run Terraform apply with `enable_rds = false` to clean state (subnet group, SSM params).

### Gamya backend DB

After RDS removal, configure `/opt/gamya-couture/config/application.env` `DB_URL` for local Postgres on EC2 or an external host. KrishiFarms uses Supabase (`ucvwtoziiqgmcyzxkwxe`) via SSM `/krishifarms/dev/db/database_url`.
