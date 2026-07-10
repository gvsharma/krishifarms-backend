#!/usr/bin/env bash
# Remove EventBridge Scheduler jobs that start/stop EC2 + RDS on a daily cron.
# KrishiFarms on Supabase no longer needs nightly EC2/RDS cycling; shared Gamya
# schedules also stop i-0426cdc00ff15bfe9 (Krishi API host).
#
# Usage:
#   bash deploy/scripts/delete-compute-schedules.sh              # delete known + list orphans
#   bash deploy/scripts/delete-compute-schedules.sh --dry-run    # print only
#
# Requires: AWS CLI, IAM scheduler:DeleteSchedule + scheduler:ListSchedules
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

# Known schedules (ap-south-1, account 085863558134 as of 2026-07-10)
KNOWN_NAMES=(
  "gamya-couture-dev-compute-start-daily_morning"
  "gamya-couture-dev-compute-stop-daily_morning"
  "shutdown-ec2"
)

log() { echo "[$(date -Iseconds)] $*"; }

delete_schedule() {
  local name="$1"
  local group="${2:-default}"
  if [[ "$DRY_RUN" == true ]]; then
    log "DRY-RUN would delete schedule name=${name} group=${group}"
    return 0
  fi
  if aws scheduler delete-schedule \
    --region "$REGION" \
    --name "$name" \
    --group-name "$group" 2>/dev/null; then
    log "Deleted schedule ${name} (group=${group})"
  else
    log "WARN: could not delete ${name} in group ${group} (missing or wrong group)"
  fi
}

resolve_group() {
  local name="$1"
  aws scheduler get-schedule \
    --region "$REGION" \
    --name "$name" \
    --query 'GroupName' \
    --output text 2>/dev/null || echo ""
}

log "Region=${REGION} dry_run=${DRY_RUN}"

for name in "${KNOWN_NAMES[@]}"; do
  group="$(resolve_group "$name")"
  if [[ -z "$group" || "$group" == "None" ]]; then
    log "Skip ${name} — not found"
    continue
  fi
  delete_schedule "$name" "$group"
done

log "Listing remaining schedules in ${REGION}:"
mapfile -t REMAINING < <(
  aws scheduler list-schedules --region "$REGION" \
    --query 'Schedules[].{Name:Name,Group:GroupName,State:State,Schedule:ScheduleExpression}' \
    --output text 2>/dev/null || true
)

if ((${#REMAINING[@]} == 0)); then
  log "No EventBridge Scheduler schedules remain."
else
  printf '%s\n' "${REMAINING[@]}"
  log "Review any remaining schedules above; re-run with manual deletes if needed."
fi

log "Done. EC2 i-0426cdc00ff15bfe9 will no longer auto stop/start on cron."
log "Optional cleanup: delete Lambda gamya-couture-dev-cost-scheduler / shutDownEc2 if unused."
