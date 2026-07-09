"""Tests for deploy/scripts/fix-firebase-env.py multiline env repair."""

import importlib.util
import json
import pathlib
import sys

_script = pathlib.Path(__file__).resolve().parents[1] / "deploy" / "scripts" / "fix-firebase-env.py"
_spec = importlib.util.spec_from_file_location("fix_firebase_env", _script)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["fix_firebase_env"] = _mod
_spec.loader.exec_module(_mod)

minify_json = _mod.minify_json
remove_env_key = _mod.remove_env_key
upsert_quoted = _mod.upsert_quoted


def test_remove_env_key_strips_multiline_orphans(tmp_path: pathlib.Path):
    env = tmp_path / "application.env"
    env.write_text(
        "SECRET_KEY=abc\n"
        'FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account"\n'
        "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCY54Fg\n"
        "-----END PRIVATE KEY-----}\n"
        "FIREBASE_PROJECT_ID=krishifarms-prod\n"
    )

    cleaned = remove_env_key(env.read_text(), "FIREBASE_SERVICE_ACCOUNT_JSON")

    assert "MIIEvAIBADAN" not in cleaned
    assert "FIREBASE_PROJECT_ID=krishifarms-prod" in cleaned
    assert cleaned.count("SECRET_KEY=abc") == 1


def test_upsert_quoted_replaces_multiline_value(tmp_path: pathlib.Path):
    env = tmp_path / "application.env"
    env.write_text(
        'FIREBASE_SERVICE_ACCOUNT_JSON={"broken": true\n'
        "orphan-line\n"
        "OTHER=value\n"
    )
    payload = minify_json('{"type":"service_account","project_id":"demo"}')

    upsert_quoted(env, "FIREBASE_SERVICE_ACCOUNT_JSON", payload)

    text = env.read_text()
    assert "orphan-line" not in text
    assert "OTHER=value" in text
    firebase_line = next(
        line for line in text.splitlines() if line.startswith("FIREBASE_SERVICE_ACCOUNT_JSON=")
    )
    raw_value = firebase_line.split("=", 1)[1].strip().strip('"').encode().decode("unicode_escape")
    assert json.loads(raw_value)["project_id"] == "demo"
