#!/usr/bin/env bash
# Pull optional secrets from SSM and merge into EC2 application.env.
# Requires: AWS CLI, EC2 instance role with ssm:GetParameter.
#
# DB precedence:
#   1. /krishifarms/dev/db/database_url  → full DATABASE_URL (Supabase / RDS)
#   2. /krishifarms/dev/db/password      → Docker Postgres password + local URL
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
# Full SQLAlchemy URL (Supabase / RDS). When set, takes precedence over Docker Postgres construction.
DB_URL_PATH="${SSM_DB_URL_PATH:-/krishifarms/dev/db/database_url}"
FIREBASE_JSON_PATH="${SSM_FIREBASE_JSON_PATH:-/krishifarms/dev/app/firebase_service_account_json}"
FIREBASE_PROJECT_ID_PATH="${SSM_FIREBASE_PROJECT_ID_PATH:-/krishifarms/dev/app/firebase_project_id}"

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

upsert_quoted() {
  local key="$1"
  local value="$2"
  UPSERT_ENV_FILE="$ENV_FILE" UPSERT_ENV_KEY="$key" UPSERT_ENV_VALUE="$value" python3 <<'PY'
import os
import pathlib
import re

ENV_KEY_PATTERN = re.compile(r"^[A-Z_][A-Z0-9_]*=")


def remove_env_key(text: str, key: str) -> str:
    prefix = f"{key}="
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        if stripped.startswith(prefix):
            i += 1
            while i < len(lines) and not ENV_KEY_PATTERN.match(lines[i].lstrip()):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


path = pathlib.Path(os.environ["UPSERT_ENV_FILE"])
key = os.environ["UPSERT_ENV_KEY"]
value = os.environ["UPSERT_ENV_VALUE"]
escaped = value.replace("\\", "\\\\").replace('"', '\\"')
line = f'{key}="{escaped}"\n'
text = path.read_text() if path.exists() else ""
text = remove_env_key(text, key)
if text and not text.endswith("\n"):
    text += "\n"
text += line
path.write_text(text)
PY
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
minify_firebase_json() {
  local raw="$1"
  FIX_FIREBASE_SCRIPT="${SCRIPT_DIR}/fix-firebase-env.py"
  if [[ -f "$FIX_FIREBASE_SCRIPT" ]]; then
    printf '%s' "$raw" | python3 "$FIX_FIREBASE_SCRIPT" --minify-only
  else
    printf '%s' "$raw" | python3 -c 'import json,sys; print(json.dumps(json.loads(sys.stdin.read()), separators=(",",":")))'
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

# Prefer full DATABASE_URL from SSM (Supabase / external Postgres). Otherwise build Docker URL.
# Use upsert_quoted so ?sslmode=require and special chars in passwords are not mangled by sed.
DB_URL="$(fetch_param "${DB_URL_PATH}")"
if [[ -n "${DB_URL}" && "${DB_URL}" != "None" ]]; then
  log "Syncing DATABASE_URL from ${DB_URL_PATH}"
  upsert_quoted "DATABASE_URL" "${DB_URL}"
else
  DB_PASSWORD="$(fetch_param "${DB_PASSWORD_PATH}")"
  if [[ -n "${DB_PASSWORD}" && "${DB_PASSWORD}" != "None" ]]; then
    log "Syncing POSTGRES_PASSWORD from ${DB_PASSWORD_PATH} (local Docker Postgres)"
    upsert "POSTGRES_PASSWORD" "${DB_PASSWORD}"
    upsert_quoted "DATABASE_URL" "postgresql+psycopg2://krishi:${DB_PASSWORD}@postgres:5432/krishifarms"
  fi
fi

FIREBASE_JSON="$(fetch_param "${FIREBASE_JSON_PATH}")"
if [[ -n "${FIREBASE_JSON}" && "${FIREBASE_JSON}" != "None" ]]; then
  log "Syncing FIREBASE_SERVICE_ACCOUNT_JSON from ${FIREBASE_JSON_PATH}"
  FIREBASE_JSON_MINIFIED="$(minify_firebase_json "${FIREBASE_JSON}")" || {
    log "ERROR: FIREBASE JSON from SSM is not valid JSON — skipping"
    exit 1
  }
  upsert_quoted "FIREBASE_SERVICE_ACCOUNT_JSON" "${FIREBASE_JSON_MINIFIED}"
fi

FIREBASE_PROJECT_ID="$(fetch_param "${FIREBASE_PROJECT_ID_PATH}")"
if [[ -n "${FIREBASE_PROJECT_ID}" && "${FIREBASE_PROJECT_ID}" != "None" ]]; then
  log "Syncing FIREBASE_PROJECT_ID from ${FIREBASE_PROJECT_ID_PATH}"
  upsert "FIREBASE_PROJECT_ID" "${FIREBASE_PROJECT_ID}"
fi

chmod 640 "$ENV_FILE"
chown root:krishifarms "$ENV_FILE"

log "SSM sync complete for ${ENV_FILE}"
