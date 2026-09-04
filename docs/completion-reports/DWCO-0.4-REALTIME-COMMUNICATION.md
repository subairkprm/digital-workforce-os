# DWCO 0.4 realtime communication completion report

CONTRACT_ID=DWCO-0.4-REALTIME-COMMUNICATION

FILES_CHANGED=Approved contract and governance references; realtime/messaging operations guide;
configuration; conversation, participant, message, receipt, and permission migration/model/schema;
HTTP messaging and one-time-ticket WebSocket APIs; presence fan-out; provider-neutral notification
adapter; mobile direct-messaging/reconnect UI; metadata-only admin view; adversarial tests; local CI
network retry hardening; Docker build resilience; Expo compatibility patch; and this completion
report

DATABASE_CHANGES=0005_realtime_messaging adds tenant-scoped conversations, exactly two application-
validated direct participants, durable sequenced messages, read receipts, retention indexes,
uniqueness/check constraints, and message.metadata.read/message.retention.manage permissions

API_CHANGES=Direct conversation create/list; bounded sequence-based participant history; durable
idempotent send; explicit read receipt; sender redaction; permissioned aggregate metrics and audited
retention purge; one-time Redis-backed realtime-ticket issue; authenticated WebSocket ping/pong and
server-only presence/message/receipt fan-out

SECURITY_CHANGES=Server-derived tenant/user/membership authority; same-tenant active-member direct
conversation validation; participant-only history and fan-out; one-time SHA-256-keyed 60-second
tickets; no bearer/refresh token in WebSocket URLs; inactive-context revalidation; 4,000-character
message, 8-KiB frame, 100-event queue, 100-record history, and 30-send/minute bounds; 90-day expiry;
sender redaction; metadata-only admin access; content-free notification boundary and operational
logging; permissioned/audited purge; cross-tenant denial events without foreign identifiers

TESTS=31 backend Phase 1-5 regression/adversarial tests and 8 admin component tests PASS; includes
cross-tenant conversation/history/fan-out denial, ordering, duplicate-key conflicts, expired-key
handling, receipts, redaction, retention, metadata authorization, provider failure containment,
rate/payload limits, one-time/expired tickets, membership revalidation, unsupported client publish,
frame limits, store failure, and slow-consumer backpressure

BUILD_RESULT=LOCAL_CI_FAST=PASS; LOCAL_CI=PASS; DOCKER_CI=PASS; 92%
backend coverage; Alembic 0005 upgrade/downgrade/re-upgrade, PostgreSQL 17, Redis 7, health/live/
readiness, admin production build, mobile type/Expo compatibility, Python audit, and admin/mobile
dependency audits PASS. The npm advisory endpoint was intermittently unavailable during consolidated
runs; fail-closed retries did not convert registry outages into false passes, and both current
lockfiles subsequently returned no known vulnerabilities in isolated runs.

KNOWN_ISSUES=GitHub Actions remains account billing-locked, so there is no remote CI attestation;
the live hub is intentionally process-local and requires an approved shared-broker architecture
before horizontal/shared deployment; the inherited mutation limiter is fail-open on Redis outage and
requires production policy review; Starlette TestClient emits one upstream deprecation warning

DEFERRED_SCOPE=Shared/horizontal realtime broker, provider push delivery and credentials, group/
guest/public/federated messaging, attachments, tenant-wide content export, content moderation,
production abuse operations, PSTN, SIP/PBX, production WebRTC calling, eSIM/carrier APIs, billing,
AI, Teams, recording, production infrastructure, data migration, and deployment

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

ROLLBACK_GUIDANCE=Stop local clients and back up any non-disposable database; run alembic downgrade
0004_presence to remove receipts, messages, participants, conversations, and the two messaging
permissions; revert the DWCO 0.4 realtime implementation commit. No shared or production rollback is
authorized by this report

VERSION_CONTROL_STATUS=MERGED_TO_MAIN_AT_D965126_ACCEPTANCE_REVIEW_PENDING_STAGE_WEIGHT_UNCHANGED
