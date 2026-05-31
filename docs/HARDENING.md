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
- ✅ **Phase 2 implemented in code/templates**: transport/cookie hardening defaults and production env/nginx guidance added (requires deployment rollout verification).

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

Implemented:
- Django settings now support secure-cookie/SSL/HSTS hardening via env vars.
- Production env example includes these hardening variables.
- nginx deploy template includes HSTS and additional security headers.
- Deploy doc includes `manage.py check --deploy` verification step.

Note on `SECURE_HSTS_PRELOAD`:
- Left as explicit opt-in (`False` by default) to avoid irreversible preload commitment until you choose it deliberately.

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

## Post-Launch Quick Checks

### First 10-minute smoke test

1. **HTTP redirects to HTTPS**
   ```bash
   curl -I http://mealplanner.matthewlemon.com
   ```
   Expect: `301` to `https://...`

2. **Security headers present on HTTPS**
   ```bash
   curl -I https://mealplanner.matthewlemon.com
   ```
   Confirm headers include:
   - `Strict-Transport-Security`
   - `X-Frame-Options`
   - `X-Content-Type-Options`
   - `Referrer-Policy`

3. **API docs disabled in production**
   - `/api/v1/schema/` returns `404`
   - `/api/v1/schema/swagger-ui/` returns `404`

4. **Session flow works**
   - Login succeeds.
   - Create/update/delete a simple object (e.g. meal type).

5. **JWT flow works**
   - Token obtain endpoint returns access/refresh.
   - Authenticated API call with Bearer token succeeds.

### First 24 hours monitoring

6. **Gunicorn error log**
   ```bash
   sudo tail -f /var/log/mealplanner/gunicorn-error.log
   ```

7. **nginx error log**
   ```bash
   sudo tail -f /var/log/nginx/mealplanner-error.log
   ```

8. **Auth noise / abuse signals in access log**
   ```bash
   sudo grep -E ' /api/v1/token/| 401 | 403 | 429 ' /var/log/nginx/mealplanner-access.log | tail -n 100
   ```

9. **Process health**
   ```bash
   sudo supervisorctl status mealplanner
   ```

10. **Deployment profile check**
   ```bash
   sudo -u www-data /var/www/.local/bin/uv run python manage.py check --deploy
   ```
   Expected acceptable warning: optional HSTS preload policy if intentionally disabled.

### After 1–2 stable days

11. Increase HSTS max-age from `3600` to `31536000`.

---

## Incident Playbook (Quick Response)

### A. Token endpoint abuse (bursts of `/api/v1/token/` and many 429/401)

1. Lower auth endpoint limits temporarily in `.env`:
   - `DRF_THROTTLE_TOKEN_OBTAIN=5/min`
   - `DRF_THROTTLE_TOKEN_REFRESH=15/min`
2. Restart app:
   ```bash
   sudo supervisorctl restart mealplanner
   ```
3. If abusive IPs are obvious, add temporary nginx deny rules and reload nginx.

### B. Legit users blocked by throttling (too many 429s)

1. Increase relevant throttle env values moderately:
   - `DRF_THROTTLE_USER`
   - `DRF_THROTTLE_TOKEN_OBTAIN`
2. Restart app and re-test login/API flow.

### C. 502/504 or upstream failures

1. Check process status:
   ```bash
   sudo supervisorctl status mealplanner
   ```
2. Inspect logs:
   ```bash
   sudo tail -100 /var/log/mealplanner/gunicorn-error.log
   sudo tail -100 /var/log/nginx/mealplanner-error.log
   ```
3. Restart app:
   ```bash
   sudo supervisorctl restart mealplanner
   ```
4. Re-check endpoint with `curl -I https://...`.

### D. Suspected credential compromise

1. Rotate `DJANGO_SECRET_KEY` (forces invalidation of signing dependent state).
2. Restart app.
3. Ask family users to log in again and rotate passwords.
4. Review auth logs around compromise window.

### E. Need emergency rollback

1. Revert to previous git revision on server.
2. `uv sync` if needed.
3. Run migrations only if rollback path permits.
4. Restart supervisor process and validate health checks.

---

## Notes

- This document intentionally separates **application-level controls** from **deployment controls**.
- Both are required for a public internet deployment.