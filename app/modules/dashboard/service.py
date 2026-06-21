from sqlalchemy.orm import Session

from app.modules.dashboard.schemas import DashboardSummaryResponse
from app.modules.documents.models import Document
from app.modules.master_data.models import CropType, Village
from app.modules.users.models import User


def get_summary(db: Session, org_id) -> DashboardSummaryResponse:
    return DashboardSummaryResponse(
        users=db.query(User).filter(User.org_id == org_id, User.deleted_at.is_(None)).count(),
        villages=db.query(Village).filter(Village.org_id == org_id, Village.deleted_at.is_(None)).count(),
        crop_types=db.query(CropType).filter(CropType.org_id == org_id, CropType.deleted_at.is_(None)).count(),
        documents=db.query(Document).filter(Document.org_id == org_id).count(),
    )
