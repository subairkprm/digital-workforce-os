# Security Baseline

## Mandatory controls
- Private repository
- MFA for privileged accounts
- No secrets in source
- Short-lived access tokens
- Rotating refresh sessions
- Tenant isolation
- RBAC
- Audit events for administrative mutations
- Rate limiting
- Structured security events
- Encrypted transport
- Production credentials outside repository

## Security invariants
1. A user may never access another tenant by changing IDs in a request.
2. Tenant context comes from verified membership.
3. Every mutating admin action is auditable.
4. Provider credentials are referenced through secret storage.
5. Production data must not be copied into development automatically.
6. Sensitive communications data is not visible to platform operators by default.

## Required test suite
`tests/security/test_cross_tenant_access.*` must exercise every tenant-controlled API family.

## Rate-limit behavior

- Authentication attempts are limited by normalized email and remote address.
- Tenant mutations are limited by the server-derived tenant and authenticated user.
- Redis stores only short-lived counters; it does not store credentials or tokens.
- A Redis outage fails open in this local foundation to preserve application availability. Readiness
  still reports Redis failure, and production behavior must be separately reviewed before deployment.

## Security events

Security events are stored separately from business audit events. Categories cover failed
authentication, refresh-token reuse, rate limiting, and authorization denial. Metadata must never
contain passwords, raw access/refresh tokens, or foreign-tenant resource identifiers. Tenant events
are readable only with `security.read`; platform-level events with no tenant are not exposed through
the tenant API. Retention is not automated in DWCO 0.2; review and deletion policy must be defined
before production deployment.
