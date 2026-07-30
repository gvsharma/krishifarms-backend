"""Outbound SMS for farmer procurement alerts (MSG91 when configured)."""

from __future__ import annotations

import logging
from urllib.parse import urlencode

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_sms(*, phone: str, message: str) -> bool:
    """Send SMS to E.164-ish Indian mobile. Returns True when accepted by provider or skipped in dev."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 10:
        logger.warning("sms_skip_invalid_phone phone=%s", phone)
        return False

    if not settings.sms_enabled:
        logger.info("sms_dev_log to=%s body=%s", digits[-4:], message[:120])
        return True

    if settings.sms_provider == "msg91" and settings.msg91_auth_key:
        return _send_msg91(mobile=digits[-10:], message=message)

    logger.warning("sms_not_configured provider=%s", settings.sms_provider)
    return False


def _send_msg91(*, mobile: str, message: str) -> bool:
    params = {
        "authkey": settings.msg91_auth_key,
        "mobiles": f"91{mobile}",
        "message": message,
        "sender": settings.msg91_sender_id,
        "route": "4",
        "country": "91",
    }
    url = f"https://api.msg91.com/api/sendhttp.php?{urlencode(params)}"
    try:
        resp = httpx.get(url, timeout=15.0)
        resp.raise_for_status()
        logger.info("sms_msg91_sent mobile=***%s", mobile[-4:])
        return True
    except Exception:
        logger.exception("sms_msg91_failed mobile=***%s", mobile[-4:])
        return False
