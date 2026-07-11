"""Import all models so Alembic metadata includes every table."""

from sqlalchemy import Column, Table
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.core.database import Base
from app.modules.audit.models import ActivityFeed, AuditLog  # noqa: F401
from app.modules.documents.models import Document, DocumentLink  # noqa: F401
from app.modules.farmers.models import Farmer, FarmerBankAccount, FarmerLandParcel  # noqa: F401
from app.modules.procurements.models import (  # noqa: F401
    FarmerLedgerEntry,
    Procurement,
    ProcurementDeduction,
)
from app.modules.financial.models import ExpenseCategory  # noqa: F401
from app.modules.master_data.models import CropType, Village  # noqa: F401
from app.modules.platform.models import (  # noqa: F401
    ActivityType,
    Buyer,
    CropPriceRule,
    EntityComment,
    EntityTag,
    FieldAgent,
    VehicleType,
)
from app.modules.users.models import (  # noqa: F401
    Organization,
    Permission,
    RefreshToken,
    Role,
    RolePermission,
    User,
)

# Migration-only tables referenced by live FKs (no ORM module yet)
if "workers" not in Base.metadata.tables:
    Table("workers", Base.metadata, Column("id", PGUUID(as_uuid=True), primary_key=True))

__all__ = ["Base"]
