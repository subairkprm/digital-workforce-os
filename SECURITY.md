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
