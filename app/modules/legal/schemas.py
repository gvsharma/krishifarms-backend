from pydantic import BaseModel, Field


class PrivacyPolicyResponse(BaseModel):
    title: str = "KrishiFarms Privacy Policy"
    url: str
    support_email: str
    summary: str = Field(
        default=(
            "KrishiFarms Field and CRM collect account, contact, device, and "
            "operational farm data to run organization-managed field operations. "
            "See the full policy URL for details."
        )
    )


class AccountDeletionInfoResponse(BaseModel):
    title: str = "Delete account & data"
    url: str
    support_email: str
    supports_in_app_deletion: bool = True
    in_app_path: str = "DELETE /users/me"
    instructions: str = Field(
        default=(
            "Signed-in users can delete their own account in the app (Settings → "
            "Delete account) or via DELETE /users/me. Organization admins can also "
            "soft-delete staff accounts from Settings → Users. Alternatively email "
            "support with your name, mobile number, and organization."
        )
    )


class LegalLinksResponse(BaseModel):
    privacy: PrivacyPolicyResponse
    account_deletion: AccountDeletionInfoResponse
