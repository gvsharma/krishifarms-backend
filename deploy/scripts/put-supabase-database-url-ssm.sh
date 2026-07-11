#!/usr/bin/env bash
# Prompt for Supabase DB password and write SecureString SSM parameter
# /krishifarms/dev/db/database_url for project ucvwtoziiqgmcyzxkwxe.
#
# EC2 cannot use direct db.<ref>.supabase.co (IPv6-only on free tier).
# Uses session pooler (IPv4). Pooler host varies (aws-0/aws-1 + region) — copy from
# Dashboard → Project Settings → Database → Connection string, or set SUPABASE_POOLER_HOST.
#
# Usage:
#   bash deploy/scripts/put-supabase-database-url-ssm.sh
#   SUPABASE_DB_PASSWORD='...' bash deploy/scripts/put-supabase-database-url-ssm.sh
#   SUPABASE_POOLER_HOST='aws-1-ap-southeast-1.pooler.supabase.com' SUPABASE_DB_PASSWORD='...' bash ...
#
# Requires: aws CLI, permission ssm:PutParameter on /krishifarms/dev/db/*
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"
PARAM_NAME="${SSM_DB_URL_PATH:-/krishifarms/dev/db/database_url}"
PROJECT_REF="${SUPABASE_PROJECT_REF:-ucvwtoziiqgmcyzxkwxe}"
CONNECTION_MODE="${SUPABASE_CONNECTION_MODE:-pooler}"

log() { echo "[put-supabase] $*"; }

urlencode() {
  python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}

discover_pooler_host() {
  local password="$1"
  python3 - "$PROJECT_REF" "$password" <<'PY'
import subprocess
import sys

project_ref, password = sys.argv[1], sys.argv[2]

try:
    import psycopg2
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"],
    )
    import importlib

    psycopg2 = importlib.import_module("psycopg2")

regions = [
    "ap-northeast-1",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "eu-west-1",
    "eu-central-1",
]
prefixes = ["aws-0", "aws-1", "aws-2"]
user = f"postgres.{project_ref}"

for prefix in prefixes:
    for region in regions:
        host = f"{prefix}-{region}.pooler.supabase.com"
        try:
            conn = psycopg2.connect(
                host=host,
                port=5432,
                dbname="postgres",
                user=user,
                password=password,
                sslmode="require",
                connect_timeout=8,
            )
            conn.close()
            print(host)
            sys.exit(0)
        except Exception:
            continue

sys.stderr.write(
    "ERROR: Could not find working pooler host. Set SUPABASE_POOLER_HOST from "
    "Supabase Dashboard → Settings → Database → Connection string (Session pooler).\n"
)
sys.exit(1)
PY
}

build_database_url() {
  local encoded="$1"
  local host="$2"
  case "${CONNECTION_MODE}" in
    pooler)
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

POOLER_HOST="${SUPABASE_POOLER_HOST:-}"
if [[ "${CONNECTION_MODE}" == "pooler" && -z "${POOLER_HOST}" ]]; then
  log "Discovering session pooler host for project ${PROJECT_REF}…"
  POOLER_HOST="$(discover_pooler_host "${PASSWORD}")"
  log "Discovered pooler host: ${POOLER_HOST}"
elif [[ "${CONNECTION_MODE}" == "pooler" ]]; then
  log "Using SUPABASE_POOLER_HOST=${POOLER_HOST}"
fi

ENCODED="$(urlencode "${PASSWORD}")"
DATABASE_URL="$(build_database_url "${ENCODED}" "${POOLER_HOST}")"

log "Writing SecureString ${PARAM_NAME} (region ${REGION}, mode=${CONNECTION_MODE})…"

aws ssm put-parameter \
  --region "${REGION}" \
  --name "${PARAM_NAME}" \
  --type SecureString \
  --value "${DATABASE_URL}" \
  --overwrite >/dev/null

log "Done. Re-run Deploy workflow on main."
