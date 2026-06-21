"""Import all models so Alembic metadata includes every table."""

from app.core.database import Base
from app.modules.audit.models import ActivityFeed, AuditLog  # noqa: F401
from app.modules.documents.models import Document, DocumentLink  # noqa: F401
from app.modules.financial.models import ExpenseCategory  # noqa: F401
from app.modules.master_data.models import CropType, Village  # noqa: F401
from app.modules.users.models import (  # noqa: F401
    Organization,
    Permission,
    RefreshToken,
    Role,
    RolePermission,
    User,
)

__all__ = ["Base"]
