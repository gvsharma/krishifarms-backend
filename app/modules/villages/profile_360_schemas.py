"""Schemas for Village 360° relationship dashboard."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class Village360Summary(BaseModel):
    id: UUID
    village_code: str | None = None
    name: str
    mandal: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None
    agent_id: UUID | None = None
    agent_name: str | None = None
    status: str = "active"
    population: int | None = None
    estimated_cultivable_area: Decimal | None = None
    notes: str | None = None


class Village360Statistics(BaseModel):
    total_farmers: int = 0
    active_farmers: int = 0
    vip_farmers: int = 0
    total_cultivated_area: Decimal = Decimal("0")
    own_farming_area: Decimal = Decimal("0")
    total_paddy_area: Decimal = Decimal("0")
    total_corn_area: Decimal = Decimal("0")
    total_other_crops_area: Decimal = Decimal("0")
    expected_procurement_kg: Decimal = Decimal("0")
    actual_procurement_kg: Decimal = Decimal("0")
    todays_procurement_kg: Decimal = Decimal("0")
    current_season_procurement_kg: Decimal = Decimal("0")
    total_tractor_hours: Decimal = Decimal("0")
    total_rotavator_hours: Decimal = Decimal("0")
    total_cultivator_hours: Decimal = Decimal("0")
    total_baler_hours: Decimal = Decimal("0")
    total_bolero_trips: int = 0
    total_dcm_trips: int = 0
    diesel_consumed: Decimal = Decimal("0")
    outstanding_payments: Decimal = Decimal("0")
    revenue: Decimal = Decimal("0")
    profit: Decimal = Decimal("0")
    pending_collections: Decimal = Decimal("0")


class VillageFarmerRow(BaseModel):
    id: UUID
    farmer_code: str
    full_name: str
    phone_primary: str
    trust_rating: int | None = None
    is_vip: bool = False
    status: str
    current_crop: str | None = None
    outstanding: Decimal = Decimal("0")
    lifetime_revenue: Decimal = Decimal("0")
    last_service_date: date | None = None
    last_procurement_date: date | None = None
    profile_href: str


class VillageProcurementRow(BaseModel):
    id: UUID
    procurement_number: str
    procurement_date: date
    crop_name: str | None = None
    farmer_name: str | None = None
    farmer_id: UUID | None = None
    buyer_name: str | None = None
    quantity_kg: Decimal = Decimal("0")
    moisture_pct: Decimal | None = None
    rate_per_quintal: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("0")
    payment_terms: str | None = None
    status: str
    vehicle: str | None = None


class VillageServiceRow(BaseModel):
    id: UUID
    record_number: str
    service_date: date
    service_category: str
    farmer_name: str | None = None
    vehicle_name: str | None = None
    vehicle_type: str | None = None
    hours: Decimal | None = None
    diesel_amount: Decimal = Decimal("0")
    amount_charged: Decimal = Decimal("0")
    status: str


class VillageVehicleRow(BaseModel):
    asset_id: UUID | None = None
    vehicle_name: str
    vehicle_type: str | None = None
    hours: Decimal = Decimal("0")
    trips: int = 0
    diesel: Decimal = Decimal("0")
    revenue: Decimal = Decimal("0")
    operator: str | None = None
    status: str = "active"
    profile_href: str | None = None


class VillagePaymentRow(BaseModel):
    id: UUID
    payment_number: str
    payment_date: date
    farmer_name: str | None = None
    amount: Decimal = Decimal("0")
    payment_mode: str | None = None
    status: str


class VillageFinanceRow(BaseModel):
    id: UUID
    record_number: str
    loan_date: date
    farmer_name: str | None = None
    amount: Decimal = Decimal("0")
    outstanding: Decimal = Decimal("0")
    status: str


class VillageFarmingRow(BaseModel):
    id: UUID
    farmer_name: str | None = None
    crop_name: str | None = None
    season: str
    year: int
    acres: Decimal | None = None
    cultivation_stage: str | None = None
    actual_yield: Decimal | None = None


class VillageBuyerRow(BaseModel):
    id: UUID
    name: str
    quantity_purchased_kg: Decimal = Decimal("0")
    average_rate: Decimal | None = None
    outstanding: Decimal = Decimal("0")
    last_purchase_date: date | None = None


class VillageDocumentRow(BaseModel):
    id: UUID
    document_type: str
    file_name: str
    mime_type: str
    created_at: datetime | None = None


class VillageCommentRow(BaseModel):
    id: UUID
    body: str
    author_name: str | None = None
    created_at: datetime


class VillageTimelineEvent(BaseModel):
    event_type: str
    title: str
    description: str | None = None
    occurred_at: datetime
    entity_type: str | None = None
    entity_id: UUID | None = None
    amount: Decimal | None = None


class VillageAnalytics(BaseModel):
    top_crop: str | None = None
    top_farmer: str | None = None
    top_buyer: str | None = None
    most_used_vehicle: str | None = None
    average_yield: Decimal | None = None
    average_procurement_rate: Decimal | None = None
    average_payment_delay_days: Decimal | None = None
    village_growth_farmers: int = 0
    revenue_trend: dict[str, Decimal] = Field(default_factory=dict)
    season_comparison: dict[str, Decimal] = Field(default_factory=dict)


class VillageMapReady(BaseModel):
    """GIS architecture stub — GPS stored; boundary/layer support future."""

    village_center: dict[str, Decimal | None] = Field(default_factory=dict)
    farmer_locations_count: int = 0
    farm_locations_count: int = 0
    supports_boundary: bool = False
    supports_live_vehicles: bool = False


class VillageReportLink(BaseModel):
    code: str
    title: str
    href: str
    status: str = "available"


class Village360ProfileResponse(BaseModel):
    summary: Village360Summary
    statistics: Village360Statistics
    farmers: list[VillageFarmerRow] = []
    procurements: list[VillageProcurementRow] = []
    services: list[VillageServiceRow] = []
    vehicles: list[VillageVehicleRow] = []
    payments: list[VillagePaymentRow] = []
    finance: list[VillageFinanceRow] = []
    farming: list[VillageFarmingRow] = []
    buyers: list[VillageBuyerRow] = []
    comments: list[VillageCommentRow] = []
    documents: list[VillageDocumentRow] = []
    timeline: list[VillageTimelineEvent] = []
    analytics: VillageAnalytics
    map: VillageMapReady
    reports: list[VillageReportLink] = []


class VillageSearchHit(BaseModel):
    id: UUID
    village_code: str | None = None
    name: str
    mandal: str | None = None
    district: str | None = None
    match_reason: str
    farmer_count: int = 0


class VillageSearchResponse(BaseModel):
    items: list[VillageSearchHit]
    total: int
    q: str
