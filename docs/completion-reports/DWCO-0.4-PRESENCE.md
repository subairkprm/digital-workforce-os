# DWCO 0.4 presence completion report

CONTRACT_ID=DWCO-0.4-PRESENCE

FILES_CHANGED=Presence contract, model, migration, schemas, API router, backend tests, admin presence
view/test, mobile presence lifecycle and directory indicators, architecture/security/plan, CI migration
assertion, and completion report

DATABASE_CHANGES=0004_presence adds tenant/user-scoped presences with unique membership identity,
status, last-seen, expiry, timestamps, and query indexes

API_CHANGES=GET/PUT /api/v1/presence/me; POST /api/v1/presence/me/heartbeat; bounded searchable
GET /api/v1/presence directory listing

SECURITY_CHANGES=Server-derived tenant/user ownership; self-only mutations; employee.read directory
authorization; 120-second offline expiry; bounded listing; rate-limited heartbeats; no surveillance-style
heartbeat audit trail

TESTS=22 backend Phase 1-4 regression/adversarial tests and 7 admin component tests PASS;
cross-tenant isolation, status validation, expiry, heartbeat, and listing bounds included

BUILD_RESULT=LOCAL_CI_FAST=PASS; LOCAL_CI=PASS; DOCKER_CI=PASS; 91% backend coverage;
Alembic 0004 round-trip, PostgreSQL, Redis, health/live/readiness, admin production build/audits,
and mobile checks PASS

KNOWN_ISSUES=GitHub Actions remains account billing-locked; the enforced local pre-commit and
pre-push quality gates remain the active CI fallback

DEFERRED_SCOPE=Production realtime transport, push notifications, presence analytics/retention,
messaging, PSTN, WebRTC production calling, eSIM, carrier APIs, billing, AI, Teams, recording, and
production deployment

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

ROLLBACK_GUIDANCE=Revert the DWCO 0.4 source commit and run alembic downgrade
0003_workforce_operations before discarding presence data; back up any non-disposable database first
