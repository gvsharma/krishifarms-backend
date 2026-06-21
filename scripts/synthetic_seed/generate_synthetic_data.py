#!/usr/bin/env python3
"""
Generate SYNTHETIC seed CSV files and SQL insert script for KrishiFarms CRM.

All records are marked with:
  - data_source=synthetic (CSV column)
  - SYN-* code prefixes
  - notes containing SYNTHETIC_DATA

Run: python scripts/synthetic_seed/generate_synthetic_data.py
"""

from __future__ import annotations

import csv
import random
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

SYN_NS = uuid.UUID("b1e5f000-0000-4000-8000-000000000001")
SYN_NOTES = "SYNTHETIC_DATA — safe to delete before loading real production data"
DATA_SOURCE = "synthetic"
VILLAGE_NAME = "Bhairkhanpally"
OUTPUT_DIR = Path(__file__).resolve().parent
CSV_DIR = OUTPUT_DIR / "csv"
SQL_DIR = OUTPUT_DIR / "sql"

# Lookup placeholders resolved at load time in SQL via subqueries
ORG_CODE = "KRISHI"
OWNER_EMAIL = "owner@krishifarms.local"


def uid(label: str) -> str:
    return str(uuid.uuid5(SYN_NS, label))


def money(value: float | Decimal) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def weight(value: float) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def rand_date_2026_h1(rng: random.Random, start_month: int = 1, end_month: int = 6) -> date:
    month = rng.randint(start_month, end_month)
    day = rng.randint(1, 28)
    return date(2026, month, day)


TELUGU_FARMER_NAMES: list[tuple[str, str, str]] = [
    ("Rama Reddy", "రామ రెడ్డి", "Venkat Reddy"),
    ("Lakshmi Devi", "లక్ష్మీ దేవి", "Narayana"),
    ("Srinivas Rao", "శ్రీనివాస్ రావు", "Rama Rao"),
    ("Padmavathi", "పద్మావతి", "Krishna"),
    ("Venkatesh Goud", "వెంకటేష్ గౌడ్", "Malla Goud"),
    ("Anjali", "అంజలి", "Ravi"),
    ("Rajender", "రాజేందర్", "Saidulu"),
    ("Sunitha", "సునీత", "Balakrishna"),
    ("Mohan Rao", "మోహన్ రావు", "Venkata Rao"),
    ("Kavitha", "కవిత", "Narsaiah"),
    ("Chandraiah", "చంద్రయ్య", "Balaiah"),
    ("Swaroopa", "స్వరూప", "Mallaiah"),
    ("Nagesh", "నాగేష్", "Ramaiah"),
    ("Vijaya", "విజయ", "Srinu"),
    ("Prabhakar", "ప్రభాకర్", "Venkaiah"),
    ("Shailaja", "శైలజ", "Komuraiah"),
    ("Ramesh Goud", "రమేష్ గౌడ్", "Bixam Goud"),
    ("Haritha", "హరిత", "Yadaiah"),
    ("Suresh", "సురేష్", "Laxmaiah"),
    ("Manjula", "మంజుల", "Peddaiah"),
    ("Krishna Murthy", "కృష్ణ మూర్తి", "Venkatesham"),
    ("Nirmala", "నిర్మల", "Sathaiah"),
    ("Gopal", "గోపాల్", "Mogili"),
    ("Savithri", "సావిత్రి", "Rangiah"),
    ("Mahesh", "మహేష్", "Kistaiah"),
    ("Lalitha", "లలిత", "Narayana"),
    ("Venkatesham", "వెంకటేశం", "Balaiah"),
    ("Jyothi", "జ్యోతి", "Saidulu"),
    ("Balaji", "బాలాజీ", "Ramaiah"),
    ("Sujatha", "సుజాత", "Mallaiah"),
    ("Narayana Goud", "నారాయణ గౌడ్", "Bojja Goud"),
    ("Radha", "రాధ", "Komuraiah"),
    ("Siddaiah", "సిద్దయ్య", "Venkataiah"),
    ("Pramila", "ప్రమిల", "Yadaiah"),
    ("Raghavender", "రాఘవేందర్", "Laxmaiah"),
    ("Mamatha", "మమత", "Peddaiah"),
    ("Yadaiah", "యాదయ్య", "Balaiah"),
    ("Swapna", "స్వప్న", "Rama Rao"),
    ("Kistaiah", "కిస్టయ్య", "Mogili"),
    ("Aruna", "అరుణ", "Srinivas"),
    ("Balaiah", "బాలయ్య", "Rangiah"),
    ("Deepa", "దీప", "Narayana"),
    ("Mallaiah", "మల్లయ్య", "Venkatesham"),
    ("Geetha", "గీత", "Sathaiah"),
    ("Saidulu", "సైదులు", "Balaiah"),
    ("Padma", "పద్మ", "Krishna"),
    ("Ravi Kumar", "రవి కుమార్", "Venkat Reddy"),
    ("Anitha", "అనిత", "Rama Rao"),
    ("Venkataiah", "వెంకటయ్య", "Mogili"),
    ("Gangadhar", "గంగాధర్", "Ramaiah"),
]

