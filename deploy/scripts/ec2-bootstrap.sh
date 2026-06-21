#!/usr/bin/env bash
# One-time EC2 bootstrap for Docker Compose deployments from GitHub Actions.
# Run on the instance as root (Session Manager or SSH):
#   sudo bash deploy/scripts/ec2-bootstrap.sh
set -euo pipefail

APP_PATH="${APP_PATH:-/opt/krishifarms}"
SERVICE_USER="krishifarms"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

log() { echo "[$(date -Iseconds)] $*"; }

if [[ "${EUID}" -ne 0 ]]; then
  log "ERROR: Run as root (sudo)."
  exit 1
fi

log "Installing Docker and Compose plugin"
if ! command -v docker >/dev/null 2>&1; then
  dnf install -y docker
  systemctl enable --now docker
fi
if ! docker compose version >/dev/null 2>&1; then
  dnf install -y docker-compose-plugin || true
fi

log "Creating service user: ${SERVICE_USER}"
if ! id "${SERVICE_USER}" >/dev/null 2>&1; then
  useradd --system --home-dir "${APP_PATH}" --shell /sbin/nologin "${SERVICE_USER}"
fi
usermod -aG docker ec2-user 2>/dev/null || true

log "Creating application directories under ${APP_PATH}"
mkdir -p "${APP_PATH}"/{repo,backup,config,logs,scripts,incoming}
chown -R "${SERVICE_USER}:${SERVICE_USER}" "${APP_PATH}"
chmod 750 "${APP_PATH}"
chown ec2-user:"${SERVICE_USER}" "${APP_PATH}/incoming" "${APP_PATH}/scripts" "${APP_PATH}/repo"
chmod 775 "${APP_PATH}/incoming" "${APP_PATH}/scripts" "${APP_PATH}/repo"
chmod 750 "${APP_PATH}/config" "${APP_PATH}/backup" "${APP_PATH}/logs"

if [[ ! -f "${APP_PATH}/config/application.env" ]]; then
  log "Creating ${APP_PATH}/config/application.env from template"
  cp "${REPO_ROOT}/deploy/env/application.env.example" "${APP_PATH}/config/application.env"
  chmod 640 "${APP_PATH}/config/application.env"
  chown root:"${SERVICE_USER}" "${APP_PATH}/config/application.env"
  log "IMPORTANT: Edit ${APP_PATH}/config/application.env with real secrets before first deploy."
fi

log "Configuring passwordless deploy for ec2-user (GitHub Actions via SSM)"
SUDOERS_FILE="/etc/sudoers.d/krishifarms-deploy"
cat > "${SUDOERS_FILE}" <<EOF
# GitHub Actions: allow ec2-user to run the deploy script as root
ec2-user ALL=(root) NOPASSWD: ${APP_PATH}/scripts/remote-deploy.sh
EOF
chmod 440 "${SUDOERS_FILE}"
visudo -cf "${SUDOERS_FILE}"

log "Installing remote deploy script"
install -m 755 "${REPO_ROOT}/deploy/scripts/remote-deploy.sh" \
  "${APP_PATH}/scripts/remote-deploy.sh"

log "Bootstrap complete."
log "Next steps:"
log "  1. Edit ${APP_PATH}/config/application.env (SECRET_KEY, POSTGRES_PASSWORD, CORS_ORIGINS)"
log "  2. Configure GitHub Actions secrets (see docs/deploy/CI_CD.md)"
log "  3. Merge to main — workflow deploys automatically via SSM"
