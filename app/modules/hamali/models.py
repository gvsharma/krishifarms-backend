from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import AuditActorMixin, Base, SoftDeleteMixin, TimestampMixin


class HamaliWorker(Base, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    """Porter / hamali roster for procurement bag handling."""

    __tablename__ = "hamali_workers"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    worker_code: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    full_name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    default_rate_per_bag: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("20.00")
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    daily_entries: Mapped[list["HamaliDailyEntry"]] = relationship(
        "HamaliDailyEntry",
        back_populates="worker",
    )


class HamaliWeeklyPayment(Base, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    """Weekly settlement batch for hamali labor."""

    __tablename__ = "hamali_weekly_payments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    payment_number: Mapped[str] = mapped_column(String(50), nullable=False)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    week_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_bags: Mapped[int] = mapped_column(nullable=False, default=0)
    total_labor_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    total_maintenance_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    total_tip_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    paid_at: Mapped[datetime | None] = mapped_column(nullable=True)
    paid_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    payment_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    daily_entries: Mapped[list["HamaliDailyEntry"]] = relationship(
        "HamaliDailyEntry",
        back_populates="weekly_payment",
    )


class HamaliDailyEntry(Base, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    """Per-day hamali work: bags lifted, labor, maintenance, tips."""

    __tablename__ = "hamali_daily_entries"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    hamali_worker_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("hamali_workers.id"), nullable=False
    )
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    bags_lifted: Mapped[int] = mapped_column(nullable=False, default=0)
    rate_per_bag: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("20.00"))
    labor_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    maintenance_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    tip_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    weekly_payment_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("hamali_weekly_payments.id"), nullable=True
    )
    procurement_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    procurement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    worker: Mapped["HamaliWorker"] = relationship("HamaliWorker", back_populates="daily_entries")
    weekly_payment: Mapped["HamaliWeeklyPayment | None"] = relationship(
        "HamaliWeeklyPayment",
        back_populates="daily_entries",
    )
