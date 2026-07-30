from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.modules.platform.schemas import CommentResponse
from app.shared.schemas.audit_meta import AuditMetaMixin

# Standard grain-procurement weight deducted per bag (kata) before pricing.
DEFAULT_PER_BAG_DEDUCTION_KG = Decimal("2.000")
# Cash discount per net quintal when farmer takes 100% payment on spot.
DEFAULT_SPOT_DEDUCTION_PER_QUINTAL = Decimal("100.00")
_THREEPLACES = Decimal("0.001")

PROCUREMENT_STATUSES = (
    "draft",
    "pending_weighment",
    "weighed",
    "priced",
    "confirmed",
    "paid_partial",
    "paid_full",
    "cancelled",
    "reversed",
)

CANCELLABLE_STATUSES = frozenset({"draft", "pending_weighment", "weighed"})

PAYMENT_TERMS = ("one_week", "10_days", "2_weeks", "20_days", "custom")
_PAYMENT_TERMS_PATTERN = "^(one_week|10_days|2_weeks|20_days|custom)$"


class ProcurementDeductionInput(BaseModel):
    deduction_type: str = Field(min_length=1, max_length=100)
    deduction_type_te: str | None = None
    amount: Decimal = Field(ge=0)
    notes: str | None = None


class ProcurementDeductionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    deduction_type: str
    deduction_type_te: str | None
    amount: Decimal
    notes: str | None


class ProcurementBagEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bag_number: int
    weight_kg: Decimal


class ProcurementCreateRequest(BaseModel):
    farmer_id: UUID
    crop_type_id: UUID
    village_id: UUID
    procurement_date: date
    bag_count: int = Field(default=0, ge=0)
    per_bag_deduction_kg: Decimal | None = Field(default=None, ge=0)
    is_spot_payment: bool = False
    spot_deduction_per_quintal: Decimal | None = Field(default=None, ge=0)
    buyer_id: UUID | None = None
    payment_terms: str | None = Field(default=None, pattern=_PAYMENT_TERMS_PATTERN)
    payment_terms_custom: str | None = None
    expected_payment_date: date | None = None
    notes: str | None = None
    weight_per_bag_kg: Decimal | None = Field(default=None, gt=0)
    # Field intake from mobile — auto-records weighment (and price when rate provided).
    gross_weight_kg: Decimal | None = Field(default=None, gt=0)
    tare_weight_kg: Decimal | None = Field(default=None, ge=0)
    moisture_pct: Decimal | None = Field(default=None, ge=0, le=100)
    bag_weights_kg: list[Decimal] | None = Field(default=None, min_length=1)
    rate_per_quintal: Decimal | None = Field(default=None, gt=0)


class ProcurementUpdateRequest(BaseModel):
    farmer_id: UUID | None = None
    crop_type_id: UUID | None = None
    village_id: UUID | None = None
    bag_count: int | None = Field(default=None, ge=0)
    per_bag_deduction_kg: Decimal | None = Field(default=None, ge=0)
    is_spot_payment: bool | None = None
    spot_deduction_per_quintal: Decimal | None = Field(default=None, ge=0)
    buyer_id: UUID | None = None
    payment_terms: str | None = Field(default=None, pattern=_PAYMENT_TERMS_PATTERN)
    payment_terms_custom: str | None = None
    expected_payment_date: date | None = None
    notes: str | None = None
    weight_per_bag_kg: Decimal | None = Field(default=None, gt=0)


class WeighmentRequest(BaseModel):
    gross_weight_kg: Decimal | None = Field(default=None, gt=0)
    tare_weight_kg: Decimal = Field(default=Decimal("0"), ge=0)
    moisture_pct: Decimal | None = Field(default=None, ge=0, le=100)
    bag_count: int | None = Field(default=None, ge=0)
    per_bag_deduction_kg: Decimal | None = Field(default=None, ge=0)
    bag_weights_kg: list[Decimal] | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _require_weight_source(self) -> WeighmentRequest:
        if not self.bag_weights_kg and self.gross_weight_kg is None:
            raise ValueError("gross_weight_kg or bag_weights_kg is required")
        return self

    def resolved_gross_weight_kg(self) -> Decimal:
        if self.bag_weights_kg:
            return sum(self.bag_weights_kg, Decimal("0"))
        if self.gross_weight_kg is None:
            raise ValueError("gross_weight_kg or bag_weights_kg is required")
        return self.gross_weight_kg


class ApplyPriceRequest(BaseModel):
    """Optional explicit rate (mobile/field entry); otherwise crop price rule applies."""

    rate_per_quintal: Decimal | None = Field(default=None, gt=0)


