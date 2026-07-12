from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import AuditActorMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ActivityType(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "activity_types"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    service_category: Mapped[str | None] = mapped_column(String(30), nullable=True)
    default_rate_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PaymentMode(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "payment_modes"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Buyer(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "buyers"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    gstin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(200), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    village_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class FieldAgent(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "field_agents"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    village_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=True)
    commission_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class VehicleType(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "vehicle_types"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity_quintals: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    fuel_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class CropPriceRule(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "crop_price_rules"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    crop_type_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crop_types.id"), nullable=False)
    village_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    rate_per_quintal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class EntityComment(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "entity_comments"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    body_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    client_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)


class EntityTag(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "entity_tags"
    __table_args__ = (UniqueConstraint("org_id", "entity_type", "entity_id", "tag", name="uq_entity_tags_org_entity_tag"),)

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    tag: Mapped[str] = mapped_column(String(50), nullable=False)
    created_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
