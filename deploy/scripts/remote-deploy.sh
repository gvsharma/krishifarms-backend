#!/usr/bin/env bash
# Idempotent deploy script — runs on EC2 via GitHub Actions (sudo).
# Extracts incoming source bundle, rebuilds Docker Compose stack, runs migrations,
# health-checks, and rolls back on failure.
set -euo pipefail

APP_PATH="${APP_PATH:-/opt/krishifarms}"
REPO_DIR="${APP_PATH}/repo"
COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose.prod.yml}"
INCOMING_ARCHIVE="${APP_PATH}/incoming/deploy.tar.gz"
BACKUP_DIR="${APP_PATH}/backup"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8082/api/v1/health}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-48}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"
KEEP_BACKUPS="${KEEP_BACKUPS:-5}"

log() {
  echo "[$(date -Iseconds)] $*"
}

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    log "ERROR: Run as root (GitHub Actions uses sudo)."
    exit 1
  fi
}

ensure_service_user() {
  if ! id krishifarms >/dev/null 2>&1; then
    log "Creating service user krishifarms (bootstrap was not run)"
    useradd --system --home-dir "${APP_PATH}" --shell /sbin/nologin krishifarms
  fi
}

is_healthy() {
  local response
  response="$(curl -sf "${HEALTH_URL}" 2>/dev/null || true)"
  [[ -n "${response}" ]] && grep -q '"status"[[:space:]]*:[[:space:]]*"ok"' <<< "${response}"
}

dump_diagnostics() {
  log "=== docker compose ps ==="
  docker compose -f "${REPO_DIR}/${COMPOSE_FILE}" ps 2>/dev/null || true
  log "=== api logs (last 40 lines) ==="
  docker compose -f "${REPO_DIR}/${COMPOSE_FILE}" logs --tail=40 api 2>/dev/null || true
  log "=== nginx logs (last 20 lines) ==="
  docker compose -f "${REPO_DIR}/${COMPOSE_FILE}" logs --tail=20 nginx 2>/dev/null || true
}

wait_for_health() {
  local label="$1"
  local attempt
  for attempt in $(seq 1 "${MAX_ATTEMPTS}"); do
    if is_healthy; then
      log "${label}: health check passed"
      return 0
    fi
    log "${label}: attempt ${attempt}/${MAX_ATTEMPTS} — not healthy yet"
    sleep "${SLEEP_SECONDS}"
  done
  return 1
}

prune_backups() {
  local backups
  mapfile -t backups < <(ls -1t "${BACKUP_DIR}/deploy.tar.gz."* 2>/dev/null || true)
  if ((${#backups[@]} <= KEEP_BACKUPS)); then
    return 0
  fi
  local to_delete
  for to_delete in "${backups[@]:KEEP_BACKUPS}"; do
    log "Removing old backup ${to_delete}"
    rm -f "${to_delete}"
  done
}

rollback() {
  local backup_file="$1"
  if [[ ! -f "${backup_file}" ]]; then
    log "ERROR: No backup to restore at ${backup_file}"
    return 1
  fi
  log "Rolling back to ${backup_file}"
  rm -rf "${REPO_DIR}.rollback"
  mv "${REPO_DIR}" "${REPO_DIR}.rollback" || true
  mkdir -p "${REPO_DIR}"
  tar -xzf "${backup_file}" -C "${REPO_DIR}"
  chown -R ec2-user:krishifarms "${REPO_DIR}"
  cd "${REPO_DIR}"
  docker compose -f "${COMPOSE_FILE}" up -d --build --remove-orphans
  wait_for_health "rollback" || return 1
  return 0
}

sync_runtime_env() {
  local env_file="${APP_PATH}/config/application.env"
  local target="${REPO_DIR}/.env"
  if [[ ! -f "${env_file}" ]]; then
    log "ERROR: ${env_file} missing"
    exit 1
  fi
  cp "${env_file}" "${target}"
  chmod 640 "${target}"
  chown ec2-user:krishifarms "${target}"
  log "Synced ${env_file} → ${target}"
}

require_root
ensure_service_user

mkdir -p "${REPO_DIR}" "${BACKUP_DIR}" "${APP_PATH}/logs"
chown -R ec2-user:krishifarms "${APP_PATH}/logs"

if [[ ! -f "${INCOMING_ARCHIVE}" ]]; then
  log "ERROR: Incoming deploy bundle not found at ${INCOMING_ARCHIVE}"
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/deploy.tar.gz.${TIMESTAMP}"

if [[ -d "${REPO_DIR}/infra" ]]; then
  log "Backing up current repo → ${BACKUP_FILE}"
  tar -czf "${BACKUP_FILE}" -C "${REPO_DIR}" .
else
  log "No existing deployment — first deploy"
  BACKUP_FILE=""
fi

log "Extracting incoming deploy bundle"
rm -rf "${REPO_DIR}.new"
mkdir -p "${REPO_DIR}.new"
tar -xzf "${INCOMING_ARCHIVE}" -C "${REPO_DIR}.new"
rm -rf "${REPO_DIR}"
mv "${REPO_DIR}.new" "${REPO_DIR}"
chown -R ec2-user:krishifarms "${REPO_DIR}"

sync_runtime_env

log "Building and starting Docker Compose stack"
cd "${REPO_DIR}"
docker compose -f "${COMPOSE_FILE}" up -d --build --remove-orphans

log "Running database migrations"
docker compose -f "${COMPOSE_FILE}" exec -T api alembic upgrade head

if wait_for_health "deploy"; then
  prune_backups
  rm -f "${INCOMING_ARCHIVE}"
  log "Deployment successful"
  exit 0
fi

log "ERROR: New version failed health check"
dump_diagnostics
if [[ -n "${BACKUP_FILE}" ]]; then
  rollback "${BACKUP_FILE}" || true
fi
exit 1
