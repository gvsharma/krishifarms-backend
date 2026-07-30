"""Import all models so Alembic metadata includes every table."""

from app.core.database import Base
from app.modules.analytics.models import AnalyticsDailyOrgFact  # noqa: F401
from app.modules.assets.models import Asset  # noqa: F401
from app.modules.assets.vehicle_trip_models import VehicleTrip  # noqa: F401
from app.modules.audit.models import ActivityFeed, AuditLog  # noqa: F401
from app.modules.devices.models import UserDeviceToken  # noqa: F401
from app.modules.documents.models import Document, DocumentLink  # noqa: F401
from app.modules.farmers.models import Farmer, FarmerBankAccount, FarmerCropHistory, FarmerLandParcel  # noqa: F401
from app.modules.farmer_payments.models import FarmerPayment, FarmerPaymentAllocation  # noqa: F401
from app.modules.farms.models import Farm, FarmActivity  # noqa: F401
from app.modules.procurements.models import (  # noqa: F401
    FarmerLedgerEntry,
    Procurement,
    ProcurementDeduction,
)
from app.modules.field_services.models import FieldServiceRecord  # noqa: F401
from app.modules.hamali.models import HamaliDailyEntry, HamaliWeeklyPayment, HamaliWorker  # noqa: F401
from app.modules.financial.models import Collection, Expense, ExpenseCategory  # noqa: F401
from app.modules.master_data.models import CropType, District, Mandal, Village  # noqa: F401
from app.modules.platform.models import (  # noqa: F401
    ActivityType,
    Buyer,
    CropPriceRule,
    EntityComment,
    EntityTag,
    FieldAgent,
    PaymentMode,
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

from app.modules.hamali.models import HamaliWorkEntry, Worker  # noqa: F401

__all__ = ["Base"]
