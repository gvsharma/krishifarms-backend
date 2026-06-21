from pydantic import BaseModel

from app.core.config import settings


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


class DashboardSummaryResponse(BaseModel):
    users: int
    villages: int
    crop_types: int
    documents: int


def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.app_env,
    )
