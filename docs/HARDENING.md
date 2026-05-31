# Security Hardening Plan

This document tracks the security requirements for the API rollout and public internet deployment.

## Current Context

- API work is on branch `api-work`.
- Production runs on Debian behind nginx (managed via supervisord).
- Production `.env` already sets:
  - `DJANGO_DEBUG=False`
  - Strong `DJANGO_SECRET_KEY`

## Implementation Status

- ✅ **Phase 1A complete**: ownership scoping and object access boundaries added for user-owned resources.
- ✅ **Phase 1B complete**: `created_by` made server-controlled for API-created `WeekPlan` and `ShoppingList` records.
- ✅ **Phase 1C complete**: JWT blacklist app enabled; refresh token rotation now invalidates reused refresh tokens.
- ✅ **Phase 1D complete**: API schema/swagger URLs are now gated by `API_DOCS_ENABLED` and disabled by default when `DEBUG=False`.
- ✅ **Phase 1E complete**: DRF throttling policy added with stricter scoped limits for JWT endpoints.
- ⏳ **Phase 2 pending**: transport/cookie hardening in production settings.

## Audit Summary (May 2026)

### Critical / High

1. **Object-level authorization gaps (IDOR/BOLA)**
   - API viewsets currently use broad querysets (e.g. `Model.objects.all()`), which allows authenticated users to access and mutate objects created by other users.
   - This is the highest-priority issue.

2. **`created_by` ownership spoofing**
   - Some serializers accept `created_by` from clients.
   - Clients must not be able to set/impersonate ownership fields.

3. **JWT refresh token replay risk**
   - `ROTATE_REFRESH_TOKENS=True` and `BLACKLIST_AFTER_ROTATION=True` are configured.
   - But blacklist app support is not active, so old refresh tokens remain reusable.

### Medium

4. **Public schema/docs endpoints**
   - `/api/v1/schema/` and `/api/v1/schema/swagger-ui/` are accessible without auth.
   - This increases API reconnaissance surface.

5. **No API throttling**
   - No DRF throttle classes/rates are configured.
   - Increases brute-force and abuse risk, especially around auth/token endpoints.

### Deployment hardening still required

Even with `DEBUG=False` and strong `SECRET_KEY` in production, additional transport/cookie hardening is still needed.

---

## Hardening Requirements

## Phase 1 — Application-Level (Do First)

### A. Enforce ownership/tenant boundaries on all API resources

- Scope querysets by ownership (or household boundary if we add multi-user household sharing).
- Ensure object-level access checks for retrieve/update/delete/custom actions.
- Add tests proving cross-user access is denied.

**Acceptance criteria**
- A user cannot read/update/delete another user’s week plans, planned meals, shopping lists, or shopping list items.
- Any endpoint returning user data enforces ownership boundary.

### B. Make ownership fields server-controlled

- Mark `created_by` fields as read-only in serializers.
- Set ownership in views using `request.user` (e.g., `perform_create`).
- Add tests verifying payload `created_by` is ignored/rejected.

**Acceptance criteria**
- Client-supplied `created_by` cannot override DB ownership.

### C. Enable JWT refresh blacklisting correctly

- Add `rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS`.
- Run migrations.
- Add regression tests to confirm rotated refresh tokens are invalidated.

**Acceptance criteria**
- Reusing an old refresh token after rotation fails.

### D. Lock down API docs/schema endpoint exposure

Decision: **Disable schema/swagger endpoints in production**.

Implementation option (preferred):
- Register schema/swagger URLs only when `DEBUG=True` (or behind an explicit env flag).

Alternative:
- Require authentication/staff-only for schema/swagger endpoints.

**Acceptance criteria**
- Unauthenticated internet users cannot access interactive API docs in production.

### E. Add DRF throttling

- Configure default throttle classes and rates.
- Add stricter rate limits for token/auth endpoints where needed.

Implemented defaults:
- `anon`: `120/min`
- `user`: `600/min`
- `token_obtain`: `10/min`
- `token_refresh`: `30/min`
- `token_verify`: `60/min`

All rates are environment-overridable via:
- `DRF_THROTTLE_ANON`
- `DRF_THROTTLE_USER`
- `DRF_THROTTLE_TOKEN_OBTAIN`
- `DRF_THROTTLE_TOKEN_REFRESH`
- `DRF_THROTTLE_TOKEN_VERIFY`

**Acceptance criteria**
- Excessive request bursts are rate-limited with predictable 429 behavior.

---

## Phase 2 — Deployment/Transport Hardening

Apply in production settings (or equivalent nginx-enforced policy):

- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_SSL_REDIRECT = True` (unless nginx already enforces strict redirect)
- `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` (behind reverse proxy)
- `SECURE_HSTS_SECONDS = 31536000` (after HTTPS-only verification)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True` (if appropriate)
- `SECURE_HSTS_PRELOAD = True` (only when confident)

nginx should forward:
- `X-Forwarded-Proto $scheme`

**Acceptance criteria**
- `manage.py check --deploy` has no unresolved warnings we accept for production.
- HTTP requests are redirected to HTTPS.
- Session/CSRF cookies are secure-only.

---

## Recommended Execution Order

1. Authorization boundary fixes (Phase 1A)
2. Ownership field hardening (Phase 1B)
3. JWT blacklist activation + tests (Phase 1C)
4. Schema/docs exposure control (Phase 1D)
5. API throttling (Phase 1E)
6. Deployment/transport settings + nginx verification (Phase 2)

---

## Verification Checklist

Before go-live:

- [ ] API test suite passes
- [ ] New negative authorization tests pass (cross-user access denied)
- [ ] Refresh token replay test fails as expected (old token rejected)
- [ ] Docs/schema endpoint restricted or disabled in production
- [ ] Throttling configured and tested
- [ ] `uv run manage.py check --deploy` reviewed in production profile
- [ ] HTTPS/cookie/HSTS behavior validated end-to-end behind nginx

---

## Notes

- This document intentionally separates **application-level controls** from **deployment controls**.
- Both are required for a public internet deployment.