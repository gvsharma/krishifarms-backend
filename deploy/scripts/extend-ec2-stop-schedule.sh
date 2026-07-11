#!/usr/bin/env bash
# Extend shared EC2 daily stop from 11:00 IST → 23:00 IST so mobile/Vercel work in the evening.
#
# Default Gamya schedule: start 06:00 IST, stop 11:00 IST (EC2 off ~13h/day → API timeouts).
#
# Usage:
#   bash deploy/scripts/extend-ec2-stop-schedule.sh
#   bash deploy/scripts/extend-ec2-stop-schedule.sh --dry-run
#   STOP_CRON_IST_HOUR=22 bash deploy/scripts/extend-ec2-stop-schedule.sh
#
# Requires: scheduler:GetSchedule + scheduler:UpdateSchedule
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"
TIMEZONE="${SCHEDULE_TIMEZONE:-Asia/Kolkata}"
STOP_SCHEDULE_NAME="${STOP_SCHEDULE_NAME:-gamya-couture-dev-compute-stop-daily_morning}"
STOP_HOUR="${STOP_CRON_IST_HOUR:-23}"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

log() { echo "[$(date -Iseconds)] $*"; }

if [[ ! "$STOP_HOUR" =~ ^[0-9]+$ ]] || (( STOP_HOUR < 0 || STOP_HOUR > 23 )); then
  echo "STOP_CRON_IST_HOUR must be 0-23" >&2
  exit 1
fi

NEW_EXPRESSION="cron(0 ${STOP_HOUR} * * ? *)"

log "Region=${REGION} schedule=${STOP_SCHEDULE_NAME} new_stop=${NEW_EXPRESSION} (${TIMEZONE})"

CURRENT_JSON="$(aws scheduler get-schedule \
  --region "$REGION" \
  --name "$STOP_SCHEDULE_NAME" \
  --output json)"

OLD_EXPR="$(echo "$CURRENT_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin)['ScheduleExpression'])")"
log "Current stop expression: ${OLD_EXPR}"

if [[ "$OLD_EXPR" == "$NEW_EXPRESSION" ]]; then
  log "Already set to ${NEW_EXPRESSION} — skip"
  exit 0
fi

UPDATE_PAYLOAD="$(echo "$CURRENT_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d['ScheduleExpression'] = sys.argv[1]
# update-schedule accepts subset; drop read-only fields
for key in ('Arn', 'CreationDate', 'LastModificationDate'):
    d.pop(key, None)
print(json.dumps(d))
" "$NEW_EXPRESSION")"

if [[ "$DRY_RUN" == true ]]; then
  log "DRY-RUN would update stop to ${NEW_EXPRESSION}"
  echo "$UPDATE_PAYLOAD" | python3 -m json.tool
  exit 0
fi

echo "$UPDATE_PAYLOAD" | aws scheduler update-schedule \
  --region "$REGION" \
  --cli-input-json file:///dev/stdin \
  >/dev/null

log "Updated ${STOP_SCHEDULE_NAME}: EC2 stops daily at ${STOP_HOUR}:00 ${TIMEZONE}"
log "If EC2 is stopped now: bash deploy/scripts/start-shared-ec2.sh --wait"
