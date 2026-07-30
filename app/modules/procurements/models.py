from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, ForeignKeyConstraint, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import AuditActorMixin, Base, SoftDeleteMixin, TimestampMixin


class Procurement(Base, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "procurements"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    procurement_date: Mapped[date] = mapped_column(Date, primary_key=True)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    procurement_number: Mapped[str] = mapped_column(String(50), nullable=False)
    farmer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    crop_type_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crop_types.id"), nullable=False)
    village_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=False)
    buyer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("buyers.id"), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_terms_custom: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    bag_count: Mapped[int] = mapped_column(nullable=False, default=0)
    weight_per_bag_kg: Mapped[Decimal | None] = mapped_column(Numeric(8, 3), nullable=True)
    per_bag_deduction_kg: Mapped[Decimal] = mapped_column(
        Numeric(6, 3), nullable=False, default=Decimal("2.000")
    )
    is_spot_payment: Mapped[bool] = mapped_column(nullable=False, default=False)
    spot_deduction_per_quintal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("100.00")
    )
    spot_deduction_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    gross_weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=Decimal("0"))
    tare_weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=Decimal("0"))
    moisture_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    net_weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=Decimal("0"))
    rate_per_quintal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    deduction_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    net_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    confirmed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    confirmed_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True)

    deductions: Mapped[list["ProcurementDeduction"]] = relationship(
        "ProcurementDeduction",
        back_populates="procurement",
        cascade="all, delete-orphan",
    )
    bag_entries: Mapped[list["ProcurementBagEntry"]] = relationship(
        "ProcurementBagEntry",
        back_populates="procurement",
        cascade="all, delete-orphan",
        order_by="ProcurementBagEntry.bag_number",
    )


class ProcurementBagEntry(Base, TimestampMixin, AuditActorMixin):
    __tablename__ = "procurement_bag_entries"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    procurement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    procurement_date: Mapped[date] = mapped_column(Date, nullable=False)
    bag_number: Mapped[int] = mapped_column(nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["procurement_id", "procurement_date"],
            ["procurements.id", "procurements.procurement_date"],
            ondelete="CASCADE",
        ),
    )

    procurement: Mapped["Procurement"] = relationship("Procurement", back_populates="bag_entries")


class ProcurementDeduction(Base):
    __tablename__ = "procurement_deductions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    procurement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    procurement_date: Mapped[date] = mapped_column(Date, nullable=False)
    deduction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    deduction_type_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["procurement_id", "procurement_date"],
            ["procurements.id", "procurements.procurement_date"],
            ondelete="CASCADE",
        ),
    )

    procurement: Mapped["Procurement"] = relationship("Procurement", back_populates="deductions")


class FarmerLedgerEntry(Base):
    __tablename__ = "farmer_ledger_entries"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    entry_date: Mapped[date] = mapped_column(Date, primary_key=True)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    farmer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    entry_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reference_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    debit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    credit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    balance_after: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reversal_of_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    posted_at: Mapped[datetime] = mapped_column(nullable=False)
    posted_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
