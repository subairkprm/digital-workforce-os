# DWCO implementation plan

`MASTER_PROJECT_PLAN.md` is the product and stage authority. `PROJECT_STATUS.md` is the current
status authority. This file preserves the implementation-epic view and must not override either.

## Foundation epics

| Epic | Outcome | Status | Evidence |
|---|---|---|---|
| DWCO-001 | Repository/foundation | Complete | DWCO 0.1 completion report |
| DWCO-002 | Local development environment | Complete | DWCO 0.1 completion report |
| DWCO-003 | PostgreSQL foundation | Complete | Migration `0001_phase1` |
| DWCO-004 | Tenant architecture | Complete | DWCO 0.1 tests and report |
| DWCO-005 | Authentication | Complete | DWCO 0.1 tests and report |
| DWCO-006 | RBAC | Complete | DWCO 0.1/0.2 tests and reports |
| DWCO-007 | Audit events | Complete | DWCO 0.1/0.2 implementation and reports |
| DWCO-008 | Admin shell | Complete | DWCO 0.1/0.2 implementation and reports |
| DWCO-009 | Remote CI authority | Blocked externally | GitHub Actions startup failure; local fallback active |
| DWCO-010 | Security baseline | Complete | `SECURITY.md` and DWCO 0.2 report |

The former statement that DWCO-007, DWCO-008, and DWCO-010 were open implementation gaps was
stale and is superseded by merged implementation evidence. DWCO-009 remains unresolved: local
quality gates are passing evidence, but they are not GitHub-attested CI.

## Accepted stages

- DWCO 0.1 foundation: complete.
- DWCO 0.2 admin and security: complete.
- DWCO 0.3 workforce operations: complete.

These three accepted stages contribute 34 percentage points under
`docs/roadmap/COMPLETION_MODEL.md`.

## Current acceptance boundary: DWCO 0.4

The next planned stage is realtime communication. A narrow presence contract has already been
implemented and merged, including polling-based status, heartbeat expiry, admin visibility, and
mobile controls. That capability is valid prerequisite evidence, not approval of production
realtime transport or the complete DWCO 0.4 stage.

The stage contract at
`docs/implementation-contracts/DWCO-0.4-REALTIME-COMMUNICATION-CONTRACT.md` was approved for bounded
local implementation and review. PR #21 merged the design based on one-time Redis-backed WebSocket
tickets, HTTP message authority and catch-up, direct conversations, 90-day retention, metadata-only
administration, and a no-op provider-neutral notification boundary. The stage remains pending
acceptance until the required independent reviewers are recorded. Shared infrastructure and
production deployment remain separate decisions.

After DWCO 0.4 acceptance, a separate contract is required before any DWCO 0.5 app-to-app
voice/WebRTC implementation.

## Later boundaries

- App-to-app voice/WebRTC and coturn.
- Authorised-provider PSTN, SIP, and PBX.
- Mobility/eSIM and carrier integration.
- CRM and other integrations.
- AI communication intelligence.
- Billing and payments.
- Production infrastructure and deployment.

No later boundary is authorized by this plan.
