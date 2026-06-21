#!/usr/bin/env bash
# Pull optional secrets from SSM and merge into EC2 application.env.
# Requires: AWS CLI, EC2 instance role with ssm:GetParameter.
#
# Usage (on EC2 as root):
#   sudo bash deploy/scripts/sync-env-from-ssm.sh
#   sudo bash deploy/scripts/sync-env-from-ssm.sh /opt/krishifarms/config/application.env
set -euo pipefail

ENV_FILE="${1:-/opt/krishifarms/config/application.env}"
REGION="${AWS_REGION:-ap-south-1}"
SECRET_KEY_PATH="${SSM_SECRET_KEY_PATH:-/krishifarms/dev/app/secret_key}"
DB_PASSWORD_PATH="${SSM_DB_PASSWORD_PATH:-/krishifarms/dev/db/password}"

log() { echo "[$(date -Iseconds)] $*"; }

if ! command -v aws >/dev/null 2>&1; then
  log "WARN: aws CLI not found — skip SSM sync"
  exit 0
fi

if [[ ! -f "$ENV_FILE" ]]; then
  log "ERROR: $ENV_FILE not found. Run ec2-bootstrap.sh first."
  exit 1
fi

upsert() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

fetch_param() {
  aws ssm get-parameter \
    --name "$1" \
    --with-decryption \
    --region "$REGION" \
    --query 'Parameter.Value' \
    --output text 2>/dev/null || true
}

SECRET_KEY="$(fetch_param "${SECRET_KEY_PATH}")"
if [[ -n "${SECRET_KEY}" && "${SECRET_KEY}" != "None" ]]; then
  log "Syncing SECRET_KEY from ${SECRET_KEY_PATH}"
  upsert "SECRET_KEY" "${SECRET_KEY}"
fi

DB_PASSWORD="$(fetch_param "${DB_PASSWORD_PATH}")"
if [[ -n "${DB_PASSWORD}" && "${DB_PASSWORD}" != "None" ]]; then
  log "Syncing POSTGRES_PASSWORD from ${DB_PASSWORD_PATH}"
  upsert "POSTGRES_PASSWORD" "${DB_PASSWORD}"
  upsert "DATABASE_URL" "postgresql+psycopg2://krishi:${DB_PASSWORD}@postgres:5432/krishifarms"
fi

chmod 640 "$ENV_FILE"
chown root:krishifarms "$ENV_FILE"

log "SSM sync complete for ${ENV_FILE}"
