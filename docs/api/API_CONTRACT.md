# KrishiFarms CRM — API Contract

**OpenAPI version:** 3.0.3  
**Spec location:** `docs/api/openapi.yaml` (modular; bundle before import into Swagger/Postman)  
**Base URL:** `/api/v1`  
**Auth:** Bearer JWT

---

## 1. Global Standards

### Success envelope

```json
{
  "success": true,
  "data": { },
  "meta": { "request_id": "550e8400-e29b-41d4-a716-446655440000" }
}
```

### Error envelope

```json
{
  "success": false,
  "error": {
    "message": "Human-readable error",
    "details": { "field": "amount", "reason": "must be > 0" }
  }
}
```

| HTTP | Meaning |
|------|---------|
| 400 | Validation / business rule violation |
| 401 | Missing or invalid token |
| 403 | RBAC permission denied |
| 404 | Entity not found |
| 409 | Duplicate / invalid state transition |
| 500 | Server error |

### Pagination

| Parameter | Type | Default | Max |
|-----------|------|---------|-----|
| `page` | integer | 1 | — |
| `page_size` | integer | 20 | 100 |

Paginated `data`:

```json
{
  "items": [],
  "total": 142,
  "page": 1,
  "page_size": 20
}
```

### Sorting

| Parameter | Example | Description |
|-----------|---------|-------------|
| `sort` | `-created_at` | Prefix `-` = descending |
| `sort` | `procurement_date` | Ascending |

### Date filtering

| Parameter | Format | Example |
|-----------|--------|---------|
| `date_from` | ISO date | `2026-01-01` |
| `date_to` | ISO date | `2026-01-31` |

### Search

| Parameter | Scope |
|-----------|--------|
| `q` | Module list endpoints — fuzzy name/phone/code (Telugu + English) |
| `GET /search?q=` | Global cross-entity search |
| `entity_types` | Comma-separated filter on global search |

### Headers

| Header | Required | Purpose |
|--------|----------|---------|
| `Authorization` | Yes (except login/refresh) | `Bearer <access_token>` |
| `Accept-Language` | No | `en` or `te` |
| `Idempotency-Key` | Financial POST | Prevent duplicate payments/procurement |
| `X-Request-ID` | No | Correlation ID echoed in `meta` |

---

## 2. Endpoint Catalog

### Authentication

| Method | Path | Request | Response `data` |
|--------|------|---------|-------------------|
| POST | `/auth/login` | `{ email, password }` | `{ access_token, refresh_token, token_type }` |
| POST | `/auth/refresh` | `{ refresh_token }` | Token pair |
| POST | `/auth/logout` | `{ refresh_token }` | `{ message }` |

### Farmers

| Method | Path | Notes |
|--------|------|-------|
| GET | `/farmers` | Filter: `village_id`, `status`; search: `q` |
| POST | `/farmers` | Create farmer |
| GET | `/farmers/{id}` | Detail + optional outstanding |
| PATCH | `/farmers/{id}` | Update |
| DELETE | `/farmers/{id}` | Soft delete |
| GET/POST | `/farmers/{id}/bank-accounts` | Encrypted at rest |
| PATCH/DELETE | `/farmers/{id}/bank-accounts/{account_id}` | |
| GET/POST | `/farmers/{id}/land-parcels` | |
| GET/POST | `/farmers/{id}/crop-history` | |
| GET | `/farmers/{id}/ledger` | Paginated ledger entries |
| GET | `/farmers/{id}/outstanding` | `{ outstanding_amount, as_of_date }` |

### Farms

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/farms` | Filter: `village_id`, `status` |
| GET/PATCH/DELETE | `/farms/{id}` | |
| GET/POST | `/farms/{id}/activities` | Farm activity log |

### Procurement

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/procurements` | Filter: farmer, village, crop, status, dates |
| GET/PATCH | `/procurements/{id}?procurement_date=` | Draft editable only |
| POST | `/procurements/{id}/confirm` | Posts ledger entry |
| POST | `/procurements/{id}/cancel` | `{ reason }` |
| POST | `/procurements/{id}/deductions` | Add deduction line |

**Procurement create body:** `farmer_id`, `crop_type_id`, `village_id`, `procurement_date`, `bag_count`, `gross_weight_kg`, `rate_per_quintal`, optional `deductions[]`, `moisture_pct`

### Payments

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/farmer-payments` | Farmer advances/finals |
| GET | `/farmer-payments/{id}?payment_date=` | |
| POST | `/farmer-payments/{id}/allocate` | Link to procurements |
| POST | `/farmer-payments/{id}/reverse` | Immutable reversal |
| GET/POST | `/payments` | Vendor/operational payments |

### Workers

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/workers` | Search: `q` |
| GET/PATCH/DELETE | `/workers/{id}` | |
| GET/POST | `/workers/{id}/skills` | |

