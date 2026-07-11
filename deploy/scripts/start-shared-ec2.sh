#!/usr/bin/env bash
# Start the shared Gamya/KrishiFarms EC2 if stopped (mobile + Vercel API proxy).
#
# Usage:
#   bash deploy/scripts/start-shared-ec2.sh
#   bash deploy/scripts/start-shared-ec2.sh --wait
#
# Requires: AWS CLI, ec2:DescribeInstances + ec2:StartInstances
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"
INSTANCE_ID="${EC2_INSTANCE_ID:-i-0426cdc00ff15bfe9}"
WAIT=false

if [[ "${1:-}" == "--wait" ]]; then
  WAIT=true
fi

log() { echo "[$(date -Iseconds)] $*"; }

state() {
  aws ec2 describe-instances \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].State.Name' \
    --output text 2>/dev/null || echo "missing"
}

STATUS="$(state)"
log "EC2 ${INSTANCE_ID} state=${STATUS}"

case "${STATUS}" in
  running)
    log "Already running — API should be reachable at http://13.232.200.243:8082"
    exit 0
    ;;
  pending)
    log "Already starting…"
    ;;
  stopped)
    log "Starting instance…"
    aws ec2 start-instances --region "$REGION" --instance-ids "$INSTANCE_ID" >/dev/null
    ;;
  missing|terminated|None)
    log "ERROR: instance ${INSTANCE_ID} not found (${STATUS})" >&2
    exit 1
    ;;
  *)
    log "WARN: unexpected state ${STATUS}" >&2
    ;;
esac

if [[ "$WAIT" == true ]]; then
  log "Waiting for running + status checks…"
  aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"
  aws ec2 wait instance-status-ok --region "$REGION" --instance-ids "$INSTANCE_ID"
  log "EC2 ready. Health: curl -sf http://13.232.200.243:8082/api/v1/health"
fi

log "Done."
