from fastapi import APIRouter

from app.modules.legal import service
from app.modules.legal.schemas import (
    AccountDeletionInfoResponse,
    LegalLinksResponse,
    PrivacyPolicyResponse,
)
from app.shared.schemas.common import APIResponse

router = APIRouter(prefix="/legal", tags=["Legal"])


@router.get("/privacy", response_model=APIResponse[PrivacyPolicyResponse])
def get_privacy_policy():
    """Public privacy policy metadata for Play Store / in-app links."""
    return APIResponse(data=service.privacy_policy())


@router.get("/account-deletion", response_model=APIResponse[AccountDeletionInfoResponse])
def get_account_deletion_info():
    """Public account/data deletion instructions (Play Console + in-app)."""
    return APIResponse(data=service.account_deletion_info())


@router.get("", response_model=APIResponse[LegalLinksResponse])
def get_legal_links():
    """Convenience bundle of privacy + account-deletion links."""
    return APIResponse(data=service.legal_links())
