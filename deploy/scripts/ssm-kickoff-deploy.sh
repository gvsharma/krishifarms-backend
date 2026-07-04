#!/usr/bin/env bash
# Runs on EC2 (via nohup from a short SSM kickoff command).
# Downloads artifacts from S3, syncs env, runs remote-deploy.sh, writes deploy.status.
set -euo pipefail

APP_PATH="${APP_PATH:-/opt/krishifarms}"
DEPLOY_BUCKET="${DEPLOY_BUCKET:?DEPLOY_BUCKET is required}"
AWS_REGION="${AWS_REGION:-ap-south-1}"
export AWS_REGION AWS_DEFAULT_REGION="${AWS_REGION}"

LOG_DIR="${APP_PATH}/logs"
STATUS_FILE="${LOG_DIR}/deploy.status"
DEPLOY_LOG="${LOG_DIR}/deploy.latest.log"
ARCHIVE_KEY="${DEPLOY_OBJECT_KEY:-incoming/deploy.tar.gz}"
SCRIPT_KEY="${DEPLOY_SCRIPT_KEY:-incoming/remote-deploy.sh}"
SYNC_KEY="${DEPLOY_SYNC_SCRIPT_KEY:-incoming/sync-env-from-ssm.sh}"

log() {
  echo "[$(date -Iseconds)] $*" | tee -a "${DEPLOY_LOG}"
}

mark_status() {
  echo "$1" > "${STATUS_FILE}"
}

on_error() {
  local exit_code=$?
  if [[ -f "${STATUS_FILE}" ]] && [[ "$(cat "${STATUS_FILE}")" == "running" ]]; then
    mark_status "failed"
    log "Deploy aborted unexpectedly (exit ${exit_code})"
  fi
  exit "${exit_code}"
}

trap on_error ERR

require_aws_cli() {
  if command -v aws >/dev/null 2>&1; then
    return 0
  fi
  log "ERROR: aws CLI not found on EC2 — run ec2-bootstrap.sh first"
  exit 1
}

ensure_runtime_user() {
  if ! id krishifarms >/dev/null 2>&1; then
    log "Creating service user krishifarms (bootstrap was not run)"
    useradd --system --home-dir "${APP_PATH}" --shell /sbin/nologin krishifarms
  fi
  usermod -aG docker ec2-user 2>/dev/null || true
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    log "ERROR: docker not found on EC2 — run ec2-bootstrap.sh first"
    exit 1
  fi
  if ! docker compose version >/dev/null 2>&1; then
    log "ERROR: docker compose plugin not found — run ec2-bootstrap.sh first"
    exit 1
  fi
}

main() {
  mkdir -p "${APP_PATH}/incoming" "${APP_PATH}/scripts" "${APP_PATH}/repo" \
    "${APP_PATH}/backup" "${LOG_DIR}" "${APP_PATH}/config"
  : > "${DEPLOY_LOG}"
  mark_status "running"
  log "Deploy started (bucket=${DEPLOY_BUCKET}, region=${AWS_REGION})"

  require_aws_cli
  require_docker
  ensure_runtime_user

  ENV_TEMPLATE_KEY="${DEPLOY_ENV_TEMPLATE_KEY:-incoming/application.env.example}"

  log "Downloading deploy scripts from S3"
  aws s3 cp "s3://${DEPLOY_BUCKET}/${SYNC_KEY}" "${APP_PATH}/scripts/sync-env-from-ssm.sh"
  aws s3 cp "s3://${DEPLOY_BUCKET}/${SCRIPT_KEY}" "${APP_PATH}/scripts/remote-deploy.sh"
  aws s3 cp "s3://${DEPLOY_BUCKET}/${ENV_TEMPLATE_KEY}" "${APP_PATH}/scripts/application.env.example" \
    || log "WARN: application.env.example not in S3 — sync-env must find an existing config file"
  chmod 755 "${APP_PATH}/scripts/sync-env-from-ssm.sh" "${APP_PATH}/scripts/remote-deploy.sh"

  log "Downloading deploy bundle from S3"
  aws s3 cp "s3://${DEPLOY_BUCKET}/${ARCHIVE_KEY}" "${APP_PATH}/incoming/deploy.tar.gz"

  log "Syncing secrets into application.env"
  sudo APP_PATH="${APP_PATH}" ENV_TEMPLATE="${APP_PATH}/scripts/application.env.example" \
    bash "${APP_PATH}/scripts/sync-env-from-ssm.sh" "${APP_PATH}/config/application.env"

  log "Running remote-deploy.sh"
  if sudo APP_PATH="${APP_PATH}" bash "${APP_PATH}/scripts/remote-deploy.sh" >> "${DEPLOY_LOG}" 2>&1; then
    mark_status "success"
    log "Deploy finished successfully"
    exit 0
  fi

  mark_status "failed"
  log "Deploy failed — see ${DEPLOY_LOG}"
  exit 1
}

main "$@"
