#!/usr/bin/env bash
# One-time: attach SSM + scheduler permissions to the GitHub OIDC backend deploy role.
# Run with admin AWS credentials (not the deploy role itself).
#
# Usage:
#   bash deploy/scripts/attach-github-deploy-iam-supabase-policy.sh
#   DEPLOY_ROLE_NAME=krishifarms-dev-gh-be-deploy-... bash deploy/scripts/attach-github-deploy-iam-supabase-policy.sh
#
# After attach: add GitHub secret SUPABASE_DB_PASSWORD on gvsharma/krishifarms-backend, then re-run deploy.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POLICY_FILE="${SCRIPT_DIR}/../iam/github-backend-deploy-ssm-supabase.json"
POLICY_NAME="${INLINE_POLICY_NAME:-krishifarms-deploy-ssm-supabase}"
ROLE_NAME="${DEPLOY_ROLE_NAME:-krishifarms-dev-gh-be-deploy-20260621161619959700000003}"

if [[ ! -f "${POLICY_FILE}" ]]; then
  echo "ERROR: policy file not found: ${POLICY_FILE}" >&2
  exit 1
fi

echo "Attaching inline policy ${POLICY_NAME} to role ${ROLE_NAME}…"
aws iam put-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-name "${POLICY_NAME}" \
  --policy-document "file://${POLICY_FILE}"

echo "Done. Verify:"
echo "  aws iam get-role-policy --role-name ${ROLE_NAME} --policy-name ${POLICY_NAME}"
echo "Next: set SUPABASE_DB_PASSWORD on gvsharma/krishifarms-backend → re-run Deploy workflow"
