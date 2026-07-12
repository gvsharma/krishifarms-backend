from pydantic import BaseModel, Field

from app.core.config import settings


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    cache_provider: str


class DashboardSummaryResponse(BaseModel):
    users: int
    villages: int
    crop_types: int
    documents: int
    farmers: int = 0
    procurements: int = 0
    assets: int = 0
    farmer_payments: int = 0
    field_services: int = 0
    vehicle_trips: int = 0


class ReportCatalogItem(BaseModel):
    id: str
    name: str
    description: str
    status: str = Field(description="available | partial | coming_soon")
    sql_file: str | None = None
    kpi_prefix: str | None = None
    module_paths: list[str] = Field(default_factory=list)
    notes: str | None = None


class ReportCatalogResponse(BaseModel):
    items: list[ReportCatalogItem]
    summary_endpoint: str = "/dashboard/summary"
    architecture_doc: str = "docs/reporting/REPORTING_ARCHITECTURE.md"


def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.app_env,
        cache_provider=settings.cache_provider,
    )
