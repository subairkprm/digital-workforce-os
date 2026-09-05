# DWCO-GOV 0.2B local CI exact-commit receipt completion report

CONTRACT_ID=DWCO-GOV-0.2B-LOCAL-CI-RECEIPT

IMPLEMENTATION_STATUS=IMPLEMENTED_AND_LOCALLY_VALIDATED

APPLICATION_CHANGES=NONE; no backend, tenant admin, mobile, database, migration, Redis, identity,
messaging, realtime, voice, provider, or production behavior changed

FILES_CHANGED=Local gate receipt writer and hook enforcement; governance receipt parser/API/tests;
dashboard structure, renderer, and CSS; Compose read-only mount; Actions/local test discovery;
repository baseline checks; fallback, parity, dependency, status, contract, and completion documents

SECURITY_BOUNDARY=Receipt data is local, ignored by Git, size-limited, schema-normalized, read-only,
and excludes secrets, environment dumps, arbitrary fields, customer data, production access, and
mutating controls

TEST_RESULTS=Fast gate PASS; clean-tree exact-commit receipt PASS for implementation commit
`93e2a3a0688ac8f532262ca2435314d676d87d79` in 45 seconds on Darwin arm64, Python 3.12.14,
Node 26.8.1, pnpm 11.19.0, and Docker 29.7.2; 35 backend tests PASS at 92% coverage; 8 admin tests
and production build PASS; 5 mobile tests and Expo dependency check PASS; 7 governance parser, HTTP,
receipt-sanitization, digest, HTML structure, and tab/view tests PASS; Python and pnpm audits PASS;
Alembic `0001` through `0005` upgrade/downgrade/re-upgrade PASS; isolated PostgreSQL 17, Redis 7,
API/governance readiness, migration-version, cleanup, and live control-plane survival PASS

READINESS_DECISION=LOCAL_CI_CONTROL_READY_FOR_PRIVATE_INTERNAL_DEVELOPMENT; full product readiness is not
claimed and requires the remaining stage, operations, remote-CI, security, legal, and release gates

KNOWN_GAPS=GitHub Actions and protected required checks remain unavailable; local runner differs from
GitHub-hosted Ubuntu/Node 22; staging, production, device E2E, accessibility review, legal approval,
DWCO 0.5 and later capabilities remain open

DEPLOYMENT_STATUS=LOCAL_DOCKER_ONLY_NOT_AUTHORIZED_FOR_PRODUCTION

ROLLBACK_GUIDANCE=Revert this bounded branch. The product application and database require no data
rollback because this change adds only local CI/governance evidence behavior.
