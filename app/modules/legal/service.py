from app.core.config import settings
from app.modules.legal.schemas import (
    AccountDeletionInfoResponse,
    LegalLinksResponse,
    PrivacyPolicyResponse,
)


def privacy_policy() -> PrivacyPolicyResponse:
    return PrivacyPolicyResponse(
        url=settings.privacy_policy_url,
        support_email=settings.support_email,
    )


def account_deletion_info() -> AccountDeletionInfoResponse:
    return AccountDeletionInfoResponse(
        url=settings.account_deletion_url,
        support_email=settings.support_email,
        supports_in_app_deletion=True,
    )


def legal_links() -> LegalLinksResponse:
    return LegalLinksResponse(
        privacy=privacy_policy(),
        account_deletion=account_deletion_info(),
    )
