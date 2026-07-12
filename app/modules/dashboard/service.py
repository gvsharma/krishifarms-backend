from sqlalchemy.orm import Session

from app.modules.assets.models import Asset
from app.modules.assets.vehicle_trip_models import VehicleTrip
from app.modules.dashboard.schemas import (
    DashboardSummaryResponse,
    ReportCatalogItem,
    ReportCatalogResponse,
)
from app.modules.documents.models import Document
from app.modules.farmer_payments.models import FarmerPayment
from app.modules.farmers.models import Farmer
from app.modules.field_services.models import FieldServiceRecord
from app.modules.master_data.models import CropType, Village
from app.modules.procurements.models import Procurement
from app.modules.users.models import User

# ERP report registry — mirrors docs/reporting SQL + product checklist.
# Full analytic endpoints (date-range KPI payloads) are not implemented yet.
REPORT_CATALOG: list[ReportCatalogItem] = [
    ReportCatalogItem(
        id="vehicle_utilization",
        name="Vehicle Utilization",
        description="Trips, distance, fuel efficiency, and fleet utilization rate.",
        status="partial",
        sql_file="docs/reporting/sql/04_vehicle_utilization.sql",
        kpi_prefix="VEH",
        module_paths=["/vehicles", "/field-services"],
        notes="Assets + vehicle-trips APIs live; dedicated utilization KPI endpoint missing.",
    ),
    ReportCatalogItem(
        id="diesel_expenses",
        name="Diesel Expenses",
        description="Fuel liters/cost from trips and field-service diesel amounts.",
        status="partial",
        sql_file="docs/reporting/sql/06_expense.sql",
        kpi_prefix="EXP",
        module_paths=["/field-services", "/vehicles", "/expenses"],
        notes="Diesel captured on trips/field services; expense posting + rollup API missing.",
    ),
    ReportCatalogItem(
        id="procurement_summary",
        name="Procurement Summary",
        description="Volume, value, moisture, deductions, and confirmed ticket counts.",
        status="partial",
        sql_file="docs/reporting/sql/01_procurement.sql",
        kpi_prefix="PROC",
        module_paths=["/procurement"],
        notes="Procurement CRUD/workflow live; period KPI aggregation endpoint missing.",
    ),
    ReportCatalogItem(
        id="farmer_ledger",
        name="Farmer Ledger",
        description="Immutable ledger credits/debits by farmer and period.",
        status="partial",
        sql_file="docs/reporting/sql/02_farmer_payments.sql",
        kpi_prefix="PAY",
        module_paths=["/farmers", "/payments", "/procurement"],
        notes="Ledger posts on confirm/pay; farmer-level ledger report endpoint missing.",
    ),
    ReportCatalogItem(
        id="outstanding_payments",
        name="Outstanding Payments",
        description="Farmer outstanding balances and unallocated payment amounts.",
        status="partial",
        sql_file="docs/reporting/sql/02_farmer_payments.sql",
        kpi_prefix="PAY",
        module_paths=["/payments", "/farmers"],
        notes="Payments list/create + allocate/reverse live; outstanding snapshot report missing.",
    ),
    ReportCatalogItem(
        id="crop_village_procurement",
        name="Crop / Village Wise Procurement",
        description="Procurement mix by crop type and village share of value/volume.",
        status="coming_soon",
        sql_file="docs/reporting/sql/01_procurement.sql",
        kpi_prefix="PROC",
        module_paths=["/procurement", "/settings/villages"],
        notes="SQL ready (PROC-011/012); no grouped report API yet.",
    ),
    ReportCatalogItem(
        id="vehicle_earnings",
        name="Vehicle Earnings",
        description="Revenue per machine hour and trip-related earnings by asset.",
        status="coming_soon",
        sql_file="docs/reporting/sql/04_vehicle_utilization.sql",
        kpi_prefix="VEH",
        module_paths=["/vehicles", "/field-services"],
        notes="Needs asset_usage_logs / rental revenue aggregation endpoints.",
    ),
    ReportCatalogItem(
        id="supervisor_productivity",
        name="Supervisor Productivity",
        description="Attendance, work orders, and labor cost for farming supervisors.",
        status="coming_soon",
        sql_file="docs/reporting/sql/03_worker_productivity.sql",
        kpi_prefix="WRK",
        module_paths=["/field-services", "/workers", "/farms"],
        notes="SQL ready; workers/work-orders report APIs not live.",
    ),
]


def get_summary(db: Session, org_id) -> DashboardSummaryResponse:
    return DashboardSummaryResponse(
        users=db.query(User).filter(User.org_id == org_id, User.deleted_at.is_(None)).count(),
        villages=db.query(Village).filter(Village.org_id == org_id, Village.deleted_at.is_(None)).count(),
        crop_types=db.query(CropType).filter(CropType.org_id == org_id, CropType.deleted_at.is_(None)).count(),
        documents=db.query(Document).filter(Document.org_id == org_id).count(),
        farmers=db.query(Farmer).filter(Farmer.org_id == org_id, Farmer.deleted_at.is_(None)).count(),
        procurements=db.query(Procurement)
        .filter(Procurement.org_id == org_id, Procurement.deleted_at.is_(None))
        .count(),
        assets=db.query(Asset).filter(Asset.org_id == org_id, Asset.deleted_at.is_(None)).count(),
        farmer_payments=db.query(FarmerPayment).filter(FarmerPayment.org_id == org_id).count(),
        field_services=db.query(FieldServiceRecord)
        .filter(FieldServiceRecord.org_id == org_id, FieldServiceRecord.deleted_at.is_(None))
        .count(),
        vehicle_trips=db.query(VehicleTrip).filter(VehicleTrip.org_id == org_id).count(),
    )


def get_report_catalog() -> ReportCatalogResponse:
    return ReportCatalogResponse(items=list(REPORT_CATALOG))
