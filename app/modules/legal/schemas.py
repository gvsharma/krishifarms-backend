from pydantic import BaseModel, Field


class PrivacyPolicyResponse(BaseModel):
    title: str = "KrishiFarms Privacy Policy"
    title_te: str = "కృషీఫార్మ్స్ గోప్యతా విధానం"
    url: str
    support_email: str
    summary: str = Field(
        default=(
            "KrishiFarms Field and CRM collect account, contact, device, and "
            "operational farm data to run organization-managed field operations. "
            "See the full policy URL for details."
        )
    )
    summary_te: str = Field(
        default=(
            "కృషీఫార్మ్స్ ఫీల్డ్ మరియు CRM ఖాతా, సంప్రదింపు, పరికరం మరియు "
            "వ్యవసాయ కార్యాచరణ డేటాను సేకరిస్తాయి. పూర్తి విధానం కోసం URL చూడండి."
        )
    )


class AccountDeletionInfoResponse(BaseModel):
    title: str = "Delete account & data"
    title_te: str = "ఖాతా మరియు డేటాను తొలగించండి"
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
    instructions_te: str = Field(
        default=(
            "లాగిన్ అయిన వినియోగదారులు యాప్‌లో (సెట్టింగ్స్ → ఖాతా తొలగించు) లేదా "
            "DELETE /users/me ద్వారా తమ ఖాతాను తొలగించవచ్చు. సంస్థ నిర్వాహకులు "
            "సెట్టింగ్స్ → యూజర్స్ నుండి సిబ్బంది ఖాతాలను తొలగించవచ్చు. మీ పేరు, "
            "మొబైల్ నంబర్ మరియు సంస్థతో సపోర్ట్‌కు ఇమెయిల్ చేయండి."
        )
    )


class LegalLinksResponse(BaseModel):
    privacy: PrivacyPolicyResponse
    account_deletion: AccountDeletionInfoResponse
