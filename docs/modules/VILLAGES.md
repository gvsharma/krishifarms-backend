# Villages Module — Village 360°

Villages are a **first-class CRM entity**. Farmers, procurements, farms, and buyers link via `village_id`. Migration `031` extends the village master for relationship management.

## Data model (`villages`)

| Field | Notes |
|-------|-------|
| `village_code` | Auto `VIL-####` on create; backfilled on migrate |
| `name`, `mandal`, `district`, `state`, `pincode` | Existing + hierarchy FKs |
| `geo_lat`, `geo_lng` | Optional GPS (GIS-ready) |
| `agent_id` | Optional FK → `field_agents` |
| `status` | `active` \| `inactive` |
| `population` | Optional |
| `estimated_cultivable_area` | Optional acres |
| `notes` | Optional |

## APIs

| Method | Path | Permission |
|--------|------|------------|
| GET | `/villages` | `villages:read` — filters: district/mandal/status/`q` |
| GET | `/villages/search?q=` | `villages:read` — village/mandal/farmer/buyer/crop |
| POST | `/villages` | `villages:create` |
| GET | `/villages/{id}` | `villages:read` |
| GET | `/villages/{id}/profile-360` | `villages:read` |
| PATCH | `/villages/{id}` | `villages:update` |
| DELETE | `/villages/{id}` | `villages:delete` |

### Profile-360 payload

Summary · statistics (farmers, crop areas, procurement, tractor/rotavator/cultivator/baler hours, bolero/DCM trips, diesel, revenue/profit, outstanding) · farmers (with Farmer 360 links) · procurements · services · vehicles · payments · finance · farming · buyers · comments · documents · analytics · timeline · map readiness · report deep-links.

## Web

| Route | Role |
|-------|------|
| `/villages` | List + search |
| `/villages/{id}` | Circular Village 360° orbit dashboard |
| `/settings/villages` | Master CRUD (unchanged, still available) |

## RBAC

Uses existing `villages:read|create|update|delete` (OWNER/MANAGER full; SUPERVISOR/AGENT read via location grants; FARMER read-only where granted).

## Android parity

See [ANDROID_CRM_PARITY.md](./ANDROID_CRM_PARITY.md) — Village 360 cards + expandable sections + offline cache of `profile-360` payload.

## GIS roadmap

GPS stored on village (and farmer/farm). Future: boundary polygons, farmer/farm pin layers, live vehicle locations. Payload includes `map` stub with readiness flags.

## Tests

`tests/test_village_360.py`
