from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, ForeignKeyConstraint, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FarmerPayment(Base):
    __tablename__ = "farmer_payments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    payment_date: Mapped[date] = mapped_column(Date, primary_key=True)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    payment_number: Mapped[str] = mapped_column(String(50), nullable=False)
    farmer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    payment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_mode_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payment_modes.id"), nullable=False
    )
    reference_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bank_account_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("farmer_bank_accounts.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    reversal_of_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    posted_at: Mapped[datetime] = mapped_column(nullable=False)
    posted_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    allocations: Mapped[list["FarmerPaymentAllocation"]] = relationship(
        "FarmerPaymentAllocation",
        back_populates="payment",
        cascade="all, delete-orphan",
    )


class FarmerPaymentAllocation(Base):
    __tablename__ = "farmer_payment_allocations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    payment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    procurement_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    procurement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["payment_id", "payment_date"],
            ["farmer_payments.id", "farmer_payments.payment_date"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["procurement_id", "procurement_date"],
            ["procurements.id", "procurements.procurement_date"],
            ondelete="RESTRICT",
        ),
    )

    payment: Mapped["FarmerPayment"] = relationship("FarmerPayment", back_populates="allocations")
