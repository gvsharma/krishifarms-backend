"""Mobile RBAC permission catalog — server-owned role → permission mappings.

Permissions use the mobile contract (FARMER_VIEW, …). Roles are informational;
the permissions list in login/refresh responses is authoritative for the client.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# All mobile permission strings (mirrors Android Permission.kt / RBAC plan §5.1)
# ---------------------------------------------------------------------------

FARMER_VIEW = "FARMER_VIEW"
FARMER_CREATE = "FARMER_CREATE"
FARMER_UPDATE = "FARMER_UPDATE"
FARMER_DELETE = "FARMER_DELETE"

FARM_VIEW = "FARM_VIEW"
FARM_CREATE = "FARM_CREATE"
FARM_UPDATE = "FARM_UPDATE"
FARM_DELETE = "FARM_DELETE"

PROCUREMENT_VIEW = "PROCUREMENT_VIEW"
PROCUREMENT_CREATE = "PROCUREMENT_CREATE"
PROCUREMENT_UPDATE = "PROCUREMENT_UPDATE"
PROCUREMENT_APPROVE = "PROCUREMENT_APPROVE"
PROCUREMENT_DELETE = "PROCUREMENT_DELETE"

EXPENSE_VIEW = "EXPENSE_VIEW"
EXPENSE_CREATE = "EXPENSE_CREATE"
EXPENSE_UPDATE = "EXPENSE_UPDATE"
EXPENSE_APPROVE = "EXPENSE_APPROVE"
EXPENSE_DELETE = "EXPENSE_DELETE"

PAYMENT_VIEW = "PAYMENT_VIEW"
PAYMENT_CREATE = "PAYMENT_CREATE"
PAYMENT_APPROVE = "PAYMENT_APPROVE"
PAYMENT_DELETE = "PAYMENT_DELETE"

COLLECTION_VIEW = "COLLECTION_VIEW"
COLLECTION_CREATE = "COLLECTION_CREATE"
COLLECTION_UPDATE = "COLLECTION_UPDATE"

WORKER_VIEW = "WORKER_VIEW"
WORKER_CREATE = "WORKER_CREATE"
WORKER_UPDATE = "WORKER_UPDATE"
WORKER_DELETE = "WORKER_DELETE"

WORK_ORDER_VIEW = "WORK_ORDER_VIEW"
WORK_ORDER_CREATE = "WORK_ORDER_CREATE"
WORK_ORDER_UPDATE = "WORK_ORDER_UPDATE"
WORK_ORDER_COMPLETE = "WORK_ORDER_COMPLETE"

ATTENDANCE_VIEW = "ATTENDANCE_VIEW"
ATTENDANCE_UPDATE = "ATTENDANCE_UPDATE"

DOCUMENT_VIEW = "DOCUMENT_VIEW"
DOCUMENT_CREATE = "DOCUMENT_CREATE"
DOCUMENT_DELETE = "DOCUMENT_DELETE"

REPORT_VIEW = "REPORT_VIEW"
REPORT_EXPORT = "REPORT_EXPORT"

SETTINGS_VIEW = "SETTINGS_VIEW"
SETTINGS_MANAGE = "SETTINGS_MANAGE"
USER_MANAGE = "USER_MANAGE"
SYNC_MANAGE = "SYNC_MANAGE"

VEHICLE_VIEW = "VEHICLE_VIEW"
TRIP_VIEW = "TRIP_VIEW"
ASSET_VIEW = "ASSET_VIEW"
RENTAL_VIEW = "RENTAL_VIEW"

ALL_MOBILE_PERMISSIONS: frozenset[str] = frozenset(
    [
        FARMER_VIEW,
        FARMER_CREATE,
        FARMER_UPDATE,
        FARMER_DELETE,
        FARM_VIEW,
        FARM_CREATE,
        FARM_UPDATE,
        FARM_DELETE,
        PROCUREMENT_VIEW,
        PROCUREMENT_CREATE,
        PROCUREMENT_UPDATE,
        PROCUREMENT_APPROVE,
        PROCUREMENT_DELETE,
        EXPENSE_VIEW,
        EXPENSE_CREATE,
        EXPENSE_UPDATE,
        EXPENSE_APPROVE,
        EXPENSE_DELETE,
        PAYMENT_VIEW,
        PAYMENT_CREATE,
        PAYMENT_APPROVE,
        PAYMENT_DELETE,
        COLLECTION_VIEW,
        COLLECTION_CREATE,
        COLLECTION_UPDATE,
        WORKER_VIEW,
        WORKER_CREATE,
        WORKER_UPDATE,
        WORKER_DELETE,
        WORK_ORDER_VIEW,
        WORK_ORDER_CREATE,
        WORK_ORDER_UPDATE,
        WORK_ORDER_COMPLETE,
        ATTENDANCE_VIEW,
        ATTENDANCE_UPDATE,
        DOCUMENT_VIEW,
        DOCUMENT_CREATE,
        DOCUMENT_DELETE,
        REPORT_VIEW,
        REPORT_EXPORT,
        SETTINGS_VIEW,
        SETTINGS_MANAGE,
        USER_MANAGE,
        SYNC_MANAGE,
        VEHICLE_VIEW,
        TRIP_VIEW,
        ASSET_VIEW,
        RENTAL_VIEW,
    ]
)

# ---------------------------------------------------------------------------
# Role → mobile permissions (RBAC plan §2.1)
# ---------------------------------------------------------------------------

_OWNER: frozenset[str] = ALL_MOBILE_PERMISSIONS

_MANAGER: frozenset[str] = frozenset(
    [
        FARMER_VIEW,
        FARMER_CREATE,
        FARMER_UPDATE,
        FARM_VIEW,
        FARM_CREATE,
        FARM_UPDATE,
        PROCUREMENT_VIEW,
        PROCUREMENT_CREATE,
        PROCUREMENT_UPDATE,
        PROCUREMENT_APPROVE,
        EXPENSE_VIEW,
        EXPENSE_CREATE,
        WORKER_VIEW,
        WORKER_CREATE,
        WORKER_UPDATE,
        WORK_ORDER_VIEW,
        WORK_ORDER_CREATE,
        WORK_ORDER_UPDATE,
        WORK_ORDER_COMPLETE,
        ATTENDANCE_VIEW,
        ATTENDANCE_UPDATE,
        DOCUMENT_VIEW,
        DOCUMENT_CREATE,
        COLLECTION_VIEW,
        PAYMENT_VIEW,
        REPORT_VIEW,
        REPORT_EXPORT,
        SETTINGS_VIEW,
        SYNC_MANAGE,
        VEHICLE_VIEW,
        TRIP_VIEW,
        ASSET_VIEW,
        RENTAL_VIEW,
    ]
)

_SUPERVISOR: frozenset[str] = frozenset(
    [
        FARMER_VIEW,
        FARM_VIEW,
        FARM_UPDATE,
        PROCUREMENT_VIEW,
        PROCUREMENT_CREATE,
        PROCUREMENT_UPDATE,
        WORKER_VIEW,
        WORK_ORDER_VIEW,
        WORK_ORDER_CREATE,
        WORK_ORDER_UPDATE,
        ATTENDANCE_VIEW,
        ATTENDANCE_UPDATE,
        DOCUMENT_VIEW,
        DOCUMENT_CREATE,
        REPORT_VIEW,
        SETTINGS_VIEW,
        VEHICLE_VIEW,
        TRIP_VIEW,
        ASSET_VIEW,
    ]
)

_WORKER: frozenset[str] = frozenset(
    [
        WORK_ORDER_VIEW,
        WORK_ORDER_UPDATE,
        WORK_ORDER_COMPLETE,
        ATTENDANCE_VIEW,
        ATTENDANCE_UPDATE,
        DOCUMENT_VIEW,
        DOCUMENT_CREATE,
        SETTINGS_VIEW,
    ]
)

_ACCOUNTANT: frozenset[str] = frozenset(
    [
        FARMER_VIEW,
        FARM_VIEW,
        PROCUREMENT_VIEW,
        EXPENSE_VIEW,
        EXPENSE_CREATE,
        EXPENSE_UPDATE,
        EXPENSE_APPROVE,
        PAYMENT_VIEW,
        PAYMENT_CREATE,
        PAYMENT_APPROVE,
        COLLECTION_VIEW,
        COLLECTION_CREATE,
        COLLECTION_UPDATE,
        REPORT_VIEW,
        REPORT_EXPORT,
        DOCUMENT_VIEW,
        SETTINGS_VIEW,
    ]
)

ROLE_MOBILE_PERMISSIONS: dict[str, frozenset[str]] = {
    "OWNER": _OWNER,
    "MANAGER": _MANAGER,
    "SUPERVISOR": _SUPERVISOR,
    "WORKER": _WORKER,
    "ACCOUNTANT": _ACCOUNTANT,
}

# Map backend DB permission codes → mobile permission strings (superset merge).
BACKEND_TO_MOBILE: dict[str, str] = {
    "farmers:read": FARMER_VIEW,
    "farmers:create": FARMER_CREATE,
    "farmers:update": FARMER_UPDATE,
    "farmers:delete": FARMER_DELETE,
    "farms:read": FARM_VIEW,
    "farms:create": FARM_CREATE,
    "farms:update": FARM_UPDATE,
    "farms:delete": FARM_DELETE,
    "procurements:read": PROCUREMENT_VIEW,
    "procurements:create": PROCUREMENT_CREATE,
    "procurements:update": PROCUREMENT_UPDATE,
    "procurements:confirm": PROCUREMENT_APPROVE,
    "procurements:cancel": PROCUREMENT_DELETE,
    "farmer_payments:read": PAYMENT_VIEW,
    "farmer_payments:create": PAYMENT_CREATE,
    "farmer_payments:reverse": PAYMENT_DELETE,
    "workers:read": WORKER_VIEW,
    "workers:create": WORKER_CREATE,
    "workers:update": WORKER_UPDATE,
    "workers:delete": WORKER_DELETE,
    "work_orders:read": WORK_ORDER_VIEW,
    "work_orders:create": WORK_ORDER_CREATE,
    "work_orders:update": WORK_ORDER_UPDATE,
    "attendance:read": ATTENDANCE_VIEW,
    "attendance:create": ATTENDANCE_UPDATE,
    "attendance:update": ATTENDANCE_UPDATE,
    "expenses:read": EXPENSE_VIEW,
    "expenses:create": EXPENSE_CREATE,
    "expenses:update": EXPENSE_UPDATE,
    "collections:read": COLLECTION_VIEW,
    "collections:create": COLLECTION_CREATE,
    "payments:read": PAYMENT_VIEW,
    "payments:create": PAYMENT_CREATE,
    "documents:read": DOCUMENT_VIEW,
    "documents:create": DOCUMENT_CREATE,
    "documents:delete": DOCUMENT_DELETE,
    "dashboard:read": REPORT_VIEW,
    "users:read": USER_MANAGE,
    "users:create": USER_MANAGE,
    "users:update": USER_MANAGE,
    "users:delete": USER_MANAGE,
    "roles:read": USER_MANAGE,
    "audit:read": REPORT_VIEW,
    "assets:read": ASSET_VIEW,
    "vehicle_trips:read": TRIP_VIEW,
    "vehicle_trips:create": TRIP_VIEW,
    "rentals:read": RENTAL_VIEW,
    "rentals:create": RENTAL_VIEW,
    "rentals:update": RENTAL_VIEW,
}

# Module keys returned as accessibleModules — any matching view permission grants access.
MODULE_VIEW_PERMISSIONS: dict[str, frozenset[str]] = {
    "dashboard": frozenset({REPORT_VIEW}),
    "farmers": frozenset({FARMER_VIEW}),
    "farms": frozenset({FARM_VIEW}),
    "procurement": frozenset({PROCUREMENT_VIEW}),
    "farmer_payments": frozenset({PAYMENT_VIEW}),
    "workers": frozenset({WORKER_VIEW}),
    "work_orders": frozenset({WORK_ORDER_VIEW}),
    "attendance": frozenset({ATTENDANCE_VIEW}),
    "expenses": frozenset({EXPENSE_VIEW}),
    "collections": frozenset({COLLECTION_VIEW}),
    "payments": frozenset({PAYMENT_VIEW}),
    "vehicles": frozenset({VEHICLE_VIEW}),
    "vehicle_trips": frozenset({TRIP_VIEW}),
    "assets": frozenset({ASSET_VIEW}),
    "rentals": frozenset({RENTAL_VIEW}),
    "documents": frozenset({DOCUMENT_VIEW}),
    "settings": frozenset({SETTINGS_VIEW}),
    "sync": frozenset({SYNC_MANAGE, SETTINGS_VIEW}),
}

MODULE_ORDER: dict[str, int] = {
    "dashboard": 0,
    "farmers": 10,
    "farms": 20,
    "procurement": 30,
    "farmer_payments": 40,
    "workers": 50,
    "work_orders": 60,
    "attendance": 70,
    "expenses": 80,
    "collections": 90,
    "payments": 100,
    "vehicles": 110,
    "vehicle_trips": 120,
    "assets": 130,
    "rentals": 140,
    "documents": 150,
    "settings": 160,
    "sync": 170,
}
