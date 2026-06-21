from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.dashboard import service
from app.modules.dashboard.schemas import DashboardSummaryResponse, HealthResponse
from app.modules.dashboard.schemas import get_health
from app.shared.schemas.common import APIResponse

router = APIRouter(tags=["Dashboard"])


@router.get("/health", response_model=APIResponse[HealthResponse])
def health():
    return APIResponse(data=get_health())


@router.get("/dashboard/summary", response_model=APIResponse[DashboardSummaryResponse])
def dashboard_summary(
    ctx: CurrentUserContext = Depends(require_permission("dashboard:read")),
    db: Session = Depends(get_db),
):
    summary = service.get_summary(db, ctx.user.org_id)
    return APIResponse(data=summary)
