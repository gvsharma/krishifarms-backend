"""Analytics request/response schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class AnalyticsModuleId(str, Enum):
    executive = "executive"
    operations = "operations"
    procurement = "procurement"
    finance = "finance"
    farming = "farming"
    vehicle = "vehicle"
    village = "village"
    farmer = "farmer"
    buyer = "buyer"
    employee = "employee"
    service = "service"
    crop_intelligence = "crop-intelligence"
    inventory = "inventory"
    ai_prediction = "ai-prediction"
    alerts = "alerts"


LIVE_MODULES = frozenset(
    {
        AnalyticsModuleId.executive.value,
        AnalyticsModuleId.operations.value,
        AnalyticsModuleId.procurement.value,
        AnalyticsModuleId.finance.value,
    }
)


class AnalyticsFilter(BaseModel):
    """Common filter chrome for all analytics modules (org from JWT)."""

    date_from: date | None = None
    date_to: date | None = None
    village_id: UUID | None = None
    crop_type_id: UUID | None = None
    farmer_id: UUID | None = None
    buyer_id: UUID | None = None
    asset_id: UUID | None = None
    season: str | None = None
    preset: str | None = Field(
        default=None,
        description="today | yesterday | this_week | this_month | 7d | 30d | season | day | custom",
    )


class DrillLink(BaseModel):
    href: str
    label: str | None = None


class KpiCard(BaseModel):
    id: str
    label: str
    label_te: str | None = None
    value: Decimal | int | float | str | None = None
    unit: str | None = None
    format: str = Field(default="number", description="number | money | percent | text")
    delta_pct: float | None = None
    status: str = Field(
        default="live",
        description="live | unavailable | coming_soon | estimate",
    )
    note: str | None = None
    drill: DrillLink | None = None


class SeriesPoint(BaseModel):
    x: str
    y: Decimal | float | int
    series: str | None = None


class SeriesResponse(BaseModel):
    module: str
    id: str
    points: list[SeriesPoint]
    unit: str | None = None
    cache_hit: bool = False


class TableColumn(BaseModel):
    key: str
    label: str
    format: str = "text"


class TableRow(BaseModel):
    """One table data row; keys match TableColumn.key."""

    cells: dict[str, str | int | float | Decimal | None]


class TablePage(BaseModel):
    id: str
    title: str
    columns: list[TableColumn]
    rows: list[TableRow]
    total: int = 0


class TablesResponse(BaseModel):
    module: str
    tables: list[TablePage]
    cache_hit: bool = False


class DataAvailabilityItem(BaseModel):
    source: str
    status: str  # available | missing | partial
    notes: str | None = None


class ModuleCatalogItem(BaseModel):
    id: str
    name: str
    name_te: str | None = None
    description: str
    status: str  # live | scaffold
    href: str
    group: str
    missing_sources: list[str] = Field(default_factory=list)


class AnalyticsCatalogResponse(BaseModel):
    modules: list[ModuleCatalogItem]
    live_count: int
    scaffold_count: int
    data_plane: str = "postgres_oltp_summary_cache"
    permission: str = "analytics:admin"


class ModuleSummaryResponse(BaseModel):
    module: str
    status: str  # live | scaffold
    filters: AnalyticsFilter
    kpis: list[KpiCard]
    series_preview: list[SeriesPoint] = Field(default_factory=list)
    tables_preview: list[TablePage] = Field(default_factory=list)
    data_availability: list[DataAvailabilityItem] = Field(default_factory=list)
    health_score: int | None = None
    health_score_method: str | None = None
    cache_hit: bool = False
    latency_ms: int | None = None


class ExportFormat(str, Enum):
    csv = "csv"


class ExportRequest(BaseModel):
    module: str
    format: ExportFormat = ExportFormat.csv
    date_from: date | None = None
    date_to: date | None = None
    village_id: UUID | None = None
    crop_type_id: UUID | None = None
    farmer_id: UUID | None = None
    buyer_id: UUID | None = None
    asset_id: UUID | None = None
    season: str | None = None
    preset: str | None = None


class ExportResponse(BaseModel):
    module: str
    format: str
    filename: str
    content_type: str
    content: str
    row_count: int
