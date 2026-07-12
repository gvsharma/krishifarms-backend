from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext, get_client_context
from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.devices import service
from app.modules.devices.schemas import PushTokenDeleteRequest, PushTokenRegisterRequest, PushTokenResponse
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(tags=["Devices"])


@router.post("/devices/push-tokens", response_model=APIResponse[PushTokenResponse])
def register_push_token(
    payload: PushTokenRegisterRequest,
    ctx: CurrentUserContext = Depends(require_permission("dashboard:read")),
    db: Session = Depends(get_db),
    client: ClientContext = Depends(get_client_context),
):
    row = service.upsert_push_token(
        db,
        org_id=ctx.user.org_id,
        user_id=ctx.user.id,
        payload=payload,
        client=client,
    )
    return APIResponse(data=PushTokenResponse.model_validate(row))


@router.delete("/devices/push-tokens", response_model=APIResponse[MessageResponse])
def delete_push_token(
    payload: PushTokenDeleteRequest,
    ctx: CurrentUserContext = Depends(require_permission("dashboard:read")),
    db: Session = Depends(get_db),
    client: ClientContext = Depends(get_client_context),
):
    service.revoke_push_token(
        db,
        org_id=ctx.user.org_id,
        user_id=ctx.user.id,
        payload=payload,
        client=client,
    )
    return APIResponse(data=MessageResponse(message="Push token revoked"))
