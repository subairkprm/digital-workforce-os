# DWCO-0.2 — Admin and security closure contract

## Status

AUTHORIZED_FOR_LOCAL_AND_BRANCH_IMPLEMENTATION

AUTHORIZED_BY_USER=2026-09-03

PRODUCTION_DEPLOYMENT_NOT_AUTHORIZED

## Goal

Close the remaining product and security gaps in DWCO-007, DWCO-008, and DWCO-010 without
expanding into messaging, voice, carrier, billing, AI, or production operations.

DWCO-009 remains a repository/account administration dependency until GitHub Actions can run and
mandatory branch checks can be verified. This contract may improve the workflow definition but
must not represent remote CI as passing when no run exists.

## Entry conditions

- PRs #11, #12, and #13 remain merged into `main`.
- The Phase-1 completion report remains the evidence baseline.
- Implementation was explicitly approved on 2026-09-03.
- Work starts from the then-current `main` on a bounded feature branch.

## In scope

### Role administration and audit closure

- tenant-scoped role list, create, update, and delete/archive APIs
- permission assignment from the fixed server-known permission catalogue
- membership role assignment and removal
- `role.manage` enforcement on every mutation
- immutable server-created audit evidence for role and membership-role mutations
- cross-tenant, permission-denial, validation, and audit tests

### Functional admin web

- authenticated session lifecycle suitable for the existing local API
- current-user and permission loading
- employee list/create/update/suspend workflows
- department list/create/update workflows
- role and membership-role administration workflows
- tenant-scoped audit event list
- permission-aware navigation and mutation controls
- explicit loading, empty, validation, authorization, and server-error states
- responsive keyboard-accessible foundation UI

### Security baseline closure

- configurable rate-limit hooks for authentication and tenant mutation endpoints
- Redis-backed local rate-limit implementation with fail-closed/fail-safe behavior documented per
  endpoint class
- structured security-event model or convention distinguishable from ordinary business audit
  events
- security events for failed authentication thresholds, refresh-token reuse, rate limiting, and
  authorization denials where recording does not disclose sensitive resource existence
- tenant-safe security-event read access for explicitly authorized administrators
- retention and sensitive-metadata rules documented

### Quality and documentation

- migration upgrade and downgrade verification for every schema change
- backend lint, type checks, unit/integration tests, and coverage report
- admin typecheck, production build, and focused component/workflow tests
- cross-tenant and permission-denial regression suite
- dependency and secret checks
- Docker Compose verification with PostgreSQL and Redis
- completion report following `AGENTS.md`

## Required security invariants

- Tenant context continues to be derived from authenticated membership.
- Role and membership assignments cannot cross tenant boundaries.
- Clients cannot create arbitrary permissions, audit events, or security events.
- Rate limiting cannot be bypassed with a client-provided tenant identifier.
- Authorization remains server-side; hidden UI controls are not an authorization boundary.
- Secrets, access tokens, and refresh tokens are not logged or stored in client-readable persistent
  browser storage.
- Security event metadata must not leak passwords, raw tokens, or foreign-tenant resource details.

## Required automated tests

- role CRUD and membership-role assignment happy paths
- role and membership-role permission denial
- cross-tenant role and membership-role denial
- role and membership-role audit creation
- admin unauthenticated access denial
- admin permission-aware visibility and mutation behavior
- admin loading, validation, and API-error states
- authentication rate-limit threshold and recovery
- tenant mutation rate-limit behavior
- refresh-token reuse security-event creation
- authorization-denial security-event safety
- cross-tenant security-event denial
- existing Phase-1 regression suite

## Exit criteria

- DWCO-007 acceptance criteria are fully evidenced and the issue can be closed.
- DWCO-008 acceptance criteria are fully evidenced and the issue can be closed.
- DWCO-010 acceptance criteria are fully evidenced and the issue can be closed.
- DWCO-009 is closed only if remote deterministic checks and the agreed branch-protection policy
  are actually verified; otherwise it remains open with the external blocker documented.
- All local quality gates and Docker verification pass.
- No production deployment occurs.

## Explicitly out of scope

- messaging and presence
- PSTN, SIP, PBX, production WebRTC calling, and coturn
- eSIM and carrier APIs
- call recording
- billing and payments
- AI and Teams integration
- SMS OTP, SSO/SAML, and passkeys
- production infrastructure or deployment

## Completion report format

Return the fields required by `AGENTS.md`, plus:

```text
DWCO_CONTRACT=DWCO-0.2-ADMIN-SECURITY
ISSUES_CLOSED=
ISSUES_REMAINING=
RATE_LIMIT_RESULT=
SECURITY_EVENT_RESULT=
ADMIN_WORKFLOW_RESULT=
REMOTE_CI_STATUS=
DEPLOYMENT_STATUS=NOT_DEPLOYED
```
