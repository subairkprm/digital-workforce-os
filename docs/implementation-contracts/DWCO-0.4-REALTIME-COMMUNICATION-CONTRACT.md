# DWCO 0.4 — Realtime communication contract (draft)

CONTRACT_STATUS=DRAFT_NOT_APPROVED

## Objective

Extend the merged polling-based presence prerequisite into secure tenant realtime presence transport
and bounded workforce messaging without introducing voice, telecom, AI, billing, or production
deployment.

## Proposed in scope

- Authenticated realtime connections with server-derived tenant and membership context.
- Presence transport preserving existing ownership and 120-second expiry invariants.
- Tenant workforce direct messaging with approved persistence and delivery semantics.
- Bounded history, deterministic pagination, validation, and rate/size limits.
- Mobile foreground/background reconnection behavior and clear delivery-state UX.
- Admin access only where permissioned; no default message-content visibility.
- Migrations, provider-neutral notification boundary, observability events, and tests.
- Retention, deletion, export, failure-mode, and local-rollback documentation.

## Required decisions before approval

1. WebSocket, SSE, or hybrid transport and authenticated connection renewal.
2. Direct-only versus group/conversation model and participant rules.
3. Ordering, idempotency, retry, offline delivery, and receipt semantics.
4. Retention/deletion/export policy and tenant administration boundary.
5. Push notification provider boundary and sensitive-content minimisation.
6. Abuse controls, payload/attachment limits, and reporting boundary.
7. Operations observability without message-content surveillance.
8. Remote CI prerequisite for merge while DEP-001 remains unresolved.

## Security and privacy invariants

- Tenant and actor identity come only from verified server-side session context.
- Every subscription, publish, history, and receipt operation is tenant- and participant-authorized.
- Client-supplied tenant/user identifiers never establish authorization.
- Resume tokens are short-lived, scoped, revocable, and never logged raw.
- Logs, metrics, notifications, and traces exclude message bodies and credentials by default.
- History/fan-out are bounded; rate, connection, payload, and backpressure limits apply.
- Administrative metadata access is permissioned/audited; ordinary exchange is not an employee-
  surveillance audit stream.

## Explicitly out of scope

- PSTN, SIP, PBX, numbering, emergency calling, recording, and production WebRTC calling.
- eSIM, carrier APIs, and mobile-core operation.
- AI summarisation, classification, scoring, training, or communication inference.
- Billing, payments, subscriptions, production deployment, or production data migration.
- Unbounded attachments, public/federated messaging, and external guest communication.

## Proposed ownership and review

ACCOUNTABLE=Implementation Director

RESPONSIBLE=Realtime,Backend,Mobile

REQUIRED_REVIEWERS=Architecture,Identity/Security,DevOps/SRE,QA/Validation

CONSULTED=Admin Web,Integration

## Proposed acceptance criteria

- Required decisions are recorded here or in linked ADRs.
- Migration round-trip passes without behavior changes outside scope.
- Cross-tenant, unauthorized subscribe/publish/history, token expiry/revocation, reconnect,
  ordering/idempotency, bounds, rate-limit, and backpressure tests pass.
- Existing DWCO 0.1–0.4 presence regressions pass.
- Backend, admin, mobile, dependency audit, and Docker readiness gates pass.
- Remote CI is stated truthfully; local evidence is attached if DEP-001 remains open.
- Completion report, dependency updates, rollback, and deployment status are reviewed.

## Deployment boundary

DEPLOYMENT_STATUS=NOT_AUTHORIZED

Approval would authorize bounded development and review only. A separate operations/deployment
contract is required for any shared or production environment.
