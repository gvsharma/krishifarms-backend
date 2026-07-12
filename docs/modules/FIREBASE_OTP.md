# Firebase Phone OTP — Auth path

Phone OTP for KrishiFarms CRM is **backend-ready**. Web OTP UI is stubbed until Firebase Web SDK is wired.

## Flow (target)

```text
1. Client (Android / future web) → Firebase Phone Auth → SMS OTP
2. Firebase returns ID token (JWT) with phone_number claim (E.164)
3. Client → POST /api/v1/auth/firebase-login
   Authorization: Bearer <firebase_id_token>
   Headers: X-Device-Id, X-Client-Type (mobile|web)
4. Backend verifies token (Admin SDK), normalizes phone, looks up User.phone
5. Issues CRM JWT access + refresh (same shape as password login)
```

## Backend (live)

| Piece | Path |
|-------|------|
| Endpoint | `POST /auth/firebase-login` — `app/modules/auth/router.py` |
| Verify ID token | `app/modules/auth/firebase.py` (`FIREBASE_SERVICE_ACCOUNT_JSON`) |
| Phone normalize / lookup | `app/modules/auth/phone.py` → `normalize_phone_for_lookup` |
| Rate limit | `app/modules/auth/rate_limit.py` |
| Schema | users may be phone-only (nullable email/password) — migration `016` |

Password login also accepts **email or mobile**: `POST /auth/login` with `{ email, password }` **or** `{ mobile, password }`.

## Web status

| Item | Status |
|------|--------|
| Phone or email + password on `/login` | ✅ |
| Mandatory phone on Settings → Users | ✅ |
| **Login with OTP (coming soon)** button | Stub on `/login` (disabled) |
| Firebase Web SDK + reCAPTCHA + `firebase-login` call | ❌ TODO |

## Android / config prerequisites

- Firebase project with Phone Auth enabled
- Service account JSON on API host (`FIREBASE_SERVICE_ACCOUNT_JSON`, optional `FIREBASE_PROJECT_ID`) — see [CI_CD.md](../deploy/CI_CD.md)
- Android: `google-services.json`; user must already exist in CRM with matching phone
- SMS quota typically requires Blaze plan

## Next implementation steps (web OTP)

1. Add Firebase Web config (`NEXT_PUBLIC_FIREBASE_*`)
2. `signInWithPhoneNumber` + reCAPTCHA verifier on `/login`
3. Exchange ID token via `POST /auth/firebase-login` (same as Android)
4. Enable the OTP button; remove “coming soon”

Until then, field staff use **phone + password** on web, or Firebase OTP on Android against the same backend.
