#!/usr/bin/env bash
# Create missing KrishiFarms SSM parameters expected by sync-env-from-ssm.sh.
# Does NOT overwrite existing values. Does NOT commit secrets.
#
# SecureString placeholders use REPLACE_ME (or a generated secret_key).
# For Supabase cutover, replace database_url with the real URL via:
#   bash deploy/scripts/put-supabase-database-url-ssm.sh
#
# Usage:
#   bash deploy/scripts/ensure-ssm-parameters.sh
#   AWS_REGION=ap-south-1 bash deploy/scripts/ensure-ssm-parameters.sh
#
# Requires: aws CLI, ssm:PutParameter + ssm:GetParameter on /krishifarms/dev/*
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"
PREFIX="${SSM_PREFIX:-/krishifarms/dev}"
PLACEHOLDER="${SSM_PLACEHOLDER:-REPLACE_ME}"

# name|type|default_value|description
PARAMS=(
  "${PREFIX}/app/secret_key|SecureString||FastAPI JWT signing key"
  "${PREFIX}/db/password|SecureString|${PLACEHOLDER}|Docker Postgres password (rollback / local)"
  "${PREFIX}/db/database_url|SecureString|${PLACEHOLDER}|Full DATABASE_URL (Supabase); takes precedence when not REPLACE_ME"
  "${PREFIX}/app/firebase_service_account_json|SecureString|${PLACEHOLDER}|Firebase Admin SDK JSON (minified)"
  "${PREFIX}/app/firebase_project_id|String|krishifarms-prod|Firebase project id"
)

log() { echo "[ensure-ssm] $*"; }

param_exists() {
  aws ssm get-parameter \
    --name "$1" \
    --region "$REGION" \
    --query 'Parameter.Name' \
    --output text >/dev/null 2>&1
}

create_param() {
  local name="$1" type="$2" value="$3"
  local err_file
  err_file="$(mktemp)"
  if aws ssm put-parameter \
    --region "$REGION" \
    --name "$name" \
    --type "$type" \
    --value "$value" \
    --tags "Key=Project,Value=krishifarms" "Key=ManagedBy,Value=ensure-ssm-parameters.sh" \
    >/dev/null 2>"${err_file}"; then
    rm -f "${err_file}"
    return 0
  fi
  if grep -qE 'AccessDenied|AccessDeniedException' "${err_file}"; then
    log "WARN  ${name} — PutParameter AccessDenied (attach deploy IAM policy or create param in Console)"
    rm -f "${err_file}"
    if [[ "${ENSURE_SSM_STRICT:-false}" == "true" ]]; then
      return 1
    fi
    return 0
  fi
  cat "${err_file}" >&2
  rm -f "${err_file}"
  return 1
}

if ! command -v aws >/dev/null 2>&1; then
  log "ERROR: aws CLI not found"
  exit 1
fi

log "Region=${REGION} prefix=${PREFIX}"
created=0
skipped=0

for entry in "${PARAMS[@]}"; do
  IFS='|' read -r name type value desc <<<"${entry}"
  if param_exists "${name}"; then
    log "SKIP  ${name} (already exists) — ${desc}"
    skipped=$((skipped + 1))
    continue
  fi

  if [[ "${name}" == */app/secret_key && -z "${value}" ]]; then
    # Random placeholder so JWT works in non-prod until rotated; not a committed secret.
    value="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
  fi
  if [[ -z "${value}" ]]; then
    value="${PLACEHOLDER}"
  fi

  log "CREATE ${name} (${type}) — ${desc}"
  create_param "${name}" "${type}" "${value}"
  created=$((created + 1))
done

log "Done. created=${created} skipped=${skipped}"
if [[ "${created}" -gt 0 ]]; then
  log "Replace REPLACE_ME values before production use:"
  log "  database_url → bash deploy/scripts/put-supabase-database-url-ssm.sh"
  log "  firebase_service_account_json → aws ssm put-parameter --overwrite ..."
fi
