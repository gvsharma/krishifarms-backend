#!/usr/bin/env bash
# Keep daily EC2 start/stop EventBridge Scheduler jobs; stop RDS start/stop.
#
# The Gamya cost Lambda (gamya-couture-dev-cost-scheduler) reads DB_INSTANCE_IDENTIFIER
# to start/stop RDS. Unset it so only EC2_INSTANCE_ID is used.
#
# Also deletes the disabled orphan schedule shutdown-ec2 (broken Lambda target).
#
# Usage:
#   bash deploy/scripts/configure-compute-scheduler-ec2-only.sh
#   bash deploy/scripts/configure-compute-scheduler-ec2-only.sh --dry-run
#
# Requires: AWS CLI, lambda:UpdateFunctionConfiguration, scheduler:DeleteSchedule
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"
LAMBDA_NAME="${COST_SCHEDULER_LAMBDA:-gamya-couture-dev-cost-scheduler}"
EC2_ID="${EC2_INSTANCE_ID:-i-0426cdc00ff15bfe9}"
ORPHAN_SCHEDULE="${ORPHAN_SCHEDULE_NAME:-shutdown-ec2}"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

log() { echo "[$(date -Iseconds)] $*"; }

update_lambda_ec2_only() {
  local cfg env_json new_env
  cfg="$(aws lambda get-function-configuration \
    --region "$REGION" \
    --function-name "$LAMBDA_NAME" \
    --output json)"
  env_json="$(echo "$cfg" | python3 -c "
import json, sys
d = json.load(sys.stdin)
vars = (d.get('Environment') or {}).get('Variables') or {}
vars.pop('DB_INSTANCE_IDENTIFIER', None)
vars['EC2_INSTANCE_ID'] = sys.argv[1]
print(json.dumps({'Variables': vars}))
" "$EC2_ID")"

  if [[ "$DRY_RUN" == true ]]; then
    log "DRY-RUN would update Lambda ${LAMBDA_NAME} env (no DB_INSTANCE_IDENTIFIER):"
    echo "$env_json" | python3 -m json.tool
    return 0
  fi

  aws lambda update-function-configuration \
    --region "$REGION" \
    --function-name "$LAMBDA_NAME" \
    --environment "$env_json" >/dev/null
  log "Updated Lambda ${LAMBDA_NAME}: EC2 only (removed DB_INSTANCE_IDENTIFIER)"
}

delete_orphan_schedule() {
  local group
  group="$(aws scheduler get-schedule \
    --region "$REGION" \
    --name "$ORPHAN_SCHEDULE" \
    --query 'GroupName' \
    --output text 2>/dev/null || echo "")"
  if [[ -z "$group" || "$group" == "None" ]]; then
    log "Orphan schedule ${ORPHAN_SCHEDULE} not found — skip"
    return 0
  fi
  if [[ "$DRY_RUN" == true ]]; then
    log "DRY-RUN would delete schedule ${ORPHAN_SCHEDULE} (group=${group})"
    return 0
  fi
  aws scheduler delete-schedule \
    --region "$REGION" \
    --name "$ORPHAN_SCHEDULE" \
    --group-name "$group"
  log "Deleted orphan schedule ${ORPHAN_SCHEDULE}"
}

log "Region=${REGION} lambda=${LAMBDA_NAME} ec2=${EC2_ID} dry_run=${DRY_RUN}"

update_lambda_ec2_only
delete_orphan_schedule

log "Kept schedules: gamya-couture-dev-compute-start-daily_morning, gamya-couture-dev-compute-stop-daily_morning"
log "RDS gamya-couture-dev-pg will no longer be started/stopped by the cron."
log "Done."
