#!/usr/bin/env bash
# Run from GitHub Actions (OIDC) before EC2 deploy — no local machine required.
#
# 1. Write Supabase DATABASE_URL from SUPABASE_DB_PASSWORD (required)
# 2. Ensure missing SSM keys (best-effort)
# 3. Configure shared cost scheduler: EC2 start/stop only (best-effort)
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

if [[ -z "${SUPABASE_DB_PASSWORD:-}" ]]; then
  log "::error::SUPABASE_DB_PASSWORD GitHub secret is not set."
  log "::error::Repo → Settings → Secrets and variables → Actions → New repository secret"
  log "::error::Name: SUPABASE_DB_PASSWORD — Value: Supabase project database password"
  exit 1
fi

log "Syncing Supabase DATABASE_URL to SSM from SUPABASE_DB_PASSWORD secret"
bash "${SCRIPT_DIR}/put-supabase-database-url-ssm.sh"

# Best-effort bootstrap for missing params (non-fatal if deploy role lacks PutParameter on new keys).
ENSURE_SSM_STRICT=false bash "${SCRIPT_DIR}/ensure-ssm-parameters.sh" || \
  log "::warning::ensure-ssm-parameters had errors — continuing if database_url was written"

log "Configuring EC2-only cost scheduler (remove RDS from daily cron)"
if ! bash "${SCRIPT_DIR}/configure-compute-scheduler-ec2-only.sh"; then
  log "::warning::EC2-only scheduler update failed — attach Lambda/scheduler IAM on deploy role (see deploy/iam/)"
fi

log "GitHub pre-deploy complete"
