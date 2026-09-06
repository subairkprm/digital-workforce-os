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
| DWCO 0.4 | Realtime presence and messaging | 14% | Complete |
| DWCO 0.5 | App-to-app voice/WebRTC | 12% | Draft reviewed; pre-implementation approvals open |
| DWCO 0.6 | Telecom/PSTN/PBX provider integration | 12% | Not started |
| DWCO 0.7 | Mobility/eSIM provider integration | 8% | Not started |
| DWCO 0.8 | Business integrations | 7% | Not started |
| DWCO 0.9 | AI communication intelligence | 6% | Not started |
| DWCO 1.0 | Billing, production operations, and pilot release | 7% | Not started |
| **Total** |  | **100%** | **Approximately 48% accepted** |

Weights express product delivery, not elapsed time. Stage credit is earned only at the acceptance
gate in `docs/roadmap/COMPLETION_MODEL.md`.

## Current checkpoint

DWCO 0.1 through DWCO 0.4 are complete and accepted. DWCO 0.4 includes its presence prerequisite,
durable direct messaging, best-effort realtime delivery, reconnect catch-up, and the reviewed
authorization/session remediation. All required reviewers accepted the bounded local stage;
DevOps/SRE retained external exceptions. Overall accepted completion is approximately 48%.

Remote GitHub Actions is unresolved because workflows fail to start under the repository account
condition documented in `docs/LOCAL_CI_FALLBACK.md`. Enforced local gates exist but do not replace
remote CI or branch protection.

## Delivery governance

The internal governance control-plane journey is documented in
`docs/roadmap/GOVERNANCE_CONTROL_PLANE_PLAN.md`. DWCO-GOV does not contribute product-stage weight
and cannot authorize customer or production operations.

1. The Implementation Director proposes a bounded contract and named owner/reviewers.
2. Architecture, security, data, operations, and dependency risks are reviewed before approval.
3. Implementation occurs on a bounded branch with no scope expansion.
4. QA/Validation verifies acceptance evidence and regressions.
5. A completion report records code, schema, API, security, tests, deployment, rollback, and gaps.
6. Only an approved and merged report may update accepted stage credit.

## Next approval gate

Draft and review a separate DWCO 0.5 app-to-app voice/WebRTC contract. Before implementation, the
gate must approve media architecture, WebRTC identity and consent, TURN/coturn boundaries,
abuse controls, observability, network-failure tests, rollback, and the continued exclusion of
PSTN/SIP/PBX and recording. DWCO 0.5 implementation is not yet authorized.

## Explicit non-authorization

This plan does not authorize production deployment, production data access, PSTN, SIP/PBX, eSIM,
carrier provisioning, AI, billing, payments, recording, or production WebRTC calling.
