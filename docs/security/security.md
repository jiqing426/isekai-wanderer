# Security Design — Isekai Wanderer

## Overview

Security is enforced at multiple layers: transport (HTTPS/TLS), authentication (JWT), authorization (Bearer middleware), input validation (Pydantic + ORM parameterization), and rate limiting (Redis sliding window).

---

## Authentication & Authorization

| Scenario | Scheme |
|----------|--------|
| User authentication | JWT (Access Token 15 min + Refresh Token 7 days) |
| Password storage | bcrypt (cost factor 12) |
| OAuth mock | Abstract `IOAuthProvider` interface; mock implementation returns fixed user |
| API authorization | Bearer Token middleware on all protected endpoints |
| Rate limiting | Redis sliding window: general API 60 req/min, LLM calls 10 req/min |
| Brute force protection | Login locked for 15 minutes after 5 failed attempts (Redis counter) |

---

## Sensitive Data Handling

| Data | Storage | Transport | Logging |
|------|---------|-----------|---------|
| Passwords | bcrypt hash | HTTPS only | Never logged |
| JWT tokens | In-memory / cookie | HTTPS only | Never logged |
| Email | Plaintext (queryable) | HTTPS only | Masked |
| Dialogue records | Plaintext storage | HTTPS only | Masked |
| Memory vectors | Vector storage | Internal calls only | Never logged |
| Mock payment data | Plaintext with mock flag | HTTPS only | Log mock flag only |

---

## Security Constraints

| Constraint | Implementation |
|------------|----------------|
| **HTTPS** | All API traffic over HTTPS; Nginx SSL termination in production |
| **CORS** | Whitelist only: frontend origin (`http://localhost:3000` dev, production domain prod) |
| **SQL Injection** | SQLAlchemy ORM parameterized queries; no raw SQL string concatenation |
| **XSS** | Vue default template escaping + Content-Security-Policy (CSP) headers |
| **CSRF** | JWT mode does not require CSRF tokens (no cookie-based auth) |
| **Brute Force** | Login: 5 failed attempts → 15-minute lockout (Redis counter) |
| **Input Validation** | Pydantic schemas on all request bodies; FastAPI auto-validation (422 on failure) |
| **Dependency Security** | Pinned versions in `pyproject.toml`; regular `pip-audit` scans |

---

## Token Lifecycle

1. User registers → email verification token (expires 24h)
2. User logs in → Access Token (15 min) + Refresh Token (7 days)
3. Access Token expires → client calls `/auth/refresh` with Refresh Token → new Access Token issued
4. Refresh Token expires → user must re-login
5. Password reset → reset token (expires 1h), single-use, invalidated after use (CR-002 AC-047: implemented)

---

## OAuth Mock Architecture

```txt
Frontend "Login with Google" button
    │
    ▼
GET /api/v1/auth/oauth/google
    │
    ▼
IOAuthProvider.authenticate()
    │ (mock: returns deterministic test user)
    │ (real: redirects to Google OAuth consent)
    │
    ▼
GET /api/v1/auth/oauth/google/callback?code=xxx
    │
    ▼
IOAuthProvider.get_user_info()
    │
    ▼
Create or link user account → Issue JWT pair
```

The `IOAuthProvider` abstraction ensures mock and real OAuth providers share the same contract, enabling seamless transition from mock to production without business code changes.

---

## CR-002 Security Additions

### Password Reset Security (AC-047)

| Risk | Mitigation |
|---|---|
| Email enumeration | forgot-password returns 200 for non-existent emails |
| Token brute force | `secrets.token_urlsafe(32)` (256-bit entropy) |
| Token reuse | Single-use: `used=TRUE` after first use |
| Token expiry | 1 hour TTL, rejected after expiry |
| Rate limiting | 3 requests/hour/email (Redis counter) |
| Password strength | Pydantic validation: min 8 chars + digit + letter |

### Free Chat Security (AC-058)

| Risk | Mitigation |
|---|---|
| Prompt injection | User input separated from system prompt |
| LLM output unpredictability | RuleEngine validation + max length + emotion tag format |
| Data privacy | Stored in DB, accessible only by owning user |

### Mock Service Security (AC-055/AC-057)

- Mock services do not send real HTTP requests (no external attack surface)
- Webhook URLs stored in DB, not exposed to frontend
- Log files contain no sensitive user data (emails masked)
- Recall cron runs internally, no public API exposure

---

## Production Security Checklist

- [ ] Nginx SSL termination with modern cipher suite
- [ ] CORS whitelist restricted to production frontend domain
- [ ] Rate limiting active on all public endpoints
- [ ] Brute force lockout active on login endpoint
- [ ] No sensitive data in application logs
- [ ] Database credentials via environment variables (not hardcoded)
- [ ] Redis AUTH enabled (if exposed beyond localhost)
- [ ] Docker secrets or equivalent for production credentials
- [ ] Regular dependency vulnerability scanning (`pip-audit`, `npm audit`)
