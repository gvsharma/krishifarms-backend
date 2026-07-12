from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import AuditActorMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

SERVICE_CATEGORIES = frozenset(
    {
        "field_service",
        "tractor_work",
        "transport",
        "fertiliser",
        "seeds",
        "agri_finance",
        "vehicle_ops",
        "godown",
    }
)


class FieldServiceRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "field_service_records"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    record_number: Mapped[str] = mapped_column(String(50), nullable=False)
    service_category: Mapped[str] = mapped_column(String(30), nullable=False)
    activity_type_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("activity_types.id"), nullable=True
    )
    farmer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farmers.id"), nullable=True)
    asset_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)
    vehicle_type_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("vehicle_types.id"), nullable=True
    )
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    hours: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    bag_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    quantity_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rate_per_unit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    diesel_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"), nullable=False)
    amount_given: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"), nullable=False)
    advance_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"), nullable=False)
    pending_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"), nullable=False)
    cleaning_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    facility_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    comments_te: Mapped[str | None] = mapped_column(Text, nullable=True)
