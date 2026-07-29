"""Locale helpers for bilingual API display names."""


def normalize_locale(tag: str | None) -> str:
    if tag and tag.lower().startswith("te"):
        return "te"
    return "en"


def pick_display(en: str | None, te: str | None, locale: str) -> str | None:
    if locale == "te" and te:
        return te
    return en
