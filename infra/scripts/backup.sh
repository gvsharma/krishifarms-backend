#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/tmp/krishifarms-backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
FILENAME="krishifarms_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

docker compose -f infra/docker-compose.yml exec -T postgres \
  pg_dump -U krishi krishifarms | gzip > "${BACKUP_DIR}/${FILENAME}"

echo "Backup created: ${BACKUP_DIR}/${FILENAME}"

if [[ -n "${S3_BACKUP_BUCKET:-}" ]]; then
  aws s3 cp "${BACKUP_DIR}/${FILENAME}" "s3://${S3_BACKUP_BUCKET}/db-backups/${FILENAME}"
  echo "Backup uploaded to s3://${S3_BACKUP_BUCKET}/db-backups/${FILENAME}"
fi
