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
- Realtime connection-ticket issuance fails closed when Redis is unavailable. Tickets are one-time,
  stored only under a SHA-256-derived key, expire after 60 seconds, and never appear in logs.

## Security events

Security events are stored separately from business audit events. Categories cover failed
authentication, refresh-token reuse, rate limiting, and authorization denial. Metadata must never
contain passwords, raw access/refresh tokens, or foreign-tenant resource identifiers. Tenant events
are readable only with `security.read`; platform-level events with no tenant are not exposed through
the tenant API. Retention is not automated in DWCO 0.2; review and deletion policy must be defined
before production deployment.

## Workforce invitations

Invitation secrets are high-entropy, expire within 30 days, are single-use, and are stored only as
SHA-256 digests. The raw token is returned once for out-of-band local delivery. Production email or
SMS delivery requires a separate provider-adapter and deployment contract.

## Workforce presence

Presence identity and tenant scope are derived exclusively from the authenticated membership.
Clients can update only their own status, while directory presence requires `employee.read` (or
`tenant.owner`). Heartbeats expire after 120 seconds and are reported as offline after expiry.
Presence mutations are rate-limited and intentionally excluded from administrative audit events to
avoid storing high-volume activity trails. Live presence events are delivered only to the actor or a
tenant member with directory visibility.

## Workforce messaging

- Conversation and message access requires active participation in the server-derived tenant.
- Direct conversations contain exactly two active same-tenant members; no group, guest, public, or
  federated channel exists in this contract.
- Accepted messages are persisted before best-effort fan-out, receive a monotonic conversation
  sequence, and use a sender idempotency key. History is capped at 100 records per request.
- Bodies are limited to 4,000 characters. Attachments and tenant-wide content export are disabled.
- Messages expire after 90 days, are hidden after expiry, and may be purged only by an authorized,
  audited tenant maintenance action. Senders may redact only their own content.
- Administrators receive aggregate counts and timestamps only; no administrative message-content
  endpoint exists. Logs, audit events, security events, notification adapters, and metrics exclude
  message bodies, raw tickets, and credentials.
