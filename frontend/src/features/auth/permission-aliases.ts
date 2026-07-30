/**
 * Backend permission codes (OpenAPI / require_permission) ↔ mobile catalog strings (/auth/me).
 * Web PermissionGuard uses backend codes; API returns mobile strings from permission_catalog.py.
 */
export const BACKEND_TO_MOBILE: Record<string, string> = {
  "farmers:read": "FARMER_VIEW",
  "farmers:create": "FARMER_CREATE",
  "farmers:update": "FARMER_UPDATE",
  "farmers:delete": "FARMER_DELETE",
  "procurements:read": "PROCUREMENT_VIEW",
  "procurements:create": "PROCUREMENT_CREATE",
  "procurements:update": "PROCUREMENT_UPDATE",
  "procurements:confirm": "PROCUREMENT_APPROVE",
  "procurements:cancel": "PROCUREMENT_DELETE",
  "farmer_payments:read": "PAYMENT_VIEW",
  "farmer_payments:create": "PAYMENT_CREATE",
  "farmer_payments:reverse": "PAYMENT_DELETE",
  "expenses:read": "EXPENSE_VIEW",
  "expenses:create": "EXPENSE_CREATE",
  "expenses:update": "EXPENSE_UPDATE",
  "expenses:delete": "EXPENSE_DELETE",
  "collections:read": "COLLECTION_VIEW",
  "collections:create": "COLLECTION_CREATE",
  "field_services:read": "FIELD_SERVICE_VIEW",
  "field_services:create": "FIELD_SERVICE_CREATE",
  "field_services:update": "FIELD_SERVICE_UPDATE",
  "field_services:delete": "FIELD_SERVICE_DELETE",
  "documents:read": "DOCUMENT_VIEW",
  "documents:create": "DOCUMENT_CREATE",
  "documents:delete": "DOCUMENT_DELETE",
  "users:read": "USER_MANAGE",
  "users:create": "USER_CREATE",
  "users:update": "USER_MANAGE",
  "users:delete": "USER_MANAGE",
  "roles:read": "USER_MANAGE",
  "dashboard:read": "REPORT_VIEW",
  "hamali_work:read": "HAMALI_VIEW",
  "hamali_work:create": "HAMALI_WORK_MANAGE",
  "hamali_work:update": "HAMALI_WORK_MANAGE",
  "hamali_work:delete": "HAMALI_WORK_MANAGE",
  "workers:read": "HAMALI_WORK_MANAGE",
  "workers:create": "HAMALI_WORK_MANAGE",
  "audit:read": "REPORT_VIEW",
  "approve": "PAYMENT_APPROVE",
};

export function permissionMatches(holdings: string[], required: string): boolean {
  if (holdings.includes(required)) return true;
  const mobile = BACKEND_TO_MOBILE[required];
  if (mobile && holdings.includes(mobile)) return true;
  const backendCodes = Object.entries(BACKEND_TO_MOBILE)
    .filter(([, mob]) => mob === required)
    .map(([backend]) => backend);
  return backendCodes.some((code) => holdings.includes(code));
}
