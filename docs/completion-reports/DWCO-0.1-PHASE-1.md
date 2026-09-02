# DWCO 0.1 Phase 1 completion report

DWCO_CONTRACT=DWCO-0.1-PHASE-1

IMPLEMENTATION_STATUS=IMPLEMENTED_LOCALLY_PENDING_REMOTE_CI

SOURCE_CHECKPOINT=feature/DWCO-phase-1 from merged main at 03e1b86

FILES_CHANGED=FastAPI backend, Alembic migration, backend security tests, admin web shell, mobile
shell, Docker Compose, CI, environment template, Makefile and README

MIGRATIONS=0001_phase1 creates tenants, users, memberships, employees, departments, roles,
permissions, role_permissions, membership_roles, refresh_sessions and audit_events; SQLite
upgrade-to-head and downgrade-to-base round trip passed locally

API_SURFACE=/health, /livez, /readyz; /api/v1/auth/login, refresh, logout, me; tenant-scoped
employee create/list/get/update/suspend; department list/create/update; read-only audit event list

SECURITY_CONTROLS=Argon2 password hashing; signed short-lived access tokens; SHA-256-digested,
rotating refresh sessions with family reuse revocation; membership-derived tenant context; RBAC;
tenant predicates on all workforce queries; server-only audit creation; restricted local CORS

TEST_RESULTS=Ruff PASS; mypy PASS; pytest 7 PASS; migration upgrade/downgrade PASS; git diff check
PASS

BUILD_RESULTS=Python syntax and backend gates PASS. Admin/mobile typecheck and build deferred to
remote CI because Node.js is not installed locally. Docker startup deferred because Docker is not
installed locally.

KNOWN_GAPS=Remote CI has not run; local machine lacks Node.js and Docker; shells are intentionally
foundation-level and do not include full product workflows

DEFERRED_SCOPE=PSTN, SIP, production WebRTC calling, coturn, eSIM, carrier APIs, call recording,
billing, AI, Teams and production deployment

DEPLOYMENT_STATUS=NOT_DEPLOYED

ROLLBACK_GUIDANCE=Revert the Phase 1 commit for source rollback. On a disposable local database,
run `alembic downgrade base` before reverting. Back up any non-disposable data before schema
rollback. Do not run rollback or deployment against production under this contract.