### Work Orders & Attendance

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/work-orders` | Filter: worker, farm, status |
| GET/PATCH | `/work-orders/{id}` | |
| POST | `/work-orders/{id}/complete` | `{ end_time, photo_document_ids[] }` |
| GET/POST | `/work-orders/{id}/photos` | Link document photos |
| GET/POST | `/attendance` | Daily attendance records |

### Assets

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/assets` | Categories: tractor, dcm, baler, air_machine, other |
| GET/PATCH/DELETE | `/assets/{id}` | |
| GET/POST | `/assets/{id}/maintenance-records` | |
| GET/POST | `/assets/{id}/usage-logs` | Hours, revenue, fuel, maintenance |

### Vehicles (Trips)

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/vehicle-trips` | Filter: asset, driver, dates |
| GET/PATCH | `/vehicle-trips/{id}?trip_date=` | Charges: fuel, loading, unloading, waiting |

### Rentals

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/rental-customers` | |
| GET/PATCH | `/rental-customers/{id}` | |
| GET/POST | `/rental-agreements` | |
| GET/PATCH | `/rental-agreements/{id}` | |
| GET | `/rental-agreements/pending-collections` | AR report |

### Expenses

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/expenses` | Filter: category, farm, asset, status, dates |
| GET/PATCH/DELETE | `/expenses/{id}` | Draft editable; attach `document_ids[]` |

### Collections

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/collections` | Source: rental/other; link UPI screenshots |
| GET | `/collections/{id}` | |

### Documents

Architecture: `docs/modules/DOCUMENT_MANAGEMENT.md`

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| GET | `/documents/types` | `documents:read` | Document taxonomy + OCR eligibility |
| POST | `/documents/presign-upload` | `documents:create` | Step 1: single S3 presigned PUT URL |
| POST | `/documents/presign-upload/batch` | `documents:create` | Step 1: up to 20 presigned URLs |
| POST | `/documents` | `documents:create` | Step 2: register metadata after S3 PUT |
| POST | `/documents/batch` | `documents:create` | Register up to 20 documents |
| GET | `/documents` | `documents:read` | Search/filter (see below) |
| GET | `/documents/{id}` | `documents:read` | Optional `include_download_url`, tags, links, OCR |
| PATCH | `/documents/{id}` | `documents:create` | Update metadata, tags |
| DELETE | `/documents/{id}` | `documents:delete` | Archive (`is_archived=true`) |
| GET | `/documents/{id}/download-url` | `documents:read` | Presigned GET URL (900 s) |
| POST | `/documents/{id}/link` | `documents:create` | Polymorphic link to transaction |
| GET | `/documents/{id}/links` | `documents:read` | List links |
| DELETE | `/documents/{id}/links/{link_id}` | `documents:create` | Soft-unlink |
| GET | `/documents/tags` | `documents:read` | List org tags |
| POST | `/documents/tags` | `documents:create` | Create tag |
| DELETE | `/documents/tags/{tag_id}` | `documents:delete` | Delete user tag (not system tags) |
| POST | `/documents/{id}/ocr` | `documents:create` | Enqueue OCR job → `202` |
| GET | `/documents/{id}/ocr/result` | `documents:read` (+ `ai:read` for full text) | Latest OCR extraction |
| POST | `/documents/{id}/ocr/verify` | `ai:review` | Accept/reject OCR fields |

**Upload flow:** `presign-upload` → client `PUT` to S3 → `POST /documents` with `object_key`.

**List/search query params:**

| Param | Description |
|-------|-------------|
| `q` | Full-text (title, file_name, description, OCR text; EN + TE) |
| `document_type` | Enum filter |
| `ocr_status` | `pending`, `processing`, `completed`, `failed`, `skipped` |
| `is_archived` | Default `false` |
| `tag` | Repeatable; AND filter by tag name |
| `entity_type`, `entity_id` | Documents linked to entity |
| `entity_partition_date` | Required with entity filter for partitioned entities |
| `uploaded_by` | UUID |
| `date_from`, `date_to` | On `captured_at` or `created_at` |
| `sort` | e.g. `-created_at`, `captured_at` |
| `include_tags`, `include_links` | Embed on list items |

**Link body (`entity_type`):** `procurement`, `farmer_payment`, `expense`, `payment`, `collection`, `rental_agreement`, `vehicle_trip`, `work_order`, `asset`, `farmer`.

**Partition key on link:** Required `entity_partition_date` for `procurement` (`procurement_date`), `farmer_payment` (`payment_date`), `vehicle_trip` (`trip_date`), `payment` (`payment_date`).

