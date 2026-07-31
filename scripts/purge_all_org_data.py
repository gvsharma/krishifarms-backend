#!/usr/bin/env python3
"""Purge ALL org-scoped business data for a fresh start (FK-safe order).

Keeps schema, global permissions, roles, the organization row, and the OWNER
login (DEFAULT_OWNER_EMAIL). Removes farmers, procurements, master data,
demo users, audit/activity, and all transactional records so you can rebuild
from scratch.

Usage:
  export DATABASE_URL=postgresql+psycopg2://...
  python scripts/purge_all_org_data.py --dry-run
  python scripts/purge_all_org_data.py --confirm PURGE-ALL-DATA

Optional:
  --org-code KRISHI          (default: KRISHI, else first org)
  --keep-master-data           keep villages, crops, districts, expense categories,
                               activity types, payment modes, vehicle types
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.modules.users.models import Organization


def _table_exists(table_name: str) -> bool:
    return inspect(engine).has_table(table_name)


def _run_delete(db: Session, sql: str, params: dict, *, label: str, dry_run: bool) -> None:
    preview = " ".join(sql.split())[:100]
    if dry_run:
        print(f"  DRY — {label}: {preview}")
        return
    result = db.execute(text(sql), params)
    count = result.rowcount if result.rowcount is not None and result.rowcount >= 0 else "?"
    print(f"  {count} rows — {label}")


def purge_all_org_data(
    db: Session,
    *,
    org_id: str,
    owner_email: str,
    keep_master_data: bool = False,
    dry_run: bool = False,
) -> None:
    params = {"org_id": org_id, "owner_email": owner_email}

    # Child / leaf tables first (rough FK order).
    deletes: list[tuple[str, str]] = [
        ("sync_conflicts", "DELETE FROM sync_conflicts WHERE sync_batch_id IN (SELECT id FROM sync_batches WHERE org_id = :org_id)"),
        ("sync_batches", "DELETE FROM sync_batches WHERE org_id = :org_id"),
        ("ai_suggestions", "DELETE FROM ai_suggestions WHERE org_id = :org_id"),
        ("ai_summaries", "DELETE FROM ai_summaries WHERE org_id = :org_id"),
        ("ocr_extractions", "DELETE FROM ocr_extractions WHERE org_id = :org_id"),
        ("voice_transcripts", "DELETE FROM voice_transcripts WHERE org_id = :org_id"),
        ("ai_jobs", "DELETE FROM ai_jobs WHERE org_id = :org_id"),
        ("whatsapp_messages", "DELETE FROM whatsapp_messages WHERE org_id = :org_id"),
        ("entity_comments", "DELETE FROM entity_comments WHERE org_id = :org_id"),
        ("entity_tags", "DELETE FROM entity_tags WHERE org_id = :org_id"),
        ("activity_feed", "DELETE FROM activity_feed WHERE org_id = :org_id"),
        ("audit_logs", "DELETE FROM audit_logs WHERE org_id = :org_id"),
        ("document_links", "DELETE FROM document_links WHERE org_id = :org_id"),
        ("documents", "DELETE FROM documents WHERE org_id = :org_id"),
        ("farmer_payment_allocations", "DELETE FROM farmer_payment_allocations WHERE org_id = :org_id"),
        ("farmer_payments", "DELETE FROM farmer_payments WHERE org_id = :org_id"),
        ("farmer_outstanding_snapshots", "DELETE FROM farmer_outstanding_snapshots WHERE org_id = :org_id"),
        ("financial_transaction_lines", "DELETE FROM financial_transaction_lines WHERE org_id = :org_id"),
        ("financial_transactions", "DELETE FROM financial_transactions WHERE org_id = :org_id"),
        ("expenses", "DELETE FROM expenses WHERE org_id = :org_id"),
        ("collections", "DELETE FROM collections WHERE org_id = :org_id"),
        ("payments", "DELETE FROM payments WHERE org_id = :org_id"),
        ("procurement_bag_entries", "DELETE FROM procurement_bag_entries WHERE org_id = :org_id"),
        ("procurement_deductions", "DELETE FROM procurement_deductions WHERE org_id = :org_id"),
        ("farmer_ledger_entries", "DELETE FROM farmer_ledger_entries WHERE org_id = :org_id"),
        ("procurements", "DELETE FROM procurements WHERE org_id = :org_id"),
        ("rental_agreements", "DELETE FROM rental_agreements WHERE org_id = :org_id"),
        ("rental_customers", "DELETE FROM rental_customers WHERE org_id = :org_id"),
        ("asset_usage_logs", "DELETE FROM asset_usage_logs WHERE org_id = :org_id"),
        ("maintenance_records", "DELETE FROM maintenance_records WHERE org_id = :org_id"),
        ("vehicle_trips", "DELETE FROM vehicle_trips WHERE org_id = :org_id"),
        ("assets", "DELETE FROM assets WHERE org_id = :org_id"),
        ("farm_activities", "DELETE FROM farm_activities WHERE org_id = :org_id"),
        ("farms", "DELETE FROM farms WHERE org_id = :org_id"),
        ("work_orders", "DELETE FROM work_orders WHERE org_id = :org_id"),
        ("attendance_records", "DELETE FROM attendance_records WHERE org_id = :org_id"),
        ("worker_skills", "DELETE FROM worker_skills WHERE org_id = :org_id"),
        ("workers", "DELETE FROM workers WHERE org_id = :org_id"),
        ("field_service_records", "DELETE FROM field_service_records WHERE org_id = :org_id"),
        ("hamali_daily_entries", "DELETE FROM hamali_daily_entries WHERE org_id = :org_id"),
        ("hamali_weekly_payments", "DELETE FROM hamali_weekly_payments WHERE org_id = :org_id"),
        ("hamali_workers", "DELETE FROM hamali_workers WHERE org_id = :org_id"),
        ("farmer_crop_history", "DELETE FROM farmer_crop_history WHERE org_id = :org_id"),
        ("farmer_land_parcels", "DELETE FROM farmer_land_parcels WHERE org_id = :org_id"),
        ("farmer_bank_accounts", "DELETE FROM farmer_bank_accounts WHERE org_id = :org_id"),
        ("farmers", "DELETE FROM farmers WHERE org_id = :org_id"),
        ("crop_price_rules", "DELETE FROM crop_price_rules WHERE org_id = :org_id"),
        ("buyers", "DELETE FROM buyers WHERE org_id = :org_id"),
        ("field_agents", "DELETE FROM field_agents WHERE org_id = :org_id"),
        ("analytics_daily_org_facts", "DELETE FROM analytics_daily_org_facts WHERE org_id = :org_id"),
        ("user_device_tokens", "DELETE FROM user_device_tokens WHERE user_id IN (SELECT id FROM users WHERE org_id = :org_id)"),
        (
            "refresh_tokens",
            "DELETE FROM refresh_tokens WHERE user_id IN (SELECT id FROM users WHERE org_id = :org_id AND email <> :owner_email)",
        ),
        (
            "users",
            "DELETE FROM users WHERE org_id = :org_id AND email <> :owner_email",
        ),
    ]

    if not keep_master_data:
        deletes.extend(
            [
                ("villages", "DELETE FROM villages WHERE org_id = :org_id"),
                ("crop_types", "DELETE FROM crop_types WHERE org_id = :org_id"),
                ("expense_categories", "DELETE FROM expense_categories WHERE org_id = :org_id"),
                ("vehicle_types", "DELETE FROM vehicle_types WHERE org_id = :org_id"),
                ("activity_types", "DELETE FROM activity_types WHERE org_id = :org_id"),
                ("payment_modes", "DELETE FROM payment_modes WHERE org_id = :org_id"),
                ("mandals", "DELETE FROM mandals WHERE org_id = :org_id"),
                ("districts", "DELETE FROM districts WHERE org_id = :org_id"),
            ]
        )

    ledger_disable = "ALTER TABLE farmer_ledger_entries DISABLE TRIGGER trg_farmer_ledger_immutable"
    ledger_enable = "ALTER TABLE farmer_ledger_entries ENABLE TRIGGER trg_farmer_ledger_immutable"

    print(f"Purging ALL org data for org_id={org_id} (owner kept: {owner_email})…")
    if dry_run:
        print("DRY RUN — no changes will be committed")

    if _table_exists("farmer_ledger_entries"):
        if dry_run:
            print(f"  DRY — disable ledger immutability trigger")
        else:
            db.execute(text(ledger_disable))

    for label, sql in deletes:
        table = label
        if not _table_exists(table):
            continue
        _run_delete(db, sql, params, label=label, dry_run=dry_run)

    settings_sql = """
        UPDATE organizations
        SET settings = COALESCE(settings, '{}'::jsonb)
          - 'demo_data_loaded' - 'demo_batch_id' - 'demo_marker'
          - 'synthetic_data_loaded' - 'synthetic_data_marker'
        WHERE id = :org_id
    """
    owner_reset_sql = """
        UPDATE users
        SET farmer_id = NULL, hamali_worker_id = NULL
        WHERE org_id = :org_id AND email = :owner_email
    """

    _run_delete(db, settings_sql, params, label="organizations.settings", dry_run=dry_run)
    if _table_exists("users"):
        _run_delete(db, owner_reset_sql, params, label="users.owner_links", dry_run=dry_run)

    if _table_exists("farmer_ledger_entries"):
        if dry_run:
            print("  DRY — enable ledger immutability trigger")
        else:
            db.execute(text(ledger_enable))

    if not dry_run:
        db.commit()
        print("Purge complete.")
        print(f"  Login: {owner_email} / (your configured DEFAULT_OWNER_PASSWORD)")
        if keep_master_data:
            print("  Master data kept — add farmers/procurements via UI or API.")
        else:
            print("  Master data cleared — run seed_locations / seed_services or create via UI.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Purge ALL KrishiFarms org business data")
    parser.add_argument("--org-code", default="KRISHI", help="Organization code (default: KRISHI)")
    parser.add_argument("--dry-run", action="store_true", help="Print planned deletes only")
    parser.add_argument(
        "--confirm",
        help="Required for live purge: pass PURGE-ALL-DATA",
    )
    parser.add_argument(
        "--keep-master-data",
        action="store_true",
        help="Keep villages, crops, districts, expense categories, platform masters",
    )
    args = parser.parse_args()

    if not args.dry_run and args.confirm != "PURGE-ALL-DATA":
        print("Refusing to purge without --confirm PURGE-ALL-DATA (or use --dry-run).", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.code == args.org_code).first()
        if org is None:
            org = db.query(Organization).first()
        if org is None:
            print("No organization found.", file=sys.stderr)
            sys.exit(1)

        purge_all_org_data(
            db,
            org_id=str(org.id),
            owner_email=settings.default_owner_email,
            keep_master_data=args.keep_master_data,
            dry_run=args.dry_run,
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
