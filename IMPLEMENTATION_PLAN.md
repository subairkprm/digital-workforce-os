# DWCO 0.1 — Foundation Implementation Plan

## Objective
Create the secure platform foundation required before messaging and voice implementation.

## Epics
- DWCO-001 Repository/Foundation
- DWCO-002 Local Development Environment
- DWCO-003 PostgreSQL Foundation
- DWCO-004 Tenant Architecture
- DWCO-005 Authentication
- DWCO-006 RBAC
- DWCO-007 Audit Events
- DWCO-008 Admin Shell
- DWCO-009 CI Pipeline
- DWCO-010 Security Baseline

## Exit condition
A tenant owner can securely authenticate, create/manage workforce records within their tenant, and all critical mutations are authorized and audited.

## Phase 1 reconciliation

- Completed: DWCO-001 through DWCO-006
- Open for implementation gaps: DWCO-007, DWCO-008, and DWCO-010
- Open for external CI/account verification: DWCO-009
- Temporary local enforcement: `docs/LOCAL_CI_FALLBACK.md`
- Completed follow-up boundaries: DWCO 0.2 admin security and DWCO 0.3 workforce operations

## DWCO 0.3 workforce operations

The bounded workforce-operations contract adds tenant invitations, employee reactivation,
department-manager assignment, bounded workforce search/pagination, and user-owned refresh-session
revocation. The closure also makes invitation acceptance and role assignment usable in the web app
and replaces the mobile placeholder with authenticated profile and directory workflows. External
delivery providers and production deployment remain deferred.

## DWCO 0.4 presence

The bounded presence contract adds tenant-derived self-service status, heartbeat expiry, directory
visibility, admin read access, and mobile presence controls. It intentionally uses polling and local
API semantics; production realtime transport, messaging, and communications remain separate future
contracts.

## Explicitly deferred
- external voice/PSTN
- WebRTC production calling
- eSIM/carrier provisioning
- call recording
- AI
- billing
- CRM
- production deployment
