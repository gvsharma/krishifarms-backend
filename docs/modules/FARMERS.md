# Farmers Module — Phase 2a / 2b / Farmer 360°

Org-scoped farmer registry for Bhairkhanpally field operations. Maps to migrations `202506210004` + `202506210030` (360° profile fields).

## Field groups

| Group | Fields | Storage | API |
|-------|--------|---------|-----|
| **Profile** | `farmer_code` (auto `FMR-####`), `full_name`, `full_name_te`, `status`, `notes`, `is_vip` | `farmers` | ✅ |
| **Family** | `father_name`, `father_name_te` | `farmers` | ✅ |
| **Contact** | `phone_primary`, `phone_secondary`, `address`, `address_te` | `farmers` | ✅ |
| **Village** | `village_id`, resolved `village_name` / mandal / district | `farmers` → `villages` | ✅ |
| **KYC** | `aadhaar_last4`, `pan_encrypted` | `farmers` | ✅ last4 only |
| **Prefs / trust** | `preferred_language`, `preferred_payment_cycle`, `preferred_payment_method`, `trust_rating` (1–5), `geo_lat`/`geo_lng` | `farmers` | ✅ optional |
| **GPS (land)** | `geo_lat`, `geo_lng` per parcel | `farmer_land_parcels` | ✅ |
| **Bank** | account holder, IFSC, masked account | `farmer_bank_accounts` | ✅ |
| **Land** | survey, acres, ownership, irrigation, water, soil | `farmer_land_parcels` | ✅ |
| **Crops** | season/year + farming detail fields | `farmer_crop_history` | ✅ |
| **Ledger** | `outstanding_amount` | `farmer_ledger_entries` | ✅ detail + `/outstanding` + `/ledger` |

**Status labels:** `active` → Active · `inactive` → Inactive · `blocked` → Blacklisted · `is_vip` + active → VIP Farmer.

## Farmer 360° profile

`GET /farmers/{id}/profile-360` aggregates the relationship hub:

- Summary card (identity, location, prefs, trust, status)
- Quick statistics (services, area, procurement, outstanding, season)
- Unified timeline (create, services, diesel, crops, procurements, payments, finance, comments, documents)
- Services / farming / procurement / agri-finance / ledger histories
- Crop intelligence + analytics + AI-ready recommendations + quick actions
- Land, documents (`entity_type=farmer`), communication (comments)

Web UI: `/farmers/{id}` — circular orbit hub + section panels (desktop multi-column; mobile cards).

## API (Python)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| GET | `/farmers` | `farmers:read` | Filter: `village_id`, `status`, `q` |
| POST | `/farmers` | `farmers:create` | Auto `farmer_code` |
| GET | `/farmers/{id}` | `farmers:read` | Detail + bank/land/comments/tags |
| GET | `/farmers/{id}/profile-360` | `farmers:read` | Full relationship profile |
| PATCH | `/farmers/{id}` | `farmers:update` | Includes prefs / trust / VIP |
| DELETE | `/farmers/{id}` | `farmers:delete` + **OWNER** | Soft delete |
| GET/POST | `/farmers/{id}/bank-accounts` | read / update | Encrypted account |
| PATCH/DELETE | `/farmers/{id}/bank-accounts/{account_id}` | `farmers:update` | |
| GET/POST | `/farmers/{id}/land-parcels` | read / update | Ownership / irrigation optional |
| PATCH/DELETE | `/farmers/{id}/land-parcels/{parcel_id}` | `farmers:update` | |
| GET/POST | `/farmers/{id}/crop-history` | read / update | Farming history |
| GET | `/farmers/{id}/ledger` | `farmers:read` | Paginated ledger |
| GET | `/farmers/{id}/outstanding` | `farmers:read` | Latest balance |

## Accountability

Mutations call `write_audit_log` + `write_activity_feed` with `ClientContext`.

## RBAC

| Role | read | create | update | delete |
|------|:----:|:------:|:------:|:------:|
| OWNER | ✅ | ✅ | ✅ | ✅ |
| MANAGER | ✅ | ✅ | ✅ | ❌ |
| SUPERVISOR | ✅ | ✅ | ✅ | ❌ |
| AGENT / DRIVER | ❌ | ❌ | ❌ | ❌ |

## Related docs

- OpenAPI: `docs/api/paths/farmers.yaml`, `docs/api/schemas/farmers.yaml`
- Cross-cutting: [CROSS_CUTTING.md](./CROSS_CUTTING.md)
- Procurement: [PROCUREMENT.md](./PROCUREMENT.md)
- Tests: `tests/test_farmer_360.py`
