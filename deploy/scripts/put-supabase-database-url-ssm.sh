#!/usr/bin/env bash
# Prompt for Supabase DB password and write SecureString SSM parameter
# /krishifarms/dev/db/database_url for project ucvwtoziiqgmcyzxkwxe.
#
# Does NOT print the password. Does NOT commit anything.
#
# Usage:
#   bash deploy/scripts/put-supabase-database-url-ssm.sh
#   SUPABASE_DB_PASSWORD='...' bash deploy/scripts/put-supabase-database-url-ssm.sh  # non-interactive
#
# Requires: aws CLI, permission ssm:PutParameter on /krishifarms/dev/db/*
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"
PARAM_NAME="${SSM_DB_URL_PATH:-/krishifarms/dev/db/database_url}"
PROJECT_REF="${SUPABASE_PROJECT_REF:-ucvwtoziiqgmcyzxkwxe}"
# EC2 has no IPv6 route; db.<ref>.supabase.co resolves to IPv6 → "Cannot assign requested address".
# Session pooler uses IPv4-friendly host (works for app + alembic on EC2).
CONNECTION_MODE="${SUPABASE_CONNECTION_MODE:-pooler}"
POOLER_REGION="${SUPABASE_POOLER_REGION:-ap-south-1}"

build_database_url() {
  local encoded="$1"
  case "${CONNECTION_MODE}" in
    pooler)
      local host="aws-0-${POOLER_REGION}.pooler.supabase.com"
      echo "postgresql+psycopg2://postgres.${PROJECT_REF}:${encoded}@${host}:5432/postgres?sslmode=require"
      ;;
    direct)
      echo "postgresql+psycopg2://postgres:${encoded}@db.${PROJECT_REF}.supabase.co:5432/postgres?sslmode=require"
      ;;
    *)
      echo "ERROR: SUPABASE_CONNECTION_MODE must be pooler or direct" >&2
      exit 1
      ;;
  esac
}

urlencode() {
  # Minimal encode for password special chars in URI userinfo
  python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}

if [[ -n "${SUPABASE_DB_PASSWORD:-}" ]]; then
  PASSWORD="${SUPABASE_DB_PASSWORD}"
else
  if [[ ! -t 0 ]]; then
    echo "ERROR: set SUPABASE_DB_PASSWORD or run interactively to enter the password." >&2
    exit 1
  fi
  read -r -s -p "Supabase database password for ${PROJECT_REF}: " PASSWORD
  echo
fi

if [[ -z "${PASSWORD}" ]]; then
  echo "ERROR: empty password" >&2
  exit 1
fi

ENCODED="$(urlencode "${PASSWORD}")"
DATABASE_URL="$(build_database_url "${ENCODED}")"

echo "Writing SecureString ${PARAM_NAME} (region ${REGION})…"
echo "Connection mode: ${CONNECTION_MODE} (password redacted)"

aws ssm put-parameter \
  --region "${REGION}" \
  --name "${PARAM_NAME}" \
  --type SecureString \
  --value "${DATABASE_URL}" \
  --overwrite >/dev/null

echo "Done. Next:"
echo "  1. Merge chore/supabase-db-migration → main (or deploy Compose/SSM script changes)"
echo "  2. On EC2: sudo APP_PATH=/opt/krishifarms bash /opt/krishifarms/scripts/sync-env-from-ssm.sh"
echo "  3. alembic upgrade head && python scripts/seed.py (local or on EC2 api container)"
echo "See docs/deploy/SUPABASE_MIGRATION.md"
