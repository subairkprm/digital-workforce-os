# Digital Workforce Communication OS master project plan

## Authority

This is the highest-level product and stage authority. `PROJECT_STATUS.md` records the current
checkpoint; implementation contracts authorize bounded work; completion reports provide evidence.
Conflicts are reconciled in that order against merged `main`.

## Product north star

Provide Indian SMEs, beginning with a Kerala pilot, one secure tenant-owned workforce identity and
communication system spanning directory, presence, messaging, calling, business voice, mobility,
integrations, and communication intelligence.

## Architectural guardrails

- Tenant identity is derived from authenticated server context.
- Provider services remain behind adapters.
- Administrative mutations are authorized and audited.
- Production access, secrets, and deployment require a separate approved contract.
- Telecom and mobility use authorised providers; DWCO does not operate a carrier core.
- Data minimisation, retention, consent, and regulatory review precede production communications.

## Stage map and weight

| Stage | Product boundary | Weight | Canonical status |
|---|---|---:|---|
| DWCO 0.1 | Foundation, tenancy, identity, core RBAC | 12% | Complete |
| DWCO 0.2 | Admin and security closure | 10% | Complete |
| DWCO 0.3 | Workforce operations | 12% | Complete |
| DWCO 0.4 | Realtime presence and messaging | 14% | Next/planned; draft contract |
| DWCO 0.5 | App-to-app voice/WebRTC | 12% | Not started |
| DWCO 0.6 | Telecom/PSTN/PBX provider integration | 12% | Not started |
| DWCO 0.7 | Mobility/eSIM provider integration | 8% | Not started |
| DWCO 0.8 | Business integrations | 7% | Not started |
| DWCO 0.9 | AI communication intelligence | 6% | Not started |
| DWCO 1.0 | Billing, production operations, and pilot release | 7% | Not started |
| **Total** |  | **100%** | **Approximately 34% accepted** |

Weights express product delivery, not elapsed time. Stage credit is earned only at the acceptance
gate in `docs/roadmap/COMPLETION_MODEL.md`.

## Current checkpoint

DWCO 0.1, 0.2, and 0.3 are complete and accepted. A bounded DWCO 0.4 presence capability has also
been merged and locally validated, but the complete realtime-communication stage has not been
approved or accepted. Overall accepted completion therefore remains approximately 34%.

Remote GitHub Actions is unresolved because workflows fail to start under the repository account
condition documented in `docs/LOCAL_CI_FALLBACK.md`. Enforced local gates exist but do not replace
remote CI or branch protection.

## Delivery governance

1. The Implementation Director proposes a bounded contract and named owner/reviewers.
2. Architecture, security, data, operations, and dependency risks are reviewed before approval.
3. Implementation occurs on a bounded branch with no scope expansion.
4. QA/Validation verifies acceptance evidence and regressions.
5. A completion report records code, schema, API, security, tests, deployment, rollback, and gaps.
6. Only an approved and merged report may update accepted stage credit.

## Next approval gate

Approve, amend, or reject the draft DWCO 0.4 realtime communication contract. Approval must lock
transport choice, messaging semantics, data/retention rules, tenancy and authorization invariants,
mobile/background behavior, observability, abuse limits, migrations, tests, and rollback. It must
also state whether remote CI restoration is a hard prerequisite for implementation or merge.

## Explicit non-authorization

This plan does not authorize production deployment, production data access, PSTN, SIP/PBX, eSIM,
carrier provisioning, AI, billing, payments, recording, or production WebRTC calling.
