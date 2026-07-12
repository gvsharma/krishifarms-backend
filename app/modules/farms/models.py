from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import AuditActorMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Farm(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "farms"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    farm_code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    acres: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    village_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=True)
    owner_farmer_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("farmers.id"), nullable=True
    )
    lease_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    lease_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    lease_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    lease_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    geo_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    geo_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)


class FarmActivity(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "farm_activities"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    farm_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farms.id"), nullable=False)
    activity_type_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("activity_types.id"), nullable=True
    )
    activity_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by_worker_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
