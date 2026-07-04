#!/usr/bin/env bash
# Pull optional secrets from SSM and merge into EC2 application.env.
# Requires: AWS CLI, EC2 instance role with ssm:GetParameter.
#
# Usage (on EC2 as root):
#   sudo bash deploy/scripts/sync-env-from-ssm.sh
#   sudo bash deploy/scripts/sync-env-from-ssm.sh /opt/krishifarms/config/application.env
set -euo pipefail

ENV_FILE="${1:-/opt/krishifarms/config/application.env}"
APP_PATH="${APP_PATH:-/opt/krishifarms}"
ENV_TEMPLATE="${ENV_TEMPLATE:-${APP_PATH}/scripts/application.env.example}"
REGION="${AWS_REGION:-ap-south-1}"
SECRET_KEY_PATH="${SSM_SECRET_KEY_PATH:-/krishifarms/dev/app/secret_key}"
DB_PASSWORD_PATH="${SSM_DB_PASSWORD_PATH:-/krishifarms/dev/db/password}"

log() { echo "[$(date -Iseconds)] $*"; }

if ! command -v aws >/dev/null 2>&1; then
  log "ERROR: aws CLI not found — run ec2-bootstrap.sh first (dnf install blocked during deploy)"
  exit 1
fi

ensure_env_file() {
  if [[ -f "$ENV_FILE" ]]; then
    return 0
  fi
  log "WARN: $ENV_FILE not found — creating from template"
  if [[ ! -f "$ENV_TEMPLATE" ]]; then
    log "ERROR: $ENV_FILE not found and no template at $ENV_TEMPLATE. Run ec2-bootstrap.sh or ensure deploy uploads application.env.example to S3."
    exit 1
  fi
  mkdir -p "$(dirname "$ENV_FILE")"
  cp "$ENV_TEMPLATE" "$ENV_FILE"
  chmod 640 "$ENV_FILE"
  if id krishifarms >/dev/null 2>&1; then
    chown root:krishifarms "$ENV_FILE"
  else
    chown root:root "$ENV_FILE"
  fi
  log "Created $ENV_FILE from template (set SSM parameters or edit file before production use)"
}

ensure_env_file

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
