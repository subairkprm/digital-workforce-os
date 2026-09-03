# DWCO 0.3 workforce operations completion report

CONTRACT_ID=DWCO-0.3-WORKFORCE-OPERATIONS

FILES_CHANGED=Contract, invitation/session/workforce backend APIs, migration 0003, admin and public
invitation workflows, functional mobile workforce client, security documentation, and tests

DATABASE_CHANGES=0003_workforce_operations adds invitations, department manager_employee_id,
indexes, and membership.manage permission

API_CHANGES=Invitation create/list/revoke/accept/available roles; auth session list/revoke; own employee
profile; employee search/status/pagination/reactivate; department search/pagination/manager assignment

SECURITY_CHANGES=One-time digested invitation tokens; expiry/revocation/reuse enforcement; tenant-
validated role and manager references; user-owned session access; bounded list limits; audited
administrative mutations; rate-limited invitation acceptance

TESTS=19 backend Phase 1-3 regression/adversarial tests and 6 admin component tests PASS;
cross-tenant role, manager, profile, invitation, and session denial tests included

BUILD_RESULT=LOCAL_CI_FAST=PASS after closure updates; prior LOCAL_CI and DOCKER_CI passed migration
0003, PostgreSQL, Redis, health/live/readiness; final admin build/audits and mobile checks PASS

KNOWN_ISSUES=GitHub Actions remains account billing-locked; Docker Desktop engine stopped after the
successful Docker gate and requires local restart before repeating container verification

DEFERRED_SCOPE=Email/SMS delivery, password-reset delivery, PSTN, WebRTC production calling, eSIM,
carrier APIs, billing, AI, Teams, recording, and production deployment

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

ROLLBACK_GUIDANCE=Revert the DWCO 0.3 source commit and run alembic downgrade 0002_admin_security
before discarding invitation data; take a database backup before any non-disposable rollback
