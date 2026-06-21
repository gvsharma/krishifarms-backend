#!/usr/bin/env bash
# Post-deploy API smoke tests for KrishiFarms CRM.
# Usage:
#   ./scripts/smoke-test-api.sh [API_HOST]
#   SMOKE_EMAIL=user@example.com SMOKE_PASSWORD='...' ./scripts/smoke-test-api.sh
set -euo pipefail

API_HOST="${1:-http://127.0.0.1}"
BASE="${API_HOST%/}/api/v1"
FAILED=0
ACCESS_TOKEN=""

log_ok() { echo "  OK  $*"; }
log_fail() { echo "  FAIL $*" >&2; FAILED=1; }

assert_http() {
  local label="$1"
  local expected="$2"
  local url="$3"
  local method="${4:-GET}"
  local body="${5:-}"
  local headers=()
  if [[ -n "$ACCESS_TOKEN" ]]; then
    headers+=(-H "Authorization: Bearer ${ACCESS_TOKEN}")
  fi
  local code
  if [[ -n "$body" ]]; then
    code="$(curl -sS -o /tmp/krishi-smoke-body.txt -w "%{http_code}" -X "$method" "${headers[@]}" \
      -H "Content-Type: application/json" -d "$body" "$url")"
  else
    code="$(curl -sS -o /tmp/krishi-smoke-body.txt -w "%{http_code}" -X "$method" "${headers[@]}" "$url")"
  fi
  if [[ "$code" == "$expected" ]]; then
    log_ok "${label} (${code})"
  else
    log_fail "${label} — expected HTTP ${expected}, got ${code}"
    head -c 200 /tmp/krishi-smoke-body.txt >&2 || true
    echo >&2
  fi
}

echo "== KrishiFarms CRM API smoke tests =="
echo "Host: ${API_HOST}"
echo

echo "== Infrastructure =="
if curl -sf "${BASE}/health" | grep -q '"status"[[:space:]]*:[[:space:]]*"ok"'; then
  log_ok "API health endpoint"
else
  log_fail "API health endpoint"
fi
echo

echo "== Auth (public endpoints) =="
assert_http "POST login missing body" 422 "${BASE}/auth/login" POST '{}'
if [[ -n "${SMOKE_EMAIL:-}" && -n "${SMOKE_PASSWORD:-}" ]]; then
  assert_http "POST login" 200 "${BASE}/auth/login" POST \
    "{\"email\":\"${SMOKE_EMAIL}\",\"password\":\"${SMOKE_PASSWORD}\"}"
  ACCESS_TOKEN="$(python3 -c "
import json
try:
  d=json.load(open('/tmp/krishi-smoke-body.txt'))
  print(d.get('data',{}).get('access_token','') or d.get('data',{}).get('accessToken',''))
except Exception:
  pass
" 2>/dev/null || true)"
  if [[ -n "$ACCESS_TOKEN" ]]; then
    assert_http "GET dashboard summary" 200 "${BASE}/dashboard/summary"
  fi
else
  echo "  SKIP authenticated flows (set SMOKE_EMAIL and SMOKE_PASSWORD secrets)"
fi
echo

if [[ "$FAILED" -ne 0 ]]; then
  echo "Smoke tests FAILED" >&2
  exit 1
fi
echo "All smoke tests passed."
