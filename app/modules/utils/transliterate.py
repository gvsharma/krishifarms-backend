"""Best-effort roman → Telugu for name fields (suggestion only)."""

from __future__ import annotations

import re

try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate as _transliterate
except ImportError:  # pragma: no cover — optional until pip install
    sanscript = None  # type: ignore[assignment]
    _transliterate = None  # type: ignore[assignment]


def suggest_telugu_from_roman(text: str) -> str:
    """Return Telugu suggestion for Latin input; empty string when unavailable."""
    cleaned = re.sub(r"\s+", " ", text.strip())
    if len(cleaned) < 2:
        return ""
    if _transliterate is None or sanscript is None:
        return ""
    try:
        # OPTITRANS handles roman letters; lowercasing improves name matches.
        return _transliterate(cleaned.lower(), sanscript.OPTITRANS, sanscript.TELUGU)
    except Exception:
        return ""
