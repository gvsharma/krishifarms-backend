"""ORM for analytics daily org facts (summary plane)."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import TimestampMixin, Base


class AnalyticsDailyOrgFact(Base, TimestampMixin):
    """Org-day rollup row. Phase 1 may leave empty and compute live; job can backfill later."""

    __tablename__ = "analytics_daily_org_facts"
    __table_args__ = (
        UniqueConstraint("org_id", "fact_date", name="uq_analytics_daily_org_facts_org_date"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    fact_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    expenses: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    collections: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    procurement_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False, default=Decimal("0"))
    procurement_net_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    field_service_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    outstanding: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    farmers_active: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    procurements_confirmed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trips_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    field_services_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
