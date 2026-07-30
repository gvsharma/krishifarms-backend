from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import AuditActorMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ExpenseCategory(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "expense_categories"
    __table_args__ = (UniqueConstraint("org_id", "name", name="uq_expense_categories_org_name"),)

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("expense_categories.id"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(20), default="expense", nullable=False)


class Expense(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "expenses"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    expense_number: Mapped[str] = mapped_column(String(50), nullable=False)
    category_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("expense_categories.id"), nullable=False
    )
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    vendor_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    payment_mode_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payment_modes.id"), nullable=False
    )
    farm_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farms.id"), nullable=True)
    asset_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)
    financial_transaction_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    financial_transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="posted")
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class Collection(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin):
    """Collections have no soft-delete column in migration 012."""

    __tablename__ = "collections"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    collection_number: Mapped[str] = mapped_column(String(50), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    collection_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_mode_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payment_modes.id"), nullable=False
    )
    financial_transaction_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    financial_transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reference_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="posted")
