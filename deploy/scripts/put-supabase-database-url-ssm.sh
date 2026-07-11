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

build_and_verify_database_url() {
  # Writes URL to out_file — NEVER print it on stdout.
  # GitHub Actions secret masking replaces the password with "***" in captured
  # command output, which would otherwise corrupt DATABASE_URL written to SSM.
  local password="$1"
  local host="$2"
  local out_file="$3"
  python3 - "$PROJECT_REF" "$password" "$host" "$CONNECTION_MODE" "$out_file" <<'PY'
import subprocess
import sys
from pathlib import Path

project_ref, password, host, mode, out_file = sys.argv[1:6]

try:
    import psycopg2
    from sqlalchemy.engine import URL
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "psycopg2-binary", "sqlalchemy", "-q"],
    )
    import importlib

    psycopg2 = importlib.import_module("psycopg2")
    URL = importlib.import_module("sqlalchemy.engine").URL

password = password.strip()
if not password:
    sys.stderr.write("ERROR: empty password after trimming whitespace\n")
    sys.exit(1)

if mode == "pooler":
    username = f"postgres.{project_ref}"
    connect_host = host
elif mode == "direct":
    username = "postgres"
    connect_host = f"db.{project_ref}.supabase.co"
else:
    sys.stderr.write("ERROR: SUPABASE_CONNECTION_MODE must be pooler or direct\n")
    sys.exit(1)

try:
    conn = psycopg2.connect(
        host=connect_host,
        port=5432,
        dbname="postgres",
        user=username,
        password=password,
        sslmode="require",
        connect_timeout=15,
    )
    conn.close()
except Exception as exc:
    sys.stderr.write(
        f"ERROR: Supabase connection failed for user {username} @ {connect_host}: {exc}\n"
    )
    sys.stderr.write(
        "Check SUPABASE_DB_PASSWORD is the raw database password from "
        "Dashboard → Project Settings → Database (not API keys, not URL-encoded).\n"
    )
    sys.exit(1)

database_url = str(
    URL.create(
        drivername="postgresql+psycopg2",
        username=username,
        password=password,
        host=connect_host,
        port=5432,
        database="postgres",
        query={"sslmode": "require"},
    )
)
Path(out_file).write_text(database_url, encoding="utf-8")
print(f"ok user={username} host={connect_host}", flush=True)
PY
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

# Trim accidental whitespace/newlines from GitHub secrets paste
PASSWORD="$(printf '%s' "${PASSWORD}" | tr -d '\r\n')"

if [[ -z "${PASSWORD}" ]]; then
  echo "ERROR: empty password" >&2
  exit 1
fi

if [[ "${#PASSWORD}" -lt 8 || "${PASSWORD}" == "***" ]]; then
  echo "ERROR: SUPABASE_DB_PASSWORD looks invalid (len=${#PASSWORD}). Re-paste the full database password into the GitHub secret (not '***' or a truncated value)." >&2
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

URL_FILE="$(mktemp)"
trap 'rm -f "${URL_FILE}"' EXIT

log "Verifying Supabase credentials before writing SSM…"
build_and_verify_database_url "${PASSWORD}" "${POOLER_HOST}" "${URL_FILE}"
DATABASE_URL="$(<"${URL_FILE}")"

if [[ -z "${DATABASE_URL}" || "${DATABASE_URL}" == *":***@"* ]]; then
  echo "ERROR: DATABASE_URL missing or corrupted (secret-masking?). Refusing to write SSM." >&2
  exit 1
fi

log "Writing SecureString ${PARAM_NAME} (region ${REGION}, mode=${CONNECTION_MODE})…"

aws ssm put-parameter \
  --region "${REGION}" \
  --name "${PARAM_NAME}" \
  --type SecureString \
  --value "${DATABASE_URL}" \
  --overwrite >/dev/null

log "Done. Re-run Deploy workflow on main."
