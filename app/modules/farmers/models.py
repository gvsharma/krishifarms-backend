from uuid import UUID

from sqlalchemy import CHAR, ForeignKey, LargeBinary, String, Text
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