WORKER_NAMES: list[tuple[str, str]] = [
    ("Raju", "రాజు"),
    ("Swamy", "స్వామి"),
    ("Naveen", "నవీన్"),
    ("Mallesh", "మల్లేష్"),
    ("Srinu", "శ్రీను"),
    ("Vijay", "విజయ్"),
    ("Prakash", "ప్రకాష్"),
    ("Ravi", "రవి"),
    ("Kumar", "కుమార్"),
    ("Shekar", "శేఖర్"),
]

FARM_NAMES: list[tuple[str, str, float]] = [
    ("North Paddy Field", "ఉత్తర వరి పొలం", 12.5),
    ("South Corn Plot", "దక్షిణ మొక్కజొన్న ప్లాట్", 8.0),
    ("Tank Bund Farm", "ట్యాంక్ బంధం పొలం", 15.25),
    ("Canal Side Farm", "కాలువ పక్కన పొలం", 10.0),
    ("Hill Slope Farm", "కొండ వెనక పొలం", 6.75),
]

ASSETS_SPEC: list[tuple[str, str, str, str, str]] = [
    ("SYN-AST-TRC-001", "Mahindra 575 DI", "మహీంద్రా 575", "tractor", "TS09SYN0001"),
    ("SYN-AST-TRC-002", "Swaraj 744 FE", "స్వరాజ్ 744", "tractor", "TS09SYN0002"),
    ("SYN-AST-TRC-003", "John Deere 5050D", "జాన్ డియర్ 5050", "tractor", "TS09SYN0003"),
    ("SYN-AST-DCM-001", "DCM Trailer", "డీసీఎం ట్రైలర్", "dcm", "TS09SYN0004"),
    ("SYN-AST-BAL-001", "Balers Pack-Master", "బేలర్", "baler", "TS09SYN0005"),
    ("SYN-AST-BOL-001", "Mahindra Bolero Pickup", "మహీంద్రా బోలెరో", "other", "TS09SYN0006"),
]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def generate() -> dict[str, int]:
    rng = random.Random(42)
    counts: dict[str, int] = {}

    village_id = uid("village-bhairkhanpally")
    crop_paddy_id = uid("crop-paddy")
    crop_corn_id = uid("crop-corn")

    # --- Farmers ---
    farmers: list[dict] = []
    for i, (name, name_te, father) in enumerate(TELUGU_FARMER_NAMES, start=1):
        farmers.append(
            {
                "id": uid(f"farmer-{i:03d}"),
                "farmer_code": f"SYN-FMR-{i:03d}",
                "full_name": name,
                "full_name_te": name_te,
                "father_name": father,
                "phone_primary": f"98765{10000 + i:05d}",
                "phone_secondary": "",
                "village_id": village_id,
                "address": f"H.No {i}, {VILLAGE_NAME}, Telangana",
                "address_te": f"హెచ్.నం {i}, భైర్ఖాన్‌పల్లి",
                "aadhaar_last4": f"{1000 + i:04d}"[-4:],
                "status": "active",
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
    write_csv(
        CSV_DIR / "farmers.csv",
        [
            "id",
            "farmer_code",
            "full_name",
            "full_name_te",
            "father_name",
            "phone_primary",
            "phone_secondary",
            "village_id",
            "address",
            "address_te",
            "aadhaar_last4",
            "status",
            "notes",
            "data_source",
        ],
        farmers,
    )
    counts["farmers"] = len(farmers)

    # --- Workers ---
    workers: list[dict] = []
    for i, (name, name_te) in enumerate(WORKER_NAMES, start=1):
        workers.append(
            {
                "id": uid(f"worker-{i:03d}"),
                "worker_code": f"SYN-WKR-{i:03d}",
                "full_name": name,
                "full_name_te": name_te,
                "phone": f"98665{10000 + i:05d}",
                "village_id": village_id,
                "hourly_rate": money(120 + i * 5),
                "daily_rate": money(800 + i * 20),
                "status": "active",
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
    write_csv(
        CSV_DIR / "workers.csv",
        [
            "id",
            "worker_code",
            "full_name",
            "full_name_te",
            "phone",
            "village_id",
            "hourly_rate",
            "daily_rate",
            "status",
            "notes",
            "data_source",
        ],
        workers,
    )
    counts["workers"] = len(workers)

    # --- Farms ---
    farms: list[dict] = []
    for i, (name, name_te, acres) in enumerate(FARM_NAMES, start=1):
        owner = farmers[(i - 1) % len(farmers)]
        farms.append(
            {
                "id": uid(f"farm-{i:03d}"),
                "farm_code": f"SYN-FRM-{i:03d}",
                "name": name,
                "name_te": name_te,
                "acres": weight(acres),
                "location": f"{VILLAGE_NAME}, Medak District",
                "village_id": village_id,
                "owner_farmer_id": owner["id"],
                "status": "active",
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
    write_csv(
        CSV_DIR / "farms.csv",
        [
            "id",
            "farm_code",
            "name",
            "name_te",
            "acres",
            "location",
            "village_id",
            "owner_farmer_id",
            "status",
            "notes",
            "data_source",
        ],
        farms,
    )
    counts["farms"] = len(farms)

    # --- Assets ---
    assets: list[dict] = []
    for code, name, name_te, category, reg in ASSETS_SPEC:
        assets.append(
            {
                "id": uid(f"asset-{code}"),
                "asset_code": code,
                "name": name,
                "name_te": name_te,
                "asset_category": category,
                "registration_number": reg,
                "status": "active",
                "is_rentable": "true" if category in ("tractor", "dcm", "baler") else "false",
                "hourly_rate": money(900 if category == "tractor" else 600),
                "daily_rate": money(5500 if category == "tractor" else 3500),
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
    write_csv(
        CSV_DIR / "assets.csv",
        [
            "id",
            "asset_code",
            "name",
            "name_te",
            "asset_category",
            "registration_number",
            "status",
            "is_rentable",
            "hourly_rate",
            "daily_rate",
            "notes",
            "data_source",
        ],
        assets,
    )
    counts["assets"] = len(assets)

    # --- Rental customers & agreements (for collections) ---
    rental_customers: list[dict] = []
    rental_agreements: list[dict] = []
    for i in range(1, 11):
        rental_customers.append(
            {
                "id": uid(f"rental-customer-{i:03d}"),
                "customer_code": f"SYN-RNT-CUS-{i:03d}",
                "name": f"Rental Customer {i}",
                "name_te": f"అద్దెకు కస్టమర్ {i}",
                "phone": f"98555{10000 + i:05d}",
                "address": f"{VILLAGE_NAME} area",
                "village_id": village_id,
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
    rentable_assets = [a for a in assets if a["is_rentable"] == "true"]
    for i in range(1, 16):
        cust = rental_customers[(i - 1) % len(rental_customers)]
        asset = rentable_assets[(i - 1) % len(rentable_assets)]
        start = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=i * 10)
        hours = Decimal(str(4 + (i % 6)))
        rate = Decimal(asset["hourly_rate"])
        revenue = (hours * rate).quantize(Decimal("0.01"))
        collected = (revenue * Decimal("0.6")).quantize(Decimal("0.01"))
        rental_agreements.append(
            {
                "id": uid(f"rental-agreement-{i:03d}"),
                "agreement_number": f"SYN-RNT-AGR-{i:03d}",
                "customer_id": cust["id"],
                "asset_id": asset["id"],
                "start_datetime": start.isoformat(),
                "end_datetime": (start + timedelta(hours=float(hours))).isoformat(),
                "rate_type": "hourly",
                "hourly_rate": money(rate),
                "total_hours": money(hours),
                "revenue": money(revenue),
                "collected_amount": money(collected),
                "status": "completed",
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
    write_csv(
        CSV_DIR / "rental_customers.csv",
        [
            "id",
            "customer_code",
            "name",
            "name_te",
            "phone",
            "address",
            "village_id",
            "notes",
            "data_source",
        ],
        rental_customers,
    )
    write_csv(
        CSV_DIR / "rental_agreements.csv",
        [
            "id",
            "agreement_number",
            "customer_id",
            "asset_id",
            "start_datetime",
            "end_datetime",
            "rate_type",
            "hourly_rate",
            "total_hours",
            "revenue",
            "collected_amount",
            "status",
            "notes",
            "data_source",
        ],
        rental_agreements,
    )
    counts["rental_customers"] = len(rental_customers)
    counts["rental_agreements"] = len(rental_agreements)

    # --- Procurements ---
    procurements: list[dict] = []
    farmer_balances: dict[str, Decimal] = {f["id"]: Decimal("0") for f in farmers}
    ledger_rows: list[dict] = []

    for i in range(1, 201):
        farmer = farmers[rng.randint(0, len(farmers) - 1)]
        is_paddy = rng.random() < 0.6
        crop_id = crop_paddy_id if is_paddy else crop_corn_id
        crop_code = "PADDY" if is_paddy else "CORN"
        proc_date = rand_date_2026_h1(rng)
        bag_count = rng.randint(5, 40)
        gross_weight = Decimal(str(bag_count * rng.uniform(48, 62))).quantize(Decimal("0.001"))
        moisture = Decimal(str(rng.uniform(12, 18 if is_paddy else 14))).quantize(Decimal("0.01"))
        net_weight = (gross_weight * (Decimal("1") - moisture / Decimal("100"))).quantize(Decimal("0.001"))
        rate = Decimal(str(rng.uniform(2100, 2400) if is_paddy else rng.uniform(1800, 2100))).quantize(
            Decimal("0.01")
        )
        gross_amount = (net_weight / Decimal("100") * rate).quantize(Decimal("0.01"))
        deduction = (gross_amount * Decimal(str(rng.uniform(0, 0.02)))).quantize(Decimal("0.01"))
        net_amount = gross_amount - deduction
        status = "confirmed" if rng.random() < 0.9 else "draft"
        proc_id = uid(f"procurement-{i:04d}")
        procurements.append(
            {
                "id": proc_id,
                "procurement_number": f"SYN-PROC-2026-{i:04d}",
                "farmer_id": farmer["id"],
                "crop_type_id": crop_id,
                "crop_code": crop_code,
                "village_id": village_id,
                "procurement_date": proc_date.isoformat(),
                "bag_count": bag_count,
                "gross_weight_kg": weight(gross_weight),
                "moisture_pct": money(moisture),
                "net_weight_kg": weight(net_weight),
                "rate_per_quintal": money(rate),
                "gross_amount": money(gross_amount),
                "deduction_amount": money(deduction),
                "net_amount": money(net_amount),
                "status": status,
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
        if status == "confirmed":
            farmer_balances[farmer["id"]] += net_amount
            ledger_rows.append(
                {
                    "id": uid(f"ledger-proc-{i:04d}"),
                    "farmer_id": farmer["id"],
                    "entry_date": proc_date.isoformat(),
                    "entry_type": "procurement",
                    "reference_type": "procurement",
                    "reference_id": proc_id,
                    "debit": money(net_amount),
                    "credit": "0.00",
                    "balance_after": money(farmer_balances[farmer["id"]]),
                    "description": f"SYNTHETIC procurement {procurements[-1]['procurement_number']}",
                    "data_source": DATA_SOURCE,
                }
            )

    write_csv(
        CSV_DIR / "procurements.csv",
        [
            "id",
            "procurement_number",
            "farmer_id",
            "crop_type_id",
            "crop_code",
            "village_id",
            "procurement_date",
            "bag_count",
            "gross_weight_kg",
            "moisture_pct",
            "net_weight_kg",
            "rate_per_quintal",
            "gross_amount",
            "deduction_amount",
            "net_amount",
            "status",
            "notes",
            "data_source",
        ],
        procurements,
    )
    write_csv(
        CSV_DIR / "farmer_ledger_entries.csv",
        [
            "id",
            "farmer_id",
            "entry_date",
            "entry_type",
            "reference_type",
            "reference_id",
            "debit",
            "credit",
            "balance_after",
            "description",
            "data_source",
        ],
        ledger_rows,
    )
    counts["procurements"] = len(procurements)
    counts["farmer_ledger_entries"] = len(ledger_rows)

    # --- Farmer payments (30) ---
    farmer_payments: list[dict] = []
    payment_modes = ["cash", "upi", "bank_transfer"]
    for i in range(1, 31):
        farmer = farmers[rng.randint(0, len(farmers) - 1)]
        pay_date = rand_date_2026_h1(rng)
        amount = Decimal(str(rng.uniform(2000, 25000))).quantize(Decimal("0.01"))
        pay_type = rng.choice(["advance", "final", "adjustment"])
        pay_id = uid(f"farmer-payment-{i:03d}")
        farmer_payments.append(
            {
                "id": pay_id,
                "payment_number": f"SYN-FPAY-2026-{i:03d}",
                "farmer_id": farmer["id"],
                "payment_type": pay_type,
                "payment_date": pay_date.isoformat(),
                "amount": money(amount),
                "payment_mode_code": rng.choice(payment_modes),
                "reference_no": f"UPI{100000 + i}",
                "status": "completed",
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
        farmer_balances[farmer["id"]] -= amount
        ledger_rows.append(
            {
                "id": uid(f"ledger-fpay-{i:03d}"),
                "farmer_id": farmer["id"],
                "entry_date": pay_date.isoformat(),
                "entry_type": pay_type,
                "reference_type": "farmer_payment",
                "reference_id": pay_id,
                "debit": "0.00",
                "credit": money(amount),
                "balance_after": money(farmer_balances[farmer["id"]]),
                "description": f"SYNTHETIC payment {farmer_payments[-1]['payment_number']}",
                "data_source": DATA_SOURCE,
            }
        )
    # Rewrite ledger with payments included
    write_csv(
        CSV_DIR / "farmer_ledger_entries.csv",
        [
            "id",
            "farmer_id",
            "entry_date",
            "entry_type",
            "reference_type",
            "reference_id",
            "debit",
            "credit",
            "balance_after",
            "description",
            "data_source",
        ],
        ledger_rows,
    )
    counts["farmer_payments"] = len(farmer_payments)
    counts["farmer_ledger_entries"] = len(ledger_rows)
    write_csv(
        CSV_DIR / "farmer_payments.csv",
        [
            "id",
            "payment_number",
            "farmer_id",
            "payment_type",
            "payment_date",
            "amount",
            "payment_mode_code",
            "reference_no",
            "status",
            "notes",
            "data_source",
        ],
        farmer_payments,
    )

    # --- Operational payments (20) ---
    operational_payments: list[dict] = []
    vendors = ["SYN Fuel Depot", "SYN Agro Shop", "SYN Mechanic", "SYN Transport", "SYN Seeds Store"]
    for i in range(1, 21):
        operational_payments.append(
            {
                "id": uid(f"payment-{i:03d}"),
                "payment_number": f"SYN-PAY-2026-{i:03d}",
                "payee_type": rng.choice(["vendor", "worker", "other"]),
                "payee_name": rng.choice(vendors),
                "payee_id": workers[rng.randint(0, len(workers) - 1)]["id"],
                "payment_date": rand_date_2026_h1(rng).isoformat(),
                "amount": money(rng.uniform(500, 15000)),
                "payment_mode_code": rng.choice(payment_modes),
                "category_name": rng.choice(["Fuel", "Labor", "Maintenance", "Miscellaneous"]),
                "reference_no": f"PAY{200000 + i}",
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
    write_csv(
        CSV_DIR / "payments.csv",
        [
            "id",
            "payment_number",
            "payee_type",
            "payee_name",
            "payee_id",
            "payment_date",
            "amount",
            "payment_mode_code",
            "category_name",
            "reference_no",
            "notes",
            "data_source",
        ],
        operational_payments,
    )
    counts["payments"] = len(operational_payments)
    counts["payments_total"] = len(farmer_payments) + len(operational_payments)

    # --- Expenses (100) ---
    expenses: list[dict] = []
    for i in range(1, 101):
        farm = farms[rng.randint(0, len(farms) - 1)]
        asset = assets[rng.randint(0, len(assets) - 1)]
        expenses.append(
            {
                "id": uid(f"expense-{i:03d}"),
                "expense_number": f"SYN-EXP-2026-{i:03d}",
                "category_name": rng.choice(["Fuel", "Labor", "Maintenance", "Miscellaneous"]),
                "expense_date": rand_date_2026_h1(rng).isoformat(),
                "amount": money(rng.uniform(200, 12000)),
                "vendor_name": rng.choice(vendors),
                "payment_mode_code": rng.choice(payment_modes),
                "farm_id": farm["id"],
                "asset_id": asset["id"],
                "description": f"SYNTHETIC expense for {VILLAGE_NAME} operations",
                "status": "posted",
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
    write_csv(
        CSV_DIR / "expenses.csv",
        [
            "id",
            "expense_number",
            "category_name",
            "expense_date",
            "amount",
            "vendor_name",
            "payment_mode_code",
            "farm_id",
            "asset_id",
            "description",
            "status",
            "notes",
            "data_source",
        ],
        expenses,
    )
    counts["expenses"] = len(expenses)

    # --- Collections (50) ---
    collections: list[dict] = []
    for i in range(1, 51):
        agreement = rental_agreements[rng.randint(0, len(rental_agreements) - 1)]
        customer = next(c for c in rental_customers if c["id"] == agreement["customer_id"])
        pending = Decimal(agreement["revenue"]) - Decimal(agreement["collected_amount"])
        amount = (pending * Decimal(str(rng.uniform(0.3, 1.0)))).quantize(Decimal("0.01"))
        if amount <= 0:
            amount = Decimal("500.00")
        collections.append(
            {
                "id": uid(f"collection-{i:03d}"),
                "collection_number": f"SYN-COL-2026-{i:03d}",
                "source_type": "rental",
                "source_id": agreement["id"],
                "customer_id": customer["id"],
                "collection_date": rand_date_2026_h1(rng).isoformat(),
                "amount": money(amount),
                "payment_mode_code": rng.choice(payment_modes),
                "reference_no": f"COL{300000 + i}",
                "notes": SYN_NOTES,
                "data_source": DATA_SOURCE,
            }
        )
    write_csv(
        CSV_DIR / "collections.csv",
        [
            "id",
            "collection_number",
            "source_type",
            "source_id",
            "customer_id",
            "collection_date",
            "amount",
            "payment_mode_code",
            "reference_no",
            "notes",
            "data_source",
        ],
        collections,
    )
    counts["collections"] = len(collections)

    # --- Manifest ---
    manifest = {
        "data_source": DATA_SOURCE,
        "village": VILLAGE_NAME,
        "village_id": village_id,
        "crop_paddy_id": crop_paddy_id,
        "crop_corn_id": crop_corn_id,
        "notes": SYN_NOTES,
        "counts": counts,
    }
    import json

    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return counts


def sql_quote(value: str | None) -> str:
    if value is None or value == "":
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def generate_sql_inserts() -> None:
    """Generate generated_inserts.sql from CSV for environments without \\copy."""
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "-- AUTO-GENERATED by generate_synthetic_data.py — SYNTHETIC DATA ONLY",
        "",
    ]

    def load_block(table: str, csv_name: str, columns: list[str], select_org: bool = True) -> None:
        path = CSV_DIR / csv_name
        if not path.exists():
            return
        with path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                vals = []
                for col in columns:
                    if col == "org_id":
                        vals.append("(SELECT id FROM organizations WHERE code = 'KRISHI')")
                    elif col == "posted_by" or col == "created_by" or col == "updated_by":
                        vals.append(
                            f"(SELECT id FROM users WHERE email = '{OWNER_EMAIL}' LIMIT 1)"
                        )
                    elif col == "payment_mode_id":
                        vals.append(
                            f"(SELECT id FROM payment_modes WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI') AND code = {sql_quote(row['payment_mode_code'])} LIMIT 1)"
                        )
                    elif col == "category_id":
                        vals.append(
                            f"(SELECT id FROM expense_categories WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI') AND name = {sql_quote(row.get('category_name'))} LIMIT 1)"
                        )
                    elif col == "crop_type_id" and "crop_code" in row:
                        code = row["crop_code"]
                        vals.append(
                            f"(SELECT id FROM crop_types WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI') AND code = '{code}' LIMIT 1)"
                        )
                    else:
                        vals.append(sql_quote(row.get(col)))
                lines.append(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(vals)});")

    # Farmers
    for row in csv.DictReader((CSV_DIR / "farmers.csv").open(encoding="utf-8")):
        lines.append(
            f"""INSERT INTO farmers (id, org_id, farmer_code, full_name, full_name_te, father_name, phone_primary, phone_secondary, village_id, address, address_te, aadhaar_last4, status, notes, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['farmer_code'])}, {sql_quote(row['full_name'])}, {sql_quote(row['full_name_te'])}, {sql_quote(row['father_name'])}, {sql_quote(row['phone_primary'])}, NULL, {sql_quote(row['village_id'])}, {sql_quote(row['address'])}, {sql_quote(row['address_te'])}, {sql_quote(row['aadhaar_last4'])}, 'active', {sql_quote(row['notes'])}, (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    # Workers, farms, assets - similar pattern in bulk via helper
    for row in csv.DictReader((CSV_DIR / "workers.csv").open(encoding="utf-8")):
        lines.append(
            f"""INSERT INTO workers (id, org_id, worker_code, full_name, full_name_te, phone, village_id, hourly_rate, daily_rate, status, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['worker_code'])}, {sql_quote(row['full_name'])}, {sql_quote(row['full_name_te'])}, {sql_quote(row['phone'])}, {sql_quote(row['village_id'])}, {row['hourly_rate']}, {row['daily_rate']}, 'active', (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "farms.csv").open(encoding="utf-8")):
        lines.append(
            f"""INSERT INTO farms (id, org_id, farm_code, name, name_te, acres, location, village_id, owner_farmer_id, status, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['farm_code'])}, {sql_quote(row['name'])}, {sql_quote(row['name_te'])}, {row['acres']}, {sql_quote(row['location'])}, {sql_quote(row['village_id'])}, {sql_quote(row['owner_farmer_id'])}, 'active', (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "assets.csv").open(encoding="utf-8")):
        lines.append(
            f"""INSERT INTO assets (id, org_id, asset_code, name, name_te, asset_category, registration_number, status, is_rentable, hourly_rate, daily_rate, notes, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['asset_code'])}, {sql_quote(row['name'])}, {sql_quote(row['name_te'])}, {sql_quote(row['asset_category'])}, {sql_quote(row['registration_number'])}, 'active', {row['is_rentable']}, {row['hourly_rate']}, {row['daily_rate']}, {sql_quote(row['notes'])}, (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "rental_customers.csv").open(encoding="utf-8")):
        lines.append(
            f"""INSERT INTO rental_customers (id, org_id, customer_code, name, name_te, phone, address, village_id, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['customer_code'])}, {sql_quote(row['name'])}, {sql_quote(row['name_te'])}, {sql_quote(row['phone'])}, {sql_quote(row['address'])}, {sql_quote(row['village_id'])}, (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "rental_agreements.csv").open(encoding="utf-8")):
        lines.append(
            f"""INSERT INTO rental_agreements (id, org_id, agreement_number, customer_id, asset_id, start_datetime, end_datetime, rate_type, hourly_rate, total_hours, revenue, collected_amount, status, notes, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['agreement_number'])}, {sql_quote(row['customer_id'])}, {sql_quote(row['asset_id'])}, {sql_quote(row['start_datetime'])}, {sql_quote(row['end_datetime'])}, 'hourly', {row['hourly_rate']}, {row['total_hours']}, {row['revenue']}, {row['collected_amount']}, 'completed', {sql_quote(row['notes'])}, (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "procurements.csv").open(encoding="utf-8")):
        confirmed = "now()" if row["status"] == "confirmed" else "NULL"
        confirmed_by = f"(SELECT id FROM users WHERE email='{OWNER_EMAIL}')" if row["status"] == "confirmed" else "NULL"
        crop_code = row["crop_code"]
        lines.append(
            f"""INSERT INTO procurements (id, org_id, procurement_number, farmer_id, crop_type_id, village_id, procurement_date, bag_count, gross_weight_kg, moisture_pct, net_weight_kg, rate_per_quintal, gross_amount, deduction_amount, net_amount, status, confirmed_at, confirmed_by, notes, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['procurement_number'])}, {sql_quote(row['farmer_id'])}, (SELECT id FROM crop_types WHERE code='{crop_code}' AND org_id=(SELECT id FROM organizations WHERE code='KRISHI')), {sql_quote(row['village_id'])}, {sql_quote(row['procurement_date'])}, {row['bag_count']}, {row['gross_weight_kg']}, {row['moisture_pct']}, {row['net_weight_kg']}, {row['rate_per_quintal']}, {row['gross_amount']}, {row['deduction_amount']}, {row['net_amount']}, {sql_quote(row['status'])}, {confirmed}, {confirmed_by}, {sql_quote(row['notes'])}, (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "farmer_ledger_entries.csv").open(encoding="utf-8")):
        lines.append(
            f"""INSERT INTO farmer_ledger_entries (id, org_id, farmer_id, entry_date, entry_type, reference_type, reference_id, debit, credit, balance_after, description, posted_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['farmer_id'])}, {sql_quote(row['entry_date'])}, {sql_quote(row['entry_type'])}, {sql_quote(row['reference_type'])}, {sql_quote(row['reference_id'])}, {row['debit']}, {row['credit']}, {row['balance_after']}, {sql_quote(row['description'])}, (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "farmer_payments.csv").open(encoding="utf-8")):
        mode = row["payment_mode_code"]
        lines.append(
            f"""INSERT INTO farmer_payments (id, org_id, payment_number, farmer_id, payment_type, payment_date, amount, payment_mode_id, reference_no, status, notes, posted_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['payment_number'])}, {sql_quote(row['farmer_id'])}, {sql_quote(row['payment_type'])}, {sql_quote(row['payment_date'])}, {row['amount']}, (SELECT id FROM payment_modes WHERE code='{mode}' AND org_id=(SELECT id FROM organizations WHERE code='KRISHI')), {sql_quote(row['reference_no'])}, 'completed', {sql_quote(row['notes'])}, (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "expenses.csv").open(encoding="utf-8")):
        mode = row["payment_mode_code"]
        cat = row["category_name"]
        lines.append(
            f"""INSERT INTO expenses (id, org_id, expense_number, category_id, expense_date, amount, vendor_name, payment_mode_id, farm_id, asset_id, description, status, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['expense_number'])}, (SELECT id FROM expense_categories WHERE name='{cat}' AND org_id=(SELECT id FROM organizations WHERE code='KRISHI')), {sql_quote(row['expense_date'])}, {row['amount']}, {sql_quote(row['vendor_name'])}, (SELECT id FROM payment_modes WHERE code='{mode}' AND org_id=(SELECT id FROM organizations WHERE code='KRISHI')), {sql_quote(row['farm_id'])}, {sql_quote(row['asset_id'])}, {sql_quote(row['description'])}, 'posted', (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "collections.csv").open(encoding="utf-8")):
        mode = row["payment_mode_code"]
        lines.append(
            f"""INSERT INTO collections (id, org_id, collection_number, source_type, source_id, customer_id, collection_date, amount, payment_mode_id, reference_no, notes, status, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['collection_number'])}, 'rental', {sql_quote(row['source_id'])}, {sql_quote(row['customer_id'])}, {sql_quote(row['collection_date'])}, {row['amount']}, (SELECT id FROM payment_modes WHERE code='{mode}' AND org_id=(SELECT id FROM organizations WHERE code='KRISHI')), {sql_quote(row['reference_no'])}, {sql_quote(row['notes'])}, 'posted', (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    for row in csv.DictReader((CSV_DIR / "payments.csv").open(encoding="utf-8")):
        mode = row["payment_mode_code"]
        cat = row["category_name"]
        lines.append(
            f"""INSERT INTO payments (id, org_id, payment_number, payee_type, payee_name, payee_id, payment_date, amount, payment_mode_id, category_id, reference_no, notes, status, created_by, updated_by)
VALUES ({sql_quote(row['id'])}, (SELECT id FROM organizations WHERE code='KRISHI'), {sql_quote(row['payment_number'])}, {sql_quote(row['payee_type'])}, {sql_quote(row['payee_name'])}, {sql_quote(row['payee_id'])}, {sql_quote(row['payment_date'])}, {row['amount']}, (SELECT id FROM payment_modes WHERE code='{mode}' AND org_id=(SELECT id FROM organizations WHERE code='KRISHI')), (SELECT id FROM expense_categories WHERE name='{cat}' AND org_id=(SELECT id FROM organizations WHERE code='KRISHI')), {sql_quote(row['reference_no'])}, {sql_quote(row['notes'])}, 'posted', (SELECT id FROM users WHERE email='{OWNER_EMAIL}'), (SELECT id FROM users WHERE email='{OWNER_EMAIL}'));"""
        )

    (SQL_DIR / "generated_inserts.sql").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    counts = generate()
    generate_sql_inserts()
    print("Synthetic seed data generated.")
    for key, value in sorted(counts.items()):
        print(f"  {key}: {value}")
    print(f"CSV directory: {CSV_DIR}")
    print(f"SQL inserts:   {SQL_DIR / 'generated_inserts.sql'}")


if __name__ == "__main__":
    main()
