# DWCO-0.1-PHASE-1 — Codex Implementation Contract

## Status
AUTHORIZED_FOR_LOCAL_AND_BRANCH_IMPLEMENTATION
PRODUCTION_DEPLOYMENT_NOT_AUTHORIZED

## Goal
Implement the first bounded engineering foundation for the Digital Workforce Communication OS.

## In scope

### Repository and local platform
- Python/FastAPI backend scaffold
- PostgreSQL integration
- Redis integration
- Alembic migrations
- Docker Compose local environment
- structured configuration
- structured logging
- `/health`, `/livez`, `/readyz`

### Multi-tenancy
Implement:
- tenants
- users
- memberships
- employees
- departments
- roles
- permissions
- role_permissions
- audit_events

Every tenant-controlled table must contain `tenant_id` where applicable.

### Authentication
Initial implementation:
- email/password authentication suitable for local development
- secure password hashing
- short-lived access token
- rotating refresh session model
- logout/revocation
- current-user endpoint

Do not implement SMS OTP until a provider is selected.

### Authorization
Implement permission-based authorization with at least:
- tenant.owner
- tenant.admin
- employee.read
- employee.create
- employee.update
- employee.suspend
- department.manage
- role.manage
- audit.read

### Workforce API
Implement:

POST /api/v1/employees
GET /api/v1/employees
GET /api/v1/employees/{id}
PATCH /api/v1/employees/{id}
POST /api/v1/employees/{id}/suspend

GET/POST/PATCH department endpoints sufficient for foundation.

### Audit
Administrative mutations must create audit events.

### Admin web shell
Create initial authenticated admin shell with:
- Dashboard placeholder
- Employees
- Departments
- Roles
- Audit

Do not attempt full visual design.

### Mobile shell
Create React Native application shell with:
- login
- current employee profile placeholder
- directory placeholder
- secure token storage abstraction

No messaging or voice yet.

## Required security invariants
- Cross-tenant reads/writes are denied.
- Client-provided tenant ID cannot override authenticated membership.
- Secrets are not committed.
- Passwords are never stored plaintext.
- Refresh tokens are not stored plaintext if a safer digest/family design is used.
- Audit events cannot be arbitrarily created by tenant clients.

## Required automated tests
- auth success/failure
- token refresh/revocation
- tenant resolution
- cross-tenant employee read denial
- cross-tenant employee mutation denial
- permission denial
- employee CRUD happy path
- audit creation after mutation
- health endpoints

## Quality gates
- backend lint PASS
- Python type/static checks PASS where configured
- frontend lint/typecheck PASS
- unit tests PASS
- integration tests PASS
- cross-tenant security tests PASS
- migration upgrade PASS
- migration downgrade/rollback strategy documented
- Docker local startup PASS
- secret scan PASS
- git diff/check equivalent PASS

## Out of scope
- PSTN
- SIP provider
- WebRTC production calling
- coturn
- eSIM
- carrier APIs
- call recording
- billing
- AI
- Teams
- production deployment

## Completion report format
Return:

DWCO_CONTRACT=DWCO-0.1-PHASE-1
IMPLEMENTATION_STATUS=
SOURCE_CHECKPOINT=
FILES_CHANGED=
MIGRATIONS=
API_SURFACE=
SECURITY_CONTROLS=
TEST_RESULTS=
BUILD_RESULTS=
KNOWN_GAPS=
DEFERRED_SCOPE=
DEPLOYMENT_STATUS=NOT_DEPLOYED
ROLLBACK_GUIDANCE=
