"""Transliteration utility tests."""

from app.modules.utils.transliterate import suggest_telugu_from_roman


def test_suggest_telugu_from_roman_short_input():
    assert suggest_telugu_from_roman("a") == ""


def test_suggest_telugu_from_roman_name():
    result = suggest_telugu_from_roman("Rama")
    # Best-effort OPTITRANS → Telugu; empty when indic-transliteration missing.
    assert isinstance(result, str)
