from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CHAR, Boolean, Date, ForeignKey, LargeBinary, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import AuditActorMixin, Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Farmer(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "farmers"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    farmer_code: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    full_name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    father_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    father_name_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone_primary: Mapped[str] = mapped_column(String(20), nullable=False)
    phone_secondary: Mapped[str | None] = mapped_column(String(20), nullable=True)
    village_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("villages.id"), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    aadhaar_last4: Mapped[str | None] = mapped_column(CHAR(4), nullable=True)
    pan_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    preferred_payment_cycle: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preferred_payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    trust_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    geo_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    geo_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)


class FarmerBankAccount(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "farmer_bank_accounts"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    farmer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    account_holder_name: Mapped[str] = mapped_column(String(200), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(200), nullable=False)
    branch: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ifsc: Mapped[str] = mapped_column(CHAR(11), nullable=False)
    account_number_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)


class FarmerLandParcel(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "farmer_land_parcels"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    farmer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    survey_number: Mapped[str] = mapped_column(String(100), nullable=False)
    acres: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    land_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    geo_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    geo_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    ownership: Mapped[str | None] = mapped_column(String(20), nullable=True)
    irrigation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    water_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    village_name: Mapped[str | None] = mapped_column(String(200), nullable=True)


class FarmerCropHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditActorMixin, SoftDeleteMixin):
    __tablename__ = "farmer_crop_history"

    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    farmer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    crop_type_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crop_types.id"), nullable=False)
    season: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    acres: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    survey_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    seed_variety: Mapped[str | None] = mapped_column(String(100), nullable=True)
    seed_supplier: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fertilizer_supplier: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pesticides_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    cultivation_stage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    expected_yield: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    actual_yield: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    selling_market: Mapped[str | None] = mapped_column(String(200), nullable=True)
    selling_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    geo_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    geo_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
