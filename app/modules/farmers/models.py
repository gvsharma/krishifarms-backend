from decimal import Decimal
from uuid import UUID

from sqlalchemy import CHAR, ForeignKey, LargeBinary, Numeric, String, Text
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
