"""Schemas for Farmer 360° relationship profile."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Farmer360Summary(BaseModel):
    id: UUID
    farmer_code: str
    full_name: str
    full_name_te: str | None = None
    phone_primary: str
    phone_secondary: str | None = None
    village_id: UUID
    village_name: str | None = None
    mandal: str | None = None
    district: str | None = None
    address: str | None = None
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None
    preferred_language: str | None = None
    preferred_payment_cycle: str | None = None
    preferred_payment_method: str | None = None
    trust_rating: int | None = None
    status: str
    is_vip: bool = False
    status_label: str
    tags: list[str] = []


class Farmer360Statistics(BaseModel):
    total_services_availed: int = 0
    total_farming_area: Decimal = Decimal("0")
    total_crops_sold: int = 0
    total_procurement_quantity_kg: Decimal = Decimal("0")
    lifetime_business_value: Decimal = Decimal("0")
    outstanding_amount: Decimal = Decimal("0")
    amount_paid: Decimal = Decimal("0")
    current_season_procurement_kg: Decimal = Decimal("0")
    last_service_date: date | None = None
    last_payment_date: date | None = None
    pending_payments: Decimal = Decimal("0")
    current_crop: str | None = None
    preferred_vehicle: str | None = None
    preferred_payment_method: str | None = None


class TimelineEvent(BaseModel):
    event_type: str
    title: str
    description: str | None = None
    occurred_at: datetime
    entity_type: str | None = None
    entity_id: UUID | None = None
    amount: Decimal | None = None
    meta: dict = Field(default_factory=dict)


class ServiceHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    record_number: str
    service_date: date
    service_category: str
    vehicle_name: str | None = None
    vehicle_type: str | None = None
    operator: str | None = None
    hours: Decimal | None = None
    trips: int | None = None
    area_covered: Decimal | None = None
    diesel_amount: Decimal = Decimal("0")
    amount_charged: Decimal = Decimal("0")
    pending_amount: Decimal = Decimal("0")
    payment_status: str
    status: str
    remarks: str | None = None


class FarmingHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    crop_type_id: UUID
    crop_type_name: str | None = None
    season: str
    year: int
    acres: Decimal | None = None
    survey_number: str | None = None
    village_name: str | None = None
    seed_variety: str | None = None
    seed_supplier: str | None = None
    fertilizer_supplier: str | None = None
    pesticides_used: str | None = None
    cultivation_stage: str | None = None
    expected_yield: Decimal | None = None
    actual_yield: Decimal | None = None
    selling_market: str | None = None
    selling_price: Decimal | None = None
    harvest_date: date | None = None
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None
    notes: str | None = None


class ProcurementHistoryItem(BaseModel):
    id: UUID
    procurement_number: str
    procurement_date: date
    crop_name: str | None = None
    quantity_kg: Decimal = Decimal("0")
    moisture_pct: Decimal | None = None
    rate_per_quintal: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("0")
    buyer_name: str | None = None
    payment_terms: str | None = None
    expected_payment_date: date | None = None
    actual_payment_date: date | None = None
    status: str
    remarks: str | None = None


class FinanceHistoryItem(BaseModel):
    id: UUID
    record_number: str
    loan_date: date
    amount: Decimal = Decimal("0")
    purpose: str | None = None
    paid_amount: Decimal = Decimal("0")
    outstanding: Decimal = Decimal("0")
    status: str
    remarks: str | None = None


class LedgerHistoryItem(BaseModel):
    id: UUID
    entry_date: date
    entry_type: str
    reference_type: str
    reference_id: UUID
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    balance_after: Decimal = Decimal("0")
    description: str | None = None
    payment_mode: str | None = None
    reference_number: str | None = None


class CropIntelligence(BaseModel):
    most_cultivated_crop: str | None = None
    average_yield: Decimal | None = None
    average_procurement_kg: Decimal | None = None
    preferred_buyer: str | None = None
    preferred_selling_season: str | None = None
    most_profitable_crop: str | None = None
    procurement_frequency: int = 0


class Farmer360LandItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    survey_number: str
    acres: Decimal
    land_type: str | None = None
    ownership: str | None = None
    irrigation_type: str | None = None
    water_source: str | None = None
    soil_type: str | None = None
    village_name: str | None = None
    location_notes: str | None = None
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None


class Farmer360DocumentItem(BaseModel):
    id: UUID
    document_type: str
    file_name: str
    mime_type: str
    link_role: str | None = None
    created_at: datetime | None = None


class CommunicationItem(BaseModel):
    id: UUID
    kind: str
    body: str
    author_name: str | None = None
    created_at: datetime


class Farmer360Analytics(BaseModel):
    total_revenue: Decimal = Decimal("0")
    total_diesel_consumed: Decimal = Decimal("0")
    total_tractor_hours: Decimal = Decimal("0")
    total_trips: int = 0
    average_payment_delay_days: Decimal | None = None
    average_procurement_rate: Decimal | None = None
    average_service_cost: Decimal | None = None
    current_outstanding: Decimal = Decimal("0")
    season_wise_revenue: dict[str, Decimal] = Field(default_factory=dict)
    year_wise_revenue: dict[str, Decimal] = Field(default_factory=dict)


class RecommendationItem(BaseModel):
    code: str
    title: str
    rationale: str
    priority: str = "medium"
    action_href: str | None = None


class QuickActionItem(BaseModel):
    code: str
    label: str
    href: str
    category: str


class Farmer360ProfileResponse(BaseModel):
    """Complete Farmer 360° relationship profile."""

    summary: Farmer360Summary
    statistics: Farmer360Statistics
    timeline: list[TimelineEvent] = []
    services: list[ServiceHistoryItem] = []
    farming: list[FarmingHistoryItem] = []
    procurements: list[ProcurementHistoryItem] = []
    finance: list[FinanceHistoryItem] = []
    ledger: list[LedgerHistoryItem] = []
    crop_intelligence: CropIntelligence
    land: list[Farmer360LandItem] = []
    documents: list[Farmer360DocumentItem] = []
    communication: list[CommunicationItem] = []
    analytics: Farmer360Analytics
    recommendations: list[RecommendationItem] = []
    quick_actions: list[QuickActionItem] = []
    bank_accounts_count: int = 0
