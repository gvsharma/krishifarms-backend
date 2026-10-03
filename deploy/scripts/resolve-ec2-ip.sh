#!/usr/bin/env bash
# Resolve the current public IP / DNS of the shared EC2 host (dynamic-IP safe).
#
# Usage:
#   bash deploy/scripts/resolve-ec2-ip.sh
#   bash deploy/scripts/resolve-ec2-ip.sh --dns
#   EC2_INSTANCE_ID=i-xxxx bash deploy/scripts/resolve-ec2-ip.sh
#
# Prints the instance's current public IPv4 address (default) or public DNS
# name (--dns). Returns non-zero when the instance has no public IP
# (stopped, or in a private subnet without an Elastic IP).
#
# After the Elastic IP is released (see docs/deploy/DYNAMIC_IP.md), the
# public IP changes on every stop/start — always resolve it live with this
# script instead of copying an IP from docs, chat, or GitHub variables.
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"
INSTANCE_ID="${EC2_INSTANCE_ID:-i-0426cdc00ff15bfe9}"
FIELD="PublicIpAddress"

if [[ "${1:-}" == "--dns" ]]; then
  FIELD="PublicDnsName"
fi

VALUE="$(aws ec2 describe-instances \
  --region "$REGION" \
  --instance-ids "$INSTANCE_ID" \
  --query "Reservations[0].Instances[0].${FIELD}" \
  --output text 2>/dev/null || echo "None")"

if [[ -z "$VALUE" || "$VALUE" == "None" ]]; then
  echo "ERROR: instance ${INSTANCE_ID} has no ${FIELD} (stopped? no Elastic IP?)." >&2
  echo "Start it first: bash deploy/scripts/start-shared-ec2.sh --wait" >&2
  exit 1
fi

echo "$VALUE"