**Primary document types:** `fuel_bill`, `crop_bill`, `rental_bill`, `vendor_bill`, `payment_receipt`, `upi_screenshot`, `photo`

**Extension types:** `weighment_slip`, `voice_note`, `whatsapp_export`, `pdf`

**Error codes (documents-specific):**

| HTTP | Condition |
|------|-----------|
| 409 | Duplicate `object_key` for org; duplicate link; OCR already running |
| 400 | Missing `entity_partition_date` for partitioned entity; invalid type/MIME/size |

### Search

| Method | Path | Notes |
|--------|------|-------|
| GET | `/search?q=&entity_types=` | Global ranked search |

---

## 3. Key Request Schemas (summary)

See `docs/api/schemas/` for full component definitions.

| Schema | Key fields |
|--------|------------|
| `FarmerCreate` | `full_name`, `full_name_te`, `phone_primary`, `village_id` |
| `ProcurementCreate` | farmer, crop, village, date, bags, weight, rate, deductions |
| `FarmerPaymentCreate` | farmer, type, date, amount, payment_mode, reference_no |
| `WorkOrderCreate` | worker, farm, start_time, rate_type, rate |
| `ExpenseCreate` | category, date, amount, payment_mode, document_ids |
| `CollectionCreate` | source_type, source_id, date, amount, payment_mode |
| `DocumentRegister` | type, file_name, mime_type, object_key, checksum, metadata, auto_ocr, tag_names, links[] |
| `DocumentUpdate` | title, title_te, description, metadata, add/remove tags |
| `DocumentLink` | entity_type, entity_id, entity_partition_date?, link_role |
| `OcrVerifyRequest` | accepted_fields, reject, rejection_reason |
| `VehicleTripCreate` | asset, source/destination (+ `_te`), date, charge breakdown |

---

## 4. Response Schemas (summary)

All entities include audit fields where applicable: `created_at`, `updated_at`, `created_by`, `updated_by`, `deleted_at`.

| Entity | Notable response fields |
|--------|-------------------------|
| `Farmer` | `farmer_code`, bilingual names, `outstanding_amount`, `status` |
| `Procurement` | amounts, `status`, nested `deductions[]` |
| `FarmerPayment` | `payment_type`, `status`, allocations on detail |
| `WorkOrder` | computed `cost`, `duration_minutes`, `photos[]` |
| `Asset` | `asset_category`, `is_rentable`, rates |
| `RentalAgreement` | `pending_collection` (computed) |
| `Document` | `ocr_status`, `metadata`, `tags[]`, `links[]`, presigned URLs via download endpoint |
| `OcrExtraction` | `raw_text`, `raw_text_te`, `extracted_fields`, `field_confidence`, `is_verified` |

---

## 5. RBAC Permission Codes (API enforcement)

Each endpoint requires a permission such as `farmers:read`, `procurements:confirm`, etc.  
Full list seeded in migration `202506210015`. Clients receive `403` with `Missing permission: <code>` on denial.

---

## 6. Partitioned resource access

These entities require a **date query parameter** when fetching by ID (matches PostgreSQL composite keys):

| Resource | Date param |
|----------|------------|
| Procurement | `procurement_date` |
| Farmer payment | `payment_date` |
| Vehicle trip | `trip_date` |

---

## 7. Bundling the spec

```bash
# Using Redocly CLI
npx @redocly/cli bundle docs/api/openapi.yaml -o docs/api/openapi.bundled.yaml

# Or Swagger CLI
npx swagger-cli bundle docs/api/openapi.yaml -o docs/api/openapi.bundled.yaml -t yaml
```

Import `openapi.bundled.yaml` into Postman, Stoplight, or generate TypeScript clients (`openapi-typescript`).

---

## 8. File layout

```text
docs/
  modules/
    DOCUMENT_MANAGEMENT.md  # Architecture (storage, OCR, search, linking)
  api/
    openapi.yaml            # Entry point
    API_CONTRACT.md           # This document
    paths/
      auth.yaml
      farmers.yaml
      farms.yaml
      procurement.yaml
      payments.yaml
      workers.yaml
      work-orders.yaml
      assets.yaml
      vehicles.yaml
      rentals.yaml
      expenses.yaml
      collections.yaml
      documents.yaml
      search.yaml
    schemas/
      common.yaml
      auth.yaml
      farmers.yaml
      farms.yaml
      procurement.yaml
      payments.yaml
      workers.yaml
      work-orders.yaml
      assets.yaml
      vehicles.yaml
      rentals.yaml
      expenses.yaml
      collections.yaml
      documents.yaml
```
