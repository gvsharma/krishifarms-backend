# Devices & Push Notifications

FCM device token registration and bilingual push fanout for the Android app.

## Table

`user_device_tokens` (migration `020`): `org_id`, `user_id`, `device_id`, `fcm_token`, `platform`, `app_version`, `last_seen_at`, `revoked_at`. Unique `(org_id, fcm_token)`.

## API

| Method | Path | Permission | Purpose |
|--------|------|------------|---------|
| `POST` | `/devices/push-tokens` | `dashboard:read` | Upsert FCM token (`X-Device-Id` or body `device_id`) |
| `DELETE` | `/devices/push-tokens` | `dashboard:read` | Revoke by token or device_id |

## Send triggers (EN + TE)

| Event | Recipients (skip actor) | Data payload |
|-------|-------------------------|--------------|
| Procurement status change | OWNER/MANAGER/SUPERVISOR (village-aware) + `created_by` | `type=procurement`, `id`, `status` |
| Farmer comment | OWNER/MANAGER/SUPERVISOR + prior commenters | `type=farmer_comment`, `farmer_id` |
| Document uploaded | OWNER/MANAGER | `type=document`, `id` |

Locale: recipient `users.preferred_locale` (`te` → Telugu title/body, else English).

## Device accountability

Mutations send `X-Device-Id` / `X-Client-Type` → persisted on `audit_logs` / `activity_feed`. Login/refresh bind `refresh_tokens.device_id`. Sessions: `GET/DELETE /users/me/sessions`.

Firebase Admin credentials (same as phone auth) send FCM HTTP v1. No Firestore required.
