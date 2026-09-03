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
- Next proposed boundary: `docs/implementation-contracts/DWCO-0.2-ADMIN-SECURITY-CODEX-CONTRACT.md`
- The proposed DWCO 0.2 contract remains a draft until explicitly approved.

## Explicitly deferred
- external voice/PSTN
- WebRTC production calling
- eSIM/carrier provisioning
- call recording
- AI
- billing
- CRM
- production deployment
