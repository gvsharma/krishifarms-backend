#!/usr/bin/env python3
"""Validate, minify, and upsert FIREBASE_SERVICE_ACCOUNT_JSON in a dotenv file.

Multi-line JSON from SSM breaks docker-compose .env parsing (unquoted newlines).
This script collapses JSON to a single line and writes a properly quoted value.

Usage:
  python3 fix-firebase-env.py /opt/krishifarms/config/application.env '<json>'
  python3 fix-firebase-env.py /opt/krishifarms/config/application.env   # read stdin
  python3 fix-firebase-env.py --minify-only '<json>'                    # stdout only
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ENV_KEY_PATTERN = re.compile(r"^[A-Z_][A-Z0-9_]*=")


def minify_json(raw: str) -> str:
    """Parse and re-serialize JSON as a single-line minified string."""
    return json.dumps(json.loads(raw), separators=(",", ":"))


def remove_env_key(text: str, key: str) -> str:
    """Remove key=value including orphaned continuation lines from prior multiline values."""
    prefix = f"{key}="
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        if stripped.startswith(prefix):
            i += 1
            while i < len(lines) and not ENV_KEY_PATTERN.match(lines[i].lstrip()):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def escape_dotenv_value(value: str) -> str:
    """Escape for docker-compose / python-dotenv double-quoted values."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def upsert_quoted(path: pathlib.Path, key: str, value: str) -> None:
    """Set key=\"value\" in a dotenv file, escaping embedded double quotes."""
    line = f'{key}="{escape_dotenv_value(value)}"\n'
    text = path.read_text() if path.exists() else ""
    text = remove_env_key(text, key)
    if text and not text.endswith("\n"):
        text += "\n"
    text += line
    path.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("env_file", nargs="?", help="Path to application.env")
    parser.add_argument("json_value", nargs="?", help="Raw JSON (optional; else stdin)")
    parser.add_argument(
        "--minify-only",
        action="store_true",
        help="Print minified JSON to stdout; do not modify env file",
    )
    args = parser.parse_args()

    raw = args.json_value if args.json_value is not None else sys.stdin.read()
    raw = raw.strip()
    if not raw:
        print("ERROR: empty JSON input", file=sys.stderr)
        return 1

    try:
        minified = minify_json(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 1

    if args.minify_only:
        print(minified)
        return 0

    if not args.env_file:
        print("ERROR: env_file required unless --minify-only", file=sys.stderr)
        return 1

    path = pathlib.Path(args.env_file)
    upsert_quoted(path, "FIREBASE_SERVICE_ACCOUNT_JSON", minified)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
