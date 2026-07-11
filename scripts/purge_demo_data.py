#!/usr/bin/env python3
"""Purge DEMO data loaded by scripts/seed_demo_data.py (FK-safe order).

Deletes rows marked with [DEMO] in notes/body, demo emails, demo land survey
numbers, and clears org.settings demo flags. Does NOT delete the OWNER user
or the organization itself.

Usage:
  export DATABASE_URL=postgresql+psycopg2://...
  python scripts/purge_demo_data.py
  python scripts/purge_demo_data.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.users.models import Organization

DEMO_MARKER = "[DEMO]"
DEMO_EMAIL_DOMAIN = "@demo.krishifarms.local"


def purge_demo(db: Session, *, dry_run: bool = False) -> None:
    org = db.query(Organization).filter(Organization.code == "KRISHI").first()
    if org is None:
        org = db.query(Organization).first()
    if org is None:
        print("No organization found — nothing to purge")
        return

    org_id = str(org.id)
    marker = f"%{DEMO_MARKER}%"
    email_like = f"%{DEMO_EMAIL_DOMAIN}"

    statements: list[tuple[str, dict]] = [
        (
            """
            DELETE FROM entity_comments
            WHERE org_id = :org_id
              AND (body LIKE :marker OR body_te LIKE :marker)
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM entity_tags
            WHERE org_id = :org_id
              AND (
                tag = 'demo'
                OR entity_id IN (
                  SELECT id FROM farmers
                  WHERE org_id = :org_id AND (notes LIKE :marker OR address LIKE :marker)
                )
                OR entity_id IN (
                  SELECT id FROM procurements
                  WHERE org_id = :org_id AND notes LIKE :marker
                )
              )
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM activity_feed
            WHERE org_id = :org_id
              AND (
                summary LIKE :marker
                OR entity_id IN (
                  SELECT id FROM farmers
                  WHERE org_id = :org_id AND notes LIKE :marker
                )
                OR entity_id IN (
                  SELECT id FROM procurements
                  WHERE org_id = :org_id AND notes LIKE :marker
                )
                OR entity_id IN (
                  SELECT id FROM buyers
                  WHERE org_id = :org_id AND notes LIKE :marker
                )
                OR entity_id IN (
                  SELECT id FROM field_agents
                  WHERE org_id = :org_id AND notes LIKE :marker
                )
              )
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM audit_logs
            WHERE org_id = :org_id
              AND entity_id IN (
                SELECT id FROM procurements WHERE org_id = :org_id AND notes LIKE :marker
                UNION
                SELECT id FROM farmers WHERE org_id = :org_id AND notes LIKE :marker
                UNION
                SELECT id FROM buyers WHERE org_id = :org_id AND notes LIKE :marker
                UNION
                SELECT id FROM field_agents WHERE org_id = :org_id AND notes LIKE :marker
              )
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM procurement_deductions
            WHERE procurement_id IN (
              SELECT id FROM procurements
              WHERE org_id = :org_id
                AND (notes LIKE :marker OR idempotency_key LIKE 'demo-%')
            )
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            "ALTER TABLE farmer_ledger_entries DISABLE TRIGGER trg_farmer_ledger_immutable",
            {},
        ),
        (
            """
            DELETE FROM farmer_ledger_entries
            WHERE org_id = :org_id
              AND reference_id IN (
                SELECT id FROM procurements
                WHERE org_id = :org_id
                  AND (notes LIKE :marker OR idempotency_key LIKE 'demo-%')
              )
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            "ALTER TABLE farmer_ledger_entries ENABLE TRIGGER trg_farmer_ledger_immutable",
            {},
        ),
        (
            """
            DELETE FROM procurements
            WHERE org_id = :org_id
              AND (
                notes LIKE :marker
                OR farmer_id IN (
                  SELECT id FROM farmers
                  WHERE org_id = :org_id
                    AND (notes LIKE :marker OR phone_primary LIKE '98765000%')
                )
                OR idempotency_key LIKE 'demo-%'
              )
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM farmer_bank_accounts
            WHERE farmer_id IN (
              SELECT id FROM farmers
              WHERE org_id = :org_id
                AND (notes LIKE :marker OR phone_primary LIKE '98765000%')
            )
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM farmer_land_parcels
            WHERE farmer_id IN (
              SELECT id FROM farmers
              WHERE org_id = :org_id
                AND (notes LIKE :marker OR phone_primary LIKE '98765000%')
            )
            OR survey_number LIKE 'DEMO-SY-%'
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM farmers
            WHERE org_id = :org_id
              AND (notes LIKE :marker OR phone_primary LIKE '98765000%')
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM crop_price_rules
            WHERE org_id = :org_id AND notes LIKE :marker
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM buyers
            WHERE org_id = :org_id AND notes LIKE :marker
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM field_agents
            WHERE org_id = :org_id AND notes LIKE :marker
            """,
            {"org_id": org_id, "marker": marker},
        ),
        (
            """
            DELETE FROM refresh_tokens
            WHERE user_id IN (
              SELECT id FROM users
              WHERE org_id = :org_id AND email LIKE :email_like
            )
            """,
            {"org_id": org_id, "email_like": email_like},
        ),
        (
            """
            DELETE FROM users
            WHERE org_id = :org_id AND email LIKE :email_like
            """,
            {"org_id": org_id, "email_like": email_like},
        ),
        (
            """
            UPDATE organizations
            SET settings = (settings - 'demo_data_loaded' - 'demo_batch_id' - 'demo_marker')
            WHERE id = :org_id
            """,
            {"org_id": org_id},
        ),
    ]

    if dry_run:
        print(f"DRY RUN — would purge DEMO data for org {org.code} ({org.id})")
        for sql, params in statements:
            preview = " ".join(sql.split())[:120]
            print(f"  {preview}… params={params or '{}'}")
        return

    print(f"Purging DEMO data for org {org.code} ({org.id})…")
    for sql, params in statements:
        result = db.execute(text(sql), params)
        if result.rowcount is not None and result.rowcount >= 0 and "ALTER" not in sql.upper():
            print(f"  {result.rowcount} rows — {sql.strip().splitlines()[0][:60]}…")
    db.commit()
    print("Purge complete. Re-seed with: python scripts/seed_demo_data.py")


def main() -> None:
    parser = argparse.ArgumentParser(description="Purge KrishiFarms DEMO data")
    parser.add_argument("--dry-run", action="store_true", help="Print planned deletes only")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        purge_demo(db, dry_run=args.dry_run)
    finally:
        db.close()


if __name__ == "__main__":
    main()
