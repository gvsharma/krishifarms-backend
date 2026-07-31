from fastapi import APIRouter, Query

from app.modules.utils.transliterate import suggest_telugu_from_roman
from app.shared.schemas.common import APIResponse

router = APIRouter(prefix="/utils", tags=["Utils"])


@router.get("/transliterate", response_model=APIResponse[dict[str, str]])
def transliterate_text(
    text: str = Query(..., min_length=1, max_length=200),
    target: str = Query(default="te"),
):
    """Suggest Telugu script for a roman name (best-effort; user should review)."""
    if target.lower() not in {"te", "telugu"}:
        return APIResponse(data={"text": "", "locale": target})
    return APIResponse(data={"text": suggest_telugu_from_roman(text), "locale": "te"})