class ProcurementCalculateRequest(BaseModel):
    """Live preview of gross/net weight and amounts (no persistence)."""

    bag_count: int = Field(ge=0)
    weight_per_bag_kg: Decimal = Field(gt=0)
    per_bag_deduction_kg: Decimal | None = Field(default=None, ge=0)
    tare_weight_kg: Decimal = Field(default=Decimal("0"), ge=0)
    moisture_pct: Decimal | None = Field(default=None, ge=0, le=100)
    rate_per_quintal: Decimal = Field(gt=0)
    is_spot_payment: bool = False
    spot_deduction_per_quintal: Decimal | None = Field(default=None, ge=0)
    line_deduction_amount: Decimal = Field(default=Decimal("0"), ge=0)


class ProcurementCalculateResponse(BaseModel):
    gross_weight_kg: Decimal
    bag_weight_deduction_kg: Decimal
    net_weight_kg: Decimal
    net_quintals: Decimal
    gross_amount: Decimal
    line_deduction_amount: Decimal
    spot_deduction_amount: Decimal
    net_amount: Decimal
    moisture_pct: Decimal | None = None


class ProcurementFieldEntryRequest(BaseModel):
    """Mobile/field one-shot: create → weigh → price → optional confirm."""

    farmer_id: UUID
    crop_type_id: UUID
    village_id: UUID
    procurement_date: date
    bag_count: int = Field(gt=0)
    weight_per_bag_kg: Decimal = Field(gt=0)
    per_bag_deduction_kg: Decimal | None = Field(default=None, ge=0)
    tare_weight_kg: Decimal = Field(default=Decimal("0"), ge=0)
    moisture_pct: Decimal | None = Field(default=None, ge=0, le=100)
    rate_per_quintal: Decimal = Field(gt=0)
    is_spot_payment: bool = False
    spot_deduction_per_quintal: Decimal | None = Field(default=None, ge=0)
    buyer_id: UUID | None = None
    payment_terms: str | None = Field(default=None, pattern=_PAYMENT_TERMS_PATTERN)
    payment_terms_custom: str | None = None
    expected_payment_date: date | None = None
    notes: str | None = None
    auto_confirm: bool = True
    notify_farmer: bool = True
    line_deductions: list[ProcurementDeductionInput] = Field(default_factory=list)


class ProcurementCancelRequest(BaseModel):
    reason: str = Field(min_length=3)


class ProcurementReverseRequest(BaseModel):
    reason: str = Field(min_length=3)


class ProcurementProfitSummary(BaseModel):
    """Buyer/org margin breakdown — omit for FARMER role clients."""

    gross_quintals: Decimal
    net_quintals: Decimal
    weight_deduction_kg: Decimal
    weight_deduction_profit_amount: Decimal
    spot_deduction_amount: Decimal
    total_profit_amount: Decimal


class ProcurementResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    procurement_number: str
    farmer_id: UUID
    farmer_name: str | None = None
    crop_type_id: UUID
    crop_type_name: str | None = None
    village_id: UUID
    village_name: str | None = None
    buyer_id: UUID | None = None
    buyer_name: str | None = None
    payment_terms: str | None = None
    payment_terms_custom: str | None = None
    expected_payment_date: date | None = None
    actual_payment_date: date | None = None
    procurement_date: date
    bag_count: int
    weight_per_bag_kg: Decimal | None = None
    per_bag_deduction_kg: Decimal
    is_spot_payment: bool
    spot_deduction_per_quintal: Decimal
    spot_deduction_amount: Decimal
    gross_weight_kg: Decimal
    tare_weight_kg: Decimal = Decimal("0")
    moisture_pct: Decimal | None
    net_weight_kg: Decimal
    rate_per_quintal: Decimal
    gross_amount: Decimal
    deduction_amount: Decimal
    net_amount: Decimal
    status: str
    confirmed_at: datetime | None = None
    confirmed_by: UUID | None = None
    confirmed_by_name: str | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    notes: str | None
    deductions: list[ProcurementDeductionResponse] = []
    bag_entries: list[ProcurementBagEntryResponse] = []
    tags: list[str] = []
    comments: list[CommentResponse] = []
    profit_summary: ProcurementProfitSummary | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def bag_weight_deduction_kg(self) -> Decimal:
        """Total weight deducted for bags = bag_count * per_bag_deduction_kg."""
        return (Decimal(self.bag_count) * self.per_bag_deduction_kg).quantize(_THREEPLACES)


class ProcurementListItemResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    procurement_number: str
    farmer_id: UUID
    farmer_name: str | None = None
    crop_type_id: UUID
    crop_type_name: str | None = None
    village_id: UUID
    buyer_id: UUID | None = None
    buyer_name: str | None = None
    payment_terms: str | None = None
    expected_payment_date: date | None = None
    procurement_date: date
    net_weight_kg: Decimal
    net_amount: Decimal
    status: str
    tags: list[str] = []


class ProcurementListResponse(BaseModel):
    items: list[ProcurementListItemResponse]
    total: int
    page: int
    page_size: int
