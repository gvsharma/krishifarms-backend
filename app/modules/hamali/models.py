from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import AuditActorMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Worker(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "workers"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    worker_code: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    full_name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    village_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=True)
    hourly_rate: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    daily_rate: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)


class HamaliWorkEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "hamali_work_entries"
    __table_args__ = (
        CheckConstraint("bag_count >= 0", name="ck_hamali_work_entries_bag_count"),
        CheckConstraint("tip_amount >= 0", name="ck_hamali_work_entries_tip_amount"),
    )

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    worker_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workers.id"), nullable=False)
    farmer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    bag_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tip_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"), nullable=False)
    procurement_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("procurements.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
