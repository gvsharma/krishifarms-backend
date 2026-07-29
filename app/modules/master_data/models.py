from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import AuditActorMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class District(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "districts"
    __table_args__ = (UniqueConstraint("org_id", "name", name="uq_districts_org_name"),)

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Mandal(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "mandals"
    __table_args__ = (
        UniqueConstraint("org_id", "district_id", "name", name="uq_mandals_org_district_name"),
    )

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    district_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("districts.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Village(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "villages"
    __table_args__ = (UniqueConstraint("org_id", "mandal", "name", name="uq_villages_org_mandal_name"),)

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    mandal: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    district_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("districts.id"), nullable=True
    )
    mandal_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("mandals.id"), nullable=True)
    village_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    geo_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    geo_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    agent_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("field_agents.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cultivable_area: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class CropType(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "crop_types"
    __table_args__ = (UniqueConstraint("org_id", "code", name="uq_crop_types_org_code"),)

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    default_moisture_pct: Mapped[float | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
