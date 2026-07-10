#!/usr/bin/env bash
# Run from GitHub Actions (OIDC) before EC2 deploy — no local machine required.
#
# 1. Ensure SSM parameter keys exist (placeholders only if missing)
# 2. Write Supabase DATABASE_URL when SUPABASE_DB_PASSWORD secret is set
# 3. Configure shared cost scheduler: EC2 start/stop only (no RDS)
#
# Required GitHub secret: SUPABASE_DB_PASSWORD
# Required IAM on deploy role: ssm:PutParameter, ssm:GetParameter (krishifarms/dev/*),
#   lambda:UpdateFunctionConfiguration + GetFunctionConfiguration (gamya-couture-dev-cost-scheduler),
#   scheduler:DeleteSchedule (orphan shutdown-ec2)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGION="${AWS_REGION:-ap-south-1}"

log() { echo "[$(date -Iseconds)] $*"; }

log "GitHub pre-deploy: region=${REGION}"

bash "${SCRIPT_DIR}/ensure-ssm-parameters.sh"

if [[ -n "${SUPABASE_DB_PASSWORD:-}" ]]; then
  log "Syncing Supabase DATABASE_URL to SSM from SUPABASE_DB_PASSWORD secret"
  bash "${SCRIPT_DIR}/put-supabase-database-url-ssm.sh"
else
  log "::warning::SUPABASE_DB_PASSWORD GitHub secret not set — skipping SSM database_url update"
  log "::warning::Add secret in repo Settings → Secrets → Actions, then re-run deploy"
fi

log "Configuring EC2-only cost scheduler (remove RDS from daily cron)"
bash "${SCRIPT_DIR}/configure-compute-scheduler-ec2-only.sh"

log "GitHub pre-deploy complete"
