# DWCO 0.2 admin and security completion report

DWCO_CONTRACT=DWCO-0.2-ADMIN-SECURITY

IMPLEMENTATION_STATUS=IMPLEMENTED_LOCALLY_PENDING_BRANCH_REVIEW_AND_REMOTE_CI

SOURCE_CHECKPOINT=codex/DWCO-0.2-implementation from the merged DWCO 0.2 contract lineage

FILES_CHANGED=Role and membership-role APIs; security-event model/API; Redis rate limiting;
functional admin workflows; backend and admin tests; CI, security, environment, contract and
completion documentation

DATABASE_CHANGES=0002_admin_security creates the separate security_events table with optional
tenant/actor scope, category, outcome, sanitized metadata and timestamp indexes

API_CHANGES=Tenant-scoped role list/create/update/delete; membership list and role assignment;
tenant-scoped security-event list; existing workforce mutations gain Redis rate-limit enforcement

SECURITY_CHANGES=Server-known permission assignment; role.manage enforcement; cross-tenant role
and membership denial; auditable role mutations; authentication and tenant-mutation rate limits;
separate security events for failed authentication, refresh reuse, rate limits and authorization
denial; security.read enforcement; no browser-persistent token storage

TESTS=Backend Ruff PASS; mypy PASS; 13 backend tests PASS on Python 3.12 with 90% coverage;
cross-tenant, permission, role, membership-role, rate-limit, refresh-reuse and security-event tests
PASS; 2 admin component tests PASS

BUILD_RESULT=Alembic upgrade/downgrade/upgrade PASS; Next.js 16 typecheck and production build
PASS; Docker Compose image and startup PASS; PostgreSQL migration 0002_admin_security PASS; Redis
PONG; /health, /livez and /readyz returned HTTP 200

KNOWN_ISSUES=GitHub Actions and branch-protection enforcement remain unverified because remote
checks previously could not start under the account billing/spending limitation; Redis failure is
documented to fail open for local request availability while readiness fails; automated security
event retention remains deferred until a production operations contract

DEFERRED_SCOPE=Messaging, presence, PSTN, SIP, PBX, production WebRTC, coturn, eSIM, carrier APIs,
call recording, billing, payments, AI, Teams, SMS OTP, SSO/SAML, passkeys and production deployment

DEPLOYMENT_STATUS=NOT_DEPLOYED

ROLLBACK_GUIDANCE=On a disposable local database run `alembic downgrade 0001_phase1` before
reverting the DWCO 0.2 source commit. Back up non-disposable data before any schema rollback. Do not
run rollback or deployment against production under this contract.

ISSUES_CLOSED=PENDING_MERGE_EVIDENCE_FOR_DWCO-007,DWCO-008,DWCO-010

ISSUES_REMAINING=DWCO-009_REMOTE_CI_ACCOUNT_DEPENDENCY

RATE_LIMIT_RESULT=PASS_FOR_AUTHENTICATION_AND_TENANT_MUTATIONS

SECURITY_EVENT_RESULT=PASS_FOR_TENANT_SCOPE_AND_REQUIRED_CATEGORIES

ADMIN_WORKFLOW_RESULT=PASS_FOR_AUTHENTICATION,PERMISSION_VISIBILITY,WORKFORCE,ROLE,MEMBERSHIP_AND_AUDIT

REMOTE_CI_STATUS=NOT_RUN
