# Field Services

Operational farm services for Bhairkhanpally — field labour, tractor work, transport, fertiliser/seeds supply, agri-finance, vehicle ops, and godown maintenance.

**Status:** ✅ Python CRUD live (`app/modules/field_services/`) · migration `021`/`022` · seeds in `scripts/seed_services.py`

---

## Design decision

Rather than five parallel tables, v1 uses a **unified `field_service_records` table** with a `service_category` discriminator and nullable category-specific columns (hours, bag_count, quantity, cleaning_status, facility_status, money fields).

| Concern | Approach |
|---------|----------|
| Service / activity catalog | Extend `activity_types` with `service_category`; seed tractor, transport, fertiliser, seeds, etc. |
| Equipment / fleet types | `vehicle_types` catalog — Tractor, Cultivator, Rotavator, Baler, Trolley, Weeder, Fertilizer Pump, Bolero, DCM, Harvester, Drone + inventory (John Deere 2W/4W, Mahindra Bolero, Eicher DCM) |
| Crop catalog | `crop_types` seed: Paddy, Corn, Maize, Cotton, Red/Green/Black/Bengal Gram, Sunflower, Groundnut, Vegetables, Others (+ legacy Pulses, Concrete Work) |
| Vehicle repairs / trips / expenses | Existing `assets`, `maintenance_records`, `vehicle_trips`, `expenses` tables — **Phase 2** Python; `field_service_records.asset_id` links facility ops now |
| Worker labour | `work_orders` — separate workforce domain; not duplicated here |
| Conditional work forms (web) | Vehicle-type profiles on field-service form: Tractor (crop/area/stage), Trolley (trips/purpose/material), Bolero (trips/locality/distance/weight/goods), DCM (trips/distance/tonnes/load/unload). Stored in `comments` as `[kf:work]…[/kf:work]` JSON |

### `service_category` values

| Value | Android / ops meaning |
|-------|----------------------|
| `field_service` | General field work — hours, location, diesel, amounts |
| `tractor_work` | Tractor + cultivator, rotavator, trolley, baler, fertilizer pump, weeder, harvester, drone |
| `transport` | Bolero / DCM carrying |
| `fertiliser` | Bags, advance, total, pending |
| `seeds` | Quantity, prices, advance, total, pending |
| `agri_finance` | Amount given / pending / total |
| `vehicle_ops` | Repairs, maintenance, cleaning status |
| `godown` | Repairs, purchases, cleaning |

---

## API

| Method | Path | Permission |
|--------|------|------------|
| GET | `/field-services` | `field_services:read` |
| POST | `/field-services` | `field_services:create` |
| GET | `/field-services/{record_id}` | `field_services:read` |
| PATCH | `/field-services/{record_id}` | `field_services:update` |
| DELETE | `/field-services/{record_id}` | `field_services:delete` (OWNER only) |

Query filters: `service_category`, `farmer_id`, `status`, `date_from`, `date_to`.

OpenAPI: `docs/api/paths/field-services.yaml`, `docs/api/schemas/field-services.yaml`.

---

## Data model (`field_service_records`)

Key columns:

- `record_number` — auto `FSR-0001` per org
- `farmer_id` — FK when farmer-linked (name/phone enriched in API response)
- `activity_type_id`, `vehicle_type_id`, `asset_id` — optional FKs to catalogs / fleet
- Money: `diesel_amount`, `amount_given`, `advance_amount`, `total_amount`, `pending_amount` — `NUMERIC(14,2)`
- `cleaning_status` — `pending` \| `done` \| `not_required`
- `facility_status` — `active` \| `repair` \| `maintenance` \| `cleaning`

---

## Seeds

Run after migrations:

```bash
docker compose -f infra/docker-compose.yml exec api python scripts/seed_services.py
```

Fresh install (`scripts/seed.py`) also invokes services seed when org is created.

Seeded catalogs:

- **Crop types:** PADDY, CORN, MAIZE, COTTON, RED_GRAM, GREEN_GRAM, BLACK_GRAM, BENGAL_GRAM, SUNFLOWER, GROUNDNUT, VEGETABLES, OTHERS (+ legacy PULSES, CONCRETEWORK)
- **Activity types:** entries across all `service_category` values (bilingual `name_te`; includes Harvester Work, Drone Spraying, Fertilizer Pump Work)
- **Vehicle types:** TRACTOR, CULTIVATOR, ROTAVATOR, BALER, TROLLEY, WEEDER, FERTILIZER_PUMP, BOLERO, DCM, HARVESTER, DRONE + JD_TRACTOR_2W/4W, MAHINDRA_BOLERO, EICHER_DCM (+ legacy PUMP name refresh)
- **Expense categories:** Fuel, Diesel, Vehicle Repairs, Godown Maintenance, …
- **Payment modes:** cash, upi, bank_transfer
- **Village:** Bhairkhanpally (if missing)

Canonical sources: `scripts/data/fleet_inventory.py`, `scripts/data/crop_catalog.py`.

---

## Phase 2 (remaining)

- Android screens per category (replace hardcoded enums with `/activity-types?service_category=`)
- Assets / maintenance_records / vehicle_trips / expenses Python modules for fleet-level ledger
- Work orders integration for paid labour vs farmer-facing services
- Crop price rules per new crop types (user updates rates)
- Reporting SQL dashboards for service revenue / pending collections
- ~~Web UI: create/edit forms per category (list placeholder exists at `/field-services`)~~ — ✅ web list + `/field-services/new` + `/field-services/[id]` (category-specific forms)

---

## Related APIs (work → comments → diesel)

| Step | API | Notes |
|------|-----|-------|
| Post work | `POST /field-services` | Includes `diesel_amount` |
| Thread comments | `GET/POST /comments` (`entity_type=field_service`) | Others with `comments:create` |
| Diesel ledger | Auto Fuel expense when `diesel_amount > 0` | `source_type=field_service`; response `diesel_expense_id` |
| Diesel receipt / photos | `POST /documents/presign-upload` → register → `POST /documents/{id}/link` | `document_type=fuel_bill` or `photo`, `entity_type=field_service` |
| Alternate diesel path | `POST /vehicle-trips` with `fuel_cost` | Separate trip ledger (`source_type=vehicle_trip`) |

Web detail (`/field-services/[id]`): comment thread + diesel receipt / work photo upload.

---

## Verify

```bash
# Migrate
docker compose -f infra/docker-compose.yml exec api alembic upgrade head

# Seed catalogs (existing org)
docker compose -f infra/docker-compose.yml exec api python scripts/seed_services.py

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"owner@krishifarms.local","password":"ChangeMe123!"}' \
  | jq -r '.data.access_token')

# List activity types (tractor work)
curl -s "http://localhost:8000/api/v1/activity-types?page_size=50" \
  -H "Authorization: Bearer $TOKEN" | jq '.data.items[] | select(.service_category=="tractor_work")'

# Create fertiliser service record (replace farmer_id)
curl -s -X POST http://localhost:8000/api/v1/field-services \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: curl-test" \
  -H "X-Client-Type: cli" \
  -d '{
    "service_category": "fertiliser",
    "service_date": "2026-07-12",
    "bag_count": 10,
    "advance_amount": "5000.00",
    "total_amount": "12000.00",
    "pending_amount": "7000.00",
    "comments": "Urea bags for kharif"
  }' | jq
```
