# Farmers Module — Phase 2a

Org-scoped farmer registry for Bhairkhanpally field operations. Maps to migration `202506210004`.

## Field groups

| Group | Fields | Storage | Phase 2a API |
|-------|--------|---------|--------------|
| **Profile** | `farmer_code` (auto `FMR-####`), `full_name`, `full_name_te`, `status`, `notes` | `farmers` | ✅ |
| **Family** | `father_name`, `father_name_te` | `farmers` | ✅ |
| **Contact** | `phone_primary`, `phone_secondary`, `address`, `address_te` | `farmers` | ✅ |
| **Village** | `village_id`, resolved `village_name` | `farmers` → `villages` | ✅ |
| **KYC** | `aadhaar_last4`, `pan_encrypted` | `farmers` | ✅ last4 only; PAN Phase 2b |
| **GPS** | `geo_lat`, `geo_lng` per land parcel | `farmer_land_parcels` | 📋 Phase 2b sub-resource |
| **Bank** | account holder, IFSC, masked account | `farmer_bank_accounts` | 📋 Phase 2b sub-resource |
| **Land / crops** | survey number, acres, crop history | `farmer_land_parcels`, `farmer_crop_history` | 📋 Phase 2b |
| **Rating** | reliability score (1–5) from procurement/payment history | derived / future column | 📋 computed in Phase 2b+ |
| **Ledger** | `outstanding_amount` | `farmer_ledger_entries` | 📋 Phase 2b |

## API (Python)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| GET | `/farmers` | `farmers:read` | Filter: `village_id`, `status`, `q` (name/phone/code) |
| POST | `/farmers` | `farmers:create` | Auto-generates `farmer_code` |
| GET | `/farmers/{id}` | `farmers:read` | Includes comments + tags |
| PATCH | `/farmers/{id}` | `farmers:update` | |
| DELETE | `/farmers/{id}` | `farmers:delete` + **OWNER role** | Soft delete |

Comments use platform polymorphic API with `entity_type=farmer`.

## Accountability

Mutations call `write_audit_log` + `write_activity_feed` with `ClientContext` (`X-Device-Id`, `X-Client-Type`).

## RBAC

| Role | read | create | update | delete |
|------|:----:|:------:|:------:|:------:|
| OWNER | ✅ | ✅ | ✅ | ✅ |
| MANAGER | ✅ | ✅ | ✅ | ❌ |
| SUPERVISOR | ✅ | ✅ | ✅ | ❌ |
| AGENT / DRIVER | ❌ | ❌ | ❌ | ❌ |

## Related docs

- OpenAPI: `docs/api/paths/farmers.yaml`, `docs/api/schemas/farmers.yaml`
- Cross-cutting patterns: [CROSS_CUTTING.md](./CROSS_CUTTING.md)
- Procurement (ledger source): [PROCUREMENT.md](./PROCUREMENT.md)
